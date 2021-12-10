from typing import Any, List, TypedDict
from unittest import TestCase

import requests
from digger.base.request_manager import RequestManager
from digger.base.request_struct import BaseRequestStruct
from digger.base.response_consumer import BaseResponseStruct
from digger.base.types import FieldMissingException, FieldTypeMismatchException, RequestMethod, Response

JSON_PLACE_HOLDER_BASE_URL = "https://jsonplaceholder.typicode.com"

class JsonPosts(TypedDict):
    userId: int
    id: int
    title: str
    body: str

class JsonPlaceholderAllPostsResponseStruct(BaseResponseStruct):

    def __init__(self, res: requests.Response) -> None:
        self.status_code = res.status_code
        self.data: List[JsonPosts] = res.json()
        super().__init__(self.status_code)
    

class JsonPlaceholderAllPostsRequestStruct(BaseRequestStruct):

    response_structs = JsonPlaceholderAllPostsResponseStruct

    def __init__(self) -> None:
        super().__init__("/posts",RequestMethod.Get)
        




class TestBaseRequestStruct(TestCase):

    def setUp(self) -> None:
        self.request_manager = RequestManager("https://jsonplaceholder.typicode.com")
    
    def test_base_request_using_posts(self):
        posts = JsonPlaceholderAllPostsRequestStruct()
        response: JsonPlaceholderAllPostsResponseStruct = posts.call_request(self.request_manager)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data) , 0)
        self.assertEqual(response.data[0]['id'], 1)
    
    def test_error_hinting_in_request(self):

        class MockResponseStruct(BaseResponseStruct):

            def __init__(self) -> None:
                self.status_code = 200
                self.krum = "head"
                super().__init__(self.status_code, required_fields=[["krum", int], "dalf"])
        response = None
        try:
            response = MockResponseStruct()
        except Exception as e:
            if isinstance(e, FieldTypeMismatchException):
                self.assertEqual(e.field, "krum")
            else:
                self.assertIsInstance(e, FieldMissingException)
        self.assertEqual(response, None)
        
        
