from django.urls import path
from .views import *

urlpatterns = [
    path("manage", RetrieveMyLinkWall.as_view(), name="create-linkwall"),
    path("<str:username>", RetrieveLinkWall.as_view(), name="linktree-username-wall-fetch"),
    path("action/<str:username>", LinkwallActionAPIView.as_view(), name="linkwall-action"),
    path("links", add_link, name="add-link"),
    path("links/edit", edit_link, name="edit-link"),
    path("links/remove", remove_link, name="remove-link"),
    path("links/props", set_props, name="set-props"),
    path("assets", change_asset, name="change-assets"),
    path("media_handles/add", set_media_handles, name="set-media-handles"),
    path("media_handles/remove", remove_media_handle, name="remove-media-handles")

]