import json
from typing import Dict, Union
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import status
from accounts.models import Account




class CreateOrResyncInstagramHandles(APIView):
    """
    Recieves short_lived_token which is then converted to long_lived_token
    Long lived token will be used to fetch all instagram accounts
    User will send short_lived_token, along with redirect_uri which will be used
    to generate long_lived_token
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


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

