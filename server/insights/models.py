from typing import Dict, List, Union
from django.db import models

from accounts.models import SocialMediaHandle
from digger.youtube.types import YTMetrics
from insights.managers import InstagramHandleMetricsManager, SocialMediaHandleMetricsManager, YoutubeHandleMetricsManager
from utils import DATE_FORMAT, get_current_time, get_handle_metrics_expire_time, merge_metric, subtract_merge
from django.db.models import JSONField
from django.db.models.query_utils import DeferredAttribute



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
    meta_data = models.JSONField(default=dict)

    objects = SocialMediaHandleMetricsManager()
    COLUMN_WHITELIST = ["id", "handle_id", "platform", "created_on", "expired_on", "meta_data"]


    @classmethod
    def get_metric_names(cls) -> List[str]:
        return [key for key, value in vars(cls).items() if key != "id" and isinstance(value, DeferredAttribute)]

    def _calculate_collective_metrics(self) -> Dict[str, Union[int ,float]]:
        data = {}
        data["follower_count"] = self.follower_count
        data["media_count"] = self.media_count
        return data


    def calculate_collective_metrics(self, **data) -> Dict[str, Union[int ,float]]:
        return data
        

    def get_collective_metrics(self) -> Dict[str, Union[int, float]]:
        """
        Returns formatted collective metric record for a week.
        """
        data = self._calculate_collective_metrics()
        return self.calculate_collective_metrics(**data)
    
    def set_total_of_metrics(self, metric_name: str) -> None:
        pass

    def calculate_collective_metrics(self, **data) -> Dict[str, Union[int, float]]:
        for key, value in vars(self).items():
            if not key.startswith('_') and key not in ("handle", "id", "platform", "created_on", "expired_on", "meta_data"):
                data[key] = value
        return data
    
    def get_total_sum_of_metric(self) -> Dict[str, Dict[str, Union[int, float]]]:
        data = {}
        data["totals"] = self.meta_data.get("totals", {})
        data["prev_totals"] = self.meta_data.get("prev_totals", {})
        data["grand_totals"] = {}
        for metric_name, metric_value in data["totals"].items():
            data["grand_totals"][metric_name] = merge_metric(data["totals"][metric_name], data["prev_totals"][metric_name])
        return data
    

    def get_metric_rows(self) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Return Metric data with 
        date as key and value containing all metric_names and their value

        for e.g
        views = {'2020-10-21': {'SUBSCRIBE': 10, 'TOTAL': 34}}
        age_gender = {'2020-10-21: {'M.age13-17': 24}}

        @returns {'2020-10-21': {"VIEWS_SUBSCRIBE": 10, 
                    "SUBSCRIBE_TOTAL": 34, "AGE_GENDER_M.age13-17": 24}}
        """
        metric_data = {}
        for metric_name, value in vars(self).items():
            if metric_name.startswith("_") or metric_name in self.COLUMN_WHITELIST:
                continue
            for date_str, metric_dict_value in value.items():
                if date_str not in metric_data:
                    metric_data[date_str] = {}
                for metric_attr, metric_value in metric_dict_value.items():
                    metric_data[date_str] |= {f"{metric_name.upper()}_{metric_attr}": metric_value}
        return metric_data


    def get_columns(self) -> List[str]:
        columns = []
        for key in vars(self).keys():
            if not key.startswith("_") and key not in self.COLUMN_WHITELIST:
                columns.append(key)
        return columns


    def get_prev_totals_row(self) -> Dict[str, Union[int, float]]:
        """
        Returns metric name and totals
        @returns {"VIEWS_SUBSCRIBE": 10, 
                    "SUBSCRIBE_TOTAL": 34, "AGE_GENDER_M.age13-17": 24}
        from above example
        """
        pass

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
        self.set_total_of_metrics("follower_count")
        self.set_total_of_metrics("media_count")
        self.impressions |= response.impressions
        self.set_total_of_metrics("impressions")
        self.reach |= response.reach
        self.set_total_of_metrics("reach")
        self.follower_count |= response.follower_count
        self.set_total_of_metrics("follower_count")
        self.profile_views |= response.profile_views
        self.set_total_of_metrics("impressions")
    

    def reduce_audience_data(self, metric_name: str, data: Dict[str, Dict[str, Union[int, float]]]):
        if len(metric := getattr(self, metric_name, {})) == 0:
            if "prev_totals" in self.meta_data and metric_name in self.meta_data["prev_totals"]:
                data = subtract_merge(data, self.meta_data["prev_totals"][metric_name])
        else:
            last_metric_data: Dict[str, Union[int, float]] = list(metric.values())[-1]
            data = subtract_merge(data, last_metric_data)
        setattr(self, metric_name, data)
        self.set_total_of_metrics(metric_name)


    
    def set_metrics_from_user_demographic_response(self, response: 'InstagramUserDemographicInsightsResponse') -> None:
        self.reduce_audience_data("audience_city", response.audience_city)
        self.reduce_audience_data("audience_gender_age", response.audience_gender_age)
        self.reduce_audience_data("audience_country", response.audience_country)
    
    def set_total_of_metrics(self, metric_name: str) -> None:
        if "totals"  not in self.meta_data:
            self.meta_data["totals"] = {}
        if metric_name not in ["audience_city", "audience_gender_age", "audience_country"]:
            if (attr := getattr(self, metric_name, None)) is not None:
                self.meta_data["totals"][metric_name] = merge_metric(*attr.values())
        else:
            if (attr := getattr(self, metric_name, None)) is not None:
                self.meta_data["totals"][metric_name] = list(attr.values())[-1]
    
    
            




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
 
    objects = YoutubeHandleMetricsManager()


    def calculate_engagements(self) -> None:
        total: Dict[str, Union[int, float]] = self.meta_data["totals"]
        positive_action = total.get("likes",0) + total.get("shares",0) + total.get("comment",0)
        negative_action = total.get("dislikes", 0)
        self.positive_engagement |= {get_current_time().strftime(DATE_FORMAT): {"TOTAL": positive_action}}
        self.negative_engagement |={get_current_time().strftime(DATE_FORMAT): {"TOTAL": negative_action}}
        self.engagement |= {get_current_time().strftime(DATE_FORMAT): {"TOTAL": positive_action + negative_action}}
        self.set_total_of_metrics("positive_engagement")
        self.set_total_of_metrics("negative_engagement")
        self.set_total_of_metrics("engagement")
    
    def calculate_normal_metrics_total(self, data: Dict[str, Dict[str, int]]) -> Union[int, float]:
        return sum([packet["TOTAL"] for packet in data.values()])
    
    

    def set_total_of_metrics(self, metric_name: str) -> None:
        if "totals" not in self.meta_data:
            self.meta_data["totals"] = {}
        if metric_name not in ["viewer_percentage", "shares", "audience_watch_ratio", "relative_retention_performance"]:
            if (attr := getattr(self, metric_name, None)) is not None:
                self.meta_data["totals"][metric_name] = merge_metric(*attr.values())
        else:
            if metric_name not in self.meta_data["totals"]:
                self.meta_data["totals"][metric_name] = 0
            self.meta_data["totals"][metric_name] += self.calculate_normal_metrics_total(getattr(self, metric_name))

    def set_metrics(self, metrics: YTMetrics, save: bool = False) -> None:
        """
        Combines new metrics with the current data and recalculate the totals and engagements
        """
        self.set_total_of_metrics("follower_count")
        self.set_total_of_metrics("media_count")
        for property_name, property_value in metrics.to_dict().items():
            if property_value is None or len(property_value) == 0:
                continue
            attr = getattr(self, property_name, None)
            if attr is None:
                attr = {}
            for day, value in property_value.items():
                if day not in attr:
                    attr[day] = {}
                attr[day] |= value
            setattr(self, property_name, attr)
            self.set_total_of_metrics(property_name)
        self.calculate_engagements()
        if save:
            self.save()
    

















    

