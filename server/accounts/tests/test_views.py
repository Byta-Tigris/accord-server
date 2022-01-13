from typing import Any, Dict, List, Optional, Union
from django.contrib.auth.models import User
from django.test.client import Client
from django.urls import reverse
from requests.models import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from dataclasses import dataclass

from accounts.models import Account
from utils.types import EntityType
from accounts.serializers import AccountSerializer


@dataclass
class CreateAccountFixture:
    email: Optional[str] = None
    password: Optional[str] = None
    entity_type: Optional[str] = None
    username: Optional[str] = None
    contact: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    banner_image: Optional[str] = None
    output_success: bool = False
    output_class: Union[None, User, Account] = None
    access_token: str = "some-token"

    def to_kwargs(self) -> Dict[str, Any]:
        data = {}
        not_allowed = ["output_success", "output_class"]
        for key in self.__dataclass_fields__.keys():
            if key not in not_allowed and getattr(self, key, None) != None:
                data[key] = getattr(self, key)
        return data


@dataclass
class LoginFixtures:
    output_status: int
    username: Optional[str] = None
    password: Optional[str] = None

    def to_kwargs(self) -> Dict[str, str]:
        data = {}
        if self.username is not None:
            data['username'] = self.username
        if self.password is not None:
            data["password"] = self.password
        return data
    


