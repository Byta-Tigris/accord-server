from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Account


class HttpOnlyCookieToAuthRequestMiddleware:
    """
    Middleware checks cookies tied with the request specifically for HttpOnlyCookie named 'token'
    Converts token to HTTP_AUTHORIZATION :  Token {token}
    """

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    
    def __call__(self, request: Request) -> Response:
        if "AUTH_TOKEN" in request.COOKIES and not ("HTTP_AUTHORIZATION" in request.META):
            token = request.COOKIES["AUTH_TOKEN"]
            request.META["HTTP_AUTHORIZATION"] = f"Token {token}"
        response: Response = self.get_response(request)
        return response

        

class AccountAuthenticationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: Request):
        account = None
        if (token_str := request.META.get('HTTP_AUTHORIZATION', None)) is not None:
            token_key: str = token_str.replace("Token ", "")
            token: Token = Token.objects.get(key=token_key)
            query = Q(user=token.user)
            access_user = None
            if "access_user" in request.GET:
                access_user = request.GET["access_user"]
                query &= Q(username=access_user)
            account_queryset = Account.objects.select_related('user').filter(query)
            if account_queryset.exists():
                account: Account = account_queryset.first()
                if account.user != token.user:
                    account = None
        setattr(request, "account", account)
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        return response