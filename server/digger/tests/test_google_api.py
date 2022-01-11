from unittest import TestCase
from digger.google.request_manager import GoogleRequestManager
from digger.google.request_struct import *


class TestGoogleAPI(TestCase):

    def setUp(self) -> None:
        self.request_manager = GoogleRequestManager()
    
    def test_user_info(self) -> None:
        access_token = input("Enter access token: ")
        if not (len(access_token) and access_token):
            self.fail("Must provide valid access token when testing")
        request = GoogleUserInfoRequestStruct(access_token)
        print(request.get_params(), request.get_ignorable_fields())
        response: GoogleUserInfoResponseStruct = request(self.request_manager)
        self.assertEqual(response.error, None)
        self.assertTrue(response.is_email_verified)
        self.assertNotEqual(response.email, None)
        self.assertNotEqual(response.full_name, None)