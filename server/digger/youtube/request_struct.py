from digger.base.request_struct import RequestStruct, RequestMethod
from .response_struct import *
from utils import get_secret


"""
SCOPES:
    https://www.googleapis.com/auth/youtube 
    https://www.googleapis.com/auth/youtube.readonly
    https://www.googleapis.com/auth/youtubepartner-channel-audit
    https://www.googleapis.com/auth/yt-analytics-monetary.readonly

    WHEN USER ENABLES TO EDIT AND UPLOAD VIDEOS:
    https://www.googleapis.com/auth/youtube.force-ssl
    https://www.googleapis.com/auth/youtube.upload
"""

class YoutubeExchangeCodeForTokenRequest(RequestStruct):

    endpoint = "/token"
    method = RequestMethod.Post
    response_struct = YoutubeExchangeCodeForTokenResponse

    def __init__(self, code: str, redirect_uri: str) -> None:
        self.code = code
        self.redirect_uri = redirect_uri
        self.client_id = get_secret("YOUTUBE_CLIENT_ID")
        self.client_secret = get_secret("YOUTUBE_CLIENT_SECRET")
        self.grant_type = "authorization_code"


class YoutubeRefreshTokenRequest(RequestStruct):
    endpoint = "/token"
    method = RequestMethod.Post
    repsonse_struct = YoutubeRefreshTokenResposne

    def __init__(self, refresh_token: str) -> None:
        self.refresh_token = refresh_token
        self.grant_type = "refresh_token"
        self.client_id = get_secret("YOUTUBE_CLIENT_ID")
        self.client_secret = get_secret("YOUTUBE_CLIENT_SECRET")


class YoutubeAuthorizedRequest(RequestStruct):

    ignorable_fields = ["access_token"]
    access_token = None

    def __init__(self) -> None:
        self.headers = {"Authorization": f"Bearer {self.access_token}"}


class YoutubeChannelListRequest(YoutubeAuthorizedRequest):
    endpoint = "/channels"
    method = RequestMethod.Get
    response_struct = YoutubeChannelListResponse

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.part = "snippet,topicDetails,statistics,auditDetails"
        self.mine = True