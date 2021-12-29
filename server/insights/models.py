import datetime
from typing import Any, Dict, List, Union
from django.db import models

from accounts.models import SocialMediaHandle
from digger.youtube.types import YTMetrics
from insights.managers import InstagramHandleMetricsManager, SocialMediaHandleMetricsManager, YoutubeHandleMetricsManager
from utils import YOUTUBE_RESPONSE_DATE_FORMAT, get_current_time, get_handle_metrics_expire_time
from django.db.models import JSONField

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
    update_fields = ['follower_count' ,'media_count', 'impressions',
                    'reach', 'audience_city', 'audience_gender_age',"audience_country",
                    "profile_views"
                    ]


    def set_metrics_from_user_insight_response(self, response: 'InstagramUserInsightsResponse') -> None:
        self.impressions |= response.impressions
        self.reach |= response.reach
        self.follower_count |= response.follower_count
        self.profile_views |= response.profile_views
    
    def set_metrics_from_user_demographic_response(self, response: 'InstagramUserDemographicInsightsResponse') -> None:
        self.audience_city |= response.audience_city
        self.audience_gender_age |= response.audience_gender_age
        self.audience_country |= response.audience_country

    @staticmethod
    def merge_metric(metrics: Dict[str, Dict[str, int]]) -> Dict[str, Union[int, float]]:
        data = {}
        for metric in metrics.values():
            for key, value in metric.items():
                if key not in data:
                    data[key] = 0
                data[key] += value
        return data
    

    def calculate_collective_metrics(self, **data) -> Dict[str, Union[int ,float]]:
        get_total = lambda _map: [_inner_map["total"] for _inner_map in _map.values()]
        data["impressions"] = sum(get_total(self.impressions))
        data["reach"] = sum(get_total(self.reach))
        data["profile_views"] = sum(get_total(self.profile_views))
        data["audience_city"] = self.merge_metric(self.audience_city)
        data["audience_gender_age"] = self.merge_metric(self.audience_gender_age)
        data["audience_country"] = self.merge_metric(self.audience_country)
        return data




