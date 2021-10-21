from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin

# Create your models here.


class AccountManager(BaseUserManager):

    def create_user(self): ...
    def create_superuser(self):...


class Account(AbstractBaseUser, PermissionError): ...
