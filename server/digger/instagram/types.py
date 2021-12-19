from utils.types import InstagramMediaProductTypes, InstagramMediaTypes
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union



class IGMedia:

    def __init__(self,
                id: str = "", ig_id: str = "", is_comment_enabled: bool = True,
                caption: str = None, comment_count: int = 0, like_count: int = 0,
                media_product_type: str = InstagramMediaProductTypes.FEED,
                media_type: str = InstagramMediaTypes.IMAGE, media_url: str = None,
                owner: Dict[str, str] = None, permalink: str = None, shortcode: str = None,
                thumbnail_url: str = None, timestamp: str = None, username: str = None,
                video_title: str = None, **kwargs

                ) -> None:
        self.id = id
        self.ig_id = ig_id
        self.is_comment_enabled = is_comment_enabled
        self.caption = caption
        self.comment_count = comment_count
        self.like_count = like_count
        self.media_product_type = media_product_type
        self.media_type = media_type
        self.media_url = media_url
        self.owner = owner
        self.permalink = permalink
        self.shortcode = shortcode
        self.thumbnail_url = thumbnail_url
        self.timestamp = timestamp
        self.username = username
        self.video_title = video_title
    
    def to_kwargs(self) -> Dict[str, Any]:
        return vars(self)


class PagingCursor:
    def __init__(self, paging: Dict[str, Union[str, Dict[str, str]]]) -> None:
        cursors = paging.get("cursors",{})
        self.before = None
        self.after = None

        if "before" in cursors:
            self.before = cursors["before"]
        if "after" in cursors:
            self.after = cursors["after"]
    
    def to_kwargs(self) -> Dict[str, Dict[str, str]]:
        return {"cursors": {
            "after": self.after,
            "before": self.before
        }}
    
    def has_after(self) -> bool:
        return self.after != None
    
    def has_before(self) -> bool:
        return self.before != None






@dataclass
class IGUser:
    username: Optional[str] = None
    id: Optional[str] = None
    ig_id: Optional[int] = None
    name: Optional[str] = None
    biography: Optional[str] = None
    followers_count: Optional[int] = 0
    profile_picture_url: Optional[str] = ""
    media_count: Optional[int] = 0

    def to_kwargs(self) -> Dict[str, Union[str, int]]:
        return vars(self)


@dataclass
class FacebookPageData:
    name: str
    id: str
    instagram_business_account: Optional[IGUser] = None

    def to_kwargs(self) -> Dict[str, Union[str, Dict[str, Union[str, int]]]]:
        return vars(self)




class InstagramMediaMetrics:

    def __init__(self, engagement: int = 0, 
                    impressions: int = 0, 
                    reach: int = 0, saved: int = 0,
                    video_views: int = 0 ) -> None:
        self.engagement = engagement
        self.impressions = impressions
        self.reach = reach
        self.saved = saved
        self.video_views = video_views


class InstagramCarouselMediaMetrics(InstagramMediaMetrics):

    def __init__(self, carousel_album_engagement: int = 0, carousel_album_impressions: int = 0,
                        carousel_album_reach: int = 0, carousel_album_saved: int = 0,
                        carousel_album_video_views: int = 0) -> None:
        super().__init__(
            carousel_album_engagement, carousel_album_impressions,
            carousel_album_reach, carousel_album_saved, carousel_album_video_views
        )


class InstagramStoryMetrics:

    def __init__(self, exits: int = 0, impressions: int = 0, reach: int = 0, replies: int = 0,
                        taps_forward: int = 0, taps_back: int = 0) -> None:
        self.exits = exits
        self.impressions = impressions
        self.reach = reach
        self.replies = replies
        self.taps_forward = taps_forward
        self.taps_back = taps_back