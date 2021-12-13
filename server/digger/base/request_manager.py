from typing import Dict, Tuple, Union
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
    
    def get(self, request: AbstractRequestStruct) -> Tuple[requests.Response, str]:
        url: str = self.get_url(request)
        _headers: Dict = None
        if request.headers:
            _headers = request.headers
        if self.headers:
            _headers |= self.headers
        return requests.get(url=url, params=request.get_params(), headers=_headers), url
    
    def post(self, request: AbstractRequestStruct) -> Tuple[requests.Response, str]:
        url: str = self.get_url(request)
        _headers: Dict = None
        if request.headers:
            _headers = request.headers
        if self.headers:
            _headers |= self.headers
        return requests.post(url=url, data=request.get_params(), headers=_headers), url
    
    def make_request(self, request: AbstractRequestStruct) -> AbstractResponseStruct:
        res: requests.Response = None
        url: str = None
        try:
            if request.method == RequestMethod.Get:
                res, url = self.get(request)
            else:
                res, url = self.post(request)
            data = res.json()
            return request.response_struct.from_data(url, res.status_code, data)            
        except Exception as exc:
            raise exc
            # logger.error(exc)







