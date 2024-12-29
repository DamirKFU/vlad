from django.conf import settings
from django.core.management.base import BaseCommand

from payments.services import YookassaService


class Command(BaseCommand):

    def handle(self, *args, **options):
        service = YookassaService()
        webhook_url = f"{settings.SITE_URL}/api/webhook/yookassa/"

        if service.register_webhook(webhook_url):
            self.stdout.write(
                self.style.SUCCESS(
                    f"Webhook успешно зарегистрирован: {webhook_url}"
                )
            )
        else:
            self.stdout.write(self.style.ERROR("Ошибка регистрации webhook"))
