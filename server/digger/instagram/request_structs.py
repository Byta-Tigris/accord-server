from digger.base.request_struct import BaseRequestStruct
from digger.base.types import RequestMethod
from .response_consumers import *
from accounts.models import SocialMediaHandle


class InstagramCreatorDetailRequest(BaseRequestStruct):

    response_structs = InstagramCreatorDetailResponse

    def __init__(self, ig_id: str, access_token: str):
        self.ig_id = ig_id
        self.access_token = access_token
        super().__init__(f"/{self.ig_id}", RequestMethod.Get,
            query_params={
                "fields": "biography,id,ig_id,followers_count,media_count,name,profile_picture_url,username",
                "access_token":self.access_token
            }
        )
    @classmethod
    def from_model(cls, model: SocialMediaHandle):
        return cls(model.media_uid, model.access_token)