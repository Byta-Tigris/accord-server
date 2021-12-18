from typing import Any, Dict, List, Tuple
from digger.base.types import AbstractRequestManager, AbstractRequestStruct, AbstractResponseStruct
from utils.types import RequestMethod


class RequestStruct(AbstractRequestStruct):
    method = RequestMethod.Get
    
    def __init__(self, params_query: List[str] = [], params_data: List[str] = [], **kwargs) -> None:
        self.params_query: List[str] = params_query
        self.params_data: List[str] = params_data
    
    def _get_params(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Returns (query, data)

        If method.GET: return (variables, None)
        Elif method.POST: return (parms, variables) 
        """
        params = {}
        data = {}
        variables = vars(self)
        for key, value in variables.items():
            if value is None or key in self.get_ignorable_fields():
                del variables[key]
            elif key  in self.params_query:
                params[key] = value
                del variables[key]
            elif key in self.params_data:
                data[key] = value
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
    
    def __call__(self, manager: AbstractRequestManager, after=None, before=None) -> AbstractResponseStruct:
        if after != None:
            self.after = after
            self.params_query += ["after"]
        elif before != None:
            self.before = before
            self.params_query += ["before"]
        return manager.make_request(self)
        
    
    
    @classmethod
    def from_response(cls, response: AbstractResponseStruct):
        data = response.to_kwargs()
        return cls(**data)

