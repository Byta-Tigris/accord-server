from datetime import datetime
from django.contrib.auth.models import User
from typing import Dict, List
from django.db import models
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from accounts.models import Account, SocialMediaHandle
from utils import get_current_time, get_modified_time
# Create your models here.


class LinkWallTemplate(models.Model):
    name = models.CharField(max_length=250, primary_key=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now=True)
    styles = models.JSONField(default=dict)


class LinkWall(models.Model):
    """
    Stores link details along with styling features

    Attributes:\n

    account -- Account with which this link wall is related\n
    background_image -- Background image of the wall (img or gif)
    avatar_image -- Avatar image on the wall, [default=account.avatar]
    description  -- Description for the wall [default=account.description]
    display_name -- Displat name for the wall [default=account.user.get_full_name()]
    media_handles -- Media Links Record
      {
          platform: [
              {
                  url
                  username: str | None
                  avatar: str | None
              }
          ]
      }

    links -- {
        name: {
            url
        }
    }
    styles -- Style of the wall, css properties
    {
        class_name {
            property_name: property_value
        }
    }
    """
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="link_tree_accounts")
    background_image = models.URLField(default="")
    avatar_image = models.URLField(default="")
    media_handles = models.JSONField(default=dict)
    description = models.CharField(max_length=250, default="")
    display_name = models.CharField(max_length=250, default="")
    links = models.JSONField(default=dict)
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

    def set_media_handles(self, media_handles: Dict[str, Dict[str, str]]) -> None:
        social_media_handles: QuerySet[SocialMediaHandle] = SocialMediaHandle.objects.filter(
            Q(account=self.account) & Q(is_disabled=False))
        transformed_handles: Dict[str, List[Dict[str, str]]] = {}
        visited_urls = []
        for handle in social_media_handles:
            if handle.platform not in transformed_handles:
                transformed_handles[handle.platform] = []
            transformed_handles[handle.platform].append({
                "username": handle.username,
                "avatar": handle.avatar,
                "url": handle.handle_url
            })
            visited_urls.append(handle.handle_url)
        for platform, platform_handles in media_handles.items():
            for handle_data in platform_handles:
                if handle_data["url"] not in visited_urls:
                    if platform not in transformed_handles:
                        transformed_handles[platform] = []
                    transformed_handles[platform].append({
                        "username": handle_data.get("username", None),
                        "avatar": handle_data.get("avatar", None),
                        "url": handle_data.get("url", None)
                    })

        self.media_handles = transformed_handles
    
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


class LinkwallViewCounterModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    linkwall = models.ForeignKey(LinkWall, on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=get_current_time)


class LinkClickCounterModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    linkwall = models.ForeignKey(LinkWall, on_delete=models.CASCADE)
    link = models.TextField(default='')
    created_on = models.DateTimeField(default=get_current_time)
