from typing import Any, Dict, List, Sequence, Tuple, Type, Union

from django.db import models
from digger.base.types import (AbstractRequestManager, AbstractRequestStructure, AbstractResponseStructure,
                             FieldMissingException, FieldTypeMismatchException, RequestEndpoint, RequestMethod, Response)





class BaseRequestStruct(AbstractRequestStructure):

    response_structs: Union[Type, Dict[int, AbstractResponseStructure]] = None
    
    def __init__(self, endpoint: RequestEndpoint, method: str = RequestMethod.Get, 
                       required_fields: Sequence[Union[str, Tuple[str, Type]]] = [],
                       query_params: Dict[str] = {}, data_params: Dict[str] = {},
                       base_url_key: Union[str, None] = "default"
                       ) -> None:
        self.endpoint: RequestEndpoint = endpoint
        self.method = method
        self.required_fields = required_fields
        self.query_params = query_params
        self.data_params = data_params
        self.base_url_key = base_url_key
    

    def verfiy_fields(self) -> None:
        if isinstance(self.required_fields, list):
            for field_data in self.required_fields:
                field = field_data
                if isinstance(field_data, (list, tuple)):
                    field = field_data[0]
                if not hasattr(self, field):
                    raise FieldMissingException(self, field)
                elif not (len(field_data) > 1 and isinstance(getattr(self, field), field_data[1])):
                    raise FieldTypeMismatchException(self, field, field_data[1])
        return True
    
    def _get_params(self, fields) -> Dict[str, Any]:
        data = dict()
        for field in fields:
            if hasattr(self, field) and getattr(self, field) != None:
                data[field] = getattr(self, field)
        return data
    
    def get_query_params(self) -> Dict[str, Any]:
        return self._get_params(self.query_params)
    
    def get_data_params(self) -> Dict[str, Any]:
        return self._get_params(self.data_params)
    
    def call_request(self, request_manager: AbstractRequestManager) -> AbstractResponseStructure:
        return request_manager.make_request(self)

    def process_response(self, response: Response) -> AbstractResponseStructure:
        """Maps response struct with suitable response"""

        if isinstance(self.response_structs, dict):
            response_struct: AbstractResponseStructure = self.response_structs[response.status_code]
        else:
            response_struct = self.response_structs
        return response_struct(response)
    
    
    @classmethod
    def from_model(cls, model: models.Model):
        pass
    

    def make_new_request_from_response(self, resposne: AbstractResponseStructure) -> AbstractRequestStructure:
        """"""
        pass
