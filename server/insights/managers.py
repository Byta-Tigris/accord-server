from django.db import models
from django.db.models.query import QuerySet
from typing import _T, Any, MutableMapping, Optional, Tuple, Union

from django.db.models.query_utils import Q
from accounts.models import SocialMediaHandle

from utils import get_current_time, get_handle_metrics_expire_time
from utils.types import Platform


class SocialMediaHandleMetricsManager(models.Manager):
    platform = None

    def before_create(self, metric: models.Model, **kwargs) -> models.Model:
        return metric

    def create(self, **kwargs: Any) -> models.Model :
        _platform = self.platform
        assert "handle" in kwargs, "Social media handle must be provided"
        handle: SocialMediaHandle = kwargs["handle"]
        if "platform" in kwargs:
            _platform = kwargs["platform"]
        elif "platform" not in kwargs and _platform is None:
            _platform = handle.platform
        metric: models.Model = self.model(
            handle=handle,
            platform=_platform,
            created_on=get_current_time(),
            expired_on=get_handle_metrics_expire_time(),
        )
        metric = self.before_create()
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
        Returns the latest social media metric
        """
        queryset: QuerySet = self.filter(Q(handle = handle) & Q(expired_on__gte=get_current_time()))
        if queryset.exists():
            return queryset.first()
        return None
    
    def get_or_create(self, handle, defaults: Optional[MutableMapping[str, Any]] = ..., **kwargs: Any) -> Tuple[_T, bool]:
        model: Union[models.Model, None] = self.get_latest_metrics(handle)
        if model:
            return model
        return self.create(handle=handle, **kwargs)


class InstagramHandleMetricsManager(SocialMediaHandleMetricsManager):
    platform = Platform.Instagram


    def before_create(self, metric: models.Model, **kwargs) -> models.Model:
        if "user_insight" in kwargs:
            metric.set_metrics_from_user_insight_response(kwargs["user_insight"])
        if "user_demographic" in kwargs:
            metric.set_metrics_from_user_demographic_response(kwargs["user_demographic"])
        return metric

    
    
    
        
        
        

        




