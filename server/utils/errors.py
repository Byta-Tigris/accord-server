"""
Accounts Related Exceptions
"""

class UserAlreadyExists(Exception):
    
    def __init__(self, email: str) -> None:
        super().__init__(f"User with {email} already exists")


class AccountAlreadyExists(Exception):
    
    def __init__(self, email: str, entity_type: str) -> None:
        super().__init__(f"Account with {email} and entity {entity_type} already exists")