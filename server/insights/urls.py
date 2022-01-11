from django.urls import path

from insights.instagram_views import CreateInstagramHandlesView
from insights.views import RetrieveHandleInsightsView, RetrievePlatformInsightsView, RetrieveSocialMediaHandleView

urlpatterns = [
    path("instagram", CreateInstagramHandlesView.as_view(), name="create-instagram-handle"),
    path("handles", RetrieveSocialMediaHandleView.as_view(), name="social-media-handles"),
    path("handles/<str:username>", RetrieveSocialMediaHandleView.as_view(), name="social-media-handles-using-username"),
    path("handles/<str:handle>", RetrieveSocialMediaHandleView.as_view(), name="social-media-handles-using-handle"),
    path("insights/platform/<str:platform>", RetrievePlatformInsightsView.as_view(), name="platform-insights"),
    path("insights/platform/<str:platform>/<str:username>", RetrievePlatformInsightsView.as_view(), name="platform-insights-username"),
    path("insights/handle/<str:handle>", RetrieveHandleInsightsView.as_view(), name="handle-insights")
]