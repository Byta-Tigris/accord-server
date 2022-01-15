from unittest import TestCase

from digger.youtube.request_manager import YoutubeRequestManager
from digger.youtube.request_struct import *
from utils import get_secret


class TestYoutubeRequestAPI(TestCase):
    """
    Youtube Test api request is very sensitive and acces token is alive only for an hour.
    Needed to be refreshed
    """

    def setUp(self) -> None:
        self.request_manager = YoutubeRequestManager()
        self.token = get_secret('YOUTUBE_TOKEN')

    # def get_token_from_code(self) -> YoutubeExchangeCodeForTokenResponse:
    #     code = get_secret("YOUTUBE_OAUTH_CODE")
    #     request = YoutubeExchangeCodeForTokenRequest(code, "http://localhost:5500")
    #     response: YoutubeExchangeCodeForTokenResponse = request(self.request_manager)
    #     return response
    
    # def test_exchange_code_for_token_request(self) -> None:
    #     response = self.get_token_from_code()
    #     self.assertEqual(response.error, None)
    #     self.assertNotEqual(response.access_token, None)
    #     self.assertGreater(response.expires_in, 0)
    #     self.assertNotEqual(response.refresh_token, None)

    def test_refresh_token_request(self) -> None:
        request = YoutubeRefreshTokenRequest(get_secret('YOUTUBE_REFRESH_TOKEN'))
        response: YoutubeRefreshTokenResponse = request(self.request_manager)
        self.assertEqual(response.error, None)
        self.assertNotEqual(response.access_token, None)
        self.token = response.access_token
        print(self.token)
    
    def test_channel_list_request(self) -> None:
        request = YoutubeChannelListRequest(self.token)
        response: YoutubeChannelListResponse = request(self.request_manager)
        self.assertEqual(response.error, None)
        # self.assertNotEqual(response.channels, None)
        self.assertGreater(len(response.channels), 0)
    

    def test_channel_video_list(self) -> None:
        request = YoutubeChannelVideoListRequest(self.token)
        response: YoutubeChannelVideoListResponse = request(self.request_manager)
        self.assertEqual(response.error, None)
        self.assertNotEqual(response.items, None)
        self.assertGreater(len(response.items), 0)
        for video in response.items:
            self.assertNotEqual(video.id, None)
    
    def test_time_based_and_subscription_based_report_request(self) -> None:
        # breakpoint()
        request = YoutubeSubscriptionBasedChannelReportRequest(self.token, start_date="2017-10-07", end_date="2022-01-15")
        response: YoutubeSubscriptionBasedChannelReportsResponse = request(self.request_manager)
        print(response.error)
        self.assertEqual(response.error, None)
        self.assertNotEqual(response.metrics, None)
        print(response.metrics)
        self.assertGreater(len(response.metrics.views), 0)
        subscription_based_metrics: YTMetrics = response.metrics

        request = YoutubeTimeBasedChannelReportRequest(self.token, start_date="2017-10-07", end_date="2022-01-15")
        response: YoutubeTimeBasedChannelReportResponse = request(self.request_manager)
        print(response.error)
        self.assertEqual(response.error, None)
        self.assertNotEqual(response.metrics, None)
        self.assertGreater(len(response.metrics.views), 0)
        time_based_metrics: YTMetrics = response.metrics

        # breakpoint()
        completed_metrics = time_based_metrics + subscription_based_metrics
        self.assertNotEqual(completed_metrics, None)
        self.assertGreater(len(completed_metrics.views), 0)
        for date_str in completed_metrics.views.keys():
            if date_str in subscription_based_metrics.views:
                subs_data = subscription_based_metrics.views[date_str]
                self.assertTrue('SUBSCRIBED' in subs_data or 'UNSUBSCRIBED' in subs_data)
            if date_str in time_based_metrics.views:
                times_data = time_based_metrics.views[date_str]
                self.assertTrue('TOTAL' in times_data)
            








