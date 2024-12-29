import http
import shutil
import tempfile
import unittest.mock

import django.core.files.uploadedfile
import django.test
import django.urls
import parameterized
import PIL
import rest_framework.test

import catalog.models
import users.models
import catalog.tasks

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

        data = response.data["data"]
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
            response.data["data"],
            "В ответе отсутствует id созданного товара",
        )

        constructor_product = catalog.models.ConstructorProduct.objects.get(
            id=response.data["data"]["id"],
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
            http.HTTPStatus.BAD_REQUEST,
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
            id=response.data["data"]["id"],
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


@django.test.override_settings(MEDIA_ROOT=MEDIA_ROOT)
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
            name="Test Product",
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

    @unittest.mock.patch("catalog.tasks.create_order_task.delay")
    def test_create_order_success(self, mock_task):
        mock_task.return_value.id = "test_task_id"

        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:create-order"),
            {
                "address": "Test Address",
                "phone": "+79991234567",
            },
        )

        self.assertEqual(
            response.status_code,
            201,
            "Неверный код ответа при создании заказа",
        )
        self.assertEqual(
            response.data["data"]["task_id"],
            "test_task_id",
            "Неверный task_id в ответе",
        )

        mock_task.assert_called_once()
        call_args = mock_task.call_args[1]
        self.assertEqual(call_args["user_id"], self.user.id)
        self.assertEqual(call_args["data"]["address"], "Test Address")
        self.assertEqual(call_args["data"]["phone"], "+79991234567")

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
            403,
            "Неавторизованный пользователь может создать заказ",
        )


