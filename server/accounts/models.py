
################# Python Built-in imports ####################
from datetime import datetime, timedelta
from typing import Any, Dict, List, Union
import string
import random

################## Django Built-in imports ###################
from django.contrib.auth.models import User
from django.db import models
from django.db.models.query_utils import Q
from django.db.models import JSONField


################# Project Built-in imports ###################
from utils import account_id_generator, get_current_time, get_handle_metrics_expire_time, time_to_string, validate_password
from django.core.validators import validate_email
from utils.ad_data import AdRate
from utils.errors import AccountAlreadyExists, UserAlreadyExists
from utils.types import *

################# Third-party imports ########################
from django_cryptography.fields import encrypt






# Create your models here.


class AccountInterface:
    objects : models.Manager
    def save(self) -> None: ...
    def to_kwargs(self) -> Dict[str, Any]: ...





class AccountManager(models.Manager):

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
        if self.check_account_exists_using_email(email, entity_type):
            raise AccountAlreadyExists(email, entity_type)
        
        if "username" not in kwargs:
            kwargs["username"] = self.generate_random_username()            
        account: AccountInterface = self.model(
            id=self.generate_account_id(email, entity_type),
            user=user,
            **self.refract_kwargs_for_account_creation(kwargs)
        )
        account.save()
        return account
    
    def create_account_using_account(self, account: AccountInterface, entity_type: str) -> AccountInterface:
        """WRANINGS: Do not use this method, highly volatile"""
        if self.check_account_exists_using_email(account.user.email, entity_type):
            raise AccountAlreadyExists(account.user.email, entity_type)
        account_kwargs = account.to_kwargs()
        new_account = self.create_account(
            account.user,
            entity_type=entity_type,
            **account_kwargs
        )
        return new_account
    

    @staticmethod
    def generate_random_username() -> str:
        LENGTH_OF_USERNAME = 12
        return "".join(random.choices(string.ascii_letters + string.digits, k = LENGTH_OF_USERNAME))
        
    

    def refract_kwargs_for_account_creation(self, kwargs: Dict) -> Dict:
        """Remove keyword arguments like email, password, first_name, last_name from kwargs"""
        return {key: kwargs[key] for key in kwargs.keys() if key not in ["email", "password", "first_name", "last_name"]}
    
    def create_user(self, email, password, **kwargs) -> User:
        """Create default User model in database if email doesn't exists -> User"""
        if self.check_user_exists_using_email(email):
            return User.objects.filter(email=email).first()
        
        # Running some validators
        validate_email(email)
        validate_password(password)

        user: User = User.objects.create(
            username=email,
            email=email,
            is_staff=False,
            is_superuser=False,
            is_active=True,
            first_name=kwargs.get("first_name", ""),
            last_name=kwargs.get("last_name", "")
        )
        user.set_password(password)
        user.save()
        return user

    
    def create(self,**kwargs) -> Union[User, AccountInterface]:
        user = self.create_user(**kwargs)
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
    
    def check_account_exists_using_email(self, email: str, entity: str) -> bool:
        """Verifies that account with email-entity pair exists"""
        if not (len(email) > 0 and "@" in email):
            return False
        return self.filter(Q(user__email = email) & Q(entity_type = entity)).exists()
    
    def check_username_exists(self, username: str) -> bool:
        """Returns True if the username exists"""
        return self.filter(username=username).exists()
    

    



