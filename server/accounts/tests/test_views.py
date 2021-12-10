from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import json


class TestAccountViews(APITestCase):

    def test_username_valid_view(self) -> None:
        url = reverse('username-valid')
        fixtures = [
            {
                "username": "piu",
                "is_valid": False
            },{
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


    def test_create_account(self) -> None:
        pass

    def test_login(self) -> None:
        pass

    def test_edit_account(self) -> None:
        pass

    def test_retrieve_creator_account(self) -> None:
        pass



