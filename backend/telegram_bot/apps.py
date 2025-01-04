import django.apps


class TelegramBotConfig(django.apps.AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "telegram_bot"

    def ready(self):
        import telegram_bot.signals  # noqa: F401
