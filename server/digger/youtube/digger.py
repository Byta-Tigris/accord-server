from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from accounts.models import Account, SocialMediaHandle
from digger.base.types import Digger
from digger.youtube.request_manager import YoutubeRequestManager
from digger.youtube.request_struct import *
from digger.youtube.response_struct import *
from digger.youtube.types import MetricRecord
from insights.models import YoutubeHandleMetricModel
from utils import reformat_age_gender
from utils.types import Platform



class YoutubeDigger(Digger):
    request_manager = YoutubeRequestManager


    def exchange_code_for_token(self, code: str, redirect_uri: str) -> YoutubeExchangeCodeForTokenResponse:
        request = YoutubeExchangeCodeForTokenRequest(code, redirect_uri)
        response: YoutubeExchangeCodeForTokenResponse = request(self.request_manager)
        return response
    
    def get_refresh_token(self, social_media_handle: SocialMediaHandle) -> YoutubeRefreshTokenResposne:
        request = YoutubeRefreshTokenRequest(social_media_handle.refresh_token)
        response: YoutubeRefreshTokenResposne = request(self.request_manager)
        return response

    def refresh_handle_token(self, social_media_handle: SocialMediaHandle) -> Union[SocialMediaHandle, None]:
        response: YoutubeRefreshTokenResposne = self.get_refresh_token(social_media_handle)
        if response.error:
            return None
        social_media_handle.set_access_token(response.access_token, token_expiration_time=response.expires_in, refresh_token=social_media_handle.refresh_token)
        return social_media_handle
    
    
    
    def resync_social_media_handles(self, account: Account, access_token: str = None) -> List[SocialMediaHandle]:
        handle_queryset: QuerySet[SocialMediaHandle] = SocialMediaHandle.objects.filter(Q(account=account) & Q(platform=Platform.Youtube))
        if access_token is None:
            if not handle_queryset.exists():
                return None
            handle: SocialMediaHandle = handle_queryset.first()
            access_token = handle.access_token
        
        request = YoutubeChannelListRequest(access_token)
        response: YoutubeChannelListResponse = request(self.request_manager)
        handle_uids = handle_queryset.values_list('handle_uid', flat=True)
        recent_uids: List[str] = []
        channels: List[YTChannel] = []

        def validate_channel_data(channel: YTChannel) -> bool:
            if channel.id not in handle_uids and channel.id not in recent_uids:
                recent_uids.append(channel.id)
                return True
            return False

        while response.error == None and len(response.channels) > 0:
            channels += list(filter(validate_channel_data, response.channels))
            if response.next_page_token == None:
                break
            response: YoutubeChannelListResponse = request(self.request_manager, pageToken=response.next_page_token)
        
        handles: List[SocialMediaHandle]- list(map(lambda data: SocialMediaHandle.from_yt_channel(account, data), channels))
        SocialMediaHandle.objects.bulk_create(handles)
        handles += list(handle_queryset)
        return handles
    
    def create_or_update_social_media_handles(self, account: Account, access_token: str, expires_in: int = 3599, refresh_token: str = None) -> List[SocialMediaHandle]:
        handles: List[SocialMediaHandle] = self.resync_social_media_handles(account, access_token=access_token)
        for handle in handles:
            handle._set_access_token(access_token, token_expiration_time=expires_in, refresh_token=refresh_token)
        SocialMediaHandle.objects.bulk_update(handles, ['access_token', 'token_expiration_time', 'refresh_token', 'is_refresh_token_dependent'])
        return handles
    
    def get_time_based_channel_metrics(self, social_media_handle: SocialMediaHandle) -> YTMetrics:
        time_based_request = YoutubeTimeBasedChannelReportRequest(social_media_handle.access_token)
        response: YoutubeTimeBasedChannelReportResponse = time_based_request(self.request_manager)
        if response.error is not None:
            return None
        return response.metrics
    
    def get_subscription_based_channel_metrics(self, social_media_handle: SocialMediaHandle, yt_metrics: YTMetrics = None) -> YTMetrics:
        subscription_request = YoutubeSubscriptionBasedChannelReportRequest(social_media_handle.access_token)
        response: YoutubeSubscriptionBasedChannelReportsResponse = subscription_request(self.request_manager)
        subscription_metrics = None
        if response.error is None:
            subscription_metrics = response.metrics
        else:
            return yt_metrics
        if yt_metrics is None:
            return subscription_metrics

        ### Combining subscription metrics with time based metrics
        metrics = yt_metrics
        for metric_name in subscription_request.metrics:
            formatted_metric_name = YTMetrics.format_argument(metric_name)
            metric_record = MetricRecord(
                "subscribed_status", "value", dimensions=["day"]
            )
            if subscription_metrics is not None:
                data = metric if (metric := getattr(subscription_metrics, metric_name, None)) is not None else []
                metric_record.extend(data)
            time_based_data = getattr(yt_metrics, formatted_metric_name)
            if time_based_data is not None:
                for packet in time_based_data:
                    if "subscribed_status" not in packet:
                        packet["subscribed_status"] = "TOTAL"
                    metric_record.add(**packet)
            setattr(metrics, formatted_metric_name, metric_record.data)
        ## Transforming rest of the properties to {day: {TOTAL: value}} format
        for field, value in vars(yt_metrics):
            if field not in subscription_request.metrics + ["viewer_percentage", "shares"]:
                metric_record = MetricRecord(
                    "metric", "values", dimensions=["day"]
                )
                for metric in value:
                    metric["metric"] = "TOTAL"
                    metric_record.add(**metric)
                setattr(metrics, field, metric_record.data)
        return metrics
    
    def get_demography_based_channel_metrics(self, social_media_handle: SocialMediaHandle, yt_metrics: YTMetrics) -> YTMetrics:
        demographic_request = YoutubeDemographicsChannelReportRequest(social_media_handle.access_token)
        response: YoutubeDemographicsChannelReportResponse = demographic_request(self.request_manager)
        demographic_metrics = None
        if response.error is None:
            demographic_metrics = response.metrics
        else:
            return yt_metrics
        if yt_metrics is None:
            return demographic_metrics

        metrics = yt_metrics
        metric_record = MetricRecord(
            "age_group", "value", dimensions=["day", "gender"]
        )
        formatted_metric_name = "viewer_percentage"
        data = demographic_metrics.viewer_percentage
        if data is not None:
            for packet in data:
                if "day" not in packet:
                    packet["day"] = get_current_time().strftime(YTMetrics.DATE_TIME_FORMAT)
                metric_record.add(**packet)
            metric_data_formatted = {}
            for day, metric_data in metric_record.data.items():
                metric_data_formatted[day] = reformat_age_gender(metric_data)
            metric_record.set_data(metric_data_formatted)
            setattr(metrics, formatted_metric_name, metric_record.data)
        return metrics
    
    def get_sharing_service_based_channel_metrics(self, social_media_handle: SocialMediaHandle, yt_metrics: YTMetrics) -> YTMetrics:
        sharing_request = YoutubeSharingServiceChannelReportRequest(social_media_handle.access_token)
        response: YoutubeSharingServiceChannelReportResponse = sharing_request(self.request_manager)
        sharing_service_metrics = None
        if response.error is None:
            sharing_service_metrics = response.metrics
        else:
            return yt_metrics
        if yt_metrics is None:
            return sharing_service_metrics
        metrics = yt_metrics
        metric_record = MetricRecord(
            "sharing_service", "value", dimensions=["day"]
        )
        if sharing_service_metrics is not None and sharing_service_metrics.shares is not None:
            for metric in sharing_service_metrics.shares:
                if "day" not in metric:
                    metric["day"] = get_current_time().strftime(YTMetrics.DATE_TIME_FORMAT)
                metric_record.add(**metric)

        for data in yt_metrics.shares:
            if "sharing_service" not in data:
                data["sharing_service"] = "TOTAL"
            metric_record.add(**data)
        setattr(metrics, "shares", metric_record.data)
        return metrics
    
    def get_social_media_handle_with_updated_token(self, social_media_handle: SocialMediaHandle) -> SocialMediaHandle:
        if not social_media_handle.is_access_token_valid:
            if (handle := self.refresh_handle_token(social_media_handle)) == None:
                return social_media_handle
            return handle
        return social_media_handle
    
    def update_handle_data(self, social_media_handle: SocialMediaHandle) -> SocialMediaHandle:
        social_media_handle = self.get_social_media_handle_with_updated_token(social_media_handle)
        request = YoutubeChannelListRequest(social_media_handle.access_token)
        response: YoutubeChannelListResponse = request(self.request_manager)
        if response.error == None or len(response.channels) == 0:
            return social_media_handle
        yt_channel: YTChannel = response.channels[0]
        social_media_handle.username = getattr(yt_channel, "title", "")
        social_media_handle.avatar = getattr(yt_channel, "avatar", "")
        social_media_handle.follower_count = getattr(yt_channel, "follower_count", 0)
        social_media_handle.media_count = getattr(yt_channel, "media_count", 0)
        social_media_handle.meta_data |= yt_channel.meta_data
        social_media_handle.last_date_time_of_token_use = get_current_time()
        social_media_handle.save()
        return social_media_handle
    
    def update_handle_insights(self, social_media_handle: SocialMediaHandle) -> Union[YoutubeHandleMetricModel, None]:
        social_media_handle = self.get_social_media_handle_with_updated_token(social_media_handle)
        metrics = self.get_time_based_channel_metrics(social_media_handle)
        if metrics is None:
            return
        metrics = self.get_subscription_based_channel_metrics(social_media_handle, yt_metrics=metrics)
        metrics = self.get_demography_based_channel_metrics(social_media_handle, yt_metrics=metrics)
        metrics = self.get_sharing_service_based_channel_metrics(social_media_handle, yt_metrics=metrics)
        ### Converting YTMetric to YoutubeHandleMetricModel
        yt_metrics_model: YoutubeHandleMetricModel = YoutubeHandleMetricModel.objects.get_or_create(social_media_handle)
        yt_metrics_model.set_metrics(metrics, save=True)

        ### Updating handle
        self.update_handle_data(social_media_handle)
        return yt_metrics_model

    def update_all_handles_insights(self, account: Account) -> List[YoutubeHandleMetricModel]:
        queryset: QuerySet[SocialMediaHandle] = SocialMediaHandle.objects.filter(Q(account=account) & Q(platform=Platform.Youtube))
        metrics: List[YoutubeHandleMetricModel] = []
        for handle in queryset:
            metrics.append(self.update_handle_insights(handle))
        return metrics
        
                


        


            





