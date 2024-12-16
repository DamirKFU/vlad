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


class ItemManager(django.db.models.Manager):
    def all_items(self):
        queryset = (
            super()
            .get_queryset()
            .select_related(
                Item.category.field.name,
                Item.color.field.name,
            )
        )
        return queryset.values(
            Item.id.field.name,
            Item.size.field.name,
            Item.count.field.name,
            f"{Item.category.field.name}__{Category.name.field.name}",
            f"{Item.color.field.name}__{Color.name.field.name}",
            f"{Item.color.field.name}__{Color.color.field.name}",
        )


class Item(django.db.models.Model):
    objects = ItemManager()

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

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"

        unique_together = (
            "category",
            "color",
            "size",
        )

    def __str__(self) -> str:
        return f"Футблка({self.category}, {self.color}, {self.size})"


class ConstructorProduct(django.db.models.Model):
    item = django.db.models.ForeignKey(
        Item,
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

    def delete(self, *args, **kwargs):
        self.item.count += 1
        self.item.save()
        super(ConstructorProduct, self).delete(*args, **kwargs)


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
        verbose_name = "изображение"
        verbose_name_plural = "изображения"


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
