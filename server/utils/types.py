from enum import Enum
from dataclasses import dataclass

class StaffRoles:
    Developer = 1
    Admin = 2


class InstagramMediaProductTypes:
    AD = "AD"
    FEED = "FEED"
    IGTV = "IGTV"
    STORY = "STORY"


class InstagramMediaTypes:
    CAROUSEL_ALBUM = "CAROUSEL_ALBUM"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"

class EntityType:
    Creator = "creator"
    Advertiser = "advertiser"
    Master = "master"


class Platform:
    Instagram = "instagram"
    Youtube = "youtube"


class AdvertismentType:
    Story = "story"
    ShortVideo = "short_video"
    Post = "post"  # Images , audios or video less than 2 min in time
    LongVideo = "long_video"


class Currency:
    INR = "INR"
    USD = "USD"


class RequestMethod:
    Get = "GET"
    Post = "POST"


class YTSubscriptionStatus:
    UNSUBSCRIBED = "UNSUBSCRIBED"
    SUBSCRIBED = "SUBSCRIBED"



class MetricData:
    pass


@dataclass
class InstagramHandleMetricData(MetricData):
    impression: int
    engagement: float
    followers_count: int
    reach: int
    audience_gender: dict
    audience_age: dict
    audience_country: dict
    audience_city: dict
    

@dataclass
class YoutubeHandleMetricData(MetricData):
    impression: int
    followers_count: int
    comments_count: int
    likes_count: int
    dislikes_count: int
    shares_count: int
    average_view_percentage: float
    audience_gender: dict
    audience_age: dict
    audience_country: dict



class LinkwallLinkTypes :
    Header = "header"
    MusicLink = "music_link"
    VideoLink = "video_link"
    ContactDetail = "contact_detail"
    FormLink = "form_link"
    Normal = "normal"