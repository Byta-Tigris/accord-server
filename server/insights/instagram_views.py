from datetime import datetime, timedelta
import json
from typing import Dict, Union
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import status
from accounts.models import Account
from digger.instagram.digger import InstagramDigger
from insights.serializers import SocialMediaHandleSerializer
from log_engine.log import logger
from utils import date_to_string, get_current_time, string_to_date
from utils.errors import AccountDoesNotExists, OAuthAuthorizationFailure
from utils.types import Platform
from django.db.models import QuerySet




class CreateInstagramHandlesView(APIView):
    """
    Recieves short_lived_token which is then converted to long_lived_token
    Long lived token will be used to fetch all instagram accounts
    User will send short_lived_token, along with redirect_uri which will be used
    to generate long_lived_token
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    digger = InstagramDigger()
    serializer = SocialMediaHandleSerializer

    def post(self, request: Request) -> Response:
        _status = status.HTTP_400_BAD_REQUEST
        response = {"data": []}
        try:
            assert request.account is not None, "Account must exists for using this service"
            account: Account = request.account
            body = request.body
            data = json.loads(body)
            assert "token" in data, "OAuth authorization must be completed."
            short_lived_token: str = data["token"]
            token_response = self.digger.get_long_lived_token(short_lived_token)
            if token_response.error:
                raise OAuthAuthorizationFailure(Platform.Instagram)
            handles = self.digger.create_or_update_social_media_handles(request.account, token_response.access_token, token_response.expires_in)
            serilzed = self.serializer(handles, many=True)
            response["data"] = [dict(data) for data in serilzed.data]
            _status = status.HTTP_201_CREATED
        except Exception as err:
            _status = status.HTTP_400_BAD_REQUEST
            if isinstance(err, (AssertionError, OAuthAuthorizationFailure)):
                response["error"] = str(err)
            else:
                response["error"] = "Unable to retrieve information from Instagram"
                logger.error(err)
        return Response(response, status=_status)





