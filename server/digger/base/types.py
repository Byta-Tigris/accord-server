from typing import Any, Dict, List, Union, TypeVar
from typing_extensions import Self
from accounts.models import Account, CreatorMetricModel, PlatformMetricModel, SocialMediaHandle, SocialMediaHandleMetrics





class AbstractResponseStruct:
    url: str = None
    
    @classmethod
    def from_data(cls, url,kwargs) -> Self: ...

    def to_kwargs(self) -> Dict[str, Any]: ...

class AbstractRequestStruct:
    response_struct: AbstractResponseStruct = None
    url_key: str = "default"
    endpoint: str = "/"
    ignorable_fields: List[str] = []
    _ignored_fields: List[str] = ["response_struct", "url_key", "endpoint", 
                                    "ignorable_fields", "_gnorable_fields",
                                    "status_code", "header", "method", "params_query", "params_data"]
    headers: Dict = None
    method: str = None
    status_code = 200

    def get_headers(self) -> Union[None,Dict[str, str]]:
        return self.headers

    def get_ignorable_fields(self) -> List[str]:
        return self.ignorable_fields + self._ignored_fields

    def _get_params(self) -> Dict[str, Any]: ...
    def format_params(self, **params) -> Dict[str, Any]: ... 
    def get_params(self) -> Dict[str, Any]: ...

class AbstractRequestManager:
    def make_request(self, request: AbstractRequestStruct) -> AbstractResponseStruct: ...


class AbstractDigger:
    pass


LongLiveTokenResponse = TypeVar('LongLiveTokenResponse', AbstractRequestStruct)

class Digger(AbstractDigger):

    """
    Wrapper object responsible for all the request-response-model operations involved in the api fetching\n
    Each Platform will have their own digger class.
    """

    def exchange_code_for_token(self, account: Account , code: str, redirect_uri: str) -> None:
        """
        After the successfull authorization flow, client-side will retrieve the code\n
        The code coupled with the redirect_uri will call Request to retrieve short-lived token\n
        """
        pass


    def get_long_lived_token(self, account: Account, short_lived_token: str) -> LongLiveTokenResponse:
        """
        Exchanges the short-lived token with the long-lived token\n
        Returns Long Live Token Response
        """
        pass
    
    
    def get_refresh_token(self, social_media_handle: SocialMediaHandle) -> LongLiveTokenResponse:
        """
        Refreshes token and returns LongLiveTokenResponse
        """
        pass

    def create_or_update_social_media_handles(self, account: Account, access_token: str, expires_in: int = 3599, refresh_token: str = None) -> List[SocialMediaHandle]:
        """
        Fetches all handles related with the access_token\n
        Update the existing handles with the new access_token\n
        Creates new if the handle does not exists\n

        Returns List of SocialMediaHandles\n

        [Keyword Arguments]: \n
        account -- Account of the access_token owner\n
        access_token -- The new access_token\n
        expires_in -- Validity of the token in seconds [default=3600]\n
        refresh_token -- Refresh token if provided, then handle's refresh_token field will store the value, [Optional]\n
        """
        pass

    def resync_social_media_handles(self, account: Account) -> List[SocialMediaHandle]:
        """
        Resync all the social media handles if such functionality is supported\n
        """
        pass

    def update_handle_insights(self, social_media_handle: SocialMediaHandle) -> SocialMediaHandleMetrics:
        """
        Fetches all handle related insights, and update the handle metrics.\n
        If the handle metrics has crossed the 7 days time, new handle metric will be contrsucted\n

        Works for single social_media_handle\n
        """
        pass
    
    def update_all_handles_insights(self, account: Account) -> List[SocialMediaHandleMetrics]:
        """
        Update handle insight in bulk or from single function
        """
        pass

    def calculate_platform_metric(self, account: Account) -> PlatformMetricModel:
        """
        Calculates all the metrics from the social handle and updates the platfrom metric similarly
        """
        pass
    
    def update_creator_insights(self, account: Account, digger: List[AbstractDigger]) -> CreatorMetricModel:
        """
        Calculates creators overall insight and Update Creator insight metric\n
        Every digger will implement 
        """
        pass