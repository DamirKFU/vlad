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
        "verifed-email/",
        users.views.VerifedEmailTokenView.as_view(),
        name="verifed_email",
    ),
    django.urls.path(
        "check-email-token/",
        users.views.CheckEmailTokenView.as_view(),
        name="check_email_token",
    ),
]
