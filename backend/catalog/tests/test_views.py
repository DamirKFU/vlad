import http
import io
import shutil

import django.db
import django.test
import django.urls
import PIL.Image
import redis
import rest_framework.test

import catalog.models
import catalog.utils
import payments.services
import users.documents
import users.models

TEST_MEDIA_ROOT = django.conf.settings.BASE_DIR / "test_media"
TEST_CELERY_BROKER_URL = "redis://localhost:6379/10"
TEST_CELERY_RESULT_BACKEND = "redis://localhost:6379/10"
TEST_CELERY_ONCE = {
    "backend": "celery_once.backends.Redis",
    "settings": {
        "url": TEST_CELERY_BROKER_URL,
        "default_timeout": 60 * 10,
    },
}


def create_test_image():
    image = PIL.Image.new("RGB", (100, 100), color="red")
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="JPEG")
    image_bytes.seek(0)
    return image_bytes


class GarmentListViewTests(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser", password="testpass"
        )
        cls.category = catalog.models.Category.objects.create(
            name="Test Category"
        )
        cls.color = catalog.models.Color.objects.create(
            name="Test Color", color="#000000"
        )
        cls.guest_client = rest_framework.test.APIClient()

    @classmethod
    def tearDownClass(cls):
        users.models.User.objects.all().delete()
        super().tearDownClass()

    def test_garment_list_view(self):
        response = self.guest_client.get(
            django.urls.reverse("api:catalog:garments")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_garment_list_view_content(self):
        response = self.guest_client.get(
            django.urls.reverse("api:catalog:garments")
        )
        response_data = response.json()
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(
            response_data,
            {"data": [], "message": "Одежда успешно получена"},
        )

    def test_garment_list_view_content_2(self):
        garment = catalog.models.Garment.objects.create(
            category=self.category,
            color=self.color,
            size=catalog.models.Size.M,
            count=10,
            price=100,
        )
        response = self.guest_client.get(
            django.urls.reverse("api:catalog:garments")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        data = response.json()
        data_expected = [
            {
                "id": garment.id,
                "category": {
                    "name": self.category.name,
                    "id": self.category.id,
                },
                "color": {
                    "name": self.color.name,
                    "color": self.color.color,
                    "id": self.color.id,
                },
                "size": "M",
                "count": 10,
                "price": 100,
            }
        ]
        self.assertEqual(
            data,
            {"data": data_expected, "message": "Одежда успешно получена"},
        )


@django.test.override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProductListViewTests(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser", password="testpass"
        )
        cls.category = catalog.models.Category.objects.create(
            name="Test Category"
        )
        cls.color = catalog.models.Color.objects.create(
            name="Test Color", color="#000000"
        )
        cls.image = django.core.files.uploadedfile.SimpleUploadedFile(
            name="test_image.jpg",
            content=create_test_image().read(),
            content_type="image/jpeg",
        )
        cls.guest_client = rest_framework.test.APIClient()
        cls.authorized_client = rest_framework.test.APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)

    @classmethod
    def tearDownClass(cls):
        users.models.User.objects.all().delete()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_product_list_view(self):
        response = self.guest_client.get(
            django.urls.reverse("api:catalog:products")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertIn("data", response.json())
        self.assertIn("message", response.json())
        self.assertEqual(
            response.json()["message"],
            "Продукты успешно получены",
        )
        self.assertIn("results", response.json()["data"])
        self.assertEqual(
            response.json()["data"]["results"],
            [],
        )

    def test_product_list_view_2(self):
        product = catalog.models.Product.objects.create(
            name="Test Product", price=100
        )
        response = self.authorized_client.get(
            django.urls.reverse("api:catalog:products")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertIn("count", response.json()["data"])
        self.assertEqual(
            response.json()["data"]["count"],
            1,
        )
        results_expected = [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "main_image": None,
                "secondary_image": None,
            }
        ]
        self.assertEqual(
            response.json()["data"]["results"],
            results_expected,
        )

    def test_product_list_view_3(self):
        product = catalog.models.Product.objects.create(
            name="Test Product", price=100
        )
        product_image = catalog.models.ProductMainImage.objects.create(
            product=product, image=self.image
        )
        response = self.authorized_client.get(
            django.urls.reverse("api:catalog:products")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertIn("count", response.json()["data"])
        self.assertEqual(
            response.json()["data"]["count"],
            1,
        )
        product_image.refresh_from_db()
        results_expected = [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "main_image": product_image.get_image_660x880().url,
                "secondary_image": None,
            }
        ]
        self.assertEqual(
            response.json()["data"]["results"],
            results_expected,
        )


@django.test.override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProductDetailViewTests(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser", password="testpass"
        )
        cls.category = catalog.models.Category.objects.create(
            name="Test Category"
        )
        cls.guest_client = rest_framework.test.APIClient()
        cls.authorized_client = rest_framework.test.APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)
        cls.image = django.core.files.uploadedfile.SimpleUploadedFile(
            name="test_image.jpg",
            content=create_test_image().read(),
            content_type="image/jpeg",
        )
        cls.color = catalog.models.Color.objects.create(
            name="Test Color", color="#000000"
        )
        cls.garment = catalog.models.Garment.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            count=10,
            price=100,
        )

    @classmethod
    def tearDownClass(cls):
        users.models.User.objects.all().delete()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_product_detail_view(self):
        response = self.guest_client.get(
            django.urls.reverse("api:catalog:product-detail", args=[1])
        )
        self.assertEqual(response.status_code, http.HTTPStatus.NOT_FOUND)

    def test_product_detail_view_2(self):
        product = catalog.models.Product.objects.create(
            name="Test Product", price=100
        )
        response = self.authorized_client.get(
            django.urls.reverse(
                "api:catalog:product-detail", args=[product.id]
            )
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        response_expected = {
            "data": {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "main_image": None,
                "additional_images": [],
                "garments": [],
            },
            "message": "Продукт успешно получен",
        }
        self.assertEqual(response.json(), response_expected)

    def test_product_detail_view_3(self):
        product = catalog.models.Product.objects.create(
            name="Test Product", price=100
        )
        product.garments.add(self.garment)
        product_image = catalog.models.ProductMainImage.objects.create(
            product=product, image=self.image
        )
        product_additional_image = (
            catalog.models.ProductAdditionalImage.objects.create(
                product=product,
                image=self.image,
                color=self.color,
                category=self.category,
            )
        )
        product.refresh_from_db()
        response = self.authorized_client.get(
            django.urls.reverse(
                "api:catalog:product-detail", args=[product.id]
            )
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        response_expected = {
            "data": {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "main_image": product_image.image.url,
                "additional_images": [
                    {
                        "image": product_additional_image.image.url,
                        "color": {
                            "id": self.color.id,
                            "name": self.color.name,
                        },
                        "category": {
                            "id": self.category.id,
                            "name": self.category.name,
                        },
                    }
                ],
                "garments": [
                    {
                        "id": self.garment.id,
                        "size": self.garment.size.value,
                        "count": self.garment.count,
                        "price": self.garment.price,
                        "category": {
                            "id": self.category.id,
                            "name": self.category.name,
                        },
                        "color": {
                            "id": self.color.id,
                            "name": self.color.name,
                            "color": self.color.color,
                        },
                    }
                ],
            },
            "message": "Продукт успешно получен",
        }
        self.assertEqual(response.json(), response_expected)


class AddToCartViewTests(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
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
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            count=10,
            price=100,
        )
        cls.product.garments.add(cls.garment)
        cls.authorized_client = rest_framework.test.APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)

    @classmethod
    def tearDownClass(cls):
        users.models.User.objects.all().delete()
        super().tearDownClass()

    def test_add_to_cart_view(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            data={
                "id_product": self.product.id,
                "id_garment": self.garment.id,
            },
        )
        self.assertEqual(response.status_code, http.HTTPStatus.CREATED)

    def test_no_valid_data(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            data={},
        )
        fields_expected = {
            "id_product": "Обязательное поле.",
            "id_garment": "Обязательное поле.",
        }
        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json()["errors"]["fields"],
            fields_expected,
        )

    def test_garment_not_found(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            data={"id_product": self.product.id, "id_garment": 999},
        )
        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)

    def test_product_not_found(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            data={"id_product": 999, "id_garment": self.garment.id},
        )
        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)

    def test_no_cart(self):
        cart = catalog.models.Cart.objects.filter(user=self.user).first()
        self.assertIsNone(cart)
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            data={
                "id_product": self.product.id,
                "id_garment": self.garment.id,
            },
        )
        self.assertEqual(response.status_code, http.HTTPStatus.CREATED)
        new_cart = catalog.models.Cart.objects.filter(user=self.user).first()
        self.assertIsNotNone(new_cart)
        self.assertEqual(new_cart.items.count(), 1)
        self.assertEqual(new_cart.items.first().product, self.product)
        self.assertEqual(new_cart.items.first().garment, self.garment)

    def test_add_to_cart_view_2(self):
        self.authorized_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            data={
                "id_product": self.product.id,
                "id_garment": self.garment.id,
            },
        )
        self.authorized_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            data={
                "id_product": self.product.id,
                "id_garment": self.garment.id,
            },
        )
        cart = catalog.models.Cart.objects.filter(user=self.user).first()
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 2)


