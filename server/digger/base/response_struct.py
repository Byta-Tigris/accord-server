

from typing import Any, Dict, List, Union
from digger.base.types import AbstractRequestStruct, AbstractResponseStruct



class ResponseStruct(AbstractResponseStruct):

    def __init__(self, url: str, status_code: int, **kwargs) -> None:
        self.url = url
        self.status_code = status_code
        self.error = None
    
    def has_error(self) -> bool:
        return self.error != None


    @staticmethod
    def process_data( kwargs: Union[Dict, List, str]) -> Dict:
        return kwargs 

    @classmethod
    def from_data(cls, url: str, status_code: int, args):
        kwargs = cls.process_data(args)
        return cls(url, status_code=status_code, **kwargs)
    
    def to_kwargs(self) -> Dict[str, Any]:
        return vars(self)