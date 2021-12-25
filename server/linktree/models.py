from typing import Dict, List
from django.db import models
from django.db.models.query import QuerySet
from accounts.models import Account, SocialMediaHandle
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
    """
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="link_tree_accounts")
    background_image = models.URLField(default="")
    avatar_image = models.URLField(default="")
    media_handles = models.JSONField(default=dict)
    description = models.CharField(max_length=250, default="")
    display_name = models.CharField(max_length=250, default="")
    links = models.JSONField(default=dict)
    styles = models.JSONField(default=dict)

    def set_styles_from_template(self, template: LinkWallTemplate, save: bool = True) -> 'LinkWall':
        self.styles = template.styles
        if save:
            self.save()
        return self
    
    def set_media_handles(self, media_handles: Dict[str, Dict[str,str]]) -> None:
        social_media_handles: QuerySet[SocialMediaHandle] = SocialMediaHandle.objects.filter(account=self.account)
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
        for platform, handle_data in media_handles.items():
            if handle_data["url"] not in visited_urls:
                if platform not in transformed_handles:
                    transformed_handles[platform] = []
                transformed_handles[platform].append({
                    "username": handle_data.get("username", None),
                    "avatar": handle_data.get("avatar", None),
                    "url": handle_data.get("url", None)
                })
                
        self.media_handles = transformed_handles
    
    def sync_media_handles(self) -> None:
        self.set_media_handles(self.media_handles)

            

        


    
