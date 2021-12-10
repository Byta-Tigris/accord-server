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


from accounts.models import Account
from utils.errors import PasswordValidationError

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
        data = request.POST
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
                user = instance_.user
            token, _ = Token.objects.get_or_create(user=user)
            response_data = {
                "token": token.key
            }
            _status = status.HTTP_201_CREATED

        except AssertionError as err:
            response_data = {"error", err}
            _status = status.HTTP_400_BAD_REQUEST
        except Exception as err:
            if isinstance(err, ValidationError):
                response_data = {
                    "error", f"{data['email']} is not a valid email."}
            elif isinstance(err, PasswordValidationError):
                response_data = {
                    "error": f"{data['password']} is not a valid password"}
            _status = status.HTTP_406_NOT_ACCEPTABLE
        finally:
            return Response(response_data, status=_status)
