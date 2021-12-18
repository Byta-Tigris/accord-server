from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from accounts.models import Account, SocialMediaHandle
from utils import get_modified_time
from utils.types import Platform
from .request_manager import InstagramRequestManager
from .request_struct import *



class InstagramDigger:

    def __init__(self) -> None:
        self.req_manager = InstagramRequestManager()
    
    def get_long_live_token(self, short_live_access_token: str) -> FacebookLongLiveTokenResponse:
        request = FacebookLongLiveTokenRequest(short_live_access_token)
        response_token_exchange: FacebookLongLiveTokenResponse = request(self.req_manager)
        return response_token_exchange
    

    def _create_or_update_token_in_handles(self, account: Account, access_token: str, expires_in: int, handle_queryset: QuerySet[SocialMediaHandle] = None) -> Union[None, List[SocialMediaHandle]]:
        request_page_accounts = FaceboolPageAccountsRequest(access_token)
        response_pages_accounts: FacebookPagesAccountsResponse = request_page_accounts(self.req_manager)
        if response_pages_accounts.has_error():
            return None
        pages = response_pages_accounts.pages
        while len(response_pages_accounts.pages) > 0 and response_pages_accounts.paging.after != None:
            response_pages_accounts = request_page_accounts(self.req_manager, after=response_pages_accounts.paging.after)
            pages += response_pages_accounts.pages
        users: List[IGUser] = []
        for page in pages:
            if page.instagram_business_account != None and page.instagram_business_account.id != None:
                users.append(page.instagram_business_account)
        
        existing_handles_queryset: QuerySet[SocialMediaHandle] = handle_queryset or SocialMediaHandle.objects.filter(
            Q(account=account) & Q(platform=Platform.Instagram))

        existing_handles: List[str] = existing_handles_queryset.values_list("handle_uid", flat=True)

        new_accounts: List[IGUser] = list(filter(lambda acc: acc.id not in existing_handles, users))

        existing_handles_models: List[SocialMediaHandle] = []
        for handle in existing_handles_queryset:
            handle._set_access_token(access_token, token_expiration_time=expires_in)
            handle._set_last_date_time_of_token_use()

        SocialMediaHandle.objects.bulk_update(existing_handles_models, ["access_token", "token_expiration_time"])

        models: List[SocialMediaHandle] = [SocialMediaHandle(
            platform = Platform.Instagram,
            account=account,
            handle_uid=user.id,
            handle_url=f"https://instagram.com/{user.username}",
            access_token=access_token,
            token_expiration_time=get_modified_time(seconds=expires_in),
            username=user.username,
            avatar=user.profile_picture_url
        ) for user in new_accounts]
        SocialMediaHandle.objects.bulk_create(models)
        return models + existing_handles_models

    
    def create_or_update_social_handles_from_sl_token(self, account: Account, short_live_access_token: str) -> Union[None, List[SocialMediaHandle]]:
        """
        Retrieves the long-lived token by exchanging the short-lived token.\n
        Retrieve all the instagram_business_accounts related with the new token.\n
        Update the existing social_handles with the new access_token and\n
        Create new social handles if any of them doesn't exists.\n\
        
        [Return]\n
        Returns None if token exchange fails or account retrieval fails\n
        Returns List[SocialMediaHandle] attached to the new access token\n

        [Keyword Arguments]\n
        account -- Account related with the handles
        short_live_access_token -- Short-Lived Access token

        """
        response_token_exchange: FacebookLongLiveTokenResponse = self.get_long_live_token(short_live_access_token)
        if response_token_exchange.has_error():
            return None
        return self._create_or_update_token_in_handles(account, response_token_exchange.access_token, response_token_exchange.expires_in)

    
    def resync_social_handles(self, account: Account) -> Union[None, SocialMediaHandle]:
        """
        If any IG user added any new IG Business ID to the Facebook ecosystem,\n
        and wants to add it into our Database\n
        Resync will fetch new accounts and add the new handles without re-login
        """
        handles_queryset: QuerySet[SocialMediaHandle] = SocialMediaHandle.objects.filter(Q(account=account) & Q(platform=Platform.Instagram))
        if not handles_queryset.exists():
            return None
        handle = handles_queryset.first()
        access_token = handle.access_token
        expires_in = 5184000
        return self._create_or_update_token_in_handles(account, access_token, expires_in, handle_queryset=handles_queryset)
        
        
        
        

