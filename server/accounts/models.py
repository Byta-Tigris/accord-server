from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin

# Create your models here.


class AccountManager(BaseUserManager):

    def create_user(self, email, password):
        account = self.model()
    def create_superuser(self):...


class Account(AbstractBaseUser, PermissionError):
    id = models.CharField(max_length=64, primary_key=True, default='')
    email = models.EmailField(db_index=True, unique=True, default='')
    created_on = models.DateTimeField(auto_now=True)
    last_login_on = models.DateTimeField(auto_now=True)
    is_creator_account = models.BooleanField(default=False)
    is_advertiser_account = models.BooleanField(default=False)



