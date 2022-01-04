from datetime import datetime
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from accounts.models import Account, SocialMediaHandle
from digger.base.types import Digger
from insights.models import InstagramHandleMetricModel
from .types import InstagramPlalformMetric
from utils import date_to_string, get_current_time, merge_metric
from utils.types import Platform
from .request_manager import InstagramRequestManager
from .request_struct import *
from log_engine.log import logger


class InstagramDigger(Digger):

    request_manager = InstagramRequestManager()

    def get_long_lived_token(self, account: Account, short_lived_token: str) -> FacebookLongLiveTokenResponse:
        request = FacebookLongLiveTokenRequest(short_lived_token)
        response: FacebookLongLiveTokenResponse = request(self.request_manager)
        return response
    
    def _get_handles_queryset(self, account: Account) -> QuerySet[SocialMediaHandle]:
        return SocialMediaHandle.objects.filter(Q(account=account) & Q(platform=Platform.Instagram))
    

    def resync_social_media_handles(self, account: Account, access_token: str = None) -> List[SocialMediaHandle]:
        handle_queryset: QuerySet[SocialMediaHandle] = self._get_handles_queryset(account)
        if access_token is None:
            if not handle_queryset.exists():
                return None
            handle: SocialMediaHandle = handle_queryset.first()
            access_token = handle.access_token

        request = FacebookPageAccountsRequest(access_token)
        # breakpoint()
        response: FacebookPagesAccountsResponse = request(self.request_manager)
        handle_uids = handle_queryset.values_list('handle_uid', flat=True)
        recent_uids: List[str] = []
        pages: List[FacebookPageData] = []


        def validate_page_data(page: FacebookPageData) -> bool:
            if page.instagram_business_account is not None \
                and page.instagram_business_account.id not in handle_uids \
                    and page.instagram_business_account.id not in recent_uids:
                recent_uids.append(page.instagram_business_account.id)
                return True
            return False

            


        while response.error == None and len(response.pages) > 0:
            pages += list(filter(validate_page_data, response.pages))
            if response.paging.after == None:
                break
            response: FacebookPagesAccountsResponse = request(self.request_manager, after=response.paging.after)
        
        handles: List[SocialMediaHandle] = list(map(lambda data: SocialMediaHandle.from_ig_user_data(account, data.instagram_business_account) , pages))
        SocialMediaHandle.objects.bulk_create(handles)
        handles += list(handle_queryset)
        return handles


        
    
    def create_or_update_social_media_handles(self, account: Account, access_token: str, expires_in: int = 3599, refresh_token: str = None) -> List[SocialMediaHandle]:
        handles: List[SocialMediaHandle] = self.resync_social_media_handles(account, access_token=access_token)
        for handle in handles:
            handle._set_access_token(access_token, expires_in)
        SocialMediaHandle.objects.bulk_update(handles, ['access_token', 'token_expiration_time'])
        return handles

    def update_handle_data(self, social_media_handle: SocialMediaHandle) -> SocialMediaHandle:
        request = InstagramUserDataRequest(social_media_handle.handle_uid, social_media_handle.access_token)
        response: InstagramUserDataResponse = request(self.request_manager)
        social_media_handle.last_date_time_of_token_use = get_current_time()
        if response.error:
            logger.error(f"SocialMediaHandle[platform={social_media_handle.platform}, username={social_media_handle.username}] is returning {response.error} on InstagramUserDataRequest")
            return social_media_handle
        social_media_handle.avatar = response.user.profile_picture_url
        social_media_handle.follower_count = response.user.followers_count
        social_media_handle.media_count = response.user.media_count
        social_media_handle.meta_data = {"name": response.user.name, "description": response.user.biography}
        social_media_handle.save()
        return social_media_handle

    

    def update_handle_insights(self, social_media_handle: SocialMediaHandle, save: bool=True) -> InstagramHandleMetricModel:
        handle_metric: InstagramHandleMetricModel = InstagramHandleMetricModel.objects.get_or_create(handle=social_media_handle)
        demographic_request = InstagramUserDemographicInsightsRequest(social_media_handle.handle_uid, access_token=social_media_handle.access_token)
        demographic_response: InstagramUserDemographicInsightsResponse = demographic_request(self.request_manager)        
        handle_metric.set_metrics_from_user_demographic_response(demographic_response)
        user_insights_request = InstagramUserInsightsRequest(social_media_handle.handle_uid, social_media_handle.access_token)
        user_insights_request: InstagramUserInsightsResponse = user_insights_request(self.request_manager)
        handle_metric.set_metrics_from_user_insight_response(user_insights_request)
        handle_metric.media_count[date_to_string(get_current_time())] = social_media_handle.media_count

        social_media_handle.last_date_time_of_token_use = get_current_time()
        social_media_handle = self.update_handle_data(social_media_handle)
        if save:
            handle_metric.save()
        return handle_metric
    
    def update_all_handles_insights(self, account: Account) -> List[InstagramHandleMetricModel]:
        handle_queryset: QuerySet[SocialMediaHandle] = SocialMediaHandle.objects.filter(Q(account=account) & Q(platform=Platform.Instagram))
        if not handle_queryset.exists():
            return []
        metrics: List[InstagramHandleMetricModel] = []
        for handle in handle_queryset:
            metrics = self.update_handle_insights(handle, save=True)
        return metrics
    

    def calculate_platform_metric(self, account: Account, start_date: datetime = None, end_date: datetime = get_current_time()) -> InstagramPlalformMetric:
        query_lookup: Q = Q(handle__account=account)
        if start_date is not None:
            query_lookup &= Q(created_on__gte=start_date)
        query_lookup &= Q(expired_on__gte=end_date)
        handle_metrics: QuerySet[InstagramHandleMetricModel] = InstagramHandleMetricModel.objects.filter(query_lookup)
        platform_metric, total_data = self.get_total_platform_metric(handle_metrics)
        platform_metric_model = InstagramPlalformMetric(**platform_metric)
        platform_metric_model.totals_record = total_data
        return platform_metric_model
    
    
        





        

    


    
    
        
        
        

