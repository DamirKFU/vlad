import http
import shutil
import tempfile

import django.core.files.uploadedfile
import django.test
import django.urls
import parameterized
import PIL
import rest_framework.test

import catalog.models
import users.models

MEDIA_ROOT = tempfile.mkdtemp()


class ItemListViewTest(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = catalog.models.Category.objects.create(
            name="Тестовая категория",
        )
        cls.color = catalog.models.Color.objects.create(
            name="Зеленый",
            color="#008000",
        )
        cls.garment = catalog.models.Garment.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            count=10,
        )

    def setUp(self):
        self.guest_client = rest_framework.test.APIClient()

    def test_items_list_structure(self):
        response = self.guest_client.get(
            django.urls.reverse("api:catalog:garments"),
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.OK,
            "Неверный код ответа",
        )

        data = response.data
        self.assertIn(
            self.category.name,
            data,
            "Категория отсутствует в ответе",
        )
        self.assertIn(
            self.garment.size,
            data[self.category.name],
            "Размер отсутствует в ответе",
        )
        self.assertIn(
            self.color.name,
            data[self.category.name][self.garment.size],
            "Цвет отсутствует в ответе",
        )

        garment_data = data[self.category.name][self.garment.size][
            self.color.name
        ]
        self.assertEqual(
            garment_data["count"],
            self.garment.count,
            "Неверное количество товара",
        )
        self.assertEqual(
            garment_data["hex"],
            self.color.color,
            "Неверный hex цвета",
        )
        self.assertEqual(
            garment_data["id"],
            self.garment.id,
            "Неверный id товара",
        )


@django.test.override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ConstructorProductCreateViewTest(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser",
            password="testpass",
        )
        cls.category = catalog.models.Category.objects.create(
            name="Тестовая категория",
        )
        cls.color = catalog.models.Color.objects.create(
            name="Зеленый",
            color="#008000",
        )
        cls.garment = catalog.models.Garment.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            count=10,
        )

    def setUp(self):
        self.guest_client = rest_framework.test.APIClient()
        self.authorized_client = rest_framework.test.APIClient()
        self.authorized_client.force_authenticate(user=self.user)

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image = PIL.Image.new("RGB", (100, 100))
            image.save(f, "PNG")
            f.seek(0)
            self.test_image = (
                django.core.files.uploadedfile.SimpleUploadedFile(
                    name="test.png", content=f.read(), content_type="image/png"
                )
            )

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            image = PIL.Image.new("RGB", (100, 100))
            image.save(f, "PNG")
            f.seek(0)
            self.test_embroidery_image = (
                django.core.files.uploadedfile.SimpleUploadedFile(
                    name="embroidery.png",
                    content=f.read(),
                    content_type="image/png",
                )
            )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_unauthorized_create(self):
        response = self.guest_client.post(
            django.urls.reverse("api:catalog:constructor-product-create"),
            {
                "garment_id": self.garment.id,
                "image": self.test_image,
                "embroidery_image": self.test_embroidery_image,
            },
            format="multipart",
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.FORBIDDEN,
            "Неавторизованный пользователь может создать товар",
        )

    def test_authorized_create(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:constructor-product-create"),
            {
                "garment_id": self.garment.id,
                "image": self.test_image,
                "embroidery_image": self.test_embroidery_image,
            },
            format="multipart",
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.CREATED,
            "Ошибка при создании товара",
        )
        self.assertIn(
            "id",
            response.data,
            "В ответе отсутствует id созданного товара",
        )

        constructor_product = catalog.models.ConstructorProduct.objects.get(
            id=response.data["id"],
        )
        self.assertTrue(
            constructor_product.image.image,
            "Изображение продукта не было сохранено",
        )
        self.assertTrue(
            constructor_product.embroidery_image.image,
            "Изображение вышивки не было сохранено",
        )

    def test_create_with_invalid_item_id(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:constructor-product-create"),
            {
                "garment_id": 99999,
                "image": self.test_image,
                "embroidery_image": self.test_embroidery_image,
            },
            format="multipart",
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.NOT_FOUND,
            "Несуществующий товар должен возвращать 404",
        )

    def test_create_without_images(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:constructor-product-create"),
            {
                "garment_id": self.garment.id,
            },
            format="multipart",
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Создание без изображений должно возвращать ошибку",
        )

    def test_create_without_embroidery_image(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:constructor-product-create"),
            {
                "garment_id": self.garment.id,
                "image": self.test_image,
            },
            format="multipart",
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.CREATED,
            "Ошибка при создании товара без изображения вышивки",
        )

        constructor_product = catalog.models.ConstructorProduct.objects.get(
            id=response.data["id"],
        )
        self.assertTrue(
            constructor_product.image.image,
            "Изображение продукта не было сохранено",
        )
        self.assertFalse(
            hasattr(constructor_product, "embroidery_image"),
            "Изображение вышивки не должно быть создано",
        )


