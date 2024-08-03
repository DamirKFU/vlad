from pathlib import Path
import uuid

import django.db.models
import django.utils.safestring
import sorl


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
    class Meta:
        verbose_name = "цвет"
        verbose_name_plural = "цвета"


class TShirt(django.db.models.Model):
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
        verbose_name = "футболка"
        verbose_name_plural = "футболки"

        unique_together = (
            "category",
            "color",
            "size",
        )

    def __str__(self) -> str:
        return f"Футблка({self.category}, {self.color}, {self.size})"


class Embroidery(AbstractModel):
    class Meta:
        verbose_name = "вышивка"
        verbose_name_plural = "вышивки"


class TShirtMainImage(BaseImage):
    tshirt = django.db.models.OneToOneField(
        TShirt,
        on_delete=django.db.models.CASCADE,
        verbose_name="футболка",
        help_text="изображение футболки",
        related_name="main_image",
        related_query_name="main_image",
    )

    class Meta:
        verbose_name = "главное изображение"
        verbose_name_plural = "главные изображения"


class EmbroideryMainImage(BaseImage):
    embroidery = django.db.models.OneToOneField(
        Embroidery,
        on_delete=django.db.models.CASCADE,
        verbose_name="футболка",
        help_text="изображение вышивки на футболке",
        related_name="main_image",
        related_query_name="main_image",
    )

    class Meta:
        verbose_name = "главное изображение"
        verbose_name_plural = "главные изображения"


class EmbroiderySecondaryImage(BaseImage):
    embroidery = django.db.models.OneToOneField(
        Embroidery,
        on_delete=django.db.models.CASCADE,
        verbose_name="футболка",
        help_text="изображение вишивки",
        related_name="secondary_image",
        related_query_name="secondary_image",
    )

    class Meta:
        verbose_name = "вторичное изображение"
        verbose_name_plural = "вторичные изображения"
