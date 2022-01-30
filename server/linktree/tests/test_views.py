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
        self.autheticated_client = Client(
            HTTP_AUTHORIZATION=f"Token {self.token_obj.key}", HTTP_CONTENT_TYPE=self.content_type)
        self.client = Client(HTTP_CONTENT_TYPE=self.content_type)

    def test_create_link_wall(self) -> None:
        links = [{
            "name": "Maritime",
            "url": "https://iconscout.com/unicons/explore/line",
        }]
        breakpoint()
        res = self.client.post(
            reverse("add-link"), data={"links": links}, content_type=self.content_type)
        self.assertEqual(res.status_code, 202)
        body = res.json()
        self.assertEqual("data" in body)
        data = body["data"]
        self.assertEqual(data["username"], self.account.username)
        self.assertEqual(data["description"], self.account.description)
        self.assertEqual(data["links"][0]["name"], links[0]["name"])
        self.assertEqual(data["links"][0]["url"], links[0]["url"])

    def test_add_link(self) -> None:
        links = [
            {
                "name": "Required",
                "url": "https://iconscout.com/unicons/explore/line/required",
            }, {
                "name": "Requirement",
                "url": "https://iconscout.com/unicons/explore/line/requirement",
            }
        ]

        for link in links:
            res = self.client.post(
                reverse("add-link"), data={"links": [link]}, content_type=self.content_type)
            self.assertEqual(res.status_code, 202)
            body = res.json()
            self.assertEqual("data" in body)
            data = body["data"]
            self.assertTrue(any(map(lambda _link: _link["name"] == link["name"] and _link["url"] == link["url"], data["links"] )))

