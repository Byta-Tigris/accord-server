from typing import List
from digger.base.request_struct import RequestStruct
from digger.instagram.request_manager import InstagramRequestManager
from digger.instagram.response_struct import *
from utils import get_secret
from utils.types import RequestMethod



class FacebookLongLiveTokenRequest(RequestStruct):
    """
    The API requests exchanges short-lived token with the long-lived token.
    The short live token will be provided by the user after successfull FB login.
    After success, the access_token along with the expiry time will be stored in the DB.

    Every handle request will refresh the token, and a token only expires if it's not used 
    within 60 days.
    """
    endpoint = "/oauth/access_token"
    method = RequestMethod.Get
    response_struct = FacebookLongLiveTokenResponse

    def __init__(self, access_token: str) -> None:
        self.fb_exchange_token = access_token
        self.grant_type = "fb_exchange_token"
        self.client_secret = get_secret("FACEBOOK_CLIENT_SECRET")
        self.client_id = get_secret("FACEBOOK_CLIENT_ID")


class FacebookPageAccountsRequest(RequestStruct):
    """
    Retrieves all fb pages related with the account\n
    The page will contain all the instagram_business_accounts and their data if connected\n
    """
    endpoint = "/me/accounts"
    method = RequestMethod.Get
    response_struct = FacebookPagesAccountsResponse

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.fields = "name,id,instagram_business_account{username,id,name,biography,followers_count,profile_picture_url,media_count, ig_id}"



class InstagramUserDataRequest(RequestStruct):
    method = RequestMethod.Get
    response_struct = InstagramUserDataResponse

    def __init__(self, ig_user_id: str, access_token: str) -> None:
        self.endpoint = f"/{ig_user_id}"
        self.access_token = access_token
        self.fields = "id,followers_count,media_count,name,profile_picture_url,username,biography"

class InstagramUserDemographicInsightsRequest(RequestStruct):
    method = RequestMethod.Get
    response_struct = InstagramUserDemographicInsightsResponse

    def __init__(self,ig_user_id: str, access_token: str , **kwargs) -> None:
        self.endpoint = f"/{ig_user_id}/insights"
        self.access_token = access_token
        self.period = "lifetime"
        self.metric = "audience_city,audience_country,audience_gender_age"
        

class InstagramUserInsightsRequest(RequestStruct):
    method = RequestMethod.Get
    response_struct = InstagramUserInsightsResponse

    def __init__(self, ig_user_id: str, access_token: str, period: str = "day", **kwargs) -> None:
        self.endpoint = f"/{ig_user_id}/insights"
        self.access_token = access_token
        self.metric = "impressions,reach,follower_count,profile_views"
        self.period = period




class InstagramUserMediaListRequest(RequestStruct):
    method = RequestMethod.Get
    response_struct = InstagramUserMediaListResponse

    def __init__(self,ig_user_id: str, access_token: str, only_id_in_response: bool = False , **kwargs) -> None:
        self.endpoint = f"/{ig_user_id}/media"
        self.access_token = access_token
        self.fields = ",".join(["caption", "comments_count", "id", "ig_id",
                                "is_comment_enabled", "like_count", "media_product_type",
                                "media_type", "media_url", "owner", "permalink", "shortcode",
                                "thumbnail_url", "timestamp", "username", "video_title", "children{id,media_url,media_type}"])
        if only_id_in_response:
            self.fields = "id"
    


class InstagramUserStoriesListRequest(InstagramUserMediaListRequest):
    def __init__(self,ig_user_id: str, access_token: str, only_id_in_response: bool = False , **kwargs) -> None:
        super().__init__(ig_user_id, access_token, only_id_in_response=only_id_in_response, **kwargs)
        self.endpoint = f"/{ig_user_id}/stories"
    

class InstagramSingleMediaDataRequest(InstagramUserMediaListRequest):
    response_struct = InstagramSingleMediaDataResponse

    def __init__(self, ig_media_id: str, access_token: str, **kwargs) -> None:
        super().__init__(ig_media_id, access_token, only_id_in_response=False, **kwargs)
        self.endpoint = f"/{ig_media_id}"


class InstagramSingleMediaInsightsRequest(RequestStruct):   
    def __init__(self,ig_media_id: str, access_token: str, media_product_type = InstagramMediaProductTypes.FEED, media_types = InstagramMediaTypes.IMAGE, **kwargs) -> None:
        self.endpoint = f"/{ig_media_id}/insights"
        self.access_token = access_token
        self.response_struct = InstagramSingleMediaInsightResponse
        self.metric = ["engagement","impressions","reach","saved",]
        if media_product_type == InstagramMediaProductTypes.STORY:
            self.response_struct = InstagramStoryMediaInsightsResponse
            self.metric = ["exits","impressions","reach","taps_forward","taps_back"]
        elif media_types == InstagramMediaTypes.CAROUSEL_ALBUM:
                self.response_struct = InstagramCarouselMediaInsightsResponse
                self.metric = ["carousel_album_engagement","carousel_album_impressions","carousel_album_reach","carousel_album_saved","carousel_album_video_views"]
        elif media_types == InstagramMediaTypes.VIDEO:
            self.metric.append("video_views")
        self.metric = ",".join(self.metric)

class InstagramStoryMediaInsightsRequest(InstagramSingleMediaInsightsRequest):
    def __init__(self,ig_media_id: str, access_token: str, **kwargs) -> None:
        super().__init__(ig_media_id, access_token, media_product_type=InstagramMediaProductTypes.STORY)
            