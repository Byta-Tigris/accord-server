from digger.base.request_manager import BaseRequestManager
import json



class FacebookGraphAPIException(Exception):

    def __init__(self, **error) -> None:
        self.error = error
        if self.error != None:
            self.error_msg = json.dumps(error)
        super().__init__(self.error_msg)


class InstagramRequestManager(BaseRequestManager):

    def __init__(self) -> None:
        super().__init__({
            "graph": "https://graph.instagram.com",
            "oauth": "https://api.instagram.com/oauth",
            "default": "https://graph.facebook.com/v12.0"
        })