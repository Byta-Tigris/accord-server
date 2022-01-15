from datetime import datetime, timedelta
import json

from typing import Dict, Tuple, Union
from django.core.exceptions import BadRequest
from django.db.models.query_utils import Q
from django.http.request import QueryDict
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
from insights.serializers import LinkwallInsightsSerializer, SocialMediaHandleSerializer
from linktree.models import LinkClickCounterModel, LinkWall, LinkwallViewCounterModel
from log_engine.log import logger
from utils import datetime_to_unix_timestamp_string, get_current_time, unix_string_to_datetime
from utils.errors import AccountAuthenticationFailed, AccountDoesNotExists, NoSocialMediaHandleExists, OAuthAuthorizationFailure
from utils.types import Platform
from rest_framework.decorators import api_view, permission_classes


@api_view(['GET'])
@permission_classes([AllowAny])
def get_platforms_view(self, request: Request) -> Response:
    platforms = [key for key in vars(Platform).keys() if not key.startswith('_')]
    return Response({"data": platforms}, status=status.HTTP_200_OK)



def get_digger(platform: str) -> Digger:
    if platform == Platform.Instagram:
        return InstagramDigger()
    elif platform == Platform.Youtube:
        return YoutubeDigger()
    return None

class CreateSocialMediaHandlesView(APIView):
    """
    Creates social media accounts using `create_or_update_handles_from_data` api
    provided by each digger.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    digger = None
    serializer = SocialMediaHandleSerializer

    def post(self, request: Request, platform: str) -> Response:
        _status = status.HTTP_400_BAD_REQUEST
        response = {}
        try:
            assert request.account is not None, "Account must exists for using this service"
            account: Account = request.account
            body = request.body
            data = json.loads(body)
            self.digger = get_digger(platform)
            if self.digger is None:
                raise BadRequest("Platform must be valid")
            handles = self.digger.create_or_update_handles_from_data(account, **data)
            serialzed = self.serializer(handles, many=True)
            response["data"] = serialzed.data
            _status = status.HTTP_201_CREATED
        except Exception as err:
            _status = status.HTTP_400_BAD_REQUEST
            if isinstance(err, (AssertionError, OAuthAuthorizationFailure, BadRequest)):
                response["error"] = str(err)
            else:
                response["error"] = "Unable to retrieve information from Instagram"
                logger.error(err)
        return Response(response, status=_status)




class RetrieveSocialMediaHandleView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SocialMediaHandleSerializer

    def get(self, request: Request, username: str = None, handle_id: str = None) -> Response:
        """
        Retrieve all social media handles of any user using username or account requesting

        filters:
         paltform -- Platform of handles
         handle_id -- Social media handle
        """
        _status = status.HTTP_400_BAD_REQUEST
        response = {} 
        query_params: QueryDict = request.GET 
        platform = query_params.get("platform", None)
        try:
            if request.account and username == "me":
                account: Account = request.account
                username = account.username

            query: Q = Q(account__username=username)

            if handle_id is None and username is None:
                raise BadRequest("Either username or handle_id must be provided")
            
            if handle_id is not None:
                query  = Q(handle_uid = handle_id)
            if platform and query:
                query &= Q(platform = platform)
            if query is None:
                raise BadRequest("Username must be provided")
            query &= Q(is_disabled=False)
            handles: QuerySet[SocialMediaHandle] = SocialMediaHandle.objects.select_related('account').filter(query)
            if not handles.exists():
                raise NoSocialMediaHandleExists(username)
            serialized = SocialMediaHandleSerializer(handles, many= handle_id == None)
            response["data"] = serialized.data
            _status = status.HTTP_200_OK
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
    start_date -- Start of the date time [Unix]
    end_date -- End of the date time [Unix]

    The default end_date is today and start_date is a day before
    
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, AllowAny]
    digger: Digger = None

    def get_date_filters(self,data, delta_days=1) -> Tuple[datetime, datetime]:
        default_end_date = datetime_to_unix_timestamp_string(get_current_time())
        default_start_date = datetime_to_unix_timestamp_string(get_current_time() - timedelta(days=delta_days))
        end_date: datetime = unix_string_to_datetime(data.get("end_date", default_end_date))
        start_date: datetime = unix_string_to_datetime(data.get("start_date",  default_start_date))
        return start_date, end_date

    def setup(self, **kwargs) -> Tuple[datetime, datetime]:
        assert "platform" in kwargs and len(kwargs["platform"]) > 0, "Platform must be provided"
        platform = kwargs["platform"]
        self.digger = get_digger(platform)
        if self.digger is None:
            raise BadRequest("Platform must be valid")
        data: Dict = kwargs["data"]
        return self.get_date_filters(data, delta_days=kwargs.get("delta_days", 1))




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




class RetrieveLinkwallInsights(RetrieveInsightsView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LinkwallInsightsSerializer


    def get(self, request: Request) -> Response:
        _status = status.HTTP_400_BAD_REQUEST
        response = {}
        query_params: QueryDict = request.GET 
        start_date, end_date = self.get_date_filters(query_params.dict(), delta_days=7) 
        try:
            if not request.account:
                raise AccountAuthenticationFailed()
            account: Account = request.account
            linkwall_queryset: QuerySet[LinkWall] = LinkWall.objects.filter(Q(account=account))
            if not linkwall_queryset.exists():
                _status = status.HTTP_200_OK
                response["data"] = "No linkwall found"
            linkwall: LinkWall = linkwall_queryset.first()
            query = Q(linkwall = linkwall) & Q(created_on__gte=start_date) & Q(created_on__lte=end_date)
            views_queryset: QuerySet[LinkwallViewCounterModel] = LinkwallViewCounterModel.objects.filter(query)
            click_queryset: QuerySet[LinkClickCounterModel] = LinkClickCounterModel.objects.filter(query)
            serialized = self.serializer_class(views_queryset, click_queryset)
            response["data"] = serialized.data
            _status = status.HTTP_200_OK
        except Exception as err:
            if isinstance(err, AccountAuthenticationFailed):
                response["error"] = str(err)
            else:
                logger.error(err)
        return Response(response, status=_status)
            
                