class TestAccountViews(APITestCase):

    def setUp(self) -> None:
        self.account, self.token_obj = Account.get_test_account()
        self.content_type = "application/json"
        self.autheticated_client = Client(HTTP_AUTHORIZATION=f"Token {self.token_obj.key}", HTTP_CONTENT_TYPE=self.content_type)
        self.client = Client(HTTP_CONTENT_TYPE=self.content_type)

    def test_username_valid_view(self) -> None:
        url = reverse('username-valid')
        fixtures = [
            {
                "username": "piu",
                "is_valid": False
            }, {
                "username": "piyushreg",
                "is_valid": True
            }
        ]
        for data in fixtures:
            response = self.client.post(url, data, content_type=self.content_type)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            res = response.json()
            self.assertTrue("is_valid" in res)
            self.assertEqual(res["is_valid"], data["is_valid"])

    def get_create_account_fixtures(self) -> List[CreateAccountFixture]:
        return [
            CreateAccountFixture(
                output_success=False,
                output_class=None
            ),
            CreateAccountFixture(
                email="test123",
                password="kdjf",
                output_success=False,
                output_class=None
            ),
            CreateAccountFixture(
                email="bytatigrisdev@gmail.com",
                password="test",
                output_success=False,
                output_class=None,
            ), CreateAccountFixture(
                email="bytatigrisdev@gmail.com",
                password="testing123",
                username="testname",
                output_success=True,
                output_class=User
            ), CreateAccountFixture(
                email="bytatigrisdev@gmail.com",
                password="testing123",
                username="testname",
                entity_type=EntityType.Creator,
                output_success=True,
                output_class=Account
            ),
            CreateAccountFixture(
                email="bytatigrisdev@gmail.com",
                password="testing123",
                username="testname",
                entity_type=EntityType.Creator,
                output_success=False,
                output_class=None
            ),
            CreateAccountFixture(
                email="testemail124@gmail.com",
                password="testing123",
                username="testname",
                entity_type=EntityType.Advertiser,
                output_success=False,
                output_class=None
            ),
            CreateAccountFixture(
                email="bytatigrisdev@gmail.com",
                password="testing123",
                username="testnamead",
                entity_type=EntityType.Advertiser,
                output_success=True,
                output_class=Account
            ),

        ]

    def test_create_account(self) -> None:
        fixtures = self.get_create_account_fixtures()
        url = reverse('create-account')
        for fixture in fixtures:
            res = self.client.post(url, fixture.to_kwargs(), content_type=self.content_type)
            if fixture.output_success:
                print(fixture.to_kwargs(), res.json())
                self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            else:
                self.assertNotEqual(res.status_code, status.HTTP_201_CREATED)
            body = res.json()
            # print(body)
            if fixture.output_class == None:
                self.assertTrue("error" in body)
            elif isinstance(fixture.output_class, Account):
                self.assertTrue("token" in body)
                self.assertTrue("username" in body)
                self.assertTrue("entity_type" in body)
                self.assertEqual(body["username"], fixture.username)
                self.assertEqual(body["entity_type"], fixture.entity_type)
            else:
                self.assertTrue("token" in body)



    def test_login(self) -> None:
        previous_token: Union[str, None] = None
        account_tokens: List[str] = []
        accounts = [
            CreateAccountFixture(
                email="bytatigrisdev@gmail.com",
                password="testing123",
                username="testname",
                entity_type=EntityType.Creator,
                output_success=False,
                output_class=None
            ),
            CreateAccountFixture(
                email="bytatigrisdeva@gmail.com",
                password="testing1234",
                username="testnamead",
                entity_type=EntityType.Advertiser,
                output_success=True,
                output_class=Account
            )
        ]

        create_account_url = reverse('create-account')
        for account in accounts:
            res = self.client.post(create_account_url, account.to_kwargs(), content_type=self.content_type)
            body = res.json()
            if res.status_code == 201:
                account_tokens.append(body["token"])


        fixtures = [
            LoginFixtures(
                output_status=status.HTTP_400_BAD_REQUEST,
            ),
            LoginFixtures(
                output_status=status.HTTP_400_BAD_REQUEST,
                username=accounts[0].username,
            ),
            LoginFixtures(
                output_status=status.HTTP_404_NOT_FOUND,
                username="abcdefgrt",
                password="pigg12345"
            ),
            LoginFixtures(
                output_status=status.HTTP_401_UNAUTHORIZED,
                username=accounts[0].username,
                password=accounts[1].password
            ),
            LoginFixtures(
                output_status=status.HTTP_202_ACCEPTED,
                username=accounts[0].username,
                password=accounts[0].password
            ),
            LoginFixtures(
                output_status=status.HTTP_202_ACCEPTED,
                username=accounts[1].username,
                password=accounts[1].password
            )
        ]
        url = reverse("login-account")
        for fixture in fixtures:
            res = self.client.post(url, fixture.to_kwargs(), content_type=self.content_type)
            self.assertEqual(res.status_code, fixture.output_status)
            if fixture.output_status == status.HTTP_202_ACCEPTED:
                body = res.json()
                self.assertTrue(body["token"] in account_tokens)
                if previous_token:
                    self.assertNotEqual(previous_token, body["token"])
                previous_token = body["token"]



    def test_edit_account(self) -> None:

        url = reverse('retrieve-edit-account')

        # edit description
        old_description = self.account.description
        description = "novo chlorae"
        res = self.autheticated_client.post(url, data={"description": {"data": description}}, content_type=self.content_type)
        print(res, res.content)
        self.assertEqual(res.status_code, 202)
        body = res.json()
        self.assertTrue("data" in body and len(body["data"]) > 0)
        self.assertNotEqual(old_description, body["data"]["description"])
        self.assertEqual(description, body["data"]["description"])


        

        # edit first_name
        full_name = self.account.user.get_full_name()
        old_first_name = self.account.user.first_name
        first_name = "Nokai"
        res = self.autheticated_client.post(url, data={"first_name": {"data": first_name}}, content_type=self.content_type)
        self.assertEqual(res.status_code, 202)
        body = res.json()
        self.assertTrue("data" in body and len(body["data"]) > 0)
        self.assertNotEqual(old_first_name, body["data"]["first_name"])
        self.assertEqual(first_name, body["data"]["first_name"])
        self.assertNotEqual(full_name, body["data"]["full_name"])

        #edit password
        old_password = "helloword103"
        res = self.autheticated_client.post(url, data={"password": {"old_password": old_password, "password": "helloworld904"}}, content_type=self.content_type)
        self.assertEqual(res.status_code, 202)


        #editing multiple fields
        last_name = "Loda"
        avatar = "https://testurl.com/"
        res = self.autheticated_client.post(url, data={"last_name": {"data": last_name}, "avatar":{"data": avatar}, "username": {"data": "testrone"}}, content_type=self.content_type)
        self.assertEqual(res.status_code, 202)
        body = res.json()
        self.assertTrue("data" in body and len(body["data"]) > 0)
        self.assertEqual(last_name, body["data"]["last_name"])
        self.assertEqual(avatar, body["data"]["avatar"])
        self.assertEqual(body["data"]["username"], self.account.username)

        # reset all data
        rest_data = {
            "description": {"data": self.account.description},
            "first_name": {"data": self.account.user.first_name},
            "last_name": {"data": self.account.user.last_name},
            "avatar": {"data": self.account.avatar}
        }
        res = self.autheticated_client.post(url, data=rest_data, content_type=self.content_type)
        self.assertEqual(res.status_code, 202)





    def test_retrieve_account(self) -> None:
        account_dict = AccountSerializer(self.account).data

        # Using me request
        res = self.autheticated_client.get(reverse('retrieve-edit-account'))
        self.assertEqual(res.status_code, 200)
        body: Dict[str, Dict[str, Union[str, bool]]] = res.json()
        self.assertTrue("data" in body)
        for key, value in body["data"].items():
            if key in account_dict:
                self.assertEqual(account_dict[key], value)
        self.assertTrue(body["data"]["is_account_owner"])
    

    def test_reset_password_view(self) -> None:
        url = reverse('reset-password')
        fixtures = [
            {
                "data": {
                    "username": self.account.username,
                    "access_token": "some-random-state"
                },
                "success": False
            },
            {
                "data": {
                    "username": self.account.username,
                    "password": "somepassword"
                },
                "success": False
            },{
                "data": {
                    "username": self.account.username,
                    "password": "small",
                    "access_token": "some-random-state"
                },
                "success": False
            },
            {
                "data": {
                    "username": self.account.username,
                    "password": "bytapass",
                    "access_token": "some-random-state"
                },
                "success": True
            }
        ]
        for fixture in fixtures:
            res = self.client.post(url, data=fixture["data"], content_type=self.content_type)
            self.assertEqual(res.status_code == 202, fixture["success"])
            if fixture["success"]:
                data = res.json()["data"]
                self.assertTrue("token" in data)
                self.assertTrue(self.account.user.check_password(fixture["data"]["password"]))
