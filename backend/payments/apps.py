import django.apps
import django.conf


class PaymentsConfig(django.apps.AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "payments"
    verbose_name = "Платежи"
