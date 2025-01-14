import django.contrib.auth.forms
import django.contrib.auth.views
import django.urls


import users.views


app_name = "users"


urlpatterns = [
    django.urls.path(
        "register/",
        users.views.CrateUserView.as_view(),
        name="register",
    ),
    django.urls.path(
        "login/",
        users.views.LoginView.as_view(),
        name="login",
    ),
    django.urls.path(
        "logout/",
        users.views.LogoutView.as_view(),
        name="logout",
    ),
    django.urls.path(
        "is_auth/",
        users.views.IsAuthView.as_view(),
        name="is_auth",
    ),
    django.urls.path(
        "password/reset/",
        users.views.PasswordResetRequestView.as_view(),
        name="password_reset_request",
    ),
    django.urls.path(
        "password/reset/confirm/",
        users.views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    django.urls.path(
        "search/",
        users.views.UserSearchView.as_view(),
        name="user_search",
    ),
]
