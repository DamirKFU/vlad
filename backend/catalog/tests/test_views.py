import http
import shutil
import tempfile

import django.core.files.uploadedfile
import django.test
import django.urls
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
        cls.item = catalog.models.Item.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            count=10,
        )

    def setUp(self):
        self.guest_client = rest_framework.test.APIClient()

    def test_items_list_structure(self):
        response = self.guest_client.get(
            django.urls.reverse("api:catalog:items"),
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
            self.item.size,
            data[self.category.name],
            "Размер отсутствует в ответе",
        )
        self.assertIn(
            self.color.name,
            data[self.category.name][self.item.size],
            "Цвет отсутствует в ответе",
        )

        item_data = data[self.category.name][self.item.size][self.color.name]
        self.assertEqual(
            item_data["count"],
            self.item.count,
            "Неверное количество товара",
        )
        self.assertEqual(
            item_data["hex"],
            self.color.color,
            "Неверный hex цвета",
        )
        self.assertEqual(
            item_data["id"],
            self.item.id,
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
        cls.item = catalog.models.Item.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            count=10,
        )
        cls.item_without_stock = catalog.models.Item.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.L,
            count=0,
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
                "item_id": self.item.id,
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
        initial_count = self.item.count
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:constructor-product-create"),
            {
                "item_id": self.item.id,
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

        self.item.refresh_from_db()
        self.assertEqual(
            self.item.count,
            initial_count - 1,
            "Количество товара не уменьшилось после создания",
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

    def test_create_with_zero_count(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:constructor-product-create"),
            {
                "item_id": self.item_without_stock.id,
                "image": self.test_image,
                "embroidery_image": self.test_embroidery_image,
            },
            format="multipart",
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Товар с нулевым количеством не должен создаваться",
        )

    def test_create_with_invalid_item_id(self):
        response = self.authorized_client.post(
            django.urls.reverse("api:catalog:constructor-product-create"),
            {
                "item_id": 99999,
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
                "item_id": self.item.id,
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
                "item_id": self.item.id,
                "image": self.test_image,
            },
            format="multipart",
        )
        self.assertEqual(
            response.status_code,
            http.HTTPStatus.BAD_REQUEST,
            "Создание без изображения вышивки должно возвращать ошибку",
        )
