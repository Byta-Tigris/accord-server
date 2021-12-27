import datetime
from typing import Any, Dict, List, Union
from django.db import models

from accounts.models import SocialMediaHandle
from insights.managers import InstagramHandleMetricsManager, SocialMediaHandleMetricsManager
from utils import get_current_time, get_handle_metrics_expire_time
from django.db.models import JSONField

from digger.instagram.response_struct import InstagramUserDemographicInsightsResponse, InstagramUserInsightsResponse

from utils.types import Platform


# Create your models here.


class SocialMediaHandleMetrics(models.Model):
    """
    handle -- Social Media Handle with which it is associated
    platform -- Social Media Platform
    created_on -- Handle Metrics created on
    expired_on -- Expiry of handle metric
    media_count -- Total number of media on the handle each day
    follower_count -- Total follower count [date_time: value::int]
    average_metrics -- Total average of all the metrics data calculated so far
    """

    handle= models.ForeignKey(SocialMediaHandle, on_delete=models.CASCADE)
    platform = models.CharField(max_length=20, default='')
    created_on = models.DateTimeField(default=get_current_time)
    expired_on = models.DateTimeField(default=get_handle_metrics_expire_time)
    follower_count = JSONField(default=dict)
    media_count = models.JSONField(default=dict)

    objects = SocialMediaHandleMetricsManager()

    def _calculate_collective_metrics(self) -> Dict[str, Union[int ,float]]:
        data = {}
        data["follower_count"] = follower_count[-1] if len((follower_count := list(self.follower_count.values()))) > 0 else 0
        data["media_count"] = media_count[-1] if len((media_count := list(self.media_count.values()))) > 0 else 0
        return data


    def calculate_collective_metrics(self, **data) -> Dict[str, Union[int ,float]]:
        return data
        

    def get_collective_metrics(self) -> Dict[str, Union[int, float]]:
        """
        Returns formatted collective metric record for a week.
        """
        data = self._calculate_collective_metrics()
        return self.calculate_collective_metrics(**data)

    class Meta:
        abstract = True


class InstagramHandleMetricModel(SocialMediaHandleMetrics): 
    """
    Manages Instagram handle metric data for a week
    impressions -- Total daily views on handle : Dict[day_str, int]
    reach -- Total daily unique views on handle: Dict[day_str, int]
    audience_city -- Total city accumulations: Dict[day_str, Dict[str(city): int]]
    audience_gender_age -- Type(audience_city)
    audience_country -- Type(audience_city)
    profile_views -- Total daily porfile views: Dict[day_str, int]
    """
    
    impressions = models.JSONField(default=dict)
    reach = models.JSONField(default=dict)
    audience_city = models.JSONField(default=dict)
    audience_gender_age = models.JSONField(default=dict)
    audience_country = models.JSONField(default=dict)
    profile_views = models.JSONField(default=dict)

    objects = InstagramHandleMetricsManager()


    def set_metrics_from_user_insight_response(self, response: InstagramUserInsightsResponse) -> None:
        self.impressions |= response.impressions
        self.reach |= response.reach
        self.follower_count |= response.follower_count
        self.profile_views |= response.profile_views
    
    def set_metrics_from_user_demographic_response(self, response: InstagramUserDemographicInsightsResponse) -> None:
        self.audience_city |= response.audience_city
        self.audience_gender_age |= response.audience_gender_age
        self.audience_country |= response.audience_country


    def merge_metric(self, metrics: Dict[str, Dict[str, int]]) -> Dict[str, Union[int, float]]:
        data = {}
        for metric in metrics.values():
            for key, value in metric.items():
                if key not in data:
                    data[key] = 0
                data[key] += value
        return data


    def calculate_collective_metrics(self, **data) -> Dict[str, Union[int ,float]]:
        data["impressions"] = sum(self.impressions.values())
        data["reach"] = sum(self.reach.values())
        data["profile_views"] = sum(self.profile_views.values())
        data["audience_city"] = self.merge_metric(self.audience_city)
        data["audience_gender_age"] = self.merge_metric(self.audience_gender_age)
        data["audience_country"] = self.merge_metric(self.audience_country)
        return data




class YoutubeHandleMetricModel(SocialMediaHandleMetrics): 
    """
    Manages Youtube handle metric data for a week

    Dimensional structure [MetricRecord]
    """
    views = models.JSONField(default=dict)
    comments = models.JSONField(default=dict)
    likes = models.JSONField(default=dict)
    dislikes = models.JSONField(default=dict)
    shares = models.JSONField(default=dict)
            


class CreatorMetricModel(models.Model): 
    """
    Manages Creators overall metric data for a week
    """
    ...


class PlatformMetricModel: 
    """
    Overall platform metric data for a week, i.e
    Overall metrics of Instagram / Youtube platform
    """
    ...






    

