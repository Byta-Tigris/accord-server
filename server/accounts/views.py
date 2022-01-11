from typing import Dict, Tuple, Union
from django.db.models.query import QuerySet
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
from accounts.serializers import AccountSerializer
from digger.google.request_manager import GoogleRequestManager
from digger.google.request_struct import GoogleUserInfoRequestStruct
from digger.google.response_struct import GoogleUserInfoResponseStruct
from log_engine.log import logger

import json
from django.core.validators import validate_email


from accounts.models import Account
from utils import is_in_debug_mode
from utils import errors
from utils.errors import AccountAlreadyExists, AccountDoesNotExists, InvalidAuthentication, NoAccountsExists, OAuthAuthorizationFailure, PasswordValidationError

# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def is_username_valid_api_view(request) -> Response:
    body = request.body
    post_data = json.loads(body)
    response = {}
    _status = status.HTTP_400_BAD_REQUEST
    try:
        assert "username" in post_data and len(
            post_data["username"]) > 0, "Username provided must be valid"
        username = post_data['username']
        response = {"is_valid": False, "username": username}
        response["is_valid"] = Account.is_valid_username_structure(
            username) and not Account.objects.check_username_exists(username)
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
    except Exception as err:
        response["exists"] = False
    return Response(response, status=_status)


class AuthenticationEngine:
    request_manager = GoogleRequestManager()

    def verify_and_retrieve_info_from_google(self, access_token: str) -> Tuple[bool, Dict[str, str]]:
        request = GoogleUserInfoRequestStruct(access_token)
        response: GoogleUserInfoResponseStruct = request(self.request_manager)
        if response.error:
            raise OAuthAuthorizationFailure("Google")
        return response.is_email_verified, {
            "email": response.email,
            "first_name": response.first_name,
            "last_name": response.last_name,
            "avatar": response.avatar
        }


class CreateAccounAPIView(APIView, AuthenticationEngine):
    permission_classes = [AllowAny]
    request_manager = GoogleRequestManager()

    def verify_and_retrieve_info_from_google(self, access_token: str) -> Tuple[bool, Dict[str, str]]:
        request = GoogleUserInfoRequestStruct(access_token)
        response: GoogleUserInfoResponseStruct = request(self.request_manager)
        if response.error:
            raise OAuthAuthorizationFailure("Google")
        return response.is_email_verified, {
            "email": response.email,
            "first_name": response.first_name,
            "last_name": response.last_name,
            "avatar": response.avatar
        }

    def post(self, request: Request) -> Response:
        data = json.loads(request.body)
        response_data = {}
        _status = status.HTTP_400_BAD_REQUEST
        try:
            assert "email" in data, "Email is required for creating account"
            assert "password" in data, "Password is required for creating account"
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
            response_data = {"error", str(err)}
            _status = status.HTTP_400_BAD_REQUEST
        except Exception as err:
            if isinstance(err, ValidationError):
                response_data = {
                    "error", f"{data['email']} is not a valid email."}
            elif isinstance(err, PasswordValidationError):
                response_data = {
                    "error": f"{data['password']} is not a valid password"}
            elif isinstance(err, AccountAlreadyExists):
                response_data = {
                    "error": f"Account in {data['entity_type']} with email {data['email']} already exists"
                }
            elif isinstance(err, OAuthAuthorizationFailure):
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
        finally:
            return Response(response_data, status=_status)


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

        finally:
            return Response(response_body, status=_status)


class EditAccountAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    ACCOUNT_EDIT_WHITELIST_FIELDS = (
        "contact", "description", "avatar", "banner_image")
    USER_EDIT_WHITELIST_FIELDS = ("first_name", "last_name")
    serializer_class = AccountSerializer

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
            if "password" in data:
                password_packet: Dict[str, str] = data["password"]
                assert "old_password" in password_packet and password_packet["old_password"] and len(
                    password_packet["old_password"]) > 0, "Provided data is incomplete or invalid"
                if not user.check_password(password_packet["old_password"]):
                    raise InvalidAuthentication(account.username)
                user.set_password(password_packet["password"])
                user.save()
                _status = status.HTTP_202_ACCEPTED
                response_body = {"data": "Password change is sucessful"}
            else:
                for key, packet in data.items():
                    if key in self.ACCOUNT_EDIT_WHITELIST_FIELDS and "data" in packet and len(packet["data"]) > 0:
                        setattr(account, key, packet["data"])
                    elif key in self.USER_EDIT_WHITELIST_FIELDS and "data" in packet and len(packet["data"]) > 0:
                        setattr(user, key, packet["data"])
                account.save()
                user.save()
                _status = status.HTTP_202_ACCEPTED
                response_body["data"] = self.serializer_class(account).data
                response_body["data"]["full_name"] = user.get_full_name()
                response_body["data"]["first_name"] = user.first_name
                response_body["data"]["last_name"] = user.last_name

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


