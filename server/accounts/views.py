from typing import Union
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from log_engine.log import logger
from django.conf import settings


from accounts.models import Account
from utils import querydict_to_dict
from utils.errors import AccountAlreadyExists, PasswordValidationError

# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def is_username_valid_api_view(request) -> Response:
    username = request.POST['username']
    data = {"is_valid": False, "username": username}
    if Account.is_valid_username_structure(username) and not Account.objects.check_username_exists(username):
        data["is_valid"] = True
    return Response(data, status=status.HTTP_200_OK)


class CreateAccounAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        data = querydict_to_dict(request.POST)
        response_data = {}
        _status = status.HTTP_400_BAD_REQUEST
        try:
            assert "email" in data, "Email is required for creating account"
            assert "password" in data, "Password is required for creating account"
            assert "username" in data and Account.is_valid_username_structure(
                data['username']), "Username is required for creating account"
            assert not Account.objects.check_username_exists(
                data["username"]), f"Username {data['username']} already exists."
            instance_: Union[User, Account] = Account.objects.create(**data)
            user = instance_
            if isinstance(instance_, Account):
                response_data["username"] = instance_.username
                response_data["entity_type"] = instance_.entity_type
                user = instance_.user
            token, _ = Token.objects.get_or_create(user=user)
            response_data ["token"] = token.key
            
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
            else:
                response_data = {
                    "error": f"Unable to accept the request. Try again later"
                }
                if settings.DEBUG:
                    raise err
                else:
                    logger.error(err)
            _status = status.HTTP_406_NOT_ACCEPTABLE
        finally:
            return Response(response_data, status=_status)




class AccountLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        _status = status.HTTP_401_UNAUTHORIZED
        response_body = {}
        data = querydict_to_dict(request.POST)
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
                logger.error(err)                
                
        finally:
            return Response(response_body, status=_status)
