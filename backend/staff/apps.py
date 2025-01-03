import django.apps


class StaffConfig(django.apps.AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "staff"
    verbose_name = "Панель управления"