class RetrieveAccountsView(APIView, AuthenticationEngine):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        _status = status.HTTP_401_UNAUTHORIZED
        response = {}
        data = json.loads(request.body)
        try:
            assert "access_token" in data and data["access_token"], "Email must be authenticated"
            is_email_verified, info = self.verify_and_retrieve_info_from_google(data["access_token"])
            if not (is_email_verified and info["email"]):
                raise InvalidAuthentication(data["username"])
            accounts_queryset: QuerySet[Account] = Account.objects.select_related("user").filter(user__email=info["email"])
            if not accounts_queryset.exists():
                raise NoAccountsExists(info["email"])
            response["data"] = [{"username": account.username, "avatar": account.avatar} for account in accounts_queryset]
            _status = status.HTTP_200_OK
        except Exception as err:
            _status = status.HTTP_400_BAD_REQUEST
            if isinstance(err, InvalidAuthentication, NoAccountsExists, OAuthAuthorizationFailure):
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
            assert "username" in data and data["username"], "Username must be provided"
            assert "password" in data and data["password"], "Password must be provided"
            assert "access_token" in data and data["access_token"], "Email must be authenticated"

            account_queryset: QuerySet[Account] = Account.objects.select_related('user').filter(username=data["username"])
            if not account_queryset.exists():
                raise AccountDoesNotExists(data["username"])
            account: Account = account_queryset.first()
            user: User = account.user
            is_email_verified, info = self.verify_and_retrieve_info_from_google(data["access_token"])
            if not (is_email_verified and info["email"] == user.email):
                raise InvalidAuthentication(data["username"])
            user.set_password(data["password"])
            user.save()

            token: Token = Token.objects.get(user=user)
            _status = status.HTTP_202_ACCEPTED
            response["data"] = {
                "token": token.key,
                "username": account.username
            }

        except Exception as err:
            _status = status.HTTP_400_BAD_REQUEST
            if isinstance(err, InvalidAuthentication, AccountDoesNotExists, OAuthAuthorizationFailure):
                _status = status.HTTP_403_FORBIDDEN
                response = {"error": repr(err)}
            elif isinstance(err, (AssertionError, ValueError, KeyError)):
                _status = status.HTTP_400_BAD_REQUEST
                response = {"error": repr(err)}
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
            assert "password" in data and data["password"], "A valid password must be provided"
            if not request.account:
                raise InvalidAuthentication("")
            account: Account = request.account
            user: User = account.user
            if not user.check_password(data["current_password"]):
                raise PasswordValidationError(data["current_password"])
            user.set_password(data["password"])
            user.save()
            _status = status.HTTP_202_ACCEPTED
            response["body"] = "Password updated"
        except Exception as err:
            _status = status.HTTP_400_BAD_REQUEST
            if isinstance(err, InvalidAuthentication, PasswordValidationError):
                _status = status.HTTP_403_FORBIDDEN
                response = {"error": repr(err)}
            elif isinstance(err, (AssertionError, ValueError, KeyError)):
                _status = status.HTTP_400_BAD_REQUEST
                response = {"error": repr(err)}
            else:
                logger.error(err)
        return Response(response, status=_status)

            


class RetrieveProfileAPIView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny, IsAuthenticated]
    serializer_class = AccountSerializer

    def get_account_details(self, account: Account) -> Dict[str, str]:
        return self.serializer_class(account).data

    def get(self, request: Request, **kwargs) -> Response:
        username: str = kwargs.get("username", None)
        _status = status.HTTP_200_OK
        response_body = {}
        try:
            account: Account = request.account
            if username is None and account is None:
                raise BadRequest()
            if (account and username and account.username != username) or (account is None and username is not None):
                account_queryset: QuerySet[Account] = Account.objects.filter(
                    username=username)
                if not account_queryset.exists():
                    raise AccountDoesNotExists(username)
                account: Account = account_queryset.first()
            response_body["data"] = self.get_account_details(account)
            response_body["data"]["is_account_owner"] = (username is not None and request.account is not None and request.account.username == username) or (
                username is None and request.account is not None)

        except Exception as err:
            _status = status.HTTP_400_BAD_REQUEST
            response_body = {}
            if isinstance(err, AccountDoesNotExists):
                _status = status.HTTP_404_NOT_FOUND
                response_body["error"] = f"No account related with username {username} was found"
            elif isinstance(err, BadRequest):
                response_body["error"] = f"Bad request parameters"
            else:
                logger.error(err)
        return Response(response_body, status=_status)
