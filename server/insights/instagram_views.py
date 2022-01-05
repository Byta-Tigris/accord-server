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
from utils.errors import OAuthAuthorizationFailure
from utils.types import EntityType, Platform




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
        response = {}
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
            response["data"] = []
            for handle in handles:
                response["data"].append(self.serializer(handle).data)
            _status = status.HTTP_201_CREATED
        except Exception as err:
            _status = status.HTTP_400_BAD_REQUEST
            if isinstance(err, (AssertionError, OAuthAuthorizationFailure)):
                response["error"] = str(err)
            else:
                response["error"] = "Unable to retrieve information from Instagram"
                logger.error(err)
        return Response(response, status=_status)


class RetrievePlatformInsights(APIView):
    """
    Retrieves collective platform insights
    If username is provided then collective_platform_metric will be sent after filtering private metrics.
    Else account will be used to retrieve platform metric of own handles

    [filters]:
    start_date -- Start of the date time
    end_date -- End of the date time
    
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, AllowAny]
    digger = InstagramDigger()


class RetrieveInstagramHandleInsights(APIView):
    """
    Retrieve insights of single instagram handle
    If username is provided then insight of instagram handle will be provided after filtering private metrics.
    Else account will be used to retrieve instagram insights

    [filters]:
    start_date -- Start of the date
    end_date -- End of the date
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, AllowAny]
    digger = InstagramDigger()

