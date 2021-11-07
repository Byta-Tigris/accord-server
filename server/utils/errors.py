"""
Accounts Related Exceptions
"""

class UserAlreadyExists(Exception):
    
    def __init__(self, email: str) -> None:
        super().__init__(f"User with {email} already exists")


class AccountAlreadyExists(Exception):
    
    def __init__(self, email: str, entity_type: str) -> None:
        super().__init__(f"Account with {email} and entity {entity_type} already exists")

class PasswordValidationError(Exception):

    def __init__(self, password: str) -> None:
        super().__init__(f"{password}: is not valid, enter password with len in range of 8 to 20 chars and containing alphabets and numbers.")