class AddToCartViewTest(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser",
            password="testpass",
        )
        cls.category = catalog.models.Category.objects.create(
            name="Тестовая категория",
        )
        cls.color = catalog.models.Color.objects.create(
            name="Зеленый",
            color="#008000",
        )
        cls.product = catalog.models.Product.objects.create(
            name="Тестовый продукт",
            price=100,
        )
        cls.garment = catalog.models.Garment.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            price=50,
            count=10,
        )
        cls.product.garments.add(cls.garment)

    def setUp(self):
        self.guest_client = rest_framework.test.APIClient()
        self.authorized_client = rest_framework.test.APIClient()
        self.authorized_client.force_authenticate(user=self.user)

    def test_unauthorized_add_to_cart(self):
        response = self.guest_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            {
                "id_product": self.product.id,
                "id_garment": self.garment.id,
            },
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.FORBIDDEN,
            "Неавторизованный пользователь может добавить товар в корзину",
        )

    def test_add_to_cart_success(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            {
                "id_product": self.product.id,
                "id_garment": self.garment.id,
            },
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.CREATED,
            "Ошибка при добавлении товара в корзину",
        )
        self.assertEqual(
            response.data["message"],
            "Товар успешно добавлен в корзину",
            "Неверное сообщение об успешном добавлении",
        )
        self.assertEqual(
            response.data["data"]["quantity"],
            1,
            "Неверное количество товара",
        )
        self.assertEqual(
            response.data["data"]["total_price"],
            150,
            "Неверная общая стоимость",
        )

    def test_add_to_cart_invalid_product(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            {
                "id_product": 99999,
                "id_garment": self.garment.id,
            },
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Неверный код ответа при несуществующем продукте",
        )
        self.assertEqual(
            response.data["errors"]["fields"]["id_product"],
            "Продукт не найден",
            "Неверное сообщение об ошибке",
        )

    def test_add_to_cart_invalid_garment(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            {
                "id_product": self.product.id,
                "id_garment": 99999,
            },
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Неверный код ответа при несуществующей одежде",
        )
        self.assertEqual(
            response.data["errors"]["fields"]["id_garment"],
            "Одежда не найдена",
            "Неверное сообщение об ошибке",
        )

    def test_add_to_cart_garment_not_belongs_to_product(self):
        other_garment = catalog.models.Garment.objects.create(
            category=self.category,
            color=self.color,
            size=catalog.models.Size.L,
            price=50,
            count=10,
        )
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            {
                "id_product": self.product.id,
                "id_garment": other_garment.id,
            },
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Неверный код ответа при несоответствии одежды продукту",
        )
        self.assertEqual(
            response.data["errors"]["form_error"],
            "Данная одежда не принадлежит этому товару",
            "Неверное сообщение об ошибке",
        )

    def test_add_to_cart_increment_quantity(self):
        url = django.urls.reverse("api:catalog:cart-add")
        data = {
            "id_product": self.product.id,
            "id_garment": self.garment.id,
        }

        self.authorized_client.post(url, data)

        response = self.authorized_client.post(url, data)

        self.assertEqual(
            response.status_code,
            http.HTTPStatus.CREATED,
            "Неверный код ответа при повторном добавлении",
        )
        self.assertEqual(
            response.data["data"]["quantity"],
            2,
            "Неверное количество товара после повторного добавления",
        )
        self.assertEqual(
            response.data["data"]["total_price"],
            300,
            "Неверная общая стоимость после повторного добавления",
        )

    def test_add_to_cart_creates_cart_item(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            {
                "id_product": self.product.id,
                "id_garment": self.garment.id,
            },
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.CREATED,
            "Ошибка при добавлении товара в корзину",
        )

        cart = catalog.models.Cart.objects.filter(user=self.user).first()
        self.assertIsNotNone(
            cart,
            "Корзина не была создана для пользователя",
        )

        cart_item = catalog.models.CartItem.objects.filter(
            cart=cart,
            product=self.product,
            garment=self.garment,
        ).first()
        self.assertIsNotNone(
            cart_item,
            "Товар не был добавлен в корзину",
        )
        self.assertEqual(
            cart_item.quantity,
            1,
            "Неверное количество товара в корзине",
        )

    def test_add_to_cart_reuses_existing_cart(self):
        cart = catalog.models.Cart.objects.create(user=self.user)

        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            {
                "id_product": self.product.id,
                "id_garment": self.garment.id,
            },
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.CREATED,
            "Ошибка при добавлении товара в корзину",
        )

        carts_count = catalog.models.Cart.objects.filter(
            user=self.user
        ).count()
        self.assertEqual(
            carts_count,
            1,
            "Была создана новая корзина вместо использования существующей",
        )

        cart_item = catalog.models.CartItem.objects.filter(
            cart=cart,
            product=self.product,
            garment=self.garment,
        ).first()
        self.assertIsNotNone(
            cart_item,
            "Товар не был добавлен в существующую корзину",
        )

    def test_add_to_cart_updates_existing_item(self):
        cart = catalog.models.Cart.objects.create(user=self.user)
        cart_item = catalog.models.CartItem.objects.create(
            cart=cart,
            product=self.product,
            garment=self.garment,
            quantity=1,
        )

        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:cart-add"),
            {
                "id_product": self.product.id,
                "id_garment": self.garment.id,
            },
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.CREATED,
            "Ошибка при добавлении товара в корзину",
        )

        cart_item.refresh_from_db()
        self.assertEqual(
            cart_item.quantity,
            2,
            "Количество товара не было увеличено",
        )

        cart_items_count = catalog.models.CartItem.objects.filter(
            cart=cart,
            product=self.product,
            garment=self.garment,
        ).count()
        self.assertEqual(
            cart_items_count,
            1,
            "Был создан новый CartItem вместо обновления существующего",
        )


