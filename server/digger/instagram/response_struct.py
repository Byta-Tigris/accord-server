from typing import Any, Dict, List, Union
from digger.base.response_struct import ResponseStruct
from .types import *
from utils import date_to_string, get_datetime_from_facebook_response, reformat_age_gender, time_to_string


class FacebookLongLiveTokenResponse(ResponseStruct):

    def __init__(self, url: str, status_code: int, access_token: str = None, token_type: str = None, expires_in: int = None, error: str = None, **kwargs) -> None:
        self.error = error
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
        super().__init__(url, status_code)


class FacebookPagesAccountsResponse(ResponseStruct):

    def __init__(self, url: str, status_code: int, data: List[Dict[str, Union[str, Dict[str, int]]]] = [], paging: Dict[str, Union[str, Dict[str, str]]] = {}, error = None, **kwargs) -> None:
        self.error = error
        self.pages: List[FacebookPageData] = list(map(lambda arg: FacebookPageData(**arg), data))
        self.paging: PagingCursor = PagingCursor(paging)
        super().__init__(url, status_code)

    def to_kwargs(self) -> Dict[str, Union[List, Dict]]:
        return {
            "data": list(map(lambda val: val.to_kwargs(), self.pages)),
            "paging": self.paging.to_kwargs()
        }
    
    def get_instagram_account_data(self) -> List[IGUser]:
        ig_user_ls: List[IGUser] = []
        for page in self.pages:
            if page.instagram_business_account != None:
                ig_user_ls.append(page.instagram_business_account)
        return ig_user_ls


class InstagramUserDataResponse(ResponseStruct):
    def __init__(self, url: str, status_code: int, error = None, id: str = None,
            followers_count: int = 0, media_count: int = 0, name: str = None,
            profile_picture_url: str = None, username: str = None, biography: str = None
             , **kwargs) -> None:
        self.error = error
        self.user = IGUser(
            id=id,
            username=username,followers_count=followers_count,
            biography=biography, media_count=media_count, name=name,
            profile_picture_url=profile_picture_url
        )
        super().__init__(url, status_code, **kwargs)


class InstagramUserDemographicInsightsResponse(ResponseStruct):

    def __init__(self, url: str, status_code: int, data: List[Dict[str, Any]] = [], error = None,**kwargs) -> None:
        self.error = error
        self.audience_city: Dict[str, Dict[str, int]] = {}
        self.audience_country: Dict[str,Dict[str, int]] = {}
        self.audience_gender_age: Dict[str, Dict[str, int]] = {}
        if not self.error:
            for insight in data:
                if "name" in insight and "values" in insight and len(insight["values"]) > 0:
                    value = insight["values"][0]
                    end_time = get_datetime_from_facebook_response(value["end_time"])
                    packet = value["value"]
                    if insight["name"] == "audience_gender_age":
                        packet = reformat_age_gender(value)
                    setattr(self, insight["name"], {date_to_string(end_time): packet})
        super().__init__(url, status_code, **kwargs)



class InstagramUserInsightsResponse(ResponseStruct):

    def __init__(self, url: str, status_code: int, data: List[Dict] = [], error = None, **kwargs) -> None:
        self.error = error
        self.impressions: Dict[str, int] = {}
        self.reach: Dict[str, int] = {}
        self.follower_count: Dict[str, int] = {}
        self.profile_views: Dict[str, int] = {}
        for insight in data:
            if "name" in insight and "values" in insight and len(insight["values"]) > 0:
                value = insight["values"][0]
                end_time = get_datetime_from_facebook_response(value["end_time"])
                setattr(self, insight["name"], {date_to_string(end_time): {"TOTAL":value["value"]}})
        super().__init__(url, status_code, **kwargs)





class InstagramUserMediaListResponse(ResponseStruct):

    def __init__(self, url: str, status_code: int, data: List[Dict[str, Any]] = [], paging: Dict[str, Any] = {}, error = None, **kwargs) -> None:
        self.error = error
        self.paging = PagingCursor(paging)
        self.data = list(map(lambda media: IGMedia(**media), data))
        super().__init__(url, status_code, **kwargs)


class InstagramSingleMediaDataResponse(ResponseStruct):

    def __init__(self, url: str, status_code: int, **kwargs) -> None:
        self.error = None
        self.media = None
        if "error" in kwargs:
            self.error = kwargs.get("error", {})
        else:
            self.media = IGMedia(**kwargs)
        super().__init__(url, status_code, **kwargs)


class InstagramSingleMediaInsightResponse(ResponseStruct):
    metrics_class = InstagramMediaMetrics

    def __init__(self, url: str, status_code: int, data: List[Dict] = [], error = None, **kwargs) -> None:
        self.error = error
        self.insights = None
        if error == None:
            args = {}
            for metric in data:
                if "name" in metric and "values" in metric and len(metric["values"]) > 0:
                    value = metric["values"][0]
                    args[metric["name"]] = value["value"]
            self.insights = self.metrics_class(**args)
        super().__init__(url, status_code, **kwargs)


class InstagramCarouselMediaInsightsResponse(InstagramSingleMediaInsightResponse):
    metrics_class = InstagramCarouselMediaMetrics


class InstagramStoryMediaInsightsResponse(InstagramSingleMediaInsightResponse):
    metrics_class  = InstagramStoryMetrics






