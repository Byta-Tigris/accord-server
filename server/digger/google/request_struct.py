from typing import Dict, Union
from digger.base.request_struct import RequestStruct
from utils.types import RequestMethod
from .response_struct import *


class GoogleAuthorizedRequest(RequestStruct):

    ignorable_fields = ["access_token"]
    access_token = None
    url_key = "default"

    def get_headers(self) -> Union[None, Dict[str, str]]:
        if self.headers == None:
            self.headers = {}
        self.headers["Authorization"] = f"Bearer {self.access_token}"
        return self.headers



class GoogleUserInfoRequestStruct(GoogleAuthorizedRequest):
    endpoint = "/userinfo/v2/me"
    method = RequestMethod.Get
    response_struct = GoogleUserInfoResponseStruct

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        super().__init__()