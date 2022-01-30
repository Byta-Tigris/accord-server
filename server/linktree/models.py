from datetime import datetime
from pyexpat import model
from django.contrib.auth.models import User
from typing import Dict, Iterable, List
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from accounts.models import Account, SocialMediaHandle
from utils import get_current_time, get_modified_time
from utils.types import LinkwallLinkTypes
# Create your models here.


class LinkWallTemplate(models.Model):
    name = models.CharField(max_length=250, primary_key=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now=True)
    styles = models.JSONField(default=dict)


class LinkwallMediaHandles(models.Model):
    platform = models.CharField(max_length=50, default="")
    username = models.CharField(max_length=70, default="")
    url = models.URLField(default="", unique=True)
    avatar = models.URLField(default="")



class LinkWallLink(models.Model):
    name = models.CharField(max_length=250, default="")
    is_visible = models.BooleanField(default=True)
    created_on = models.DateTimeField(default=get_current_time)
    url = models.URLField(default="")
    icon = models.URLField(default="")
    type = models.CharField(max_length=30, default=LinkwallLinkTypes.Normal)



class LinkWall(models.Model):
    """
    Stores link details along with styling features

    Attributes:\n

    account -- Account with which this link wall is related\n
    background_image -- Background image of the wall (img or gif)
    avatar_image -- Avatar image on the wall, [default=account.avatar]
    description  -- Description for the wall [default=account.description]
    display_name -- Displat name for the wall [default=account.user.get_full_name()]
    media_handles -- Media Links Record, ManyToManyField[LinkwallMediaHandles]
    links -- Links Record, ManyToManyField[LinkWallLink]
    styles -- Style of the wall, css properties
    {
        component {
            property_name: property_value
        }
    }
    """
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="link_tree_accounts")
    background_image = models.URLField(default="")
    avatar_image = models.URLField(default="")
    media_handles = models.ManyToManyField(LinkwallMediaHandles, related_name="links", blank=True, default="")
    description = models.CharField(max_length=250, default="")
    display_name = models.CharField(max_length=250, default="")
    links = models.ManyToManyField(LinkWallLink, related_name="links", blank=True, default="")
    styles = models.JSONField(default=dict)

    views = models.ManyToManyField(
        User, through='LinkwallViewCounterModel', blank=True, related_name="linkwall_views", default='')
    clicks = models.ManyToManyField(
        User, through='LinkClickCounterModel', blank=True, related_name="link_clicks", default="")

    def set_styles_from_template(self, template: LinkWallTemplate, save: bool = True) -> 'LinkWall':
        self.styles = template.styles
        if save:
            self.save()
        return self
    
    def remove_handles(self, handles_url: str) -> None:
        handles: QuerySet[LinkwallMediaHandles] = self.media_handles.filter(url__in=handles_url)
        if handles.exists():
            self.media_handles.remove(*handles)
            handles.delete()
    
    
    
    @staticmethod
    def get_bound_time(self) -> datetime:
        return get_modified_time(hours=1)

    def sync_media_handles(self) -> None:
        self.set_media_handles(self.media_handles)
    
    def get_time_bound_query(self) -> Q:
        current_time = get_current_time()
        min_time_bound = self.get_bound_time()
        return Q(created_on__lte = current_time) & Q(created_on__gte=min_time_bound)

    def add_view(self, user: User) -> None:
        time_bound_query = self.get_time_bound_query()
        query = Q(user=user) & Q(linkwall=self) & time_bound_query
        counter_queryset: QuerySet[LinkwallViewCounterModel] = LinkwallViewCounterModel.objects.filter(query)
        if not counter_queryset.exists():
            counter = LinkwallViewCounterModel(
                 user=user, linkwall=self, created_on=get_current_time())
            counter.save()
            self.clicks.add(counter)

    def add_click(self, user: User, link: str) -> None:
        time_bound_query = self.get_time_bound_query()
        query = Q(user=user) & Q(linkwall=self) & Q(link=link) & time_bound_query
        counter_queryset: QuerySet[LinkClickCounterModel]  = LinkClickCounterModel.objects.filter(query)
        if not counter_queryset.exists():
            counter = LinkClickCounterModel(user=user,
                                            linkwall=self, link=link,
                                            created_on=get_current_time()
                                            )
            counter.save()
            self.clicks.add(counter)

class LinkwallViewCounterModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    linkwall = models.ForeignKey(LinkWall, on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=get_current_time)


class LinkClickCounterModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    linkwall = models.ForeignKey(LinkWall, on_delete=models.CASCADE)
    link = models.URLField(default="")
    created_on = models.DateTimeField(default=get_current_time)
