from django.urls import path
from .views import *

urlpatterns = [
    path("me", RetrieveMyLinkWall.as_view(), name="retrieve-linkwall"),
    path("<str:username>", RetrieveLinkWall.as_view(), name="linktree-username-wall-fetch"),
    path("action/<str:username>", LinkwallActionAPIView.as_view(), name="linkwall-action"),
    path("manage/<str:action>", ManageLinkwallAPIView.as_view(), name="manage-linkwall"),

]