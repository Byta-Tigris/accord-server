from typing import Any, Dict, List, Tuple, Union
from digger.base.types import AbstractRequestManager, AbstractRequestStruct, AbstractResponseStruct
from utils.types import RequestMethod


class RequestStruct(AbstractRequestStruct):
    method = RequestMethod.Get
    params_query: List[str] = []
    params_data: List[str] = []
    
    
    def _get_params(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Returns (query, data)

        If method.GET: return (variables, None)
        Elif method.POST: return (parms, variables) 
        """
        params = {}
        data = {}
        variables = {}
        for key, value in vars(self).items():
            if key in self.params_query:
                params[key] = value
            elif key in self.params_data:
                data[key] = value
            elif value is not None and key not in self.get_ignorable_fields() and not value.startswith("__"):
                variables[key]  = value
        if self.method == RequestMethod.Post:
            return (params, variables)
        return (variables, data)

    def format_params(self, **params) -> Dict[str, Any]:
        return params
    
    

    
    def get_params(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Returns (query, data)

        If method.GET: return (variables, None)
        Elif method.POST: return (parms, variables) 
        """
        var = self._get_params()
        return self.format_params(**var[0]), self.format_params(**var[1])
    
    def process_after_request(self, manager: AbstractRequestManager, response: AbstractResponseStruct) -> AbstractResponseStruct:
        return response
    
    def __call__(self, manager: AbstractRequestManager, **extra_params) -> AbstractResponseStruct:
        response =  manager.make_request(self, **extra_params)
        return self.process_after_request(manager, response)
        
    
    
    @classmethod
    def from_response(cls, response: AbstractResponseStruct):
        data = response.to_kwargs()
        return cls(**data)

