from typing import Dict, List, Union
from digger.base.request_manager import BaseRequestManager
from digger.base.request_struct import RequestStruct
from unittest import TestCase
from dataclasses import dataclass
from utils.types import RequestMethod

from digger.base.response_struct import ResponseStruct

@dataclass
class JSONResponse:
    userId: int
    id: int
    title: int
    body: int


class JSONPlacesholdResponse(ResponseStruct):

    def __init__(self, url: str, posts: List[JSONResponse] = [], **kwargs) -> None:
        self.posts = posts
        super().__init__(url, **kwargs)
    
    @staticmethod
    def process_data(kwargs: Union[Dict, List, str]) -> Dict[str, List[JSONResponse]]:
        data = []
        for post in kwargs:
            data.append(JSONResponse(**post))
        return {"posts": data}


class JSONPlaceholderRequest(RequestStruct):
    response_struct: JSONPlacesholdResponse = JSONPlacesholdResponse
    endpoint = "/posts"
    method: str = RequestMethod.Get


class JSONRequestManager(BaseRequestManager):

    def __init__(self) -> None:
        super().__init__("https://jsonplaceholder.typicode.com")

def test_digger_base() -> None:
    request_manager = JSONRequestManager()
    req = JSONPlaceholderRequest()
    response: JSONPlacesholdResponse = req(request_manager)
    assert response.status_code == req.status_code, "Status code is making the difference"
    assert len(response.posts) == 100
    assert isinstance(response.posts[0], JSONResponse)
    assert response.posts[0].id == 1





