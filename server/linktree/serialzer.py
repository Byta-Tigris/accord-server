
from typing import Dict, List, Union
from .models import LinkCase, LinkWall
from django.urls import reverse
from log_engine.log import logger


LinkWallSerialzedType = Dict[str, Union[str, List[Dict[str, str]], Dict[str, Union[str, Dict[str,str]]]]]



class LinkWallSerializer:

    

    @staticmethod
    def _serialize(link_tree: LinkWall) -> LinkWallSerialzedType:
        try:
            return {
            "username": link_tree.account.username,
            "assets": {
                "background_image": link_tree.background_image,
                "avatar_image": link_tree.avatar_image,
                "styles": link_tree.styles
            },
            "description": link_tree.description,
            "display_name": link_tree.display_name,
            "media_handles": link_tree.media_handles,
            "links": link_tree.links,
            "url": reverse("linktree-username-wall-fetch", args=[link_tree.account.username])
        }
        except Exception as err:
            logger.error(err)
            return {
                "error": "Unable to fetch data"
            }
    
    def __call__(self, link_tree: LinkWall) -> LinkWallSerialzedType:
        return self._serialize(link_tree)
