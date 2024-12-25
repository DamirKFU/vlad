from pathlib import Path
import uuid

import django.core.validators
import django.db.models
import django.utils.safestring
import sorl.thumbnail

import catalog.validators
import users.models


def get_path_image(instance, filename):
    ext = Path(filename).suffix
    return f"catalog/{uuid.uuid4()}{ext}"


class Size(django.db.models.TextChoices):
    XS = "XS", "XS"
    S = "S", "S"
    M = "M", "M"
    L = "L", "L"
    XL = "XL", "XL"
    XXL = "XXL", "XXL"


class ConstructorProductStatus(django.db.models.TextChoices):
    IN_MODERATION = "IM", "На модерации"
    ACCEPTED = "AC", "Принято"
    REJECTED = "RJ", "Отказано"


class BaseImage(django.db.models.Model):
    image = sorl.thumbnail.ImageField(
        "изображение",
        upload_to=get_path_image,
        help_text="загрузите изображение",
    )

    def get_image_300x300(self):
        return sorl.thumbnail.get_thumbnail(
            self.image,
            "300x300",
            crop="center",
            quality=100,
        )

    def image_tmb(self):
        if self.image:
            tag = f'<img src="{self.get_image_300x300().url}">'
            return django.utils.safestring.mark_safe(tag)

        return "изображение отсутствует"

    image_tmb.short_description = "превью"
    image_tmb.allow_tags = True
    image_tmb.field_name = "image_tmb"

    class Meta:
        verbose_name = "абстрактная модель изображения"
        verbose_name_plural = "абстрактные модели изображений"
        abstract = True

    def __str__(self):
        return Path(self.image.path).stem


class AbstractModel(django.db.models.Model):
    name = django.db.models.CharField(
        "название",
        max_length=150,
        unique=True,
        help_text="напишите название",
    )

    class Meta:
        verbose_name = "абстрактная модель"
        verbose_name_plural = "абстрактные модели"
        abstract = True

    def __str__(self) -> str:
        return self.name


class Category(AbstractModel):
    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"


class Color(AbstractModel):
    color = django.db.models.CharField(
        "hex цвета",
        max_length=7,
        validators=[
            catalog.validators.HexColorValidator(),
        ],
        help_text="напишите hex цвета иммет формат #008000",
    )

    class Meta:
        verbose_name = "цвет"
        verbose_name_plural = "цвета"


class GarmentManager(django.db.models.Manager):
    def all_items(self):
        queryset = (
            super()
            .get_queryset()
            .select_related(
                Garment.category.field.name,
                Garment.color.field.name,
            )
        )
        return queryset.values(
            Garment.id.field.name,
            Garment.size.field.name,
            Garment.count.field.name,
            f"{Garment.category.field.name}__{Category.name.field.name}",
            f"{Garment.color.field.name}__{Color.name.field.name}",
            f"{Garment.color.field.name}__{Color.color.field.name}",
        )

    def items_by_category(self, category):
        return self.all_items().filter(category=category)


class Garment(django.db.models.Model):
    objects = GarmentManager()

    category = django.db.models.ForeignKey(
        Category,
        on_delete=django.db.models.CASCADE,
        verbose_name="категория",
        related_name="tshirts",
        related_query_name="tshirts",
        help_text="выберите категорию",
    )
    color = django.db.models.ForeignKey(
        Color,
        on_delete=django.db.models.CASCADE,
        verbose_name="цвет",
        related_name="tshirts",
        related_query_name="tshirts",
        help_text="выберите цвет",
    )
    size = django.db.models.CharField(
        "размер",
        choices=Size.choices,
        help_text="выберите размер",
        max_length=3,
    )

    count = django.db.models.PositiveIntegerField(
        "количество",
        help_text="укажите количество",
        default=0,
        validators=[
            django.core.validators.MinValueValidator(0),
        ],
    )
    price = django.db.models.PositiveIntegerField(
        "цена",
        help_text="цена одежды",
        default=0,
    )

    class Meta:
        verbose_name = "одежда"
        verbose_name_plural = "одежды"

        unique_together = (
            "category",
            "color",
            "size",
        )

    def __str__(self) -> str:
        return f"Футблка({self.category}, {self.color}, {self.size})"


