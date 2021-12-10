import json
from typing import Dict, Union
import requests
from digger.base.types import AbstractRequestManager, AbstractResponseStructure, RequestMethod, Response, AbstractRequestStructure


class RequestManager(AbstractRequestManager):
    """
    base_url -- must be a single string url or dict with key, value pair with a default key for fallback
    """
    
    def __init__(self, base_url: Union[str, Dict[str, str]], headers: Dict = None) -> None:
        self.base_url = base_url
        self.headers = headers
    
    def process_params(self, params: Dict) -> Dict:
        return params
    
    def process_data(self, data: Dict) -> Dict:
        return data
    
    def get_url(self, req: AbstractRequestStructure) -> str:
        if isinstance(self.base_url, str):
            return self.base_url + req.endpoint
        elif isinstance(self.base_url, dict):
            return self.base_url[req.base_url_key] + req.endpoint
    
    def make_get_request(self, req: AbstractRequestStructure) -> AbstractResponseStructure:
        query = req.get_query_params()
        resp = requests.get(self.get_url(query), params=query, headers=self.headers)
        return req.process_response(resp)

    def make_post_request(self, req: AbstractRequestStructure) -> AbstractResponseStructure:
        data = req.get_data_params()
        query = req.get_query_params()
        resp = requests.post(self.get_url(query), query=query, data=data, headers=self.headers)
        return req.process_response(resp)
    
    def make_request(self, request: AbstractRequestStructure) -> AbstractResponseStructure:
        if request.method == RequestMethod.Get:
            return self.make_get_request(request)
        elif request.method == RequestMethod.Post:
            return self.make_post_request(request)
        else:
            raise ValueError("incompatible method in the request %s".format(request.__class__.__name__))