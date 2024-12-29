import django.conf
import yookassa
import yookassa.domain
import yookassa.domain.notification as notification


class YooKassaService:
    def __init__(self):
        yookassa.Configuration.account_id = (
            django.conf.settings.YOOKASSA_SHOP_ID
        )
        yookassa.Configuration.secret_key = (
            django.conf.settings.YOOKASSA_SECRET_KEY
        )
        site_url = django.conf.settings.SITE_URL
        self.webhook_url = f"{site_url}/api/payments/webhook/yookassa/"

    def create_payment(self, order, return_url):
        payment_data = {
            "amount": {"value": str(order.total_sum), "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": return_url,
            },
            "capture": True,
            "description": f"Заказ #{order.id}",
            "metadata": {"order_id": order.id},
        }

        payment = yookassa.Payment.create(payment_data)

        return {
            "id": payment.id,
            "status": payment.status,
            "confirmation_url": payment.confirmation.confirmation_url,
            "created_at": payment.created_at,
        }

    def get_status_payment(self, payment_id):
        payment = yookassa.Payment.find_one(payment_id)
        return payment.status

    def register_webhook(self, webhook_url):

        webhooks = yookassa.Webhook.list()
        events = [
            notification.WebhookNotificationEventType.PAYMENT_SUCCEEDED,
            notification.WebhookNotificationEventType.PAYMENT_CANCELED,
        ]
        webhooks = yookassa.Webhook.list()

        for event in events:
            hook_is_set = False
            for wh in webhooks.items:
                if wh.event != event:
                    continue

                if wh.url != webhook_url:
                    yookassa.Webhook.remove(wh.id)
                else:
                    hook_is_set = True

            if not hook_is_set:
                yookassa.Webhook.add({"event": event, "url": webhook_url})

    def cancel_payment(self, payment_id: str) -> dict:
        response = yookassa.Payment.cancel(payment_id)
        return {
            "id": response.id,
            "status": response.status,
            "cancellation_details": (
                {
                    "party": response.cancellation_details.party,
                    "reason": response.cancellation_details.reason,
                }
                if response.cancellation_details
                else None
            ),
        }