class YoutubeHandleMetricModel(SocialMediaHandleMetrics):

    subscribed_status_fields = ["views", "likes", "dislikes", "shares", "estimated_minutes_watched", 
                                "average_view_duration", "average_view_percentage", "annotation_click_through_rate", 
                                "annotation_close_rate", "annotation_impressions", "annotation_clickable_impressions", 
                                "annotation_closable_impressions", "annotation_clicks", "annotation_closes", "card_click_rate", 
                                "card_teaser_click_rate", "card_impressions", "card_teaser_impressions", "card_clicks", "card_teaser_clicks"
]

    """
    Manages Youtube handle metric data for a week

    Dimensional structure [MetricRecord]
    """
    views = models.JSONField(default=dict)
    comments = models.JSONField(default=dict)
    likes = models.JSONField(default=dict)
    dislikes = models.JSONField(default=dict)
    shares = models.JSONField(default=dict)
    estimated_minutes_watched = models.JSONField(default=dict)
    average_view_duration = models.JSONField(default=dict)
    subscriber_gained = models.JSONField(default=dict)
    subscriber_lost = models.JSONField(default=dict)
    viewer_percentage = models.JSONField(default=dict)
    audience_watch_ratio = models.JSONField(default=dict)
    relative_retention_performance = models.JSONField(default=dict)
    card_impressions = models.JSONField(default=dict)
    card_clicks = models.JSONField(default=dict)
    card_click_rate = models.JSONField(default=dict)
    card_teaser_impressions = models.JSONField(default=dict)
    card_teaser_clicks = models.JSONField(default=dict)
    card_teaser_click_rate = models.JSONField(default=dict)
    annotation_impressions = models.JSONField(default=dict)
    annotation_clickable_impressions = models.JSONField(default=dict)
    annotation_clicks = models.JSONField(default=dict)
    annotation_click_through_rate = models.JSONField(default=dict)
    annotation_closable_impressions = models.JSONField(default=dict)
    annotation_closes = models.JSONField(default=dict)
    annotation_close_rate = models.JSONField(default=dict)
    positive_engagement = models.JSONField(default=dict)
    negative_engagement = models.JSONField(default=dict)
    engagement = models.JSONField(default=dict)
    meta_data = models.JSONField(default=dict)

    objects = YoutubeHandleMetricsManager()


    @staticmethod
    def _transform_age_group_gender_record(self, data: Dict[str, Dict[str, Dict[str, float]]]) -> Dict[str, float]:
        gender = {"M": [], "F": [], "U": []}
        age = {"age13-17": [], "age18-24":[], "age25-34": [], "age45-54": [], "age55-64": [], "age65-": []}
        compressed: Dict[str, List[float]] = {}
        for value in data.values():
            for gender_key, gender_value in value.items():
                for age_group, perc in gender_value.items():
                    age[age_group].append(perc)
                    gender[gender_key].append(perc)
                    codec = f"{gender_key}.{age_group.replace('age','')}"
                    if codec not in compressed:
                        compressed[codec] = []
                    compressed[codec].append(perc)
        metric_map = {}
        for key, value in gender.items():
            metric_map[key] = sum(value)/(count if (count := len(value)) > 0 else 1)
        for key, value in age.items():
            metric_map[key] = sum(value)/(count if (count := len(value)) > 0 else 1)
        for key, value in compressed.items():
            metric_map[key] = sum(value)/(count if (count := len(value)) > 0 else 1)
        return metric_map



    def calculate_engagements(self) -> None:
        total: Dict[str, Union[int, float]] = self.meta_data["totals"]
        positive_action = total.get("likes",0) + total.get("shares",0) + total.get("comment",0)
        negative_action = total.get("dislikes", 0)
        self.positive_engagement |= {get_current_time().strftime(YOUTUBE_RESPONSE_DATE_FORMAT): {"TOTAL": positive_action}}
        self.negative_engagement |={get_current_time().strftime(YOUTUBE_RESPONSE_DATE_FORMAT): {"TOTAL": negative_action}}
        self.engagement |= {get_current_time().strftime(YOUTUBE_RESPONSE_DATE_FORMAT): {"TOTAL": positive_action + negative_action}}
        self.set_total_of_metrics("positive_engagement")
        self.set_total_of_metrics("negative_engagement")
        self.set_total_of_metrics("engagement")
    
    def calculate_normal_metrics_total(self, data: Dict[str, Dict[str, int]]) -> Union[int, float]:
        return sum([packet["TOTAL"] for packet in data.values()])
    
    

    def set_total_of_metrics(self, metric_name: str) -> None:
        if "totals" not in self.meta_data:
            self.meta_data["totals"] = {}
        if metric_name not in ["viewer_percentage", "shares", "audience_watch_ratio", "relative_retention_performance"]:
            if metric_name not in self.meta_data["totals"]:
                self.meta_data["totals"][metric_name] = 0
            self.meta_data["totals"][metric_name] += self.calculate_normal_metrics_total(getattr(self, metric_name))

    def set_metrics(self, metrics: YTMetrics, save: bool = False) -> None:
        for key, value in vars(metrics):
            if value is not None:
                data = getattr(self, key, {})
                data |= value
                setattr(self, key, data)
                self.set_total_of_metrics(key)
        self.calculate_engagements()
        if save:
            self.save()
    
    def calculate_collective_metrics(self, **data) -> Dict[str, Union[int, float]]:
        total: Dict[str, Union[int, float]] = self.meta_data["totals"]
        old_total: Dict[str, Union[int, float]] = self.meta_data.get("prev_totals", {})
        calc_total = lambda key: total.get("views", 0) + old_total.get("views", 0)
        data["views"] = calc_total("views")
        data["engagement"] = calc_total("engagement")
        data["estimated_minutes_watched"] = calc_total("estimated_minutes_watched")
        data["average_view_duration"] = calc_total("average_view_duration")


class CreatorMetricModel: 
    """
    Manages Creators overall metric data for a week
    """
    ...


class InstagramPlalformMetric(CreatorMetricModel):
    
    def __init__(self, follower_count: int, media_count: int, impressions: int, reach: int, profile_views: int, audience_city: Dict[str, int], audience_gender_age: Dict[str, int], audience_country: Dict[str, int]) -> None:
        self.follower_count = follower_count
        self.media_count = media_count
        self.impressions = impressions
        self.reach = reach
        self.profile_views = profile_views
        self.audience_city = audience_city
        self.audience_gender_age = audience_gender_age
        self.audience_country = audience_country


class YoutubePlatformMetric(CreatorMetricModel):

    ...



class PlatformMetricModel: 
    """
    Overall platform metric data for a week, i.e
    Overall metrics of Instagram / Youtube platform
    """
    ...








    

