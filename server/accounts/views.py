from datetime import datetime
from typing import Dict, List, Tuple, Union
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.core.exceptions import BadRequest, ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from accounts.serializers import AccountSerializer, SocialMediaHandlePublicSerializer
from digger.google.request_manager import GoogleRequestManager
from digger.google.request_struct import GoogleUserInfoRequestStruct
from digger.google.response_struct import GoogleUserInfoResponseStruct
from insights.models import InstagramHandleMetricModel, SocialMediaHandleMetrics, YoutubeHandleMetricModel
from log_engine.log import logger

import json
from django.core.validators import validate_email
from django.conf import settings

from accounts.models import Account, SocialMediaHandle
from utils import is_in_debug_mode, is_in_testing_mode
from utils import errors
from utils.errors import AccountAlreadyExists, AccountAuthenticationFailed, AccountDoesNotExists, GoogleOAuthAuthorizationFailure, InvalidAuthentication, NoAccountsExistsRelatedWithEmail, NoSocialMediaHandleExists, OAuthPlatformAuthorizationFailure, PasswordValidationError

# Create your views here.


def attach_httponly_cookie(response: Response, response_data: Dict) -> Response:
    MAX_AGE: int = 60*60*24*60  # 60 days
    if "token" in response_data:
        token = response_data["token"]
        del response_data["token"]
        response = Response(response_data, status=response.status_code)
        response.set_cookie(
            "AUTH_TOKEN", token,
            domain=settings.FRONT_END_DOMAIN,
            max_age=MAX_AGE,
            httponly=True,
            secure=is_in_debug_mode() == False,
        )
    return response


