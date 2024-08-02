import django.contrib.admin
import django.urls
import rest_framework_simplejwt
import rest_framework_simplejwt.views

import api.views

urlpatterns = [
    django.urls.path(
        "api/user/register/",
        api.views.CrateUserView.as_view(),
        name="register",
    ),
    django.urls.path(
        "api/token/",
        rest_framework_simplejwt.views.TokenObtainPairView.as_view(),
        name="get_token",
    ),
    django.urls.path(
        "api/token/refresh/",
        rest_framework_simplejwt.views.TokenRefreshView.as_view(),
        name="refresh",
    ),
    django.urls.path(
        "api-auth/",
        django.urls.include("rest_framework.urls"),
        name="rest_framework-auth",
    ),
    django.urls.path(
        "admin/",
        django.contrib.admin.site.urls,
        name="admin",
    ),
]
