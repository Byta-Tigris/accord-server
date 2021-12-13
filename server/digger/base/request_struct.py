from typing import Any, Dict
from digger.base.types import AbstractRequestManager, AbstractRequestStruct, AbstractResponseStruct


class RequestStruct(AbstractRequestStruct):
    
    def __init__(self, **kwargs) -> None:
        pass
    
    def _get_params(self) -> Dict[str, Any]:
        variables = vars(self)
        for key, value in variables.items():
            if value is None or key in self.get_ignorable_fields():
                del variables[key]
        return variables

    def format_params(self, **params) -> Dict[str, Any]:
        return params
    
    def get_params(self) -> Dict[str, Any]:
        var = self._get_params()
        return self.format_params(**var)
    
    def __call__(self, manager: AbstractRequestManager) -> AbstractResponseStruct:
        return manager.make_request(self)
    
    @classmethod
    def from_response(cls, response: AbstractResponseStruct):
        data = response.to_kwargs()
        return cls(**data)

