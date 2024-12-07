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
        "get-csrf-token/",
        api.views.GetCSRFTokenView.as_view(),
        name="get-csrf-token",
    ),
]
