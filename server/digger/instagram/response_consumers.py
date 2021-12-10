

from typing import Dict
from digger.base.response_consumer import BaseResponseStruct
from digger.base.types import Response


class InstagramCreatorDetailResponse(BaseResponseStruct):

    def __init__(self, resp: Response):
        self.status_code = resp.status_code
        data: Dict = resp.json()
        self.id = data.get("id", None)
        self.description = data.get("biography", "")
        self.username = data.get("username", "")
        self.fan_count = data.get("followers_count", 0)
        self.avatar = data.get("profile_picture_url", None)
        self.media_count = data.get("media_count", 0)
        self.name = data.get("name", "")
        self.ig_id = data.get("ig_id", None)
        super().__init__(self.status_code)


class InstagramCreatorInsightResponse(BaseResponseStruct):

    def __init__(self, resp: Response):

        super().__init__(resp.status_code)