from digger.base.request_manager import BaseRequestManager


class YoutubeRequestManager(BaseRequestManager):

    def __init__(self) -> None:
        super().__init__({
            "oauth":"https://oauth2.googleapis.com",
            "analytics": "https://youtubeanalytics.googleapis.com/v2",
            "default": "https://www.googleapis.com/youtube/v3"
        })