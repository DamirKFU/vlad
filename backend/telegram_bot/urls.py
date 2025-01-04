import django.urls

import telegram_bot.views

app_name = "telegram_bot"

urlpatterns = [
    django.urls.path("auth/", telegram_bot.views.TelegramAuthView.as_view()),
]
