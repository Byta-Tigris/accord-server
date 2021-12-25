from rest_framework.request import Request

from accounts.models import Account

class AccountAuthenticationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: Request):
        account = None
        if not request.user:
            account_queryset = Account.objects.filter(user=request.user)
            if account_queryset.exists():
                account: Account = account_queryset.first()
        setattr(request, "account", account)
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response