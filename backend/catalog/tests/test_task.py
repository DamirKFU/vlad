import django.db
import django.test

import catalog.models
import catalog.tasks
import payments.services
import users.models


TEST_CELERY_BROKER_URL = "redis://localhost:6379/10"
TEST_CELERY_RESULT_BACKEND = "redis://localhost:6379/10"
TEST_CELERY_ONCE = {
    "backend": "celery_once.backends.Redis",
    "settings": {
        "url": TEST_CELERY_BROKER_URL,
        "default_timeout": 60 * 10,
    },
}


@django.test.override_settings(
    CELERY_BROKER_URL=TEST_CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND=TEST_CELERY_RESULT_BACKEND,
    CELERY_ONCE=TEST_CELERY_ONCE,
)
class TestCreateOrderTask(django.test.TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser", password="testpass"
        )
        cls.category = catalog.models.Category.objects.create(
            name="Test Category"
        )
        cls.color = catalog.models.Color.objects.create(
            name="Test Color", color="#000000"
        )
        cls.product = catalog.models.Product.objects.create(
            name="Test Product", price=100
        )
        cls.garment = catalog.models.Garment.objects.create(
            price=50, category=cls.category, color=cls.color, count=10
        )
        cls.yookassa_service = payments.services.YooKassaService()
        cls.product.garments.add(cls.garment)

        cls.cart = catalog.models.Cart.objects.create(user=cls.user)
        cls.cart_item = catalog.models.CartItem.objects.create(
            cart=cls.cart,
            product=cls.product,
            garment=cls.garment,
            quantity=6,
        )

        cls.order_data = {
            "address": "Test Address",
            "phone": "+79991234567",
        }
        super().setUpClass()

    def tearDown(self):
        users.models.User.objects.all().delete()
        super().tearDown()

    def test_concurrent_order_creation(self):
        result = catalog.tasks.create_order_task_sync(
            None, self.order_data, self.user.id
        )
        order_id = result["data"]["order_id"]
        order = catalog.models.Order.objects.get(id=order_id)
        self.assertEqual(
            order.status, catalog.models.OrderStatus.WAITING_PAYMENT
        )
        self.garment.refresh_from_db()
        self.assertEqual(self.garment.count, 4)
        self.assertEqual(
            order.payment_status, catalog.models.PaymentStatus.PENDING
        )
        payment_id = order.payment_id
        payment_status = self.yookassa_service.get_status_payment(payment_id)
        self.assertEqual(payment_status, catalog.models.PaymentStatus.PENDING)
