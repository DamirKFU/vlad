import django.urls
import rest_framework_simplejwt.views

app_name = "api"

urlpatterns = [
    django.urls.path(
        "users/",
        django.urls.include("users.urls"),
        name="users",
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
