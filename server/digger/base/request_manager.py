from typing import Dict, Union
from utils import is_in_debug_mode
from utils.types import RequestMethod
from .types import AbstractRequestManager, AbstractRequestStruct, AbstractResponseStruct
from log_engine.log import logger
import requests



class BaseRequestManager(AbstractRequestManager):

    def __init__(self, base_url: Union[str, Dict[str, str]]) -> None:
        self.base_url_record = {}
        self.headers = None
        if isinstance(base_url, str):
            self.base_url_record["default"] = base_url
        elif isinstance(base_url, dict):
            self.base_url_record = base_url

    def get_url(self, request: AbstractRequestStruct) -> str:
        return self.base_url_record[request.url_key] + request.endpoint
    
    def make_request(self, request: AbstractRequestStruct, **extra_params) -> AbstractResponseStruct:
        res: requests.Response = None
        url: str = None
        _headers: Dict = None
        if request.get_headers():
            _headers = request.get_headers()
        if self.headers:
            _headers |= self.headers
        try:
            url = self.get_url(request)
            params, data = request.get_params()
            caller = requests.get
            if request.method == RequestMethod.Post:
                caller = requests.post
            params |= extra_params
            res = caller(url=url, params=params, data=data, headers=_headers)
            data = res.json()
            return request.response_struct.from_data(res.url, res.status_code, data)            
        except Exception as exc:
            if is_in_debug_mode():
                raise exc
            else:
                logger.error(exc)







