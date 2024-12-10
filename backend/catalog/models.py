from pathlib import Path
import uuid

import django.db.models
import django.utils.safestring
import sorl.thumbnail

import catalog.validators


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
            quality=0,
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
            catalog.validators.HexColorValidator,
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
