import django.contrib.admin
import django.urls

import api.views

app_name = "api"

urlpatterns = [
    django.urls.path(
        "users/",
        django.urls.include("users.urls"),
        name="users",
    ),
    django.urls.path(
        "token/",
        api.views.CustomTokenObtainPairView.as_view(),
        name="get_token",
    ),
    django.urls.path(
        "token/refresh/",
        api.views.CustomTokenRefreshView.as_view(),
        name="refresh",
    ),
    django.urls.path(
        "api-auth/",
        django.urls.include("rest_framework.urls"),
        name="rest_framework-auth",
    ),
]
