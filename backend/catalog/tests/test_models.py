# backend/catalog/tests/test_models.py
import django.test
import parameterized.parameterized

import catalog.models
import users.models


class CategoryModelTest(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = catalog.models.Category.objects.create(
            name="Тестовая категория 1",
        )

    @parameterized.parameterized.expand(
        [
            ("Тестовая категория 2", True),
            ("", False),
            ("x" * 151, False),  # max_length=150
        ]
    )
    def test_category_name_validation(self, value, expected):
        category = catalog.models.Category(name=value)
        if expected:
            try:
                category.full_clean()
            except django.core.exceptions.ValidationError:
                self.fail("Валидная категория не проходит валидацию")
        else:
            with self.assertRaises(
                django.core.exceptions.ValidationError,
                msg="Невалидная категория проходит валидацию",
            ):
                category.full_clean()

    def test_category_str(self):
        self.assertEqual(
            str(self.category),
            "Тестовая категория 1",
            "Неверное строковое представление категории",
        )


class ColorModelTest(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.color = catalog.models.Color.objects.create(
            name="Зеленый",
            color="#008000",
        )

    @parameterized.parameterized.expand(
        [
            ("Зеленый2", "#008000", True),  # Изменили имя на уникальное
            ("", "#008000", False),
            ("x" * 151, "#008000", False),
            ("Тест1", "invalid_hex", False),
            ("Тест2", "#fff", True),
            ("Тест3", "#ffffff", True),
            ("Тест4", "ffffff", False),
        ]
    )
    def test_color_validation(self, color_name, hex_value, expected):
        color = catalog.models.Color(name=color_name, color=hex_value)
        if expected:
            try:
                color.full_clean()
            except django.core.exceptions.ValidationError:
                self.fail("Валидный цвет не проходит валидацию")
        else:
            with self.assertRaises(
                django.core.exceptions.ValidationError,
                msg=f"Невалидный цвет проходит валидацию {color_name}",
            ):
                color.full_clean()


class ItemModelTest(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = catalog.models.Category.objects.create(
            name="Тестовая категория"
        )
        cls.color = catalog.models.Color.objects.create(
            name="Зеленый", color="#008000"
        )
        cls.item = catalog.models.Item.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            count=10,
        )

    @parameterized.parameterized.expand(
        [
            (catalog.models.Size.M, True),
            (catalog.models.Size.S, True),
            (catalog.models.Size.L, True),
            (catalog.models.Size.XL, True),
            ("INVALID", False),
            ("XXLL", False),  # max_length=3
        ]
    )
    def test_item_size_validation(self, size, expected):
        category = catalog.models.Category.objects.create(
            name="Тестовая категория 2"
        )
        color = catalog.models.Color.objects.create(
            name="Красный", color="#FF0000"
        )
        item = catalog.models.Item(
            category=category,
            color=color,
            size=size,
            count=10,
        )
        if expected:
            try:
                item.full_clean()
            except django.core.exceptions.ValidationError:
                self.fail("Валидный размер не проходит валидацию")
        else:
            with self.assertRaises(
                django.core.exceptions.ValidationError,
                msg="Невалидный размер проходит валидацию",
            ):
                item.full_clean()

    @parameterized.parameterized.expand(
        [
            (10, True),
            (0, True),
            (-1, False),
        ]
    )
    def test_item_count_validation(self, count, expected):
        category = catalog.models.Category.objects.create(
            name="Тестовая категория 2"
        )
        color = catalog.models.Color.objects.create(
            name="Красный", color="#FF0000"
        )
        item = catalog.models.Item(
            category=category,
            color=color,
            size=catalog.models.Size.M,
            count=count,
        )
        if expected:
            try:
                item.full_clean()
            except django.core.exceptions.ValidationError:
                self.fail("Валидное количество не проходит валидацию")
        else:
            with self.assertRaises(
                django.core.exceptions.ValidationError,
                msg="Невалидное количество проходит валидацию",
            ):
                item.full_clean()

    def test_item_str(self):
        expected = f"Футблка({self.category}, {self.color}, {self.item.size})"
        self.assertEqual(
            str(self.item),
            expected,
            "Неверное строковое представление товара",
        )

    def test_item_unique_together(self):
        with self.assertRaises(
            django.core.exceptions.ValidationError,
            msg="Валидация пропускает дубликат товара",
        ):
            duplicate_item = catalog.models.Item(
                category=self.category,
                color=self.color,
                size=catalog.models.Size.M,
                count=5,
            )
            duplicate_item.full_clean()

    def test_item_manager(self):
        items = catalog.models.Item.objects.all_items()
        self.assertTrue(
            len(items) > 0,
            "Менеджер не возвращает товары",
        )
        item = items[0]
        required_fields = {
            "id",
            "size",
            "count",
            "category__name",
            "color__name",
            "color__color",
        }
        self.assertEqual(
            set(item.keys()),
            required_fields,
            "Менеджер возвращает неверный набор полей",
        )


class ConstructorProductModelTest(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = catalog.models.Category.objects.create(
            name="Тестовая категория"
        )
        cls.color = catalog.models.Color.objects.create(
            name="Зеленый", color="#008000"
        )
        cls.item = catalog.models.Item.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            count=10,
        )
        cls.user = users.models.User.objects.create_user(username="testuser")
        cls.constructor_product = (
            catalog.models.ConstructorProduct.objects.create(
                item=cls.item,
                user=cls.user,
            )
        )

    @parameterized.parameterized.expand(
        [
            (catalog.models.ConstructorProductStatus.IN_MODERATION, True),
            (catalog.models.ConstructorProductStatus.ACCEPTED, True),
            (catalog.models.ConstructorProductStatus.REJECTED, True),
            ("INVALID", False),
            ("TOOLONG", False),  # max_length=2
        ]
    )
    def test_constructor_product_status_validation(self, status, expected):
        product = catalog.models.ConstructorProduct(
            item=self.item, user=self.user, status=status
        )
        if expected:
            try:
                product.full_clean()
            except django.core.exceptions.ValidationError:
                self.fail("Валидный статус не проходит валидацию")
        else:
            with self.assertRaises(
                django.core.exceptions.ValidationError,
                msg="Невалидный статус проходит валидацию",
            ):
                product.full_clean()

    def test_constructor_product_str(self):
        self.assertEqual(
            str(self.constructor_product),
            "Товар Конструктора",
            "Неверное строковое представление",
        )

    def test_constructor_product_delete(self):
        initial_count = self.item.count
        self.constructor_product.delete()
        self.item.refresh_from_db()
        self.assertEqual(
            self.item.count,
            initial_count + 1,
            "Количество товара не увеличилось после удаления",
        )
