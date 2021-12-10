from digger.base.types import BaseErrorCode, BaseErrorException, BasePlatformStatusCodes


class InstagramRequestError(BaseErrorException):

    def __init__(self, error: BaseErrorCode) -> None:
        super().__init__(f"INSTAGRAM RESPONSE ERROR: {error.message} with status code {error.status_code}, code {error.code}, subcode {error.sub_code}")

class InstagramErrorCode(BaseErrorCode):

    def __init__(self, status_code: int, code: int, sub_code: int, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.sub_code = sub_code
        self.message = message
    
    def raise_error(self):
        raise InstagramRequestError(self)


class InstagramPlatformStatusCodes(BasePlatformStatusCodes):
    SUB_CODE_2207003 = InstagramErrorCode(400, -2, 2207003, "It takes too long to download the media.")
    SUB_CODE_2207020 = InstagramErrorCode(400, -2, 2207020, "The media you are trying to access has expired. Please try to upload again.")
    SUB_CODE_2207001 = InstagramErrorCode(400, -1, 2207001, "Instagram Server error.")
    SUB_CODE_2207032 = InstagramErrorCode(400, -1, 2207032, "Create media fail, please try to re-create media.")
    