class CartViewTest(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(
            username="testuser", password="testpass"
        )
        cls.category = catalog.models.Category.objects.create(
            name="Тестовая категория"
        )
        cls.color = catalog.models.Color.objects.create(
            name="Зеленый", color="#008000"
        )
        cls.product = catalog.models.Product.objects.create(
            name="Тестовый продукт", price=100
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

    def test_unauthorized_get_cart(self):
        response = self.guest_client.get(
            django.urls.reverse("api:catalog:cart")
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.FORBIDDEN,
            "Неавторизованный пользователь может получить корзину",
        )

    def test_get_cart_success(self):
        response = self.authorized_client.get(
            django.urls.reverse("api:catalog:cart")
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.OK,
            "Неверный код ответа при получении корзины",
        )
        self.assertEqual(
            response.data["message"],
            "Корзина успешно получена",
            "Неверное сообщение об успешном получении",
        )

        cart_data = response.data["data"][0]
        expected_fields = {
            "id",
            "name",
            "category",
            "color",
            "size",
            "quantity",
            "available_quantity",
            "price",
            "total_price",
            "image",
        }
        self.assertEqual(
            set(cart_data.keys()),
            expected_fields,
            "Неверный набор полей в ответе",
        )
        self.assertEqual(
            cart_data["name"], self.product.name, "Неверное имя продукта"
        )
        self.assertEqual(
            cart_data["category"], self.category.name, "Неверная категория"
        )
        self.assertEqual(cart_data["color"], self.color.color, "Неверный цвет")
        self.assertEqual(
            cart_data["size"], self.garment.size, "Неверный размер"
        )
        self.assertEqual(
            cart_data["quantity"],
            self.cart_item.quantity,
            "Неверное количество",
        )
        self.assertEqual(
            cart_data["available_quantity"],
            self.garment.count,
            "Неверное доступное количество",
        )
        self.assertEqual(
            cart_data["price"],
            self.product.price + self.garment.price,
            "Неверная цена",
        )
        self.assertEqual(
            cart_data["total_price"],
            (self.product.price + self.garment.price)
            * self.cart_item.quantity,
            "Неверная общая стоимость",
        )

    def test_get_empty_cart(self):
        self.cart_item.delete()
        response = self.authorized_client.get(
            django.urls.reverse("api:catalog:cart")
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.OK,
            "Неверный код ответа при пустой корзине",
        )
        self.assertEqual(
            len(response.data["data"]),
            0,
            "Пустая корзина должна возвращать пустой список",
        )

    def test_cart_not_found(self):
        self.cart.delete()
        response = self.authorized_client.get(
            django.urls.reverse("api:catalog:cart")
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Отсутствующая корзина должна возвращать 400",
        )

    def test_update_cart_item_quantity_validation(self):
        test_cases = [
            ("", "Некорректное количество"),
            ("0", "Некорректное количество"),
            ("-1", "Некорректное количество"),
            ("abc", "Некорректное количество"),
        ]

        for quantity, expected_error in test_cases:
            with self.subTest(quantity=quantity):
                response = self.authorized_client.patch(
                    django.urls.reverse("api:catalog:update-cart-item"),
                    {
                        "item_id": self.cart_item.id,
                        "quantity": quantity,
                    },
                )
                self.assertEqual(
                    response.status_code,
                    http.HTTPStatus.BAD_REQUEST,
                    "Неверный код ответа при невалидном количестве",
                )
                self.assertEqual(
                    response.data["errors"]["fields"]["quantity"],
                    expected_error,
                    "Неверное сообщение об ошибке",
                )

    def test_update_nonexistent_cart_item(self):
        response = self.authorized_client.patch(
            django.urls.reverse("api:catalog:update-cart-item"),
            {
                "item_id": 99999,
                "quantity": 2,
            },
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Неверный код ответа при обновлении несуществующего товара",
        )
        self.assertEqual(
            response.data["errors"]["form_error"],
            "Товар не найден в корзине",
            "Неверное сообщение об ошибке",
        )

    def test_delete_nonexistent_cart_item(self):
        response = self.authorized_client.delete(
            django.urls.reverse("api:catalog:update-cart-item"),
            {"item_id": 99999},
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Неверный код ответа при удалении несуществующего товара",
        )
        self.assertEqual(
            response.data["errors"]["form_error"],
            "Товар не найден в корзине",
            "Неверное сообщение об ошибке",
        )

    def test_delete_cart_item_validation(self):
        response = self.authorized_client.delete(
            django.urls.reverse("api:catalog:update-cart-item"),
            {},
            content_type="application/json",
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Неверный код ответа при отсутствии item_id",
        )
        self.assertEqual(
            response.data["errors"]["fields"]["item_id"],
            "Обязательное поле.",
            "Неверное сообщение об ошибке",
        )

    def test_delete_nonexistent_cart_item_bulk(self):
        response = self.authorized_client.delete(
            django.urls.reverse("api:catalog:update-cart-item"),
            {"item_id": 99999},
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Неверный код ответа при удалении несуществующего товара",
        )

        self.assertEqual(
            response.data["errors"]["form_error"],
            "Товар не найден в корзине",
            "Неверное сообщение об ошибке",
        )

    def test_get_cart_without_cart(self):
        self.cart.delete()
        response = self.authorized_client.get(
            django.urls.reverse("api:catalog:cart")
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Неверный код ответа при отсутствии корзины",
        )
        self.assertEqual(
            response.data["errors"]["form_error"],
            "Корзина не найдена",
            "Неверное сообщение об ошибке",
        )

    @parameterized.parameterized.expand(
        [
            (2, True, "Количество успешно обновлено"),
            (10, True, "Максимальное доступное количество"),
            (11, False, "Превышение доступного количества"),
        ]
    )
    def test_update_cart_item_quantity(
        self, new_quantity, should_succeed, test_name
    ):
        initial_quantity = self.cart_item.quantity
        response = self.authorized_client.patch(
            django.urls.reverse("api:catalog:update-cart-item"),
            {
                "item_id": self.cart_item.id,
                "quantity": new_quantity,
            },
        )

        if should_succeed:
            self.assertEqual(
                response.status_code,
                http.HTTPStatus.OK,
                f"Неверный код ответа при {test_name}",
            )
            self.cart_item.refresh_from_db()
            self.assertEqual(
                self.cart_item.quantity,
                new_quantity,
                f"Количество товара не обновилось при {test_name}",
            )
            self.assertEqual(
                response.data["data"]["quantity"],
                new_quantity,
                f"Неверное количество в ответе при {test_name}",
            )
            self.assertEqual(
                response.data["data"]["total_price"],
                (self.product.price + self.garment.price) * new_quantity,
                f"Неверная общая стоимость в ответе при {test_name}",
            )
        else:
            self.assertEqual(
                response.status_code,
                http.HTTPStatus.BAD_REQUEST,
                f"Неверный код ответа при {test_name}",
            )
            self.cart_item.refresh_from_db()
            self.assertEqual(
                self.cart_item.quantity,
                initial_quantity,
                f"Количество товара изменилось при {test_name}",
            )
            self.assertEqual(
                response.data["errors"]["form_error"],
                "Недостаточно товара на складе",
                f"Неверное сообщение об ошибке при {test_name}",
            )


class OrderHistoryViewTest(django.test.TestCase):
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

        self.order = catalog.models.Order.objects.create(
            user=self.user,
            status=catalog.models.OrderStatus.WAITING_PAYMENT,
            address="Test Address",
            phone="+79991234567",
        )
        self.order_item = catalog.models.OrderItem.objects.create(
            order=self.order,
            product=self.product,
            garment=self.garment,
            quantity=2,
            price=self.product.price + self.garment.price,
        )

    def test_unauthorized_get_orders(self):
        response = self.guest_client.get(
            django.urls.reverse("api:catalog:order-history")
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.FORBIDDEN,
            "Неавторизованный пользователь может получить заказы",
        )

    def test_get_orders_success(self):
        response = self.authorized_client.get(
            django.urls.reverse("api:catalog:order-history")
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.OK,
            "Неверный код ответа при получении заказов",
        )

        data = response.data["data"]
        self.assertEqual(
            data["count"],
            1,
            "Неверное количество заказов",
        )
        order_data = data["results"][0]
        self.assertEqual(
            order_data["status"],
            self.order.status,
            "Неверный статус заказа",
        )
        self.assertEqual(
            order_data["address"],
            self.order.address,
            "Неверный адрес заказа",
        )

        item_data = order_data["items"][0]
        self.assertEqual(
            item_data["name"],
            self.product.name,
            "Неверное имя продукта",
        )
        self.assertEqual(
            item_data["category"],
            self.category.name,
            "Неверная категория",
        )
        self.assertEqual(
            item_data["color"],
            self.color.color,
            "Неверный цвет",
        )
        self.assertEqual(
            item_data["size"],
            self.garment.size,
            "Неверный размер",
        )
        self.assertEqual(
            item_data["quantity"],
            self.order_item.quantity,
            "Неверное количество",
        )
        self.assertEqual(
            item_data["price"],
            self.order_item.price,
            "Неверная цена",
        )

    @parameterized.parameterized.expand(
        [
            (
                catalog.models.OrderStatus.WAITING_PAYMENT,
                True,
                "Отмена заказа в ожидании оплаты",
            ),
            (
                catalog.models.OrderStatus.PAID,
                False,
                "Попытка отменить оплаченный заказ",
            ),
            (
                catalog.models.OrderStatus.IN_DELIVERY,
                False,
                "Попытка отменить заказ в доставке",
            ),
            (
                catalog.models.OrderStatus.DELIVERED,
                False,
                "Попытка отменить доставленный заказ",
            ),
            (
                catalog.models.OrderStatus.CANCELED,
                False,
                "Попытка отменить отмененный заказ",
            ),
        ]
    )
    def test_cancel_order(self, status, should_succeed, test_name):
        self.order.status = status
        self.order.save()

        initial_garment_count = self.garment.count
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:order-history"),
            {"order_id": self.order.id},
        )

        if should_succeed:
            self.assertEqual(
                response.status_code,
                http.HTTPStatus.OK,
                f"Неверный код ответа при {test_name}",
            )
            self.assertEqual(
                response.data["message"],
                "Заказ успешно отменен",
                f"Неверное сообщение при {test_name}",
            )
            self.order.refresh_from_db()
            self.assertEqual(
                self.order.status,
                catalog.models.OrderStatus.CANCELED,
                f"Статус заказа не изменился при {test_name}",
            )
            self.garment.refresh_from_db()
            self.assertEqual(
                self.garment.count,
                initial_garment_count + self.order_item.quantity,
                f"Количество товара не увеличилось при {test_name}",
            )
        else:
            self.assertEqual(
                response.status_code,
                http.HTTPStatus.BAD_REQUEST,
                f"Неверный код ответа при {test_name}",
            )
            self.assertEqual(
                response.data["errors"]["form_error"],
                "Заказ не найден или не может быть отменен",
                f"Неверное сообщение об ошибке при {test_name}",
            )
            self.garment.refresh_from_db()
            self.assertEqual(
                self.garment.count,
                initial_garment_count,
                f"Количество товара изменилось при {test_name}",
            )

    def test_cancel_nonexistent_order(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:order-history"),
            {"order_id": 99999},
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Неверный код ответа при отмене несуществующего заказа",
        )
        self.assertEqual(
            response.data["errors"]["form_error"],
            "Заказ не найден или не может быть отменен",
            "Неверное сообщение об ошибке",
        )

    def test_cancel_order_validation(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:order-history"),
            {},
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Неверный код ответа при отсутствии order_id",
        )
        self.assertEqual(
            response.data["errors"]["fields"]["order_id"],
            "Обязательное поле.",
            "Неверное сообщение об ошибке",
        )
