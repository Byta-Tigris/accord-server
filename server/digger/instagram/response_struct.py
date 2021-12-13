from digger.base.response_struct import ResponseStruct


class InstagramShortLiveTokenResponse(ResponseStruct):


    def __init__(self, url: str, status_code: int, 
                access_token: str = None, user_id: str = None, error_type: str = None,
                code: int = None, error_message: str = None) -> None:
        self.access_token = access_token
        self.user_id = user_id
        self.error_type = error_type
        self.code = code
        self.error_message = error_message
        super().__init__(url, status_code)


class InstagramLongLiveTokenResponse(ResponseStruct):

    def __init__(self, url: str, status_code: int, access_token: str, token_type: str, expires_in: int) -> None:
        self.access_token = access_token
        self.token_type = token_type
        self.expires_in = expires_in
        super().__init__(url, status_code)



