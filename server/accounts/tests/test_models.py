from typing import List, Union
from django.test import TestCase
from accounts.models import Account, User
import json
from utils.errors import AccountAlreadyExists
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
    
    @staticmethod
    def create_test_account() -> Account:
        return Account.objects.create(
            "devtandem@gmail.com",
            "testcors123",
            entity_type=EntityType.Creator,
            contact="917714171428"
        )
    

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
    

    def test_enable_disable_accounts(self) -> None:
        if len(self.accounts) == 0:
            account = AccountFixtureTestCase.create_test_account()
        else:
            account = self.accounts[0]
        self.assertEqual(account.is_disabled_account, False)
        account.disable_account()
        self.assertEqual(account.is_disabled_account, True)
        account.enable_account()
        self.assertEqual(account.is_disabled_account,False)
    
    def test_create_account_using_account(self) -> None:
        if len(self.accounts) == 0:
            account = AccountFixtureTestCase.create_test_account()
        else:
            account = self.accounts[0]
        if len(account.contact) == 0:
            account.contact = "917714171428"
            account.save()
        try:
            new_account = Account.objects.create_account_using_account(account, EntityType.Creator)
        except Exception as e:
            self.assertIsInstance(e, AccountAlreadyExists)
        new_account: Account = Account.objects.create_account_using_account(account, EntityType.Advertiser)
        self.assertNotEqual(new_account.entity_type, account.entity_type)
        self.assertEqual(new_account.contact, account.contact)
        self.assertEqual(new_account.user.email,account.user.email)
        self.assertDictEqual(new_account.to_kwargs(), account.to_kwargs())


    
    def tearDown(self) -> None:
       if len(self.accounts) > 0 :
           for account in self.accounts:
               account.delete()