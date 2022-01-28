from django.urls import path
from .views import *

urlpatterns = [
    path('username/valid', is_username_valid_api_view, name="username-valid"),
    path("user/exists", is_user_with_email_exists, name="user-exists"),
    path('create', CreateAccounAPIView.as_view(), name="create-account"),
    path('login', AccountLoginAPIView.as_view(), name="login-account"),
    path("me", RetrieveAndEditAccountAPIView.as_view(), name="retrieve-edit-account"),
    path("reset_password", ResetPasswordView.as_view(), name="reset-password"),
    path("retrieve_accounts", RetrieveAccountsFromEmailView.as_view(), name="retrieve-accounts"),
    path("change_password", ChangePasswordView.as_view(), name='change-password'),
    path('handles/me', RetrieveAndDeleteSocialHandlesAPIView.as_view(), name="retrieve-delete-handles"),
    path("account_metrics_visibility", PlatformMetricVisibilityView.as_view(), name="account-metric-visibility"),
    path("logout", AccountLogoutAPIVIew.as_view(), name="logout")
]