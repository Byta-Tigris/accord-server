from django.urls import path

from insights.instagram_views import CreateInstagramHandlesView
from insights.views import RetrievePlatformInsights, RetrieveSocialMediaHandle

urlpatterns = [
    path("instagram", CreateInstagramHandlesView.as_view(), name="create-instagram-handle"),
    path("handles", RetrieveSocialMediaHandle.as_view(), name="social-media-handles"),
    path("handles/<str:username>", RetrieveSocialMediaHandle.as_view(), name="social-media-handles-using-username"),
    path("handles/<str:handle>", RetrieveSocialMediaHandle.as_view(), name="social-media-handles-using-handle"),
    path("insights/platform/<str:platform>", RetrievePlatformInsights.as_view(), name="platform-insights"),
    path("insights/platform/<str:platform>/<str:username>", RetrievePlatformInsights.as_view(), name="platform-insights-username")
]