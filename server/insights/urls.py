from django.urls import path

from insights.views import CreateSocialMediaHandlesView, RetrieveHandleInsightsView, RetrieveLinkwallInsights, RetrievePlatformInsightsView, RetrieveSocialMediaHandleView, get_platforms_view

urlpatterns = [
    path("create_handle/<str:platform>", CreateSocialMediaHandlesView.as_view(), name="create-social-media-handle"),
    path("handle/<str:handle_id>", RetrieveSocialMediaHandleView.as_view(), name="social-media-handles-retrieve-handle_id"),
    path("handles/<str:username>", RetrieveSocialMediaHandleView.as_view(), name="social-media-handles-retrieve"),
    path("insights/platform/<str:platform>", RetrievePlatformInsightsView.as_view(), name="platform-insights"),
    path("insights/platform/<str:platform>/<str:username>", RetrievePlatformInsightsView.as_view(), name="platform-insights-username"),
    path("insights/handle/<str:handle>", RetrieveHandleInsightsView.as_view(), name="handle-insights"),
    path("insights/linkwall", RetrieveLinkwallInsights.as_view(), name="linkwall-insights"),
    path('platforms', get_platforms_view, name='get-platforms')
]