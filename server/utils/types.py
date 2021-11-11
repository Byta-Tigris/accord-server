from enum import Enum

class StaffRoles(Enum):
    Developer = 1
    Admin = 2


class EntityType(Enum):
    Creator = "Creator"
    Advertiser = "Advertiser"
    Master = "Master"


class Platform(Enum):
    Instagram = "instagram"
    Youtube = "youtube"


class AdvertismentType(Enum):
    Story = "story"
    ShortVideo = "short_video"
    Post = "post"  # Images , audios or video less than 2 min in time
    LongVideo = "long_video"


class Currency(Enum):
    INR = "INR"
    USD = "USD"
        

