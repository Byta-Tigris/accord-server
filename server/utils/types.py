from enum import Enum
from dataclasses import dataclass

class StaffRoles:
    Developer = 1
    Admin = 2


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

