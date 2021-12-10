from enum import Enum
from typing import Any, Dict, Literal, NewType, Type, Union
import requests

RequestEndpoint = NewType("RequestEndpoint", (str,))
Response = NewType( "Response",requests.Response)


class FieldMissingException(Exception):
    
    def __init__(self, cls, field: str) -> None:
        super().__init__("Field %s is not present in %s instance.".format(field, cls.__class__.__name__))

class FieldTypeMismatchException(Exception):

    def __init__(self, cls, field: str, types) -> None:
        self.field = field
        super().__init__("Field %s from %s must be of types %s".format(field, cls.__class__.__name__, types))


class RequestMethod(Enum):
    Get = "GET"
    Post = "POST"

class AbstractResponseStructure:
    pass

class AbstractRequestStructure:

    method: str = Literal[RequestMethod.Get, RequestMethod.Post]
    base_url_key: Union[str, None] = None
    
    def get_query_params(self) -> Dict[str, Any]: ...
    def get_data_params(self) -> Dict[str, Any]: ...

    def process_response(self, response: requests.Response) -> AbstractResponseStructure: ...



class AbstractRequestManager:
    
    def make_request(self, request: AbstractRequestStructure) -> AbstractResponseStructure: ...


class BaseErrorException(Exception):
    pass

class BaseErrorCode:
    
    def raise_error(self): pass
        

class BasePlatformStatusCodes(Enum):
    pass