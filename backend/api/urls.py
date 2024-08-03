import django.urls
import rest_framework_simplejwt.views

import api.views

app_name = "api"

urlpatterns = [
    django.urls.path(
        "user/register/",
        api.views.CrateUserView.as_view(),
        name="register",
    ),
    django.urls.path(
        "token/",
        rest_framework_simplejwt.views.TokenObtainPairView.as_view(),
        name="get_token",
    ),
    django.urls.path(
        "token/refresh/",
        rest_framework_simplejwt.views.TokenRefreshView.as_view(),
        name="refresh",
    ),
]
