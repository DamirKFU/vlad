import shutil

import django.conf
import django.core.files.uploadedfile
import django.db
import django.test
import parameterized.parameterized

import catalog.models
import users.models


TEST_MEDIA_ROOT = django.conf.settings.BASE_DIR / "test_media"


class TestCategoryModel(django.test.TestCase):
    @parameterized.parameterized.expand(
        [
            "Тест",
            "Т" * 150,
        ]
    )
    def test_access_add_category(self, name):
        catalog_item = catalog.models.Category(
            name=name,
        )
        catalog_item.full_clean()
        catalog_item.save()

    @parameterized.parameterized.expand(
        [
            "",
            "Т" * 151,
        ]
    )
    def test_error_add_category(self, name):
        catalog_item = catalog.models.Category(
            name=name,
        )
        with self.assertRaises(django.core.exceptions.ValidationError):
            catalog_item.full_clean()
            catalog_item.save()

    def test_unique_category(self):
        category_1 = catalog.models.Category(
            name="Тест",
        )
        category_1.full_clean()
        category_1.save()

        with self.assertRaises(django.core.exceptions.ValidationError):
            category_2 = catalog.models.Category(
                name="Тест",
            )
            category_2.full_clean()
            category_2.save()


class TestColorModel(django.test.TestCase):
    @parameterized.parameterized.expand(
        [
            "#008000",
            "#008000",
            "#ffffff",
        ]
    )
    def test_access_add_color(self, color):
        color = catalog.models.Color(
            name="Тест",
            color=color,
        )
        color.full_clean()
        color.save()

    @parameterized.parameterized.expand(
        [
            "test",
            "#008@000",
            "#f#fffff",
        ]
    )
    def test_error_add_color(self, color):
        color = catalog.models.Color(
            name="Тест",
            color=color,
        )
        with self.assertRaises(django.core.exceptions.ValidationError):
            color.full_clean()
            color.save()


