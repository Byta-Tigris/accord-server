from digger.base.response_struct import ResponseStruct


class GoogleUserInfoResponseStruct(ResponseStruct):

    def __init__(self, url: str, status_code: int,
        error = None, family_name: str = None, name: str = None,
        picture: str = None, email: str = None, given_name: str = None,
        verified_email: str = None
        ,**kwargs) -> None:
        self.error = error
        self.last_name = family_name
        self.first_name = given_name
        self.full_name = name
        self.email = email
        self.is_email_verified = verified_email
        self.avatar = picture
        super().__init__(url, status_code, **kwargs)