from typing import Dict, Iterable, List, Union
from .models import LinkWall, LinkWallLink, LinkwallMediaHandles
from django.urls import reverse
from log_engine.log import logger



LinkWallSerialzedType = Dict[str, Union[str, List[Dict[str, str]], Dict[str, Union[str, Dict[str,str]]]]]



class LinkWallSerializer:


    def serialize_media_handle(self,media_handle: LinkwallMediaHandles) -> Dict[str, str]:
        return {
            "username": media_handle.username,
            "url": media_handle.url,
            "avatar": media_handle.avatar,
            "platform": media_handle.platform
        }
    
    def serialize_media_handle_queryset(self, media_handles: Iterable[LinkwallMediaHandles]) -> Dict:
        handles: Dict[str, List[Dict[str, str]]] = {}
        for handle in media_handles:
            if handle.platform not in handles:
                handles[handle.platform] = []
            handles[handle.platform].append(self.serialize_media_handle(handle))
        return handles
    

    def serialize_link(self,link: LinkWallLink) -> Dict[str, Union[str, bool]]:
        return {
            "name": link.name,
            "is_visible": link.is_visible,
            "url": link.url,
            "icon": link.icon,
            "type": link.type
        }
    
    def serialize_link_queryset(self, links: Iterable[LinkWallLink]) -> Dict[str, Dict[str, Union[str, bool]]]:
        return [self.serialize_link(link) for link in links]





    def _serialize(self,link_tree: LinkWall, current_username: str = None) -> LinkWallSerialzedType:
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
            "media_handles": self.serialize_media_handle_queryset(link_tree.media_handles.all()),
            "links": self.serialize_link_queryset(link_tree.links.filter(is_visible=True)),
            "url": reverse("linktree-username-wall-fetch", args=[link_tree.account.username]),
            "is_owner": current_username is not None and link_tree.account.username == current_username
        }
        except Exception as err:
            logger.error(err)
            return {
                "error": "Unable to fetch data"
            }
    
    def __call__(self, link_tree: LinkWall, current_username: str = None) -> LinkWallSerialzedType:
        return self._serialize(link_tree, current_username)
