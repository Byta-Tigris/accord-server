from typing import Dict, List, Union
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from rest_framework.authtoken.models import Token

from accounts.models import Account
from utils.types import EntityType

# Create your tests here.


class TestLinkWallViews(TestCase):
    def setUp(self) -> None:
        self.account: Account = Account.objects.create(
            email="bytatigrisdev2022@gmail.com",
            first_name="Byta",
            last_name="Tigris",
            username="bitatigris",
            entity_type=EntityType.Creator,
            password="helloword103",
            description="none cord",

        )
        self.content_type = "application/json"
        self.token_obj: Token = Token.objects.create(user=self.account.user)
        self.autheticated_client = Client(HTTP_AUTHORIZATION=f"Token {self.token_obj.key}", HTTP_CONTENT_TYPE=self.content_type)
        self.client = Client(HTTP_CONTENT_TYPE=self.content_type)
    
    def test_create_or_update_link_wall(self) -> None:
        url = reverse('create-linkwall')
        fixtures = [
            {
                "args":{
                    "description" : "My personal collection"
                },
                "status_code": 400
            },{
                "args":{
                    "links": []
                },
                "status_code": 401
            },{
                "args":{
                    "links": {
                        "personal_spot": {
                            "url": "https://www.personalspot.com/arbitaty"
                        }
                    },
                    "styles":{
                        "personal_spot_btn":{
                            "background-color": "black"
                        }
                    },
                    "media_handles": {
                        "intagram": [
                            {"url": "https://instagram.com/testuser",
                             "username": "someuser"
                            }
                        ]
                    },
                    "background_image": "https://bg.image.com"
                },
                "status_code": 202
            },
            
        ]

        def validate_media_handle(fixture_handles: List[Dict[str, str]], data_handles: List[Dict[str, str]]):
            for handle in fixture_handles:
                handle_in_data_handles = False
                for handle_in_data in data_handles:
                    if handle_in_data["url"] == handle["url"]:
                        handle_in_data_handles = True
                self.assertTrue(handle_in_data_handles)

        def validate_linkwall(data: Dict[str, Union[str, Dict[str, Union[str, Dict[str, str]]]]],fixture_arg: Dict[str, Union[str, Dict[str, Dict[str, str]]]]) -> None:
            self.assertTrue("username" in data)
            self.assertEqual(data["username"], self.account.username)
            self.assertTrue("description" in data)
            if "description" in fixture_arg:
                self.assertEqual(data["description"], fixture_arg["description"])
            else:
                self.assertEqual(data["description"], self.account.description)
            self.assertTrue("display_name" in data)
            if "display_name" in fixture_arg:
                self.assertEqual(data["display_name"], fixture_arg["display_name"])
            else:
                self.assertEqual(data["display_name"], self.account.user.get_full_name())
            self.assertTrue("assets" in data)
            self.assertTrue("background_image" in data["assets"])
            if "background_image" in fixture_arg:
                self.assertEqual(data["assets"]["background_image"], fixture_arg["background_image"])
            self.assertTrue("avatar_image" in data["assets"])
            if "avatar_image" in fixture_arg:
                self.assertEqual(data["assets"]["avatar_image"], fixture_arg["avatar_image"])
            else:
                self.assertEqual(data["assets"]["avatar_image"], self.account.avatar)
            self.assertTrue("media_handles" in data)
            if "media_handles" in fixture_arg:
                for platform, datas in fixture_arg["media_handles"].items():
                    self.assertTrue(platform in data["media_handles"])
                    validate_media_handle(datas, data["media_handles"][platform])
            self.assertTrue("links" in data)
            if "links" in fixture_arg:
                for key, link_data in fixture_arg["links"].items():
                    self.assertTrue(key in data["links"])
                    self.assertEqual(data["links"][key], link_data)

        
        for fixture in fixtures:
            _client = self.autheticated_client
            if fixture["status_code"] == 401:
               _client = self.client
            res = _client.post(url, data=fixture["args"], content_type=self.content_type)
            self.assertEqual(res.status_code, fixture["status_code"])
            
            if res.status_code == 202:
                data: Dict[str, Dict[str, Union[str, Dict[str, str]]]] = res.json()
                self.assertTrue("data" in data)
                validate_linkwall(data["data"], fixture["args"])
            

        
        update_fixture = {
                "args":{
                    "links": {
                        "personal_spot2": {
                            "url": "https://www.personalspot2.com/arbitaty"
                        },
                        "personal_spot": {
                            "url": "https://www.personalspot.com/arbitaty"
                        }
                    },
                    "styles":{
                        "personal_spot2_btn":{
                            "background-color": "black"
                        },
                        "personal_spot_btn":{
                            "background-color": "black",
                            "color": "white"
                        }
                    },
                    "media_handles": {
                        "intagram": [
                            {"url": "https://instagram.com/testuser2",
                             "username": "someuser3"
                            }
                        ],
                        "youtube": [
                            {
                                "url": "https://youtube.com/channle/dkfgjifjg"
                            }
                        ]
                    },
                    "background_image": "https://bg.image2.com"
                },
                "status_code": 202
            }
        complete_fixture = fixtures[-1]["args"]
        for key, value in update_fixture["args"].items():
            if key not in complete_fixture:
                complete_fixture[key] = value
            else:
                if isinstance(value, dict):
                    complete_fixture[key] |= value
                elif isinstance(value, list):
                    complete_fixture += value
                else:
                    complete_fixture[key] = value
        
        res = self.autheticated_client.post(url, data=update_fixture["args"], content_type=self.content_type)
        self.assertEqual(update_fixture["status_code"], res.status_code)
        body = res.json()
        self.assertTrue("data" in body)
        validate_linkwall(body["data"], complete_fixture)



