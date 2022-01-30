"""
Accounts Related Exceptions
"""

class ServerException(Exception):

    def __repr__(self) -> str:
        return self.args[0] if len(self.args) > 0 else "Unexpected error"
    
    def __str__(self) -> str:
        return repr(self)

class UserAlreadyExists(ServerException):
    
    def __init__(self, email: str) -> None:
        super().__init__(f"User with {email} already exists")


class AccountAlreadyExists(ServerException):
    
    def __init__(self, email: str, entity_type: str) -> None:
        super().__init__(f"Account with {email} and entity {entity_type} already exists")

class PasswordValidationError(ServerException):

    def __init__(self, password: str) -> None:
        super().__init__(f"{password} is not valid, enter password with len in range of 5 to 21 chars and containing alphabets and numbers")


class NoAccountsExistsRelatedWithEmail(ServerException):
    def __init__(self, email:str) -> None:
        super().__init__(f"No account exists related with {email}")

class AccountDoesNotExists(ServerException):
    def __init__(self, username: str) -> None:
        super().__init__(f"Account with username {username} does not exists")

class InvalidAuthentication(ServerException):
    def __init__(self, username: str) -> None:
        super().__init__(f"Authentication for account {username} is invalid")


class OAuthPlatformAuthorizationFailure(ServerException):
    def __init__(self, platform: str) -> None:
        super().__init__(f"{platform} authorization failed")

class GoogleOAuthAuthorizationFailure(ServerException):
    def __init__(self, ) -> None:
        super().__init__(f"OAuth Authorization of your email failed. Try again")


class NoSocialMediaHandleExists(ServerException):
    def __init__(self, username: str) -> None:
        super().__init__(f"No social media associated with account of username {username}")

class AccountAuthenticationFailed(ServerException):

    def __init__(self) -> None:
        super().__init__(f"Account authentication failed. Please Login again")


class NoLinkwallExists(ServerException):
    def __init__(self) -> None:
        super().__init__(f"No linkwall exists")

class NoLinkExists(ServerException):
    def __init__(self) -> None:
        super().__init__(f"No link exists")
