from django.urls import path
from .views import *

urlpatterns = [
    path('username/valid', is_username_valid_api_view, name="username-valid"),
    path('create', CreateAccounAPIView.as_view(), name="create-account"),
    path('login', AccountLoginAPIView.as_view(), name="login-account")
]