from digger.base.request_manager import BaseRequestManager


class InstagramRequestManager(BaseRequestManager):

    def __init__(self) -> None:
        super().__init__({
            "graph": "https://graph.instagram.com",
            "oauth": "https://api.instagram.com/oauth",
            "default": "https://graph.facebook.com/v12.0"
        })