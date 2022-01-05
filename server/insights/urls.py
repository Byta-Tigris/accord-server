from django.urls import path

from insights.instagram_views import CreateInstagramHandlesView

urlpatterns = [
    path("instagram", CreateInstagramHandlesView.as_view(), name="create-instagram-handle")
]