class TestGarmentModel(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = catalog.models.Category.objects.create(
            name="Тестовая категория",
        )
        cls.color = catalog.models.Color.objects.create(
            name="Тестовый цвет",
            color="#008000",
        )

    @parameterized.parameterized.expand(
        [
            (catalog.models.Size.M, 10, 100, True),
            (catalog.models.Size.S, 10, 100, True),
            (catalog.models.Size.L, 10, 100, True),
            (catalog.models.Size.XL, 10, 100, True),
            ("INVALID", 10, 100, False),
            ("XXLL", 10, 100, False),
            (catalog.models.Size.M, 0, 100, True),
            (catalog.models.Size.M, 0, 0, True),
            (catalog.models.Size.M, -1, 100, False),
            (catalog.models.Size.M, 10, -1, False),
        ]
    )
    def test_access_add_garment(self, size, count, price, expected):
        garment = catalog.models.Garment(
            category=self.category,
            color=self.color,
            size=size,
            count=count,
            price=price,
        )
        if expected:
            garment.full_clean()
            garment.save()
        else:
            with self.assertRaises(django.core.exceptions.ValidationError):
                garment.full_clean()
                garment.save()

    def test_unique_garment(self):
        garment_1 = catalog.models.Garment(
            category=self.category,
            color=self.color,
            size=catalog.models.Size.M,
            count=10,
            price=100,
        )
        garment_1.full_clean()
        garment_1.save()

        with self.assertRaises(django.core.exceptions.ValidationError):
            garment_2 = catalog.models.Garment(
                category=self.category,
                color=self.color,
                size=catalog.models.Size.M,
                count=10,
                price=100,
            )
            garment_2.full_clean()
            garment_2.save()


@django.test.override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class TestProductModel(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = catalog.models.Category.objects.create(
            name="Тестовая категория",
        )
        cls.color = catalog.models.Color.objects.create(
            name="Тестовый цвет",
            color="#008000",
        )
        cls.garment = catalog.models.Garment.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            count=10,
            price=100,
        )
        cls.user = users.models.User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        cls.embroidery_jef = django.core.files.uploadedfile.SimpleUploadedFile(
            name="test.jef",
            content=b"test",
            content_type="application/octet-stream",
        )
        cls.embroidery_png = django.core.files.uploadedfile.SimpleUploadedFile(
            name="test.png",
            content=b"test",
            content_type="image/png",
        )
        cls.image = django.core.files.uploadedfile.SimpleUploadedFile(
            name="test.jpg",
            content=b"test",
            content_type="image/jpeg",
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
        users.models.User.objects.all().delete()
        super().tearDownClass()

    @parameterized.parameterized.expand(
        [
            (100, True),
            (0, True),
            (-1, False),
        ]
    )
    def test_price_add_product(self, price, expected):
        product = catalog.models.Product(
            price=price,
            name="Тестовый товар",
            embroidery=self.embroidery_jef,
        )
        if expected:
            product.full_clean()
            product.save()
        else:
            with self.assertRaises(django.core.exceptions.ValidationError):
                product.full_clean()
                product.save()

    def test_unique_product(self):
        product_1 = catalog.models.Product(
            price=100,
            name="Тестовый товар",
            embroidery=self.embroidery_jef,
        )
        product_1.full_clean()
        product_1.save()

        with self.assertRaises(django.core.exceptions.ValidationError):
            product_2 = catalog.models.Product(
                price=100,
                name="Тестовый товар",
            )
            product_2.full_clean()
            product_2.save()

    def test_embroidery_add_product(self):
        product = catalog.models.Product(
            price=100,
            name="Тестовый товар",
            embroidery=self.embroidery_jef,
        )
        product_2 = catalog.models.Product(
            price=100,
            name="Тестовый товар",
            embroidery=self.embroidery_png,
        )
        product.full_clean()
        product.save()

        with self.assertRaises(django.core.exceptions.ValidationError):
            product_2.full_clean()
            product_2.save()

    def test_image_access_add_product(self):
        product = catalog.models.Product(
            price=100,
            name="Тестовый товар",
            embroidery=self.embroidery_jef,
        )
        product.full_clean()
        product.save()

        product_image = catalog.models.ProductMainImage(
            product=product,
            image=self.image,
        )
        product_image.full_clean()
        product_image.save()

        product_additional_image = catalog.models.ProductAdditionalImage(
            product=product,
            image=self.image,
            color=self.color,
            category=self.category,
        )
        product_additional_image.full_clean()
        product_additional_image.save()

    def test_image_error_add_product(self):
        product = catalog.models.Product(
            price=100,
            name="Тестовый товар",
            embroidery=self.embroidery_jef,
        )
        product.full_clean()
        product.save()

        product_image = catalog.models.ProductMainImage(
            product=product,
            image=self.embroidery_jef,
        )
        with self.assertRaises(django.core.exceptions.ValidationError):
            product_image.full_clean()
            product_image.save()

        product_additional_image = catalog.models.ProductAdditionalImage(
            product=product,
            image=self.embroidery_jef,
            color=self.color,
        )

        with self.assertRaises(django.core.exceptions.ValidationError):
            product_additional_image.full_clean()
            product_additional_image.save()


class CartModelTest(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser",
            password="testpassword",
        )

    @classmethod
    def tearDownClass(cls):
        users.models.User.objects.all().delete()
        super().tearDownClass()

    def test_access_add_cart(self):
        cart = catalog.models.Cart(
            user=self.user,
        )
        cart.full_clean()
        cart.save()


class CartItemModelTest(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        cls.cart = catalog.models.Cart.objects.create(
            user=cls.user,
        )
        cls.category = catalog.models.Category.objects.create(
            name="Тестовая категория",
        )
        cls.product = catalog.models.Product.objects.create(
            price=100,
            name="Тестовый товар",
        )
        cls.color = catalog.models.Color.objects.create(
            name="Тестовый цвет",
            color="#008000",
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
        super().tearDownClass()

    @parameterized.parameterized.expand(
        [
            (1, True),
            (0, False),
            (-1, False),
        ]
    )
    def test_quantity_add_cart_item(self, quantity, expected):
        cart_item = catalog.models.CartItem(
            product=self.product,
            cart=self.cart,
            garment=self.garment,
            quantity=quantity,
        )
        if expected:
            cart_item.full_clean()
            cart_item.save()
        else:
            with self.assertRaises(django.core.exceptions.ValidationError):
                cart_item.full_clean()
                cart_item.save()

    def test_total_price_cart_item(self):
        cart_item = catalog.models.CartItem(
            product=self.product,
            cart=self.cart,
            garment=self.garment,
            quantity=2,
        )
        self.assertEqual(cart_item.total_price, 400)


class OrderModelTest(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        cls.phone = "+79999999999"
        cls.address = "Тестовый адрес"

    @classmethod
    def tearDownClass(cls):
        users.models.User.objects.all().delete()
        super().tearDownClass()

    def test_access_add_order(self):
        order = catalog.models.Order(
            user=self.user,
            phone=self.phone,
            address=self.address,
        )
        order.full_clean()
        order.save()

    @parameterized.parameterized.expand(
        [
            ("+79631231248", True),
            ("89631231248", True),
            ("+7999", False),
            ("19999999999", False),
            ("", False),
        ]
    )
    def test_phone_validation(self, phone, expected):
        order = catalog.models.Order(
            user=self.user,
            phone=phone,
            address=self.address,
        )
        if expected:
            order.full_clean()
            order.save()
        else:
            with self.assertRaises(django.core.exceptions.ValidationError):
                order.full_clean()
                order.save()

    @parameterized.parameterized.expand(
        [
            ("Тестовый адрес", True),
            ("", False),
            ("x" * 256, False),
            ("x" * 255, True),
        ]
    )
    def test_address_validation(self, address, expected):
        order = catalog.models.Order(
            user=self.user,
            phone=self.phone,
            address=address,
        )
        if expected:
            order.full_clean()
            order.save()
        else:
            with self.assertRaises(django.core.exceptions.ValidationError):
                order.full_clean()
                order.save()

    def test_unique_order(self):
        order_1 = catalog.models.Order(
            user=self.user,
            phone=self.phone,
            address=self.address,
            status=catalog.models.OrderStatus.WAITING_PAYMENT,
        )
        order_2 = catalog.models.Order(
            user=self.user,
            phone=self.phone,
            address=self.address,
            status=catalog.models.OrderStatus.WAITING_PAYMENT,
        )
        order_1.full_clean()
        order_1.save()

        with self.assertRaises(django.core.exceptions.ValidationError):
            order_2.full_clean()
            order_2.save()

        order_1.status = catalog.models.OrderStatus.IN_DELIVERY
        order_1.save()

        order_2.full_clean()
        order_2.save()

    def test_delete_order(self):
        order = catalog.models.Order(
            user=self.user,
            phone=self.phone,
            address=self.address,
            status=catalog.models.OrderStatus.WAITING_PAYMENT,
        )
        order.full_clean()
        order.save()
        with self.assertRaises(django.core.exceptions.ValidationError):
            order.delete()

        order.cancel_order()
        self.assertEqual(order.status, catalog.models.OrderStatus.CANCELED)


class OrderItemModelTest(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        cls.phone = "+79999999999"
        cls.address = "Тестовый адрес"
        cls.order = catalog.models.Order.objects.create(
            user=cls.user,
            phone=cls.phone,
            address=cls.address,
        )
        cls.category = catalog.models.Category.objects.create(
            name="Тестовая категория",
        )
        cls.product = catalog.models.Product.objects.create(
            price=100,
            name="Тестовый товар",
        )
        cls.color = catalog.models.Color.objects.create(
            name="Тестовый цвет",
            color="#008000",
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
        super().tearDownClass()

    def test_access_add_order_item(self):
        order_item = catalog.models.OrderItem(
            order=self.order,
            product=self.product,
            garment=self.garment,
            quantity=1,
            price=100,
        )
        order_item.full_clean()
        order_item.save()

    def test_total_price_order_item(self):
        order_item = catalog.models.OrderItem(
            order=self.order,
            product=self.product,
            garment=self.garment,
            quantity=2,
            price=100,
        )
        order_item.full_clean()
        order_item.save()
        self.assertEqual(order_item.total_price, 200)

    def test_delete_order_item(self):
        order_item = catalog.models.OrderItem(
            order=self.order,
            product=self.product,
            garment=self.garment,
            quantity=2,
            price=100,
        )
        order_item.full_clean()
        order_item.save()
        self.order.cancel_order()
        self.garment.refresh_from_db()
        self.assertEqual(order_item.garment.count, 12)
