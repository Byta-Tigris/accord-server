from typing import List, Union
from django.test import TestCase
import os

from accounts.models import Account, SocialMediaHandle
from digger.instagram.digger import InstagramDigger
from utils.types import EntityType


class TestInstagramDigger(TestCase):

    def setUp(self) -> None:
        self.access_token = os.getenv('FB_GRAPH_API_TEST_TOKEN')
        self.ig_user_id = os.getenv('IG_USER_ID')
        self.account = Account.objects.create(
            email="bitatigrisdev@gmail.com",
            password="testing@123",
            first_name="Bita",
            last_name="Tigris",
            username="bitatigris",
            entity_type=EntityType.Creator
        )
        self.digger = InstagramDigger()
        self.ig_user: SocialMediaHandle = self.get_social_media_handle()
        if self.ig_user is None:
            self.assertTrue(False,  "No handle found")
    
    def get_social_media_handle(self) -> Union[SocialMediaHandle, None]:
        handles: List[SocialMediaHandle] = self.digger.resync_social_media_handles(self.account, self.access_token)
        for handle in handles:
            if handle.handle_uid == self.ig_user_id:
                handle.set_access_token(self.access_token, 60*24*60*60)
                return handle
        return None

    def test_update_handle_data(self) -> None:
        
        handle: SocialMediaHandle = self.digger.update_handle_data(self.ig_user)
        self.assertTrue(handle is not None)
        self.assertGreater(handle.follower_count, 0)
        self.assertGreater(handle.media_count, 0)
    

    def test_update_handle_insights(self) -> None:
        handle_metric = self.digger.update_handle_insights(self.ig_user, save=True)
        self.assertTrue(handle_metric is not None)
        self.assertTrue(len(handle_metric.impressions) > 0)

    
        