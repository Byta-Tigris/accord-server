from digger.base.request_manager import BaseRequestManager


class GoogleRequestManager(BaseRequestManager):
    def __init__(self) -> None:
        super().__init__({
            "default": "https://www.googleapis.com"
        })