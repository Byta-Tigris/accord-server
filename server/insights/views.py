from datetime import datetime, timedelta

from typing import Dict, Tuple, Union
from django.core.exceptions import BadRequest
from django.db.models.query_utils import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import QuerySet

from rest_framework import status
from accounts.models import Account, SocialMediaHandle
from digger.base.types import Digger
from digger.instagram.digger import InstagramDigger
from digger.youtube.digger import YoutubeDigger
from insights.serializers import SocialMediaHandleSerializer
from log_engine.log import logger
from utils import date_to_string, datetime_to_unix_timestamp_string, get_current_time, string_to_date, unix_string_to_datetime
from utils.datastructures import MetricTable
from utils.errors import AccountDoesNotExists, NoSocialMediaHandleExists
from utils.types import Platform


class RetrieveSocialMediaHandleView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, AllowAny]
    serializer_class = SocialMediaHandleSerializer

    def get(self, request: Request, **kwargs) -> Response:
        _status = status.HTTP_400_BAD_REQUEST
        response = {}
        username: str = kwargs.get("username", None)
        handle_id: str = kwargs.get("handle", None) 
        platform = None
        if "platform" in request.GET and len(request.GET["platform"]) > 0:
            platform = request.GET["platform"][0]
        try:
            query: Q = None
            account: Account = request.account
            if handle_id is not None:
                query  = Q(handle_uid = handle_id)
            elif username is not None:
                query = Q(account__username=username)
            elif account is not None:
                query  = Q(account=account)
            if platform and query:
                query &= Q(platform = platform)
            if query is None:
                raise BadRequest("Username must be provided")
            query &= Q(is_disabled=False)
            handles: QuerySet[SocialMediaHandle] = SocialMediaHandle.objects.select_related('account').filter(query)
            if not handles.exists():
                raise NoSocialMediaHandleExists(username)
            serialized = SocialMediaHandleSerializer(handles, many=True)
            response["data"] = [dict(data) for data in serialized.data]
                
        except Exception as err:
            _status = status.HTTP_400_BAD_REQUEST
            if isinstance(err, BadRequest):
               
                response["error"] = str(err)
            elif isinstance(err, NoSocialMediaHandleExists):
                _status = status.HTTP_404_NOT_FOUND
                response["error"] = str(err)
            else:
                logger.error(err)
        return Response(response, status=_status)



class RetrieveInsightsView(APIView):
    """
    Retrieves collective platform insights
    If username is provided then collective_platform_metric will be sent after filtering private metrics.
    Else account will be used to retrieve platform metric of own handles

    [filters]:
    start_date -- Start of the date time
    end_date -- End of the date time

    The default end_date is today and start_date is a day before
    
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, AllowAny]
    digger: Digger = None

    def setup(self, **kwargs) -> Tuple[datetime, datetime]:
        assert "platform" in kwargs and len(kwargs["platform"]) > 0, "Platform must be provided"
        platform = kwargs["platform"]
        if platform == Platform.Instagram:
            self.digger = InstagramDigger()
        elif platform == Platform.Youtube:
            self.digger = YoutubeDigger()
        if self.digger is None:
            raise BadRequest("Platform must be valid")
        data = kwargs["data"]
        default_end_date = datetime_to_unix_timestamp_string(get_current_time())
        default_start_date = datetime_to_unix_timestamp_string(get_current_time() - timedelta(days=1))
        end_date: datetime = unix_string_to_datetime(data.get("end_date", default_end_date))
        start_date: datetime = unix_string_to_datetime(data.get("start_date",  default_start_date))
        return start_date, end_date




class RetrievePlatformInsightsView(RetrieveInsightsView):
    """
    Retrieves collective platform insights
    If username is provided then collective_platform_metric will be sent after filtering private metrics.
    Else account will be used to retrieve platform metric of own handles

    [filters]:
    start_date -- Start of the date time
    end_date -- End of the date time

    The default end_date is today and start_date is a day before
    
    """

    def get(self, request: Request, **kwargs) -> Response:
        _status = status.HTTP_400_BAD_REQUEST
        response = {}
        data: Dict = request.GET.dict()
        username = kwargs.get("username", None)
        try:
            platform = kwargs["platform"]
            start_date, end_date = self.setup(data=data,**kwargs)
            account: Account = request.account
            is_owner = False
            if (account is not None and username is not None and account.username == username) or (account is not None and username is None):
                is_owner = True
            else:
                account_queryset: QuerySet[Account] = Account.objects.filter(username=username)
                if not account_queryset.exists():
                    raise AccountDoesNotExists(username)
                account = account_queryset.first()
            metric_table = self.digger.calculate_platform_metric(account, start_date, end_date)
            metric_filters = []
            if not is_owner:
                metric_filters = account.platform_specific_private_metric[platform]
            response["data"] = metric_table.json(*metric_filters)
            _status = status.HTTP_200_OK
        except Exception as err:
            _status = status.HTTP_400_BAD_REQUEST
            if isinstance(err, (AccountDoesNotExists, AssertionError, BadRequest)):
                response["error"] = str(err)
            else:
                response["error"] = f"Unable to fetch platform insights"
                logger.error(err)
        return Response(response, status=_status)


class RetrieveHandleInsightsView(RetrieveInsightsView):
    """
    Retrieve insights of single  handle
    If username is provided then insight of  handle will be provided after filtering private metrics.
    Else account will be used to retrieve  insights

    [filters]:
    start_date -- Start of the date
    end_date -- End of the date
    """

    def get(self, request: Request, handle: str) -> Response:
        _status = status.HTTP_400_BAD_REQUEST
        response = {}
        data: Dict = request.GET.dict()
        try:
            handles: QuerySet[SocialMediaHandle] = SocialMediaHandle.objects.select_related('account').filter(Q(handle_uid=handle) & Q(is_disabled=False))
            if not handles.exists():
                raise NoSocialMediaHandleExists("")
            handle: SocialMediaHandle = handles.first()
            start_date, end_date = self.setup(data=data, platform=handle.platform)
            is_owner = False
            if request.account is not None and handle.account == request.account:
                is_owner = True
            account: Account = handle.account
            
            metric_table = self.digger.get_handle_insights(handle, start_date, end_date)
            metric_filters = []
            if not is_owner:
                metric_filters = account.platform_specific_private_metric[handle.platform]
            response["data"] = metric_table.json(*metric_filters)
            _status = status.HTTP_200_OK
        except Exception as err:
            _status = status.HTTP_400_BAD_REQUEST
            if isinstance(err, (NoSocialMediaHandleExists, AssertionError, BadRequest)):
                response["error"] = str(err)
            else:
                response["error"] = f"Unable to fetch platform insights"
                logger.error(err)
        return Response(response, status=_status)
