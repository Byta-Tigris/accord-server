from typing import Dict, List
from django.test.client import Client
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import Account, SocialMediaHandle
from utils.types import Platform
# Create your tests here.

class TestSocialMediaHandleViews(APITestCase):

    def setUp(self) -> None:
        self.account, self.token_obj = Account.get_test_account()
        
        self.content_type = "application/json"
        self.client = Client(HTTP_CONTENT_TYPE=self.content_type)
        self.autheticated_client = Client(HTTP_AUTHORIZATION=f"Token {self.token_obj.key}", HTTP_CONTENT_TYPE=self.content_type)
        
        self.instagram_handle = SocialMediaHandle.get_test_handle(Platform.Instagram, self.account)
        self.youtube_handle = SocialMediaHandle.get_test_handle(Platform.Youtube, self.account)
    

    def test_retrieve_social_media_handle_view_using_username(self) -> None:


        def check_handle_id(handle_id: str) -> bool:
            return handle_id == self.instagram_handle.handle_uid or handle_id == self.youtube_handle.handle_uid
        
        def verify_handles(handles: Dict[str, str]) -> bool:
            return all(["handle_uid" in handle and check_handle_id(handle["handle_uid"]) for handle in body["data"]])
        
        # Fetching using username
        url = reverse('social-media-handles-retrieve', kwargs={"username": self.account.username})
        res = self.autheticated_client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        body = res.json()
        self.assertTrue("data" in body)
        self.assertTrue(verify_handles(body["data"]))


        # Fetching using me
        url = reverse('social-media-handles-retrieve', kwargs={"username": "me"})
        res = self.autheticated_client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        body = res.json()
        self.assertTrue("data" in body)
        self.assertTrue(verify_handles(body["data"]))

        #Fetching using me and platform

        url = reverse('social-media-handles-retrieve', kwargs={"username": self.account.username})
        res = self.autheticated_client.get(url, data={"platform": Platform.Instagram})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        body = res.json()
        self.assertTrue("data" in body)
        data: List[Dict[str, str]] = body["data"]
        self.assertTrue(len(data) > 0)
        handle = data[0]
        self.assertTrue("platform" in handle and handle["platform"] == Platform.Instagram)