def remove_httponly_cookie(response: Response) -> Response:
    response.set_cookie(
        "AUTH_TOKEN", "",
        domain=settings.FRONT_END_DOMAIN,
        expires=datetime(year=2022, month=1, day=1),
        httponly=True,
        secure=is_in_debug_mode() == False,
    )
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def is_username_valid_api_view(request) -> Response:
    body = request.body
    post_data = json.loads(body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    try:
        assert "username" in post_data and len(
            post_data["username"]) > 3, "Username provided must be valid"
        username = post_data['username']
        response = {"is_valid": False, "username": username}
        response["is_valid"] = Account.is_valid_username_structure(
            username) and (not Account.objects.check_username_exists(username))
        _status = status.HTTP_200_OK
    except Exception as err:
        response["is_valid"] = False
    return Response(response, status=_status)


@api_view(['POST'])
@permission_classes([AllowAny])
def is_user_with_email_exists(request: Request) -> Response:
    body = request.body
    data = json.loads(body)
    response = {"exists": False}
    _status = status.HTTP_400_BAD_REQUEST
    try:
        assert "email" in data and len(data["email"]), "Email must be provided"
        validate_email(data["email"])
        response["exists"] = User.objects.filter(email=data["email"]).exists()
        _status = status.HTTP_200_OK
    except Exception as err:
        response["exists"] = False
    return Response(response, status=_status)


class AuthenticationEngine:
    request_manager = GoogleRequestManager()

    def verify_and_retrieve_info_from_google(self, access_token: str, email: str = None) -> Tuple[bool, Dict[str, str]]:
        if is_in_testing_mode():
            return True, {"email": email}
        request = GoogleUserInfoRequestStruct(access_token)
        response: GoogleUserInfoResponseStruct = request(self.request_manager)
        if response.error:
            raise OAuthPlatformAuthorizationFailure("Google")
        return response.is_email_verified, {
            "email": response.email,
            "first_name": response.first_name,
            "last_name": response.last_name,
            "avatar": response.avatar
        }


class CreateAccounAPIView(APIView, AuthenticationEngine):
    permission_classes = [AllowAny]
    request_manager = GoogleRequestManager()

    def post(self, request: Request) -> Response:
        data: Dict = json.loads(request.body)
        response_data = {}
        _status = status.HTTP_400_BAD_REQUEST
        try:
            for key, value in data.items():
                if value == None:
                    del data[key]

            assert "email" in data and data["email"], "Email is required for creating account"
            assert "username" in data and Account.is_valid_username_structure(
                data['username']), "Username is required for creating account"
            assert not Account.objects.check_username_exists(
                data["username"]), f"Username {data['username']} already exists."

            if isinstance(request.user, User) and request.account is not None:
                instance_ = Account.objects.create_account(
                    request.user, **data)
            else:
                assert "access_token" in data, "Email is not authorized"
                is_email_verified, info = self.verify_and_retrieve_info_from_google(
                    data["access_token"])
                # print(is_email_verified, info)
                assert is_email_verified and info["email"] == data["email"], "Invalid Email data"
                data = info | data
                instance_: Union[User,
                                 Account] = Account.objects.create(**data)
            user = instance_
            if isinstance(instance_, Account):
                response_data["username"] = instance_.username
                response_data["entity_type"] = instance_.entity_type
                user = instance_.user
            token, _ = Token.objects.get_or_create(user=user)
            response_data["token"] = token.key
            _status = status.HTTP_201_CREATED

        except AssertionError as err:

            response_data = {"error": str(err)}
            _status = status.HTTP_400_BAD_REQUEST
        except Exception as err:

            if isinstance(err, ValidationError):
                response_data = {
                    "error", f"{data['email']} is not a valid email."}
            elif isinstance(err, PasswordValidationError):
                response_data = {
                    "error": str(err)}
            elif isinstance(err, AccountAlreadyExists):
                response_data = {
                    "error": f"Account in {data['entity_type']} with email {data['email']} already exists"
                }
            elif isinstance(err, OAuthPlatformAuthorizationFailure):
                response_data = {
                    "error": f"Provided email is not verified"
                }
            else:
                response_data = {
                    "error": f"Unable to accept the request. Try again later"
                }
                if is_in_debug_mode():
                    raise err
                else:
                    logger.error(err)
            _status = status.HTTP_406_NOT_ACCEPTABLE

        response = Response(response_data, status=_status)
        return attach_httponly_cookie(response, response_data)


class AccountLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        _status = status.HTTP_401_UNAUTHORIZED
        response_body = {}
        data = json.loads(request.body)

        try:
            assert "username" in data, "Username is required for login"
            assert "password" in data, "Password is required for login"
            queryset = Account.objects.filter(username=data['username'])
            if not queryset.exists():
                response_body["error"] = "No account related to that username was found."
                _status = status.HTTP_404_NOT_FOUND
            else:
                account: Account = queryset.first()
                user: User = account.user
                if not user.check_password(data["password"]):
                    response_body["error"] = "Password is incorrect."
                else:
                    token: Token = Token.objects.get(user=user)
                    response_body["token"] = token.key
                    response_body["entity_type"] = account.entity_type
                    response_body["username"] = account.username
                    response_body["avatar"] = account.avatar
                    _status = status.HTTP_202_ACCEPTED
        except Exception as err:
            response_body["error"] = str(err)
            _status = status.HTTP_400_BAD_REQUEST
            if isinstance(err, AssertionError):
                pass
            elif isinstance(err, Token.DoesNotExist):
                # TODO: Need to find some work around to avoid token missing
                response_body["error"] = "Account related with username was not found."
                _status = status.HTTP_404_NOT_FOUND
            else:
                response_body = {
                    "error": f"Unable to accept the request. Try again later"
                }
                if is_in_debug_mode():
                    raise err
                else:
                    logger.error(err)
                _status = status.HTTP_406_NOT_ACCEPTABLE

        return attach_httponly_cookie(Response(response_body, status=_status), response_body)


class AccountLogoutAPIVIew(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        _status = status.HTTP_403_FORBIDDEN
        response = Response({"logged_out": True}, status=_status)
        if request.account is not None:
            _status = status.HTTP_202_ACCEPTED
            response = remove_httponly_cookie(
                Response({"logged_out": True}, status=_status))
        return response


class RetrieveAndEditAccountAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    ACCOUNT_EDIT_WHITELIST_FIELDS = (
        "contact", "description", "avatar", "banner_image")
    USER_EDIT_WHITELIST_FIELDS = ("first_name", "last_name")
    serializer_class = AccountSerializer

    def get_account_details(self, account: Account) -> Dict[str, str]:
        return self.serializer_class(account).data

    def get(self, request: Request, **kwargs) -> Response:
        _status = status.HTTP_200_OK
        response_body = {}
        try:
            account: Account = request.account
            if account is None:
                raise AccountAuthenticationFailed()
            response_body["data"] = self.get_account_details(account)
            response_body["data"]["is_account_owner"] = True

        except Exception as err:
            _status = status.HTTP_400_BAD_REQUEST
            response_body = {}
            if isinstance(err, AccountAuthenticationFailed):
                _status = status.HTTP_404_NOT_FOUND
                response_body["error"] = f"No account was found"
            elif isinstance(err, BadRequest):
                response_body["error"] = f"Bad request parameters"
            else:
                logger.error(err)
        return Response(response_body, status=_status)

    def post(self, request: Request) -> Response:
        _status = status.HTTP_401_UNAUTHORIZED
        response_body = {}
        try:
            body = request.body
            data = json.loads(body)
            if not request.account:
                raise InvalidAuthentication("")
            account: Account = request.account
            user: User = account.user
            for key, packet in data.items():
                if key in self.ACCOUNT_EDIT_WHITELIST_FIELDS and "data" in packet and len(packet["data"]) > 0:
                    setattr(account, key, packet["data"])
                elif key in self.USER_EDIT_WHITELIST_FIELDS and "data" in packet and len(packet["data"]) > 0:
                    setattr(user, key, packet["data"])
            account.save()
            user.save()
            _status = status.HTTP_202_ACCEPTED
            response_body["data"] = self.serializer_class(account).data
            response_body["is_account_owner"] = True
        except Exception as err:
            if isinstance(err, InvalidAuthentication):
                _status = status.HTTP_403_FORBIDDEN
                response_body = {"error": repr(err)}
            elif isinstance(err, (AssertionError, ValueError, KeyError)):
                _status = status.HTTP_400_BAD_REQUEST
                response_body = {"error": repr(err)}
            else:
                logger.error(err)
        return Response(response_body, status=_status)


class RetrieveAccountsFromEmailView(APIView, AuthenticationEngine):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        _status = status.HTTP_401_UNAUTHORIZED
        response = {}
        data = json.loads(request.body)
        try:
            assert "access_token" in data and data["access_token"], "Email must be authenticated"
            is_email_verified, info = self.verify_and_retrieve_info_from_google(
                data["access_token"])
            if not (is_email_verified and info["email"]):
                raise InvalidAuthentication(data["username"])
            accounts_queryset: QuerySet[Account] = Account.objects.select_related(
                "user").filter(user__email=info["email"])
            if not accounts_queryset.exists():
                raise NoAccountsExistsRelatedWithEmail(info["email"])
            response["data"] = [{"username": account.username,
                                 "avatar": account.avatar} for account in accounts_queryset]
            _status = status.HTTP_200_OK
        except Exception as err:
            _status = status.HTTP_400_BAD_REQUEST
            if isinstance(err, (InvalidAuthentication, NoAccountsExistsRelatedWithEmail, OAuthPlatformAuthorizationFailure)):
                _status = status.HTTP_403_FORBIDDEN
                response = {"error": repr(err)}
            elif isinstance(err, (AssertionError, ValueError, KeyError)):
                _status = status.HTTP_400_BAD_REQUEST
                response = {"error": repr(err)}
            else:
                logger.error(err)
        return Response(response, status=_status)


class ResetPasswordView(APIView, AuthenticationEngine):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        _status = status.HTTP_401_UNAUTHORIZED
        response = {}
        data = json.loads(request.body)
        try:
            assert "email" in data, "Email not provided"
            assert "password" in data and data["password"] and len(
                data["password"]) > 5, "Valid password is required"
            assert "access_token" in data and data["access_token"], "Email must be authenticated"

            is_email_verified, info = self.verify_and_retrieve_info_from_google(
                data["access_token"])
            if (not is_email_verified) or info.get("email", None) == None or (info["email"] != data["email"]):
                raise GoogleOAuthAuthorizationFailure()
            user_queryset: QuerySet[User] = User.objects.filter(
                email=info["email"])
            if not user_queryset.exists():
                raise NoAccountsExistsRelatedWithEmail(data["email"])
            user: User = user_queryset.first()
            user.set_password(data["password"])
            user.save()
            _status = status.HTTP_202_ACCEPTED
            response["data"] = "Password change successfull"

        except Exception as err:

            _status = status.HTTP_400_BAD_REQUEST
            if isinstance(err, (GoogleOAuthAuthorizationFailure, AccountDoesNotExists, OAuthPlatformAuthorizationFailure)):
                _status = status.HTTP_403_FORBIDDEN
                response = {"error": repr(err)}
            elif isinstance(err, (AssertionError, ValueError, KeyError)):
                _status = status.HTTP_400_BAD_REQUEST
                response = {"error": repr(err)}
            else:
                if is_in_testing_mode():
                    raise err
                else:
                    logger.error(err)
        return Response(response, status=_status)


class ChangePasswordView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        _status = status.HTTP_401_UNAUTHORIZED
        response = {}
        data = json.loads(request.body)
        try:
            assert "current_password" in data and data["current_password"], "Current password must be provided"
            assert "password" in data and data["password"] and len(
                data["password"]) > 7, "Password validity is required for creating account"
            if not request.account:
                raise InvalidAuthentication("")
            account: Account = request.account
            user: User = account.user
            if not user.check_password(data["current_password"]):
                raise PasswordValidationError(data["current_password"])
            user.set_password(data["password"])
            user.save()
            _status = status.HTTP_202_ACCEPTED
            response["data"]["updated"] = user.check_password(data["password"])
        except Exception as err:
            _status = status.HTTP_400_BAD_REQUEST
            if isinstance(err, (InvalidAuthentication, PasswordValidationError)):
                _status = status.HTTP_403_FORBIDDEN
                response = {"error": repr(err)}
            elif isinstance(err, (AssertionError, ValueError, KeyError)):
                _status = status.HTTP_400_BAD_REQUEST
                response = {"error": repr(err)}
            else:
                logger.error(err)
        return Response(response, status=_status)


class RetrieveAndDeleteSocialHandlesAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer = SocialMediaHandlePublicSerializer

    def get_serialized_handles(self, account: Account) -> List[Dict]:
        handles: QuerySet[SocialMediaHandle] = SocialMediaHandle.objects.filter(
            Q(account=account))
        return [dict(handle) for handle in self.serializer(handles, many=True)]

    def get(self, request: Request) -> Response:
        _status = status.HTTP_400_BAD_REQUEST
        response = {}
        try:
            if not request.account:
                raise AccountAuthenticationFailed()
            account: Account = request.account
            response["data"] = self.get_serialized_handles(account)
            _status = status.HTTP_200_OK
        except Exception as err:
            response["error"] = str(err)
        return Response(response, status=_status)

    def post(self, request: Request) -> Response:
        """
        Changes visibility of social media handles by tweaking is_disabled property
        Request Body:
            handle_ids: List[handle_id]
        """
        _status = status.HTTP_400_BAD_REQUEST
        response = {}
        data: Dict = json.load(request.body)
        try:
            if not request.account:
                raise AccountAuthenticationFailed()
            account: Account = request.account
            handle_ids: List[str] = data.get("handle_ids", [])
            handles: QuerySet[SocialMediaHandle] = SocialMediaHandle.objects.filter(
                Q(handle_uid__in=handle_ids))
            if handles.exists():
                handles.delete()
            response["data"] = self.get_serialized_handles(account)
            _status = status.HTTP_202_ACCEPTED
        except Exception as err:
            response["error"] = str(err)
            if not is_in_debug_mode():
                logger.error(err)
        return Response(response, status=_status)


class PlatformMetricVisibilityView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get_metrics(private_metrics: Dict[str, List[str]] = []) -> List[Dict[str, Union[str, bool]]]:
        """
        List[Struct{platform, metric_name, is_visible:bool}]
        """
        metrics = []
        metric_classes: List[SocialMediaHandleMetrics] = [
            InstagramHandleMetricModel, YoutubeHandleMetricModel]
        for metric_class in metric_classes:
            platform = metric_class.objects.platform
            for metrc_name in metric_class.get_metric_names():
                data = {"metric_name": metrc_name,
                        "platform": platform, "is_visible": True}
                if platform in private_metrics and metrc_name in private_metrics[platform]:
                    data["is_visible"] = False
                metrics.append(data)
        return metrics

    def get(self, request: Request) -> Response:
        _status = status.HTTP_400_BAD_REQUEST
        response = {}
        try:
            if not request.account:
                raise AccountAuthenticationFailed()
            account: Account = request.account
            _status = status.HTTP_200_OK
            response["data"] = self.get_metrics(
                account.platform_specific_private_metric)
        except Exception as err:
            if isinstance(err, AccountAuthenticationFailed):
                response["error"] = str(err)
            else:
                logger.error(err)
        return Response(response, status=_status)

    def post(self, request: Request) -> Response:
        """
        Request Body:
            metrics: List[Struct{platform, metric_name}]
        """
        _status = status.HTTP_400_BAD_REQUEST
        response = {}
        data = json.loads(request.body)
        try:
            if not request.account:
                raise AccountAuthenticationFailed()
            assert "metrics" in data, "Metrics must be provided"
            metrics: List[Dict[str, str]] = data["metrics"]
            account: Account = request.account
            platform_specific_private_metric: Dict[str, List[str]
                                                   ] = account.platform_specific_private_metric
            for metric in metrics:
                if metric["platform"] not in platform_specific_private_metric:
                    platform_specific_private_metric[metric["platform"]] = []
                if metric["metric_name"] in platform_specific_private_metric[metric["platform"]]:
                    platform_specific_private_metric[metric["platform"]].remove(
                        metric["metric_name"])
                else:
                    platform_specific_private_metric[metric["platform"]].append(
                        metric["metric_name"])
            account.platform_specific_private_metric = platform_specific_private_metric
            account.save()
            _status = status.HTTP_202_ACCEPTED
            response["data"] = self.get_metrics(
                account.platform_specific_private_metric)
        except Exception as err:
            if isinstance(err, (AccountAuthenticationFailed, AssertionError)):
                response["error"] = str(err)
            else:
                logger.error(err)
        return Response(response, status=_status)
