from django.urls import path
from .views import CreateOrUpdateLinkWall, LinkwallActionAPIView, RetrieveLinkWall

urlpatterns = [
    path("create", CreateOrUpdateLinkWall.as_view(), name="create-linkwall"),
    path("<str:username>", RetrieveLinkWall.as_view(), name="linktree-username-wall-fetch"),
    path("action/<str:username>", LinkwallActionAPIView.as_view(), name="linkwall-action")
]