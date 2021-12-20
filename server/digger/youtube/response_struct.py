from typing import Dict, List, Union
from digger.base.response_struct import ResponseStruct
from digger.youtube.types import YTChannel



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


class YoutubeRefreshTokenResposne(ResponseStruct):

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
        self.nextPageToken = nextPageToken
        self.channles = []
        if items != None:
            self.channles = list(map(lambda data: YTChannel(**data), items))
        super().__init__(url, status_code, **kwargs)
