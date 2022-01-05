import datetime
from typing import Any, Dict, List, Tuple, Union

from django.db.models.query import QuerySet

from utils import get_current_time, merge_metric
from utils.datastructures import MetricTable




class AbstractResponseStruct:
    url: str = None
    
    @classmethod
    def from_data(cls, url,kwargs) -> 'AbstractResponseStruct': ...

    def to_kwargs(self) -> Dict[str, Any]: ...

class AbstractRequestStruct:
    response_struct: AbstractResponseStruct = None
    url_key: str = "default"
    endpoint: str = "/"
    ignorable_fields: List[str] = []
    _ignored_fields: List[str] = ["response_struct", "url_key", "endpoint", 
                                    "ignorable_fields", "_gnorable_fields",
                                    "status_code", "header", "method", "params_query", "params_data"]
    headers: Dict = None
    method: str = None
    status_code = 200

    def get_headers(self) -> Union[None,Dict[str, str]]:
        return self.headers

    def get_ignorable_fields(self) -> List[str]:
        return self.ignorable_fields + self._ignored_fields

    def _get_params(self) -> Dict[str, Any]: ...
    def format_params(self, **params) -> Dict[str, Any]: ... 
    def get_params(self) -> Dict[str, Any]: ...

class AbstractRequestManager:
    def make_request(self, request: AbstractRequestStruct) -> AbstractResponseStruct: ...


class AbstractDigger:
    pass


class PlatformMetricModel:
    
    totals_record: Dict[str, Dict[str, Dict[str, Union[int, float]]]]

class CreatorMetricModel: 
    """
    Manages Creators overall metric data for a week
    """
    ...

LongLiveTokenResponse = type(AbstractResponseStruct)

class Digger(AbstractDigger):

    """
    Wrapper object responsible for all the request-response-model operations involved in the api fetching\n
    Each Platform will have their own digger class.
    """

    def exchange_code_for_token(self, code: str, redirect_uri: str) -> AbstractResponseStruct:
        """
        After the successfull authorization flow, client-side will retrieve the code\n
        The code coupled with the redirect_uri will call Request to retrieve short-lived token\n
        """
        pass


    def get_long_lived_token(self, account: 'Account', short_lived_token: str) -> LongLiveTokenResponse:
        """
        Exchanges the short-lived token with the long-lived token\n
        Returns Long Live Token Response
        """
        pass
    
    
    def get_refresh_token(self, social_media_handle: 'SocialMediaHandle') -> LongLiveTokenResponse:
        """
        Refreshes token and returns LongLiveTokenResponse
        """
        pass

    def create_or_update_social_media_handles(self, account: 'Account', access_token: str, expires_in: int = 3599, refresh_token: str = None) -> List['SocialMediaHandle']:
        """
        Fetches all handles related with the access_token\n
        Update the existing handles with the new access_token\n
        Creates new if the handle does not exists\n

        Returns List of SocialMediaHandles\n

        [Keyword Arguments]: \n
        account -- Account of the access_token owner\n
        access_token -- The new access_token\n
        expires_in -- Validity of the token in seconds [default=3600]\n
        refresh_token -- Refresh token if provided, then handle's refresh_token field will store the value, [Optional]\n
        """
        pass

    def resync_social_media_handles(self, account: 'Account', access_token: str = None) -> List['SocialMediaHandle']:
        """
        Resync all the social media handles if such functionality is supported\n
        """
        pass

    def update_handle_insights(self, social_media_handle: 'SocialMediaHandle') -> 'SocialMediaHandleMetrics':
        """
        Fetches all handle related insights, and update the handle metrics.\n
        If the handle metrics has crossed the 7 days time, new handle metric will be contrsucted\n

        Works for single social_media_handle\n
        """
        pass

    def update_handle_data(self, social_media_handle: 'SocialMediaHandle') -> 'SocialMediaHandle':
        """
        Update the social media handle data
        """
        pass
    
    def update_all_handles_insights(self, account: 'Account') -> List['SocialMediaHandleMetrics']:
        """
        Update handle insight in bulk or from single function
        """
        pass

    def calculate_platform_metric(self, account: 'Account',start_date: datetime = None, end_date: datetime = get_current_time()) -> MetricTable:
        """
        Calculates all the metrics from the social handle and updates the platfrom metric similarly
        Return MetricTable
        """
        pass
    
    def update_creator_insights(self, account: 'Account', digger: List[AbstractDigger]) -> CreatorMetricModel:
        """
        Calculates creators overall insight and Update Creator insight metric\n
        Every digger will implement 
        """
        pass

    def get_metric_table_from_queryset(self, queryset: QuerySet) -> MetricTable:
        """
        Returns MetricTable from the provided queryset
        """
        if queryset.exists():
            return MetricTable(queryset.first().get_columns(), *list(queryset))
        return MetricTable()

    def get_handle_insights(self, handle: 'SocialMediaHandle', start_date: datetime = None, end_date: datetime = get_current_time()) -> MetricTable:
        """
        Returns MetricTable, containing all insights of the handle

        """
        pass

    def get_total_platform_metric(self, handle_metric_queryset:QuerySet['SocialMediaHandleMetrics']) -> Tuple[Dict[str, Dict[str, Union[int, float]]], Dict[str, Dict[str, Union[int, float]]]]:
        platform_metric = {}
        total_metric = {"totals":{}, "grand_totals": {}}
        for handle in handle_metric_queryset:
            totals_data = handle.get_total_sum_of_metric()
            for metric_name, metric_value in vars(handle.get_collective_metrics()).items():
                if metric_name.startswith('_'):
                    continue
                if metric_name not in platform_metric:
                    platform_metric[metric_name] = {}
                for date_str, metric_data in metric_value.items():
                    if date_str not in platform_metric[metric_name]:
                        platform_metric[metric_name][date_str] = {}
                    platform_metric[metric_name][date_str] = merge_metric(platform_metric[metric_name][date_str], metric_data)
                if metric_name in totals_data["totals"]:
                    if metric_name not in total_metric["totals"]:
                        total_metric['totals'][metric_name] = {}
                    total_metric["totals"][metric_name] = merge_metric(total_metric["totals"][metric_name], totals_data["totals"][metric_name])
                if metric_name in totals_data["grand_totals"]:
                    if metric_name not in total_metric["grand_totals"]:
                        total_metric['grand_totals'][metric_name] = {}
                    total_metric["grand_totals"][metric_name] = merge_metric(total_metric["grand_totals"][metric_name], totals_data["grand_totals"][metric_name])

        return platform_metric