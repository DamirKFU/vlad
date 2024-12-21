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
            ("x" * 151, False),
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
            ("Зеленый2", "#008000", True),
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
        cls.garment = catalog.models.Garment.objects.create(
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
            ("XXLL", False),
        ]
    )
    def test_item_size_validation(self, size, expected):
        category = catalog.models.Category.objects.create(
            name="Тестовая категория 2"
        )
        color = catalog.models.Color.objects.create(
            name="Красный", color="#FF0000"
        )
        garment = catalog.models.Garment(
            category=category,
            color=color,
            size=size,
            count=10,
        )
        if expected:
            try:
                garment.full_clean()
            except django.core.exceptions.ValidationError:
                self.fail("Валидный размер не проходит валидацию")
        else:
            with self.assertRaises(
                django.core.exceptions.ValidationError,
                msg="Невалидный размер проходит валидацию",
            ):
                garment.full_clean()

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
        garment = catalog.models.Garment(
            category=category,
            color=color,
            size=catalog.models.Size.M,
            count=count,
        )
        if expected:
            try:
                garment.full_clean()
            except django.core.exceptions.ValidationError:
                self.fail("Валидное количество не проходит валидацию")
        else:
            with self.assertRaises(
                django.core.exceptions.ValidationError,
                msg="Невалидное количество проходит валидацию",
            ):
                garment.full_clean()

    def test_item_str(self):
        expected = (
            f"Футблка({self.category}, {self.color}, {self.garment.size})"
        )
        self.assertEqual(
            str(self.garment),
            expected,
            "Неверное строковое представление товара",
        )

    def test_item_unique_together(self):
        with self.assertRaises(
            django.core.exceptions.ValidationError,
            msg="Валидация пропускает дубликат товара",
        ):
            duplicate_garment = catalog.models.Garment(
                category=self.category,
                color=self.color,
                size=catalog.models.Size.M,
                count=5,
            )
            duplicate_garment.full_clean()

    def test_item_manager(self):
        garments = catalog.models.Garment.objects.all_items()
        self.assertTrue(
            len(garments) > 0,
            "Менеджер не возвращает товары",
        )
        garment = garments[0]
        required_fields = {
            "id",
            "size",
            "count",
            "category__name",
            "color__name",
            "color__color",
        }
        self.assertEqual(
            set(garment.keys()),
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
        cls.garment = catalog.models.Garment.objects.create(
            category=cls.category,
            color=cls.color,
            size=catalog.models.Size.M,
            count=10,
        )
        cls.user = users.models.User.objects.create_user(username="testuser")
        cls.constructor_product = (
            catalog.models.ConstructorProduct.objects.create(
                garment=cls.garment,
                user=cls.user,
            )
        )

    @parameterized.parameterized.expand(
        [
            (catalog.models.ConstructorProductStatus.IN_MODERATION, True),
            (catalog.models.ConstructorProductStatus.ACCEPTED, True),
            (catalog.models.ConstructorProductStatus.REJECTED, True),
            ("INVALID", False),
            ("TOOLONG", False),
        ]
    )
    def test_constructor_product_status_validation(self, status, expected):
        product = catalog.models.ConstructorProduct(
            garment=self.garment, user=self.user, status=status
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
