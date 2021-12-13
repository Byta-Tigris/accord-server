
from django.db import models
from django.db.models import Model
from django.db.models.query import QuerySet


from utils import get_current_time, time_to_string
from utils.types import InstagramHandleMetricData, MetricData, YoutubeHandleMetricData



class SocialMediaHandleMetricsManager(models.Manager):

    def _create(self, metric: Model, data: MetricData) -> Model: ...

    def create(self, handle, data: MetricData):
        queryset: QuerySet = self.filter(handle=handle).order_by('-expired_on')
        if queryset.exists() and (queryset.first()).expired_on >= get_current_time():
            return queryset.first()
        metric: Model = self.model(handle=handle, last_metric_expired_on=(queryset.first()).expired_on)
        metric = self._create(metric, data)
        metric.save()
        return metric
    


class InstagramHandleMetricManager(SocialMediaHandleMetricsManager):
    
    def _create(self, metric: Model, data: InstagramHandleMetricData) -> Model:
        self.model.set_metric("impression", data.impression)
        self.model.set_metric("engagement", data.engagement)
        self.model.set_metric("followers_count", data.followers_count)
        self.model.set_metric("reach", data.reach)

        self.model.set_time_invariant_metric("audience_gender", data.audience_gender)
        self.model.set_time_invariant_metric("audience_age", data.audience_age)
        self.model.set_time_invariant_metric("audience_country", data.audience_country)
        self.model.set_time_invariant_metric("audience_city", data.audience_city)
        return metric


class YoutubeHandleMetricManager(SocialMediaHandleMetricsManager):
    
    def _create(self, metric: Model, data: YoutubeHandleMetricData) -> Model:
        self.model.set_metric("impression", data.impression)
        self.model.set_metric("followers_count", data.impression)
        self.model.set_metric("comments_count", data.impression)
        self.model.set_metric("likes_count", data.impression)
        self.model.set_metric("dislikes_count", data.impression)
        self.model.set_metric("average_view_percentage", data.impression)

        self.model.set_time_invariant_metric("audience_gender", data.audience_gender)
        self.model.set_time_invariant_metric("audience_age", data.audience_age)
        self.model.set_time_invariant_metric("audience_country", data.audience_country)
        self.model.calculate_engagement()
        return metric



    
    

