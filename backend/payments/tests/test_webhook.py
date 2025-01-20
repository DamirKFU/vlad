import json

import django.db
import django.test
import django.urls
import rest_framework.status as status

import catalog.models
import users.models


class YooKassaWebhookTest(django.test.TestCase):
    def setUp(self):
        self.client = django.test.Client()
        self.webhook_url = django.urls.reverse("api:payments:yookassa-webhook")

        self.user = users.models.User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.category = catalog.models.Category.objects.create(
            name="Test Category"
        )
        self.color = catalog.models.Color.objects.create(
            name="Test Color", color="#000000"
        )
        self.garment = catalog.models.Garment.objects.create(
            category=self.category,
            color=self.color,
            size=catalog.models.Size.M,
            count=10,
            price=1000,
        )
        self.product = catalog.models.Product.objects.create(
            name="Test Product",
        )

        self.order = catalog.models.Order.objects.create(
            user=self.user,
            status=catalog.models.OrderStatus.WAITING_PAYMENT,
            payment_status=catalog.models.PaymentStatus.PENDING,
            payment_id="22d6d597-000f-5000-9000-145f6df21d6f",
            address="Test Address",
            phone="+79991234567",
        )

    def tearDown(self):
        users.models.User.objects.all().delete()
        super().tearDown()

    def test_payment_succeeded(self):
        webhook_data = {
            "type": "notification",
            "event": "payment.succeeded",
            "object": {
                "id": "22d6d597-000f-5000-9000-145f6df21d6f",
                "status": "succeeded",
                "amount": {"value": "2.00", "currency": "RUB"},
                "description": "Заказ №72",
                "recipient": {"account_id": "100500", "gateway_id": "100700"},
                "payment_method": {
                    "type": "bank_card",
                    "id": "22d6d597-000f-5000-9000-145f6df21d6f",
                    "saved": False,
                    "card": {
                        "first6": "555555",
                        "last4": "4444",
                        "expiry_month": "07",
                        "expiry_year": "2021",
                        "card_type": "MasterCard",
                        "issuer_country": "RU",
                        "issuer_name": "Sberbank",
                    },
                    "title": "Bank card *4444",
                },
                "created_at": "2018-07-10T14:27:54.691Z",
                "captured_at": "2018-07-10T14:28:27.606Z",
                "metadata": {"order_id": "72"},
            },
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "data": {},
                "message": "Webhook успешно обработан",
            },
        )

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, catalog.models.OrderStatus.PAID)
        self.assertEqual(
            self.order.payment_status, catalog.models.PaymentStatus.SUCCEEDED
        )

    def test_payment_canceled(self):
        webhook_data = {
            "type": "notification",
            "event": "payment.canceled",
            "object": {
                "id": "22d6d597-000f-5000-9000-145f6df21d6f",
                "status": "canceled",
                "amount": {"value": "2.00", "currency": "RUB"},
                "created_at": "2018-07-10T14:27:54.691Z",
                "description": "Заказ №72",
                "metadata": {"order_id": "72"},
                "payment_method": {
                    "type": "bank_card",
                    "id": "22d6d597-000f-5000-9000-145f6df21d6f",
                    "saved": False,
                    "card": {
                        "first6": "555555",
                        "last4": "4444",
                        "expiry_month": "07",
                        "expiry_year": "2021",
                        "card_type": "MasterCard",
                        "issuer_country": "RU",
                        "issuer_name": "Sberbank",
                    },
                    "title": "Bank card *4444",
                },
                "cancellation_details": {
                    "party": "merchant",
                    "reason": "fraud_suspected",
                },
            },
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "data": {},
                "message": "Webhook успешно обработан",
            },
        )

        self.order.refresh_from_db()
        self.assertEqual(
            self.order.status, catalog.models.OrderStatus.CANCELED
        )
        self.assertEqual(
            self.order.payment_status, catalog.models.PaymentStatus.CANCELED
        )

    def test_invalid_event(self):
        webhook_data = {
            "type": "notification",
            "event": "invalid.event",
            "object": {
                "id": "22d6d597-000f-5000-9000-145f6df21d6f",
            },
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_payment_id(self):
        webhook_data = {
            "type": "notification",
            "event": "payment.succeeded",
            "object": {
                "status": "succeeded",
            },
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_content_type(self):
        webhook_data = {
            "type": "notification",
            "event": "payment.succeeded",
        }

        response = self.client.post(
            self.webhook_url,
            data=webhook_data,
            content_type="application/x-www-form-urlencoded",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_order_not_found(self):
        webhook_data = {
            "type": "notification",
            "event": "payment.succeeded",
            "object": {
                "id": "non-existent-payment-id",
                "status": "succeeded",
            },
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.json(),
            {
                "errors": {
                    "fields": {},
                    "form_error": "Заказ не найден",
                },
                "message": "Заказ не найден",
            },
        )

    def test_missing_notification_type(self):
        webhook_data = {
            "event": "payment.succeeded",
            "object": {
                "id": "22d6d597-000f-5000-9000-145f6df21d6f",
            },
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_succeeded_without_embroidery(self):
        catalog.models.OrderItem.objects.create(
            order=self.order,
            product=self.product,
            garment=self.garment,
            quantity=1,
            price=1000,
        )

        webhook_data = {
            "type": "notification",
            "event": "payment.succeeded",
            "object": {
                "id": "22d6d597-000f-5000-9000-145f6df21d6f",
                "status": "succeeded",
            },
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, catalog.models.OrderStatus.PAID)
        self.assertEqual(
            self.order.payment_status, catalog.models.PaymentStatus.SUCCEEDED
        )

    def test_payment_succeeded_with_embroidery(self):
        embroidery_file = django.core.files.uploadedfile.SimpleUploadedFile(
            name="test.jef",
            content=b"test",
        )
        self.product.embroidery = embroidery_file
        self.product.save()

        catalog.models.OrderItem.objects.create(
            order=self.order,
            product=self.product,
            garment=self.garment,
            quantity=1,
            price=1000,
        )

        webhook_data = {
            "type": "notification",
            "event": "payment.succeeded",
            "object": {
                "id": "22d6d597-000f-5000-9000-145f6df21d6f",
                "status": "succeeded",
            },
        }

        response = self.client.post(
            self.webhook_url,
            data=json.dumps(webhook_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, catalog.models.OrderStatus.IN_WORK)
        self.assertEqual(
            self.order.payment_status, catalog.models.PaymentStatus.SUCCEEDED
        )
