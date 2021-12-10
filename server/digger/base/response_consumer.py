

from typing import Any, Dict, List, Sequence, Tuple, Type, Union

from digger.base.types import AbstractResponseStructure, FieldMissingException, FieldTypeMismatchException


class BaseResponseStruct(AbstractResponseStructure):

    def __init__(self, status_code: int, required_fields: Union[list, Sequence[Union[str, Tuple[str, Type]]]] = []) -> None:
        """Response struct holds data about the response\n
        This serves as the base class for every kind of response structure\n
        
        Keyword Arguments:\n
        status_code -- Status code of the response\n
        required_fields -- Fields which are compulsory to be present in the response\n
                           If the requires_fields is set, then we wont check for the data types\n
                           Elif required_fields is Dict, we should check data types of each field, and raise Error in cases.


        """
        self.status_code = status_code
        self.required_fields = required_fields

        self.verify_response()

        if self.required_fields:
            self.verify_inputs()
    
    def process_error(self) -> None:
        return
    
    def verify_response(self) -> None:
        """Verifies that the response does not have error, on error code, the response starts process_erro"""
        return 
    
    
    def verify_inputs(self):
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
 