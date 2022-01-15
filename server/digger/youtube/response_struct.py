from typing import Dict, List, Union
from digger.base.response_struct import ResponseStruct
from digger.youtube.types import YTChannel, YTMetrics, YTVideo



class YoutubeExchangeCodeForTokenResponse(ResponseStruct):

    def __init__(self, url: str, status_code: int,
        error = None, access_token: str = None,
        expires_in: int = None, token_type: str = None,
        scope: str = None, refresh_token: str = None
        , **kwargs) -> None:
        self.error = error
        self.access_token = access_token
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        super().__init__(url, status_code, **kwargs)


class YoutubeRefreshTokenResponse(ResponseStruct):

    def __init__(self, url: str, status_code: int, 
        error = None, access_token: str = None,
        expires_in: int  = None
        , **kwargs) -> None:
        self.error = error
        self.access_token = access_token
        self.expires_in = expires_in
        super().__init__(url, status_code, **kwargs)


class YoutubeChannelListResponse(ResponseStruct):

    def __init__(self, url: str, status_code: int, 
        error = None, nextPageToken: str = None,
        items: List[Dict[str, Union[str, Dict]]] = None
        ,**kwargs) -> None:
        self.error = error
        self.next_page_token = nextPageToken
        self.channels = []
        if items != None:
            self.channels = list(map(lambda data: YTChannel(**data), items))
        super().__init__(url, status_code, **kwargs)


class YoutubeChannelVideoListResponse(ResponseStruct):

    def __init__(self, url: str, status_code: int, error=None, nextPageToken: str = None, items: List[Dict] = None,**kwargs) -> None:
        self.error = error
        self.items: List[YTVideo] = None
        if error == None:
            self.items = []
            for video in items:
                video_id = video["id"]["videoId"]
                self.items.append(YTVideo(video_id, video["snippet"]))
        super().__init__(url, status_code, **kwargs)


class YoutubeMultipleVideoDataResponse(ResponseStruct):

    def __init__(self, url: str, status_code: int, nextPageToken: str = None, error = None, items: List[Dict] = None , **kwargs) -> None:
        self.error = error
        self.next_page_token = nextPageToken
        self.items = None
        if error == None:
            self.items = []
            for video in items:
                video_id = video["id"]
                self.items.append(YTVideo(**video))
        super().__init__(url, status_code, **kwargs)

class YoutubeChannelReportResponse(ResponseStruct):

    def __init__(self, url: str, status_code: int, error = None, columnHeaders: List[Dict[str, str]] = [], rows: List[List[Union[str, int]]] = [], **kwargs) -> None:
        self.error = error
        self.metrics = None
        if error == None:
            self.metrics = YTMetrics.from_yt_response(columnHeaders, rows)
        super().__init__(url, status_code, **kwargs)

class YoutubeSubscriptionBasedChannelReportsResponse(YoutubeChannelReportResponse):
    pass

class YoutubeTimeBasedChannelReportResponse(YoutubeChannelReportResponse):
    pass


class YoutubeDemographicsChannelReportResponse(YoutubeChannelReportResponse):
    pass

class YoutubeSharingServiceChannelReportResponse(YoutubeChannelReportResponse):
    pass

class YoutubeAudienceRetentionVideoReportResponse(YoutubeChannelVideoListResponse):
    pass