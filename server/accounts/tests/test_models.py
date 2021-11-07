from typing import List, Union
from django.test import TestCase
from accounts.models import Account, User
import json
from utils.types import EntityType
import os


class AccountFixtureTestCase:
    def __init__(self,output: Union[str, None], **kwargs) -> None:
        self.email = kwargs.get("email", None)
        self.password = kwargs.get("password", None)
        self.entity_type = kwargs.get("entity_type", None)
        self.first_name = kwargs.get("first_name",  None)
        self.last_name = kwargs.get("last_name", None)
        self.kwargs = kwargs
        self.output = str(output)
    

    @classmethod
    def load(cls, data) :
        return cls(data["output"], **data["input"])
    

class AccountTestCase(TestCase):

    def setUp(self) -> None:
        self.accounts: List[Account] = []
        self.create_test_fixtures: List[AccountFixtureTestCase] = None
        with open(os.path.dirname(__file__) + "/fixtures/account_fixtures.json", "r") as file:
            self.create_test_fixtures = [AccountFixtureTestCase.load(data) for data in json.load(file)]
        
        
    
    def test_create(self) -> None:
        for test_case in self.create_test_fixtures:
            try:
                account = Account.objects.create(**test_case.kwargs)
                self.assertEqual(test_case.output, type(account).__name__, account)
                
            except Exception as e:
                if isinstance(account, User):
                    account = Account.objects.create_account(account, entity_type=EntityType.Creator)
                    self.assertEqual(isinstance(account, Account), True, account)
                    self.accounts.append(account)
                else:
                    self.assertEqual("None", test_case.output, e)


    def test_check_user_exists_using_email(self):
        emails = ['', "jardenjais","testdrivendev@gmail.com"]
        for email in emails:
            exists = Account.objects.check_user_exists_using_email(email)
            self.assertEqual(exists, User.objects.filter(email=email).count() == 1)
    
    
    def tearDown(self) -> None:
       if len(self.accounts) > 0 :
           for account in self.accounts:
               account.delete()