import django.apps


class ApiConfig(django.apps.AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
    verbose_name = "АПИ"
