from django.db import models
from django.db.models.query import QuerySet
from typing import  Any, MutableMapping, Optional, Tuple, Union

from django.db.models.query_utils import Q
from accounts.models import SocialMediaHandle

from utils import get_current_time, get_handle_metrics_expire_time, merge_metric
from utils.types import Platform


class SocialMediaHandleMetricsManager(models.Manager):
    platform = None

    def before_create(self, metric: models.Model, **kwargs) -> models.Model:
        return metric

    def create(self, handle: 'SocialMediaHandle', **kwargs: Any) -> models.Model :
        _platform = self.platform
        if "platform" in kwargs:
            _platform = kwargs["platform"]
        elif "platform" not in kwargs and _platform is None:
            _platform = handle.platform
        metric: models.Model = self.model(
            handle=handle,
            platform=_platform,
            created_on=get_current_time(),
            expired_on=get_handle_metrics_expire_time(),
            meta_data={}
        )
        metric = self.before_create(metric, **kwargs)
        metric.save()
        return metric
    

    def get_recent_metrics(self, handle) -> QuerySet:
        """
        Returns queryset of metrics ordered in descending dates. Recent -> old
        """
        queryset: QuerySet =  self.filter(Q(handle=handle)).latest('expired_on')
        if queryset.exists() and queryset.count() >= 10:
            return queryset[:10]
        return queryset 
    
    def get_latest_metrics(self, handle) -> Union[models.Model, None]:
        """
        Returns the latest and active social media metric
        """
        queryset: QuerySet = self.filter(Q(handle = handle) & Q(expired_on__gte=get_current_time()))
        if queryset.exists():
            return queryset.first()
        return None
    
    def get_or_create(self, handle, defaults: Optional[MutableMapping[str, Any]] = ..., **kwargs: Any) -> Tuple[Any, bool]:
        model: Union[models.Model, None] = self.get_latest_metrics(handle)
        if model:
            return model
        return self.create(handle=handle, **kwargs)
    
    def retain_old_metric_total(self, metric: models.Model) -> models.Model:
        queryset: QuerySet = self.filter(Q(handle=metric.handle) & Q(expired_on__lte=metric.created_on)).order_by('-expired_on')
        if queryset.exists():
            old_metric: models.Model = queryset.first()
            totals = {}
            for key, value in old_metric.meta_data.get("totals").items():
                if key in old_metric.meta_data["prev_totals"]:
                    totals[key] = merge_metric(value, old_metric.meta_data["prev_totals"][key])
            metric.meta_data["prev_totals"] = totals
        return metric



class InstagramHandleMetricsManager(SocialMediaHandleMetricsManager):
    platform = Platform.Instagram


    def before_create(self, metric: models.Model, **kwargs) -> models.Model:
        if "user_insight" in kwargs:
            metric.set_metrics_from_user_insight_response(kwargs["user_insight"])
        if "user_demographic" in kwargs:
            metric.set_metrics_from_user_demographic_response(kwargs["user_demographic"])
        metric = self.retain_old_metric_total(metric)
        return metric



class YoutubeHandleMetricsManager(SocialMediaHandleMetricsManager):
    platform = Platform.Youtube

    def before_create(self, metric: models.Model, **kwargs) -> models.Model:
        metric = self.retain_old_metric_total(metric)
        return metric




    
    
    
        
        
        

        