class ConstructorProduct(django.db.models.Model):
    garment = django.db.models.ForeignKey(
        Garment,
        on_delete=django.db.models.CASCADE,
        verbose_name="одежда",
        help_text="одежда товара",
        related_name="construct_products",
        related_query_name="construct_products",
    )
    status = django.db.models.CharField(
        "статус модерации",
        choices=ConstructorProductStatus.choices,
        default=ConstructorProductStatus.IN_MODERATION,
        help_text="выберите статус",
        max_length=2,
    )
    user = django.db.models.ForeignKey(
        users.models.User,
        on_delete=django.db.models.CASCADE,
        verbose_name="пользователь",
        help_text="пользователь, отправивший запрос",
        related_name="construct_products",
        related_query_name="construct_products",
    )

    class Meta:
        verbose_name = "товар конструктора"
        verbose_name_plural = "товары конструктора"

    def __str__(self):
        return "Товар Конструктора"


class ConstructorProductImage(BaseImage):
    product = django.db.models.OneToOneField(
        ConstructorProduct,
        on_delete=django.db.models.CASCADE,
        verbose_name="товар",
        help_text="товар изображения",
        related_name="image",
        related_query_name="image",
    )

    class Meta:
        verbose_name = "изображение товара конструктора"
        verbose_name_plural = "изображения товаров конструктора"


class ConstructorEmbroideryImage(BaseImage):
    product = django.db.models.OneToOneField(
        ConstructorProduct,
        on_delete=django.db.models.CASCADE,
        verbose_name="товар",
        help_text="товар изображения",
        related_name="embroidery_image",
        related_query_name="embroidery_image",
    )

    class Meta:
        verbose_name = "изображение вышивки"
        verbose_name_plural = "изображения вышивки"


class ProductManager(django.db.models.Manager):
    def all_items(self):
        return (
            super()
            .get_queryset()
            .select_related("category")
            .prefetch_related("image")
            .only(
                "id",
                "name",
                "price",
                "category__name",
            )
        )

    def detail_view(self):
        return self.all_items().only(
            "id",
            "name",
            "price",
            "category__id",
        )


class Product(AbstractModel):
    objects = ProductManager()

    price = django.db.models.PositiveIntegerField(
        "цена",
        help_text="цена товара",
        default=0,
    )
    category = django.db.models.ForeignKey(
        Category,
        on_delete=django.db.models.CASCADE,
        verbose_name="категория",
        help_text="атегория товара",
        related_name="products",
        related_query_name="products",
    )

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"

    def __str__(self):
        return f"Товар({self.name})"


class ProductImage(BaseImage):
    product = django.db.models.OneToOneField(
        Product,
        on_delete=django.db.models.CASCADE,
        verbose_name="товар",
        help_text="товар изображения",
        related_name="image",
        related_query_name="image",
    )

    def image_tmb(self):
        if self.image:
            tag = f'<img src="{self.get_image_660x880().url}">'
            return django.utils.safestring.mark_safe(tag)

        return "изображение отсутствует"

    def get_image_660x880(self):
        return sorl.thumbnail.get_thumbnail(
            self.image,
            "660x880",
            upscale=False,
            crop=False,
            quality=100,
        )

    class Meta:
        verbose_name = "изображение товара"
        verbose_name_plural = "изображения товаров"


class CartItem(django.db.models.Model):
    product = django.db.models.ForeignKey(
        Product,
        verbose_name="товар",
        help_text="товар предмета корзины",
        on_delete=django.db.models.CASCADE,
    )
    garment = django.db.models.ForeignKey(
        Garment,
        verbose_name="одежда",
        help_text="одежда предмета корзины",
        on_delete=django.db.models.CASCADE,
    )
    quantity = django.db.models.PositiveIntegerField(
        "количество",
        help_text="количество предмета корзины",
        default=1,
        validators=[
            django.core.validators.MinValueValidator(1),
        ],
    )

    class Meta:
        verbose_name = "предмет корзины"
        verbose_name_plural = "предметы корзины"


class Cart(django.db.models.Model):
    items = django.db.models.ManyToManyField(
        CartItem,
        verbose_name="предметы корзины",
        help_text="предметы корзины",
    )
    user = django.db.models.ForeignKey(
        users.models.User,
        verbose_name="пользователь",
        help_text="пользователь корзины",
        on_delete=django.db.models.CASCADE,
        related_name="carts",
        related_query_name="carts",
    )

    class Meta:
        verbose_name = "корзина"
        verbose_name_plural = "корзины"
