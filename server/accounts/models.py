from datetime import datetime
from typing import Any, Dict, List, Tuple, Union
from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields.related import ForeignKey
from django.db.models.query_utils import Q
from utils import account_id_generator, validate_password
from django.core.validators import validate_email
from utils.ad_data import AdRate


from utils.errors import AccountAlreadyExists, UserAlreadyExists

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
        
        account: AccountInterface = self.model(
            id=self.generate_account_id(email, entity_type),
            user=user,
            **self.refract_kwargs_for_account_creation(kwargs)
        )
        account.save()
        return account
    
    def create_account_using_account(self, account: AccountInterface, entity_type: str) -> AccountInterface:
        if self.check_account_exists_using_email(account.user.email, entity_type):
            raise AccountAlreadyExists(account.user.email, entity_type)
        account_kwargs = account.to_kwargs()
        new_account = self.create_account(
            account.user,
            entity_type=entity_type,
            **account_kwargs
        )
        return new_account
        
        
    

    def refract_kwargs_for_account_creation(self, kwargs: Dict) -> Dict:
        """Remove keyword arguments like email, password, first_name, last_name from kwargs"""
        return {key: kwargs[key] for key in kwargs.keys() if key not in ["email", "password", "first_name", "last_name"]}
    
    def create_user(self, email, password, **kwargs) -> User:
        """Create default User model in database if email doesn't exists -> User"""
        if self.check_user_exists_using_email(email):
            raise UserAlreadyExists(email)
        
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
    
    def check_account_exists_using_email(self, email: str, entity: str) -> bool:
        """Verifies that account with email-entity pair exists"""
        if not (len(email) > 0 and "@" in email):
            return False
        return self.filter(Q(user__email = email) & Q(entity_type = entity)).exists()


    



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
    """
    id = models.CharField(max_length=64, primary_key=True, default='')
    user = models.ForeignKey(User, related_name="user_account_relation", on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now=True)
    entity_type = models.CharField(max_length=20, blank=False, null=False, default="")
    is_disabled_account = models.BooleanField(default=False)
    contact = models.CharField(max_length=14, default="")
    username = models.CharField(max_length=70, unique=True, default="", db_index=True)
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
    
    def to_kwargs(self) -> Dict[str, Any]:
        return {
            "is_disabled_account": self.is_disabled_account,
            "contact": self.contact,
            "avatar": self.avatar,
            "banner_image": self.banner_image,
        }



class SocialMediaHandle(models.Model):
    platform = models.CharField(max_length=20, db_index=True, default="")
    account = ForeignKey(Account, on_delete=models.CASCADE, related_name="social_handle_account")
    access_token = models.TextField()
    token_expiration_time = models.DateTimeField(auto_now=False, default=datetime.now())
    created_on = models.DateTimeField(auto_now=True)
    username = models.CharField(max_length=70, default="")
    avatar = models.URLField()
    fan_count = models.IntegerField(default=0)
    is_publish_permission_valid = models.BooleanField(default=False)
    rates = models.JSONField()  # {"platform_ad_code": {...data}}

    def get_rate(self, key: str) -> AdRate:
        if key not in self.rates:
            raise KeyError("Platform %s doesn't have rates specified.".format(key))
        return AdRate.from_dict(self.rates[key])
    
    @property
    def all_rates(self) -> List[AdRate]:
        return [self.get_rate(platform_ad_code) for platform_ad_code in self.rates]
    
    def add_rate(self, ad_rate: AdRate) -> None:
        self.rates[ad_rate.ad_name] = ad_rate.serialize()
    
    




    
    