class CreateOrderViewTest(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser",
            password="testpass",
        )
        cls.category = catalog.models.Category.objects.create(
            name="Тестовая категория",
        )
        cls.color = catalog.models.Color.objects.create(
            name="Зеленый",
            color="#008000",
        )
        cls.product = catalog.models.Product.objects.create(
            name="Тестовый продукт",
            price=100,
        )
        cls.garment = catalog.models.Garment.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            price=50,
            count=10,
        )
        cls.product.garments.add(cls.garment)

    def setUp(self):
        self.guest_client = rest_framework.test.APIClient()
        self.authorized_client = rest_framework.test.APIClient()
        self.authorized_client.force_authenticate(user=self.user)

        self.cart = catalog.models.Cart.objects.create(user=self.user)
        self.cart_item = catalog.models.CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            garment=self.garment,
            quantity=2,
        )

    def test_unauthorized_create_order(self):
        response = self.guest_client.post(
            django.urls.reverse("api:catalog:create-order"),
            {
                "address": "Test Address",
                "phone": "+79991234567",
            },
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.FORBIDDEN,
            "Неавторизованный пользователь может создать заказ",
        )

    @parameterized.parameterized.expand(
        [
            ("", "+79991234567", "Это поле не может быть пустым."),
            ("Test Address", "", "Это поле не может быть пустым."),
            (
                "Test Address",
                "invalid_phone",
                "Неверный формат номера телефона",
            ),
        ]
    )
    def test_create_order_validation(self, address, phone, expected_error):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:create-order"),
            {
                "address": address,
                "phone": phone,
            },
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Неверный код ответа при невалидных данных",
        )
        self.assertIn(
            expected_error,
            str(response.data),
            "Неверное сообщение об ошибке",
        )

    def test_create_order_success(self):
        initial_garment_count = self.garment.count
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:create-order"),
            {
                "address": "Test Address",
                "phone": "+79991234567",
            },
        )

        self.assertEqual(
            response.status_code,
            http.HTTPStatus.CREATED,
            "Неверный код ответа при создании заказа",
        )
        self.assertEqual(
            response.data["message"],
            "Заказ успешно создан",
            "Неверное сообщение об успешном создании",
        )

        order = catalog.models.Order.objects.first()
        self.assertIsNotNone(order, "Заказ не был создан")
        self.assertEqual(
            order.status,
            catalog.models.OrderStatus.WAITING_PAYMENT,
            "Неверный статус заказа",
        )

        self.garment.refresh_from_db()
        self.assertEqual(
            self.garment.count,
            initial_garment_count - self.cart_item.quantity,
            "Количество товара не уменьшилось",
        )

        order_item = order.items.first()
        self.assertEqual(
            order_item.quantity,
            self.cart_item.quantity,
            "Неверное количество товара в заказе",
        )
        self.assertEqual(
            order_item.price,
            self.product.price + self.garment.price,
            "Неверная цена товара в заказе",
        )

    def test_create_order_with_existing_waiting_payment(self):
        catalog.models.Order.objects.create(
            user=self.user,
            status=catalog.models.OrderStatus.WAITING_PAYMENT,
            address="Test Address",
            phone="+79991234567",
        )

        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:create-order"),
            {
                "address": "Test Address",
                "phone": "+79991234567",
            },
        )

        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Неверный код ответа при попытке создать "
            "второй неоплаченный заказ",
        )
        self.assertEqual(
            response.data["errors"]["form_error"],
            "У вас уже есть заказ в ожидании оплаты.",
            "Неверное сообщение об ошибке",
        )

    def test_create_order_insufficient_quantity(self):
        self.garment.count = 1
        self.garment.save()

        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:create-order"),
            {
                "address": "Test Address",
                "phone": "+79991234567",
            },
        )

        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Неверный код ответа при недостаточном количестве товара",
        )
        self.assertIn(
            "Недостаточно товара",
            str(response.data["errors"]["form_error"]),
            "Неверное сообщение об ошибке",
        )

    def test_create_order_empty_cart(self):
        self.cart_item.delete()

        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:create-order"),
            {
                "address": "Test Address",
                "phone": "+79991234567",
            },
        )

        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Неверный код ответа при пустой корзине",
        )
        self.assertEqual(
            response.data["errors"]["form_error"],
            "Корзина пуста",
            "Неверное сообщение об ошибке",
        )
