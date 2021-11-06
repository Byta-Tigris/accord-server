from django.test import TestCase
from server.accounts.models import Account, User


class AccountTestCase(TestCase):

    # def setUp(self) -> None:
    #     self.account_normal = Account.objects.create()

    def test_check_user_exists_using_email(self):
        emails = ['', "jardenjais","testdrivendev@gmail.com"]
        for email in emails:
            exists = Account.objects.check_user_exists_using_email(email)
            self.assertEqual(exists, User.objects.filter(email=email).count() == 1)
