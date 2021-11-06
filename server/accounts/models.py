from datetime import datetime
from typing import Union
from django.contrib.auth.models import User
from django.db import models
from django.db.models.manager import BaseManager
from server.utils import account_id_generator

from server.utils.types import (EntityType)

from utils.errors import AccountAlreadyExists, UserAlreadyExist, UserAlreadyExists

# Create your models here.


class AccountsModel(models.Model):
    class Meta:
        app_label = "server.accounts"
        abstract  = True



class AccountInterface:
    objects : BaseManager





class AccountManager(BaseManager):

    def create_account(self, user: User,**kwargs) -> AccountInterface:
        """Create Account model -> Account\n
        Keyword Arguments:\n
        user -- User model \n
        kwargs -- Dict must containing `entity_type`\n

        Create new account only if one doesn't exists\n
        throws exception on account existance.
        
        """
        email = user.email
        entity_type = kwargs["entity_type"]
        if not "entity_type" in kwargs:
            raise KeyError("entity_type key is required for Account creation")
        if self.check_account_exists(email, entity_type):
            raise AccountAlreadyExists(email, entity_type)
        account = self.model(
            id=self.generate_account_id(email, entity_type),
            user=user,
  
            **kwargs
        )
        account.save()
        return account

    
    def create_user(self, email, password, **kwargs) -> User:
        """Create default User model in database if email doesn't exists -> User"""
        if self.check_user_exists_using_email(email):
            raise UserAlreadyExists(email)
        user: User = User.objects.create(
            username=email,
            email=email,
            is_staff=False,
            is_superuser=False,
            is_active=True,
            **kwargs
        )
        user.set_password(password)
        user.save()
        return user

    
    def create(self, email, password, **kwargs) -> Union[User, AccountInterface]:
        user = self.create_user(email, password, **kwargs)
        if "entity_type" in kwargs:
            return self.create_account(user, **kwargs)
        return user

    
    @staticmethod
    def generate_account_id(email: str, time: datetime) -> str:
        """Wrapper for utils.account_id_generator [Returns string]\n
        
        Keyword arguments:
        email -- Email ID for the account\n
        time -- Time used as randomizer

        """
        return account_id_generator(email, time)
    
    def check_user_exists_using_email(self, email: str) -> bool:
        """Verifies the existance of email associated account in the database\n
        Returns: bool\n
        True -- Account exists\n
        False -- Account does not exists
        """
        if not (len(email) > 0 and "@" in email):
            return False
        return User.objects.filter(email=email).exists()
    
    def check_account_exists(self, email: str, entity: str) -> bool:
        if not (len(email) > 0 and "@" in email):
            return False
        return self.filter(user__email = email).exists()
    



class Account(AccountsModel, AccountInterface):
    """Account model representing all users in the system.
    All types of entities like Creator, Business will be connected with an Account.

    An Account can hold multiple types of entities at same time.

    Keyword arguments:\n
    user -- User associated with this account \n
    created_on -- Account created on (default=datetime.now())\n
    last_login_on -- Last time the holder loged into the platform (default=datetime.now())\n
    is_creator_account -- Is the account hold creator entity (default=False)\n
    is_advertiser_account -- Is the account hold advertiser entity (default=False)\n
    is_disabled_account -- Is the account disabled/banned from the platform (default=False)\n
    """
    id = models.CharField(max_length=64, primary_key=True, default='')
    user = models.ForeignKey(User, related_name="user_account_relation", on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now=True)
    entity_type = models.CharField(max_length=20, blank=False, null=False, default=EntityType.Unknown)
    is_disabled_account = models.BooleanField(default=False)

    objects: AccountManager = AccountManager()

    def disable_account(self) -> None:
        self.is_disabled_account = True
        self.save()
    
    def enable_account(self) -> None:
        self.is_disabled_account = False
        self.save()
    
    class Meta:
        app_label = "server.accounts"



