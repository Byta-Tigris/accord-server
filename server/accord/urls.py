"""accord URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("biddings/", include("biddings.urls")),
    path("campaigns/", include("campaigns.urls")),
    path("payment/", include("payment.urls")),
    path("content_manager/", include("content_manager.urls")),
    path("sacred_logs/", include("log_engine.urls")),
    path("wall/", include('linktree.urls')),
    path("insights/", include("insights.urls"))
]
