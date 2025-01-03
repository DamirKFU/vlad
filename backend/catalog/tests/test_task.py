import concurrent.futures

import django.db
import django.test

import catalog.tasks
import users.models


class FakeSelf:
    def update_state(self, state=None, meta=None):
        pass


class TestCreateOrderTask(django.test.TransactionTestCase):
    def setUp(self):
        self.user = users.models.User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.category = catalog.models.Category.objects.create(
            name="Test Category"
        )
        self.color = catalog.models.Color.objects.create(
            name="Test Color", color="#000000"
        )
        self.product = catalog.models.Product.objects.create(
            name="Test Product", price=100
        )
        self.garment = catalog.models.Garment.objects.create(
            price=50, category=self.category, color=self.color, count=10
        )
        self.product.garments.add(self.garment)

        self.cart = catalog.models.Cart.objects.create(user=self.user)
        self.cart_item = catalog.models.CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            garment=self.garment,
            quantity=6,
        )

        self.order_data = {
            "address": "Test Address",
            "phone": "+79991234567",
        }
        django.db.transaction.commit()

    def test_concurrent_order_creation(self):
        def side_effect():
            fake_self = FakeSelf()
            try:
                with django.db.transaction.atomic():
                    return catalog.tasks.create_order_task_sync(
                        fake_self, self.order_data, self.user.id
                    )
            finally:
                django.db.connections.close_all()

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(side_effect) for _ in range(2)]
            results = [
                f.result() for f in concurrent.futures.as_completed(futures)
            ]

        success_count = sum(
            1 for r in results if "data" in r and "order_id" in r["data"]
        )
        error_count = sum(1 for r in results if "data" not in r)

        self.assertEqual(
            success_count, 1, "Должен быть создан ровно один заказ"
        )
        self.assertEqual(error_count, 1, "Вторая задача должна вернуть ошибку")

        self.garment.refresh_from_db()
        self.assertGreaterEqual(self.garment.count, 0)
        orders = catalog.models.Order.objects.filter(user=self.user)
        self.assertEqual(orders.count(), 1)

        order = orders.first()
        self.assertEqual(order.address, "Test Address")
        self.assertEqual(order.phone, "+79991234567")
        self.assertEqual(order.items.count(), 1)

        order_item = order.items.first()
        self.assertEqual(order_item.quantity, 6)
        self.assertEqual(order_item.garment, self.garment)
        self.assertEqual(order_item.product, self.product)
