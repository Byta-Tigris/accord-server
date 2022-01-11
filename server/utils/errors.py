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


class NoAccountsExists(Exception):
    def __init__(self, email:str) -> None:
        super().__init__(f"No account exists related with {email}")
class AccountDoesNotExists(Exception):
    def __init__(self, username: str) -> None:
        super().__init__(f"Account with username {username} does not exists")

class InvalidAuthentication(Exception):
    def __init__(self, username: str) -> None:
        super().__init__(f"Authentication for account {username} is invalid")


class OAuthAuthorizationFailure(Exception):
    def __init__(self, platform: str) -> None:
        super().__init__(f"{platform} authorization failed")


class NoSocialMediaHandleExists(Exception):
    def __init__(self, username: str) -> None:
        super().__init__(f"No social media associated with account of username {username}")