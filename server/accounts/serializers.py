from typing import Dict
from django.contrib.auth.models import User

from accounts.models import Account


class AccountSerializer:

    def __init__(self, account: Account) -> None:
        self.account = account
        self.user: User = account.user
    
    @staticmethod
    def serializer(account: Account, user: User) -> Dict[str, str]:
        _ser = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.get_full_name(),
            "email_id": user.email,
            "username": account.username,
            "contact": account.contact,
            "description": account.description,
            "avatar": account.avatar,
            "banner_image": account.banner_image,
            "entity_type": account.entity_type,
            "is_dsiabled_account": account.is_disabled_account
        }
        return _ser
    
    @property
    def data(self) -> Dict[str, str]:
        return self.serializer(self.account, self.user)