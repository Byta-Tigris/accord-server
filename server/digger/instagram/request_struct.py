from digger.base.request_struct import RequestStruct
from digger.instagram.response_struct import *
from utils import get_secret
from utils.types import RequestMethod


class InstagramShortLiveTokenRequest(RequestStruct):

    endpoint="/authorize"
    method = RequestMethod.Get
    response_struct = InstagramShortLiveTokenResponse
    url_key = "oauth"

    def __init__(self, code: str) -> None:
        self.code = code
        self.grant_type = "authorization_code"
        self.client_id = get_secret("INSTAGRAM_CLIENT_ID")
        self.client_secret = get_secret("INSTAGRAM_CLIENT_SECRET")
        


class InstagramLongLiveTokenRequest(RequestStruct):
    endpoint = "/access_token"
    method = RequestMethod.Get
    response_struct = InstagramLongLiveTokenResponse
    url_key = "graph"

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.grant_type = "ig_exchange_token"
        self.client_secret = get_secret("INSTAGRAM_CLIENT_SECRET")


class InstagramRefreshLongLiveTokenRequest(RequestStruct):
    endpoint = "/refresh_access_token"
    method = RequestMethod.Get
    response_struct = InstagramLongLiveTokenResponse
    url_key = "graph"

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.grant_type = "ig_refresh_token"
