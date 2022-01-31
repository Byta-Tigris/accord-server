import datetime
from typing import Any, Dict, List, Union

from django.db.models.query import QuerySet





class AbstractResponseStruct:
    url: str = None
    
    @classmethod
    def from_data(cls, url,kwargs) -> 'AbstractResponseStruct': ...

    def to_kwargs(self) -> Dict[str, Any]: ...

class AbstractRequestStruct:
    response_struct: AbstractResponseStruct = None
    url_key: str = "default"
    endpoint: str = "/"
    ignorable_fields: List[str] = []
    _ignored_fields: List[str] = ["response_struct", "url_key", "endpoint", 
                                    "ignorable_fields", "_gnorable_fields",
                                    "status_code", "headers", "method", "params_query", "params_data"]
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


class PlatformMetricModel:
    
    totals_record: Dict[str, Dict[str, Dict[str, Union[int, float]]]]

class CreatorMetricModel: 
    """
    Manages Creators overall metric data for a week
    """
    ...

LongLiveTokenResponse = type(AbstractResponseStruct)