class Account(models.Model, AccountInterface):
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
    username -- unique username for each instance of account, different usernames must be selected\n
                for different entity types
    """
    id = models.CharField(max_length=64, primary_key=True, default='')
    user = models.ForeignKey(User, related_name="user_account_relation", on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=get_current_time)
    entity_type = models.CharField(max_length=20, blank=False, null=False, default="")
    is_disabled_account = models.BooleanField(default=False)
    contact = models.CharField(max_length=14, default="")
    username = models.CharField(max_length=25, unique=True, default="", db_index=True)
    description = models.TextField(default="")
    avatar = models.URLField(default="")
    banner_image = models.URLField(default="")

    objects: AccountManager = AccountManager()

    def disable_account(self) -> None:
        self.is_disabled_account = True
        self.save()
    
    def enable_account(self) -> None:
        self.is_disabled_account = False
        self.save()
    
    @staticmethod
    def is_valid_username_structure(username: str) -> bool:
        USERNAME_MIN_LENGTH = 5
        USERNAME_MAX_LENGTH = 25
        return USERNAME_MIN_LENGTH <= len(username) and len(username) <= USERNAME_MAX_LENGTH 

    
    def to_kwargs(self) -> Dict[str, Any]:
        return {
            "is_disabled_account": self.is_disabled_account,
            "contact": self.contact,
            "avatar": self.avatar,
            "banner_image": self.banner_image,
        }



class SocialMediaHandle(models.Model):
    """SocialMediaHandle represents all data about the specific media handle\n
    This class holds data about the handle which to display on the site\n
    Authorization details to run api requests\n

    Keyword Arguments:\n
    platform -- Social Media Platform to which this handle is related with\n
    account -- Account on this platform which owns the handle\n
    handle_url -- Complete url to the media handle, used to redirect users to profile directly\n
    handle_uid -- UID for the handle with which the platforms backend will identify the request\n
    handle_access_token -- Encrypted Access Token of the handle generated for data exchange\n
    token_expiration_time -- Validity Time bound of the Handle Acess Token\n
    last_date_time_of_token_use -- Last time the token was used to make nay request
    created_on -- The column created in the Table\n
    username -- Username of Display Name on the media handle\n
                for e.g Ajay Nagar has Channels with name Carryminati and CarryIsLive\n
                both of them are seperate media handles, with different usernames\n
    avatar -- Similar to Username\n
    is_publish_permission_valid -- Determines whether the media handle holds power to directly publish contents\n
    rates -- JSON containing rates of each applicable ad_type\n
             for e.g {"IG_STORY_AD": data}\n
             where data: AdRate =  {\n
                ad_name: string\n
                amount: int\n
                currency: string\n
                decimal_places: int\n
             }
    
    
    """
    platform = models.CharField(max_length=20, db_index=True, default="")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="social_handle_account")
    # complete url to the channel/handle
    handle_url = models.URLField()
    # unique-identifier-about the handle for e.g channel_id, username_of_insta_account, or special_id_provided_by_api_for_identification
    handle_uid = models.CharField(max_length=255, default="", db_index=True)
    access_token = encrypt(models.TextField(default=""))
    refresh_token = encrypt(models.TextField(default=""))
    is_refresh_token_dependent = models.BooleanField(default=False)
    token_expiration_time = models.DateTimeField(default=get_current_time)
    last_date_time_of_token_use  = models.DateTimeField(default=get_current_time)
    created_on = models.DateTimeField(default=get_current_time)
    username = models.CharField(max_length=70, default="")
    avatar = models.URLField(null=True, blank=True)
    is_publish_permission_valid = models.BooleanField(default=False)
    follower_count = models.PositiveBigIntegerField(default=0)
    media_count = models.PositiveIntegerField(default=0)
    meta_data = models.JSONField(default=dict)
    rates = models.JSONField(default=dict)  # {"ad_name": {...data}}


    def get_rate(self, key: str) -> AdRate:
        if key not in self.rates:
            raise KeyError("Platform %s doesn't have rates specified.".format(key))
        return AdRate.from_dict(self.rates[key])
    
    @property
    def all_rates(self) -> List[AdRate]:
        return [self.get_rate(platform_ad_code) for platform_ad_code in self.rates]
    
    def add_rate(self, ad_rate: AdRate) -> None:
        self.rates[ad_rate.ad_name] = ad_rate.serialize()
    
    def get_token_expiration_datetime(self, seconds: int, time: datetime = get_current_time()):
        self.token_expiration_time = get_current_time() + timedelta(seconds=seconds)
    
    def _set_access_token(self, value: str, token_expiration_time: int, refresh_token: str = None) -> None:
        self.access_token = value
        self.token_expiration_time = self.get_token_expiration_datetime(token_expiration_time)
        if refresh_token:
            self.refresh_token = refresh_token
            self.is_refresh_token_dependent = True
    
    def set_access_token(self, value: str, token_expiration_time: int, refresh_token: str = None) -> None:
        """
        Addes refresh token along with converting seconds to datetime

        Keyword Arguments:
        value -- Acccess token
        token_expiration_time -- Time in seconds for token to expire
        refresh_token -- If the token refresh requires an refresh token, Optional
        """
        self._set_access_token(value, token_expiration_time, refresh_token=refresh_token)
        self.save()
    

    def _set_last_date_time_of_token_use(self) -> None:
        self.last_date_time_of_token_use = get_current_time()
        # 5184000 = 60 days
        self.token_expiration_time = self.get_token_expiration_datetime(seconds=5184000, time=self.last_date_time_of_token_use)


    def set_last_date_time_of_token_use(self) -> None:
        """
        Used in case of fb graph api, as the graph api access_token is usable for 60 days after the last use
        """
        self._set_last_date_time_of_token_use()
        self.save()
    
    @property
    def is_access_token_valid(self) -> bool:
        """Returns true if token is still valid"""
        now = datetime.now()
        return now < self.token_expiration_time



