from rest_framework.authtoken.models import Token
from rest_framework.request import Request

from accounts.models import Account

class AccountAuthenticationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: Request):
        account = None
        if (token_str := request.META.get('HTTP_AUTHORIZATION', None)) is not None:
            token_key: str = token_str.replace("Token ", "")
            token: Token = Token.objects.get(key=token_key)
            account_queryset = Account.objects.select_related('user').filter(user=token.user)
            if account_queryset.exists():
                account: Account = account_queryset.first()
        setattr(request, "account", account)
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response