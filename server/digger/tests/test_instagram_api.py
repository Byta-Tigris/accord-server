from django.test import TestCase
from digger.instagram.request_manager import InstagramRequestManager
from digger.instagram.request_struct import *
import os


class TestInstagramAPI(TestCase):

    def setUp(self) -> None:
        self.req_manager = InstagramRequestManager()
        self.access_token = os.getenv('FB_GRAPH_API_TEST_TOKEN')
    
    def test_page_accounts_request(self) -> None:
        request = FaceboolPageAccountsRequest(self.access_token)
        response: FacebookPagesAccountsResponse = request(self.req_manager)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.pages), 0)
        self.assertGreater(len(response.get_instagram_account_data()), 0)

        