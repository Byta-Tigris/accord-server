from django.test import TestCase
from digger.instagram.request_manager import InstagramRequestManager
from digger.instagram.request_struct import *
import os


class TestInstagramAPI(TestCase):

    def setUp(self) -> None:
        self.req_manager = InstagramRequestManager()
        self.access_token = os.getenv('FB_GRAPH_API_TEST_TOKEN')
        self.ig_user_id = os.getenv("IG_USER_ID")
        self.ig_media_id = os.getenv('IG_TEST_MEDIA_ID')
        self.media_count = 0
    
    def test_page_accounts_request(self) -> None:
        request = FaceboolPageAccountsRequest(self.access_token)
        response: FacebookPagesAccountsResponse = request(self.req_manager)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.pages), 0)
        self.assertGreater(len(response.get_instagram_account_data()), 0)
        self.media_count = response.get_instagram_account_data()[0].media_count
    
    def test_instagram_user_data_request(self) -> None:
        request = InstagramUserDataRequest(self.ig_user_id, self.access_token)
        response: InstagramUserDataResponse = request(self.req_manager)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.error == None)
        self.assertGreater(response.user.media_count, 0)
        self.assertGreater(response.user.followers_count, 0)
        self.media_count = response.user.media_count
    
    def test_instagram_account_demographic_request(self) -> None:
        request = InstagramUserDemographicInsightsRequest(self.ig_user_id, self.access_token)
        response: InstagramUserDemographicInsightsResponse = request(self.req_manager)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.audience_city), 0)
        self.assertTrue("Santipur, West Bengal" in list(response.audience_city.values())[0])
        self.assertTrue("F.18-24" in list(response.audience_gender_age.values())[0])
        self.assertGreaterEqual(list(response.audience_gender_age.values())[0]["F.18-24"], 7)
    
    def test_instagram_account_insights_request(self) -> None:
        request = InstagramUserInsightsRequest(self.ig_user_id, self.access_token)
        response: InstagramUserInsightsResponse = request(self.req_manager)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.impressions), 0)
        self.assertGreaterEqual(list(response.impressions.values())[0], 0)
        self.assertGreaterEqual(list(response.follower_count.values())[0], 0)
    
    def test_instagram_account_media_list_request(self) -> None:
        request = InstagramUserMediaListRequest(self.ig_user_id, self.access_token, only_id_in_response=True)
        response: InstagramUserMediaListResponse = request(self.req_manager)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        media_count = len(response.data)
        medias: List[IGMedia] = []
        medias += response.data
        while response.paging.has_after() and len(response.data) > 0:
            after = response.paging.after
            response = request(self.req_manager, after=after)
            self.assertEqual(response.status_code, 200)
            media_count += len(response.data)
            medias += response.data
        media_ids = list(map(lambda media: media.id, medias))
        for media in medias:
            if media.media_type == InstagramMediaTypes.CAROUSEL_ALBUM:
                self.assertNotEqual(media.children, None)
                self.assertGreater(len(media.children), 0)
        self.assertTrue(self.ig_media_id in media_ids)
    
    def test_instagram_single_media_data_request(self) -> None:
        request = InstagramSingleMediaDataRequest(self.ig_media_id, self.access_token)
        response: InstagramSingleMediaDataResponse = request(self.req_manager)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.error, None)
        self.assertNotEqual(response.media, None)
        self.assertEqual(response.media.id, self.ig_media_id)

        ## Testing for error
        request = InstagramSingleMediaDataRequest(self.ig_media_id + "0", self.access_token)
        response = request(self.req_manager)
        self.assertNotEqual(response.status_code, 200)
        self.assertNotEqual(response.error, None)
        self.assertEqual(response.media, None)
    
    
    def test_instagram_single_media_insight_request(self) -> None:
        request = InstagramSingleMediaInsightsRequest(self.ig_media_id, self.access_token)
        # breakpoint()
        response: InstagramSingleMediaInsightResponse = request(self.req_manager)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.error, None)
        self.assertNotEqual(response.insights, None)
        self.assertGreater(response.insights.impressions, 0)

        # Testing error
        request = InstagramSingleMediaInsightsRequest(self.ig_media_id + "0", self.access_token)
        response: InstagramSingleMediaInsightResponse = request(self.req_manager)
        self.assertNotEqual(response.status_code, 200)
        self.assertNotEqual(response.error, None)
        self.assertEqual(response.insights, None)

        




        