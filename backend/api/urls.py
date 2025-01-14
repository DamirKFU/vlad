import django.contrib.admin
import django.urls

import api.views

app_name = "api"

urlpatterns = [
    django.urls.path(
        "users/",
        django.urls.include("users.urls", "users"),
        name="users",
    ),
    django.urls.path(
        "catalog/",
        django.urls.include("catalog.urls", "catalog"),
        name="catalog",
    ),
    django.urls.path(
        "get-csrf-token/",
        api.views.GetCSRFTokenView.as_view(),
        name="get-csrf-token",
    ),
    django.urls.path(
        "payments/",
        django.urls.include("payments.urls", "payments"),
        name="payments",
    ),
    django.urls.path(
        "staff/",
        django.urls.include("staff.urls", "staff"),
        name="staff",
    ),
    django.urls.path(
        "core/",
        django.urls.include("core.urls", "core"),
        name="core",
    ),
    django.urls.path(
        "telegram-bot/",
        django.urls.include("telegram_bot.urls", "telegram_bot"),
        name="telegram_bot",
    ),
    django.urls.path(
        "support/",
        django.urls.include("support.urls", "support"),
        name="support",
    ),
]
