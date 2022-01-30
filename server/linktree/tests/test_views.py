import json
from typing import Dict, List, Union
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from rest_framework.authtoken.models import Token

from accounts.models import Account
from utils.types import EntityType, LinkWallComponents, LinkwallLinkTypes, LinkwallManageActions, Platform

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
        # breakpoint()
        res = self.autheticated_client.post(reverse("manage-linkwall", args=[LinkwallManageActions.AddLink]), data={"links": links}, content_type=self.content_type)
        self.assertEqual(res.status_code, 202)
        body = res.json()
        self.assertTrue("data" in body)
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
            res = self.autheticated_client.post(reverse("manage-linkwall", args=[LinkwallManageActions.AddLink]), data={"links": [link]}, content_type=self.content_type)
            self.assertEqual(res.status_code, 202)
            body = res.json()
            self.assertTrue("data" in body)
            data = body["data"]
            self.assertTrue(any(map(lambda _link: _link["name"] == link["name"] and _link["url"] == link["url"], data["links"] )))


    def test_edit_link(self) -> None:
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
            res = self.autheticated_client.post(reverse("manage-linkwall", args=[LinkwallManageActions.AddLink]), data={"links": [link]}, content_type=self.content_type)
        
        edit_links = [
            {
                "name": "Required All the way",
                "url": "https://iconscout.com/unicons/explore/line/required",
                "type": LinkwallLinkTypes.VideoLink
            }
        ]
        for link in edit_links:
            res = self.autheticated_client.post(reverse("manage-linkwall", args=[LinkwallManageActions.EditLink]), data={"link": link}, content_type=self.content_type)
            self.assertEqual(res.status_code, 202)
            data = res.json()["data"]
            print(data)
            def validate_link(provided: Dict, link: Dict) -> bool:
                return provided["name"] == link["name"] and provided["type"] == link["type"]
            self.assertTrue(any(map(lambda _data: validate_link(_data, link), data["links"])))
    
    def test_remove_link(self) -> None:
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
            res = self.autheticated_client.post(reverse("manage-linkwall", args=[LinkwallManageActions.AddLink]), data={"links": [link]}, content_type=self.content_type)
        
        remove_links = ["https://iconscout.com/unicons/explore/line/required"]
        for link in remove_links:
            res = self.autheticated_client.post(reverse("manage-linkwall", args=[LinkwallManageActions.RemoveLink]), data={"links":[ link]}, content_type=self.content_type)
            self.assertEqual(res.status_code, 202)
            data = res.json()["data"]
            print(data)
            self.assertEqual(len(data["links"]), 1)
    
    def test_edit_props_link(self) -> None:
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
            res = self.autheticated_client.post(reverse("manage-linkwall", args=[LinkwallManageActions.AddLink]), data={"links": [link]}, content_type=self.content_type)
        
        assets = [
            {
                "background_image": "https://www.geeksforgeeks.org/prefetch_related-and-select_related-functions-in-django/"
            },
            {
                "background_image": "https://www.geeksforgeeks.org/prefetch_related-and-select_related-functions-in-django/d",
                "display_name": "Random Guy"
            }, {
                "avatar_image": "https://stackoverflow.com/questions/15933689/how-to-get-primary-keys-of-objects-created-using-django-bulk-create",
                "description": "Twisted men"
            }
        ]
        for asset in assets:
            res = self.autheticated_client.post(reverse("manage-linkwall", args=[LinkwallManageActions.EditProps]), data={"props": asset}, content_type=self.content_type)
            self.assertEqual(res.status_code, 202)
            data = res.json()["data"]
            self.assertGreater(len(data["assets"]), 0)
            for key, value in asset.items():
                if key in data:
                    self.assertEqual(data[key], value)
                elif key in data["assets"]:
                    self.assertEqual(data["assets"][key], value)
                else:
                    self.fail()
    
    def test_set_media_handles(self) -> None:

        handles = [
            {
                "platform": Platform.Instagram,
                "url": "https://iconscout.com/unicons/explore/line/requirement",
                "username": "Meta kritic"
            },{
                "platform": "twitch",
                "url": "https://iconscout.com/unicons/explore/line/requirement/twitch"
            }
        ]

        for handle in handles:
            res = self.autheticated_client.post(reverse("manage-linkwall", args=[LinkwallManageActions.AddHandles]), data={"media_handles": [handle]}, content_type=self.content_type)
            self.assertEqual(res.status_code, 202)
            data = res.json()["data"]
            def validate_handle(data: Dict):
                rt = None
                for key, value in handle.items():
                    if rt is None:
                        rt = key in data and data[key] == value
                    else:
                        rt &= key in data and data[key] == value
                return rt

            self.assertTrue(handle["platform"] in data["media_handles"])
            handles = data["media_handles"][handle["platform"]]
            self.assertTrue(any(map(lambda _data: validate_handle(_data), handles)))
    
    def test_remove_media_handles(self) -> None:

        handles = [
            {
                "platform": Platform.Instagram,
                "url": "https://iconscout.com/unicons/explore/line/requirement",
                "username": "Meta kritic"
            },{
                "platform": "twitch",
                "url": "https://iconscout.com/unicons/explore/line/requirement/twitch"
            }
        ]

        for handle in handles:
            res = self.autheticated_client.post(reverse("manage-linkwall", args=[LinkwallManageActions.AddHandles]), data={"media_handles": [handle]}, content_type=self.content_type)
            
        remove_handles = ["https://iconscout.com/unicons/explore/line/requirement/twitch"]
        for handle in remove_handles:
            res = self.autheticated_client.post(reverse("manage-linkwall", args=[LinkwallManageActions.RemoveHandles]), data={"media_handles": [handle]}, content_type=self.content_type)
            self.assertEqual(res.status_code, 202)
            data = res.json()["data"]
            self.assertEqual(len(data["media_handles"]), 1)
    
    def test_edit_styles(self) -> None:

        auth_call = lambda styles, action = LinkwallManageActions.EditStyle: self.autheticated_client.post(reverse("manage-linkwall", args=[action]), data={"styles": styles}, content_type=self.content_type)

        styles = {
            LinkWallComponents.LinkButton: {
                "borderRadius": "2rem",
                "backgroundColor": "#FFFFFF",
                "fontFamily": "Poppins"
            },
            LinkWallComponents.Background: {
                "fontFamily": "Work-Sans",
                "color": "#000000"
            }
        }

        res = auth_call(styles)
        self.assertEqual(res.status_code, 202)
        data = res.json()["data"]
        self.assertEqual(data["assets"]["styles"], styles)

        edited_styles = {
            LinkWallComponents.Background: {
                "backgroundColor": "#FFFFFF"
            }
        }
        res = auth_call(edited_styles)
        self.assertEqual(res.status_code, 202)
        data = res.json()["data"]
        self.assertTrue("styles" in data["assets"])
        styles = data["assets"]["styles"]
        for component, prop in edited_styles.items():
            self.assertTrue(component in styles)
            for property_name, propert_value in prop.items():
                self.assertTrue(property_name in styles[component])
                self.assertEqual(styles[component][property_name], propert_value)
        
        remove_property = {
            LinkWallComponents.Background: ["backgroundColor"],
            LinkWallComponents.LinkButton: ["fontFamily"]
        }

        res = auth_call(remove_property, action=LinkwallManageActions.RemoveStyle)
        self.assertEqual(res.status_code, 202)
        data = res.json()["data"]
        self.assertTrue("styles" in data["assets"])
        styles = data["assets"]["styles"]
        for component, props in remove_property.items():
            self.assertTrue(component in styles)
            for prop in props:
                self.assertFalse(prop in styles[component])

        remove_components = {
            LinkWallComponents.Background: []
        }
        res = auth_call(remove_components, action=LinkwallManageActions.RemoveStyle)
        self.assertEqual(res.status_code, 202)
        data = res.json()["data"]
        self.assertTrue("styles" in data["assets"])
        styles = data["assets"]["styles"]
        for component, props in remove_components.items():
            self.assertFalse(component in styles)





        