from typing import Dict, Union

from utils.types import AdvertismentType, Currency, Platform


class PlatformAdMetaData:
    """Data about each ads on specific platform\n
    
    Key Arguments:\n
    platform -- Platform of ad\n
    ad_type -- Advertisment Type from the  `AdvertisementType` enumeration\n
    max_time -- maximum Time limit in seconds [default=0]\n
    min_time -- minimum time limit in seconds [default=0]\n

    IF max_time or min_time is -1 => then no time limit is bound\n

    """

    def __init__(self, platform: str, ad_type: str, max_time: int = 0, min_time: int = 0) -> None:
        self.platform = platform
        self.ad_type = ad_type
        self.max_time = max_time  # in seconds
        self.min_time = min_time # in seconds

    
    def serialize(self) -> Dict[str, Union[str, int]]:
        return {
            "platform": self.platform,
            "ad_type": self.ad_type,
            "max_time": self.max_time,
            "min_time": self.min_time
        }


class Advertisments:

    # INSTAGRAM ADS
    IG_STORY_AD = PlatformAdMetaData(Platform.Instagram, AdvertismentType.Story, max_time=15)
    IG_SHORT_VIDEO_AD = PlatformAdMetaData(Platform.Instagram, AdvertismentType.ShortVideo, max_time=60)
    IG_IMAGE_POST_AD = PlatformAdMetaData(Platform.Instagram, AdvertismentType.Post, max_time=0)
    IG_VIDEO_POST_AD = PlatformAdMetaData(Platform.Instagram, AdvertismentType.Post, max_time=150)
    IG_LONG_VIDEO_AD = PlatformAdMetaData(Platform.Instagram, AdvertismentType.LongVideo, max_time=3600, min_time=151)

    #YOUTUBE ADS
    YT_LONG_VIDEO_AD = PlatformAdMetaData(Platform.Youtube, AdvertismentType.LongVideo, max_time=-1, min_time=150)


    def __get__(self, value: str) -> PlatformAdMetaData:
        return getattr(self, value)
    

class AdRate:
    def __init__(self, ad_name: str, amount: int, currency: str = Currency.INR, decimal_places: int = 2) -> None:
        self.ad_name = ad_name
        self._amount = amount
        self.currency = currency or Currency.INR
        self.decimal_places = decimal_places
        self.ad_meta_data = Advertisments[ad_name]
    
    @property
    def amount(self) -> float:
        return self._amount / (10 ** self.decimal_places)
    
    def serialize(self) -> Dict[str, Union[str, int]]:
        return {
            "ad_name": self.ad_name,
            "amount": self._amount,
            "currency": self.currency,
            "decimal_places": self.decimal_places
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Union[str,int]]):
        return cls(**data)