@django.test.override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CartViewTests(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_without_cart = users.models.User.objects.create_user(
            username="testuser_without_cart",
            password="testpass",
            email="testuser_without_cart@test.com",
        )
        cls.user_with_cart = users.models.User.objects.create_user(
            username="testuser_with_cart",
            password="testpass",
            email="testuser_with_cart@test.com",
        )
        cls.category = catalog.models.Category.objects.create(
            name="Test Category"
        )
        cls.color = catalog.models.Color.objects.create(
            name="Test Color", color="#000000"
        )
        cls.garment = catalog.models.Garment.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            count=10,
            price=100,
        )
        cls.image = django.core.files.uploadedfile.SimpleUploadedFile(
            name="test_image.jpg",
            content=create_test_image().read(),
            content_type="image/jpeg",
        )
        cls.product = catalog.models.Product.objects.create(
            name="Test Product", price=100
        )
        cls.product_image = catalog.models.ProductMainImage.objects.create(
            product=cls.product, image=cls.image
        )
        cls.product.garments.add(cls.garment)
        cls.authorized_client_without_cart = rest_framework.test.APIClient()
        cls.authorized_client_without_cart.force_authenticate(
            user=cls.user_without_cart
        )
        cls.cart = catalog.models.Cart.objects.create(user=cls.user_with_cart)
        cls.cart_item = catalog.models.CartItem.objects.create(
            cart=cls.cart, product=cls.product, garment=cls.garment
        )
        cls.cart.items.add(cls.cart_item)
        cls.authorized_client_with_cart = rest_framework.test.APIClient()
        cls.authorized_client_with_cart.force_authenticate(
            user=cls.user_with_cart
        )

    @classmethod
    def tearDownClass(cls):
        users.models.User.objects.all().delete()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_cart_view(self):
        response = self.authorized_client_without_cart.get(
            django.urls.reverse("api:catalog:cart")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(
            response.json()["data"]["items"],
            [],
        )
        self.assertIsNotNone(
            catalog.models.Cart.objects.filter(
                user=self.user_without_cart
            ).first()
        )

    def test_cart_view_2(self):
        response = self.authorized_client_with_cart.get(
            django.urls.reverse("api:catalog:cart")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        expected_garment = {
            "id": self.garment.id,
            "size": self.garment.size.value,
            "count": self.garment.count,
            "price": self.garment.price,
            "category": {
                "id": self.category.id,
                "name": self.category.name,
            },
            "color": {
                "id": self.color.id,
                "name": self.color.name,
                "color": self.color.color,
            },
        }
        expected_product = {
            "id": self.product.id,
            "name": self.product.name,
            "price": self.product.price,
            "main_image": self.product_image.get_image_660x880().url,
            "secondary_image": None,
        }
        self.assertEqual(
            response.json()["data"]["items"][0]["product"],
            expected_product,
        )
        self.assertEqual(
            response.json()["data"]["items"][0]["garment"],
            expected_garment,
        )


class UpdateCartItemViewTests(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser", password="testpass"
        )
        cls.category = catalog.models.Category.objects.create(
            name="Test Category"
        )
        cls.color = catalog.models.Color.objects.create(
            name="Test Color", color="#000000"
        )
        cls.garment = catalog.models.Garment.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            count=10,
            price=100,
        )
        cls.product = catalog.models.Product.objects.create(
            name="Test Product", price=100
        )
        cls.product.garments.add(cls.garment)
        cls.cart = catalog.models.Cart.objects.create(user=cls.user)
        cls.cart_item = catalog.models.CartItem.objects.create(
            cart=cls.cart, product=cls.product, garment=cls.garment
        )
        cls.cart.items.add(cls.cart_item)
        cls.authorized_client = rest_framework.test.APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)

    @classmethod
    def tearDownClass(cls):
        users.models.User.objects.all().delete()
        super().tearDownClass()

    def test_update_cart_item_view(self):
        response = self.authorized_client.patch(
            django.urls.reverse(
                "api:catalog:update-cart-item", args=[self.cart_item.id + 1]
            ),
            data={"quantity": 2},
        )
        self.assertEqual(response.status_code, http.HTTPStatus.NOT_FOUND)
        self.assertEqual(
            response.json()["message"],
            "Товар не найден в корзине",
        )

    def test_no_valid_data(self):
        response = self.authorized_client.patch(
            django.urls.reverse(
                "api:catalog:update-cart-item", args=[self.cart_item.id]
            ),
            data={"quantity": 0},
        )
        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json()["errors"]["fields"]["quantity"],
            "Некорректное количество",
        )

    def test_not_enough_garment(self):
        response = self.authorized_client.patch(
            django.urls.reverse(
                "api:catalog:update-cart-item", args=[self.cart_item.id]
            ),
            data={"quantity": 11},
        )
        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json()["errors"]["form_error"],
            "Недостаточно товара на складе",
        )

    def test_update_cart_item_view_2(self):
        before_quantity = self.cart_item.quantity
        response = self.authorized_client.patch(
            django.urls.reverse(
                "api:catalog:update-cart-item", args=[self.cart_item.id]
            ),
            data={"quantity": 2},
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.quantity, before_quantity + 1)

    def test_delete_cart_item_view(self):
        response = self.authorized_client.delete(
            django.urls.reverse(
                "api:catalog:update-cart-item", args=[self.cart_item.id]
            )
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertFalse(
            catalog.models.CartItem.objects.filter(
                id=self.cart_item.id
            ).exists()
        )


@django.test.override_settings(
    CELERY_BROKER_URL=TEST_CELERY_BROKER_URL,
    CELERY_RESULT_BACKEND=TEST_CELERY_RESULT_BACKEND,
    CELERY_ONCE=TEST_CELERY_ONCE,
)
class OrderHistoryViewTests(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser", password="testpass"
        )
        cls.category = catalog.models.Category.objects.create(
            name="Test Category"
        )
        cls.color = catalog.models.Color.objects.create(
            name="Test Color", color="#000000"
        )
        cls.garment = catalog.models.Garment.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            count=10,
            price=100,
        )
        cls.product = catalog.models.Product.objects.create(
            name="Test Product", price=100
        )
        cls.product.garments.add(cls.garment)
        cls.cart = catalog.models.Cart.objects.create(user=cls.user)
        cls.cart_item = catalog.models.CartItem.objects.create(
            cart=cls.cart, product=cls.product, garment=cls.garment
        )
        cls.cart.items.add(cls.cart_item)
        cls.authorized_client = rest_framework.test.APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)

    @classmethod
    def tearDownClass(cls):
        users.models.User.objects.all().delete()
        super().tearDownClass()

    def tearDown(self):
        host = TEST_CELERY_BROKER_URL.split("//")[1].split(":")[0]
        port = TEST_CELERY_BROKER_URL.split(":")[2].split("/")[0]
        db = TEST_CELERY_BROKER_URL.split("/")[3]
        redis_client = redis.Redis(host=host, port=port, db=db)
        redis_client.flushall()
        super().tearDown()

    def test_order_history_view(self):
        response = self.authorized_client.get(
            django.urls.reverse("api:catalog:order-history")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(
            response.json()["data"]["results"],
            [],
        )

    def test_order_history_post(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:order-history")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.CREATED)
        self.assertEqual(
            response.json()["message"],
            "Задача создания заказа запущена",
        )

    def test_order_history_view_2(self):
        order = catalog.models.Order.objects.create(
            user=self.user,
            status=catalog.models.OrderStatus.WAITING_PAYMENT,
        )
        order_item = catalog.models.OrderItem.objects.create(
            order=order,
            product=self.product,
            garment=self.garment,
            quantity=1,
            price=self.product.price + self.garment.price,
        )
        order.items.add(order_item)
        response = self.authorized_client.get(
            django.urls.reverse("api:catalog:order-history")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        expected_data = {
            "id": order.id,
            "status": {
                "status": order.status.value,
                "status_display": order.status._label_,
            },
            "total_sum": order.total_sum,
            "address": order.address,
        }
        for key, value in expected_data.items():
            self.assertEqual(response.json()["data"]["results"][0][key], value)

        expected_items = [
            {
                "id": order_item.id,
                "product": {
                    "id": self.product.id,
                    "name": self.product.name,
                    "price": self.product.price,
                    "main_image": None,
                    "secondary_image": None,
                },
                "garment": {
                    "id": self.garment.id,
                    "size": self.garment.size.value,
                    "count": self.garment.count,
                    "price": self.garment.price,
                    "category": {
                        "id": self.category.id,
                        "name": self.category.name,
                    },
                    "color": {
                        "id": self.color.id,
                        "name": self.color.name,
                        "color": self.color.color,
                    },
                },
                "quantity": order_item.quantity,
                "price": order_item.price,
                "total_price": order_item.total_price,
            }
        ]
        self.assertEqual(
            response.json()["data"]["results"][0]["items"],
            expected_items,
        )


class OrderDetailViewTests(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser", password="testpass"
        )
        cls.category = catalog.models.Category.objects.create(
            name="Test Category"
        )
        cls.color = catalog.models.Color.objects.create(
            name="Test Color", color="#000000"
        )
        cls.garment = catalog.models.Garment.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            count=10,
            price=100,
        )
        cls.product = catalog.models.Product.objects.create(
            name="Test Product", price=100
        )
        cls.product.garments.add(cls.garment)
        cls.yookassa_service = payments.services.YooKassaService()
        cls.order = catalog.models.Order.objects.create(
            user=cls.user,
            status=catalog.models.OrderStatus.WAITING_PAYMENT,
            payment_status=catalog.models.PaymentStatus.SUCCEEDED,
            address="Test Address",
            phone="+79991234567",
        )
        cls.order_item = catalog.models.OrderItem.objects.create(
            order=cls.order,
            product=cls.product,
            garment=cls.garment,
            quantity=1,
            price=cls.product.price + cls.garment.price,
        )
        cls.order.total_sum = cls.order_item.total_price
        cls.order.save()
        cls.payment_data = cls.yookassa_service.create_payment(
            order=cls.order,
            return_url=None,
        )
        cls.order.payment_id = cls.payment_data["id"]
        cls.order.confirmation_url = cls.payment_data["confirmation_url"]
        cls.order.save()

        cls.order.items.add(cls.order_item)
        cls.authorized_client = rest_framework.test.APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)

    @classmethod
    def tearDownClass(cls):
        users.models.User.objects.all().delete()
        super().tearDownClass()

    def test_order_detail_view(self):
        response = self.authorized_client.get(
            django.urls.reverse(
                "api:catalog:order-detail", args=[self.order.id]
            )
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.order.refresh_from_db()
        self.assertEqual(
            self.order.status, catalog.models.OrderStatus.WAITING_PAYMENT
        )
        self.assertEqual(
            self.order.payment_status, catalog.models.PaymentStatus.PENDING
        )
        self.assertEqual(
            self.order.confirmation_url, self.payment_data["confirmation_url"]
        )
        expected_items = [
            {
                "id": self.order_item.id,
                "product": {
                    "id": self.product.id,
                    "name": self.product.name,
                    "price": self.product.price,
                    "main_image": None,
                    "secondary_image": None,
                },
                "garment": {
                    "id": self.garment.id,
                    "size": self.garment.size.value,
                    "count": self.garment.count,
                    "price": self.garment.price,
                    "category": {
                        "id": self.category.id,
                        "name": self.category.name,
                    },
                    "color": {
                        "id": self.color.id,
                        "name": self.color.name,
                        "color": self.color.color,
                    },
                },
                "quantity": self.order_item.quantity,
                "price": self.order_item.price,
                "total_price": self.order_item.total_price,
            }
        ]
        self.assertEqual(
            response.json()["data"]["items"],
            expected_items,
        )

    def test_delete_no_valid_order(self):
        response = self.authorized_client.delete(
            django.urls.reverse(
                "api:catalog:order-detail", args=[self.order.id + 1]
            )
        )
        self.assertEqual(response.status_code, http.HTTPStatus.NOT_FOUND)

    def test_delete_order_with_status_not_waiting_payment(self):
        self.order.status = catalog.models.OrderStatus.PAID
        self.order.save()
        response = self.authorized_client.delete(
            django.urls.reverse(
                "api:catalog:order-detail", args=[self.order.id]
            )
        )
        self.assertEqual(response.status_code, http.HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json()["message"],
            "Заказ может быть отменен только в статусе ожидания оплаты",
        )

    def test_delete_valid_order(self):
        response = self.authorized_client.delete(
            django.urls.reverse(
                "api:catalog:order-detail", args=[self.order.id]
            )
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.garment.refresh_from_db()
        self.assertEqual(self.garment.count, 11)
        self.order.refresh_from_db()
        self.assertEqual(
            self.order.status, catalog.models.OrderStatus.CANCELED
        )
        self.assertEqual(
            self.order.payment_status, catalog.models.PaymentStatus.CANCELED
        )
