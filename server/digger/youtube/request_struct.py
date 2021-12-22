from datetime import datetime, timedelta
from digger.base.request_struct import RequestStruct, RequestMethod
from .response_struct import *
from utils import YOUTUBE_RESPONSE_DATE_FORMAT, get_current_time, get_secret


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
    url_key = "oauth"

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
    url_key = "oauth"

    def __init__(self, refresh_token: str) -> None:
        self.refresh_token = refresh_token
        self.grant_type = "refresh_token"
        self.client_id = get_secret("YOUTUBE_CLIENT_ID")
        self.client_secret = get_secret("YOUTUBE_CLIENT_SECRET")


class YoutubeAuthorizedRequest(RequestStruct):

    ignorable_fields = ["access_token"]
    access_token = None
    url_key = "default"

    def get_headers(self) -> Union[None, Dict[str, str]]:
        if self.headers == None:
            self.headers = {}
        self.headers["Authorization"] = f"Bearer {self.access_token}"
        return self.headers



class YoutubeAuthorizedAnalyticsRequest(YoutubeAuthorizedRequest):
    url_key = "analytics"


class YoutubeChannelListRequest(YoutubeAuthorizedRequest):
    endpoint = "/channels"
    method = RequestMethod.Get
    response_struct = YoutubeChannelListResponse

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.part = "snippet,topicDetails,statistics,auditDetails"
        self.mine = True
        super().__init__()


class YoutubeChannelVideoListRequest(YoutubeAuthorizedRequest):
    """
    
    """
    endpoint = "/search"
    method = RequestMethod.Get
    response_struct = YoutubeChannelVideoListResponse

    def __init__(self, access_token: str, max_results: int = 10) -> None:
        self.access_token = access_token
        self.part = "snippet"
        self.forMine = True
        self.maxResults = max_results
        self.order = "date"
        self.type = "video"
        super().__init__()


class YoutubeMultipleVideoDataRequest(YoutubeAuthorizedRequest):
    endpoint = '/video'
    method = RequestMethod.Get
    response_struct = YoutubeMultipleVideoDataResponse

    def __init__(self, access_token: str, video_ids: List) -> None:
        self.access_token = access_token
        self.id = ",".join(video_ids)
        self.part = "snippet,statistics,topicDetails,status"
        super().__init__()


class YoutubeChannelReportRequest(YoutubeAuthorizedAnalyticsRequest):
    endpoint = "/query"
    method = RequestMethod.Get
    DATE_FORMAT = YOUTUBE_RESPONSE_DATE_FORMAT

    def __init__(self, access_token, end_date: datetime = get_current_time(), start_date: datetime = None) -> None:
        self.access_token = access_token
        self.endDate =end_date
        self.startDate = self.endDate
        if start_date != None:
            self.startDate = start_date
        self.startDate = self.startDate.strftime(self.DATE_FORMAT)
        self.ids = "channel==MINE"
        super().__init__()
        



class YoutubeSubscriptionBasedChannelReportRequest(YoutubeChannelReportRequest):
    response_struct = YoutubeSubscriptionBasedChannelReportsResponse

    def __init__(self,access_token: str, end_date: datetime = get_current_time(), start_date: datetime = None) -> None:
        super().__init__(access_token, end_date=end_date, start_date=start_date)
        self.dimesions = "subscribedStatus,day"
        self.sort = "day"
        self.metrics = ",".join(["views", "estimatedMinutesWatched",
                                 "averageViewDuration", "averageViewPercentage", "annotationClickThroughRate", "annotationCloseRate",
                                 "annotationImpressions", "annotationClickableImpressions", "annotationClosableImpressions",
                                 "annotationClicks", "annotationCloses", "cardClickRate", "cardTeaserClickRate", "cardImpressions",
                                 "cardTeaserImpressions", "cardClicks", "cardTeaserClicks"])


class YoutubeTimeBasedChannelReportRequest(YoutubeChannelReportRequest):
    response_struct = YoutubeTimeBasedChannelReportResponse

    def __init__(self, access_token: str, end_date: datetime = get_current_time(), start_date: datetime = None, video_id: str = None) -> None:
        super().__init__(access_token, end_date=end_date, start_date=start_date)
        self.dimesions = "day"
        self.sort = "day"
        self.metrics = ",".join(["views", "comments", "likes", "dislikes",
                                 "shares", "estimatedMinutesWatched",
                                 "averageViewDuration", "averageViewPercentage",
                                 "annotationClickThroughRate", "annotationCloseRate", "annotationImpressions",
                                 "annotationClickableImpressions", "annotationClosableImpressions", "annotationClicks",
                                 "annotationCloses", "cardClickRate", "cardTeaserClickRate", "cardImpressions", "cardTeaserImpressions",
                                 "cardClicks", "cardTeaserClicks", "subscribersGained", "subscribersLost"])
        if video_id:
            self.filters = f"video=={video_id}"


class YoutubeDemographicsChannelReportRequest(YoutubeChannelReportRequest):
    response_struct = YoutubeDemographicsChannelReportResponse

    def __init__(self, access_token: str, end_date: datetime = get_current_time(), start_date: datetime = None,video_id: str = None) -> None:
        super().__init__(access_token, end_date=end_date, start_date=start_date)
        self.dimensions = "ageGroup,gender"
        self.metrics = "viewerPercentage"
        if video_id:
            self.filters = f"video=={video_id}"


class YoutubeSharingServiceChannelReportRequest(YoutubeChannelReportRequest):
    response_struct = YoutubeSharingServiceChannelReportResponse
    def __init__(self, access_token: str, end_date: datetime = get_current_time(), start_date: datetime = None, video_id: str = None) -> None:
        super().__init__(access_token, end_date=end_date, start_date=start_date)
        self.dimensions = "sharingService,subscribedStatus"
        self.metrics = "shares"
        if video_id:
            self.filters = f"video=={video_id}"

class YoutubeAudienceRetentionVideoReportRequest(YoutubeChannelReportRequest):
    response_struct = YoutubeAudienceRetentionVideoReportResponse

    def __init__(self, access_token, video_id, published_on: datetime, end_date: datetime = get_current_time()) -> None:
        super().__init__(access_token, end_date=end_date, start_date=published_on)
        self.dimension = "elapsedVideoTimeRatio"
        self.metrics = "audienceWatchRatio,relativeRetentionPerformance"
        self.filters = f"video=={video_id}"
