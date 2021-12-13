from typing import Any, Dict, List, Optional, Union
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import json
from dataclasses import dataclass

from accounts.models import Account
from utils.types import EntityType


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
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            res = json.loads(response.content)
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
            res = self.client.post(url, fixture.to_kwargs())
            print(fixture.to_kwargs(), res)
            if fixture.output_success:
                self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            else:
                self.assertNotEqual(res.status_code, status.HTTP_201_CREATED)
            body = json.loads(res.content)
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
            res = self.client.post(create_account_url, account.to_kwargs())
            body = json.loads(res.content)
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
        print(account_tokens)
        for fixture in fixtures:
            res = self.client.post(url, fixture.to_kwargs())
            print(fixture.to_kwargs(), res)
            self.assertEqual(res.status_code, fixture.output_status)
            if fixture.output_status == status.HTTP_202_ACCEPTED:
                body = json.loads(res.content)
                self.assertTrue(body["token"] in account_tokens)
                if previous_token:
                    self.assertNotEqual(previous_token, body["token"])
                previous_token = body["token"]



    def test_edit_account(self) -> None:
        pass

    def test_retrieve_creator_account(self) -> None:
        pass
