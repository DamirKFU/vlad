import pathlib
import uuid

import django.core.validators
import django.db.models
import django.utils.safestring
import sorl.thumbnail


def get_path_image(instance, filename):
    ext = pathlib.Path(filename).suffix
    return f"catalog/image/{uuid.uuid4()}{ext}"


class BaseImageManager(django.db.models.Manager):
    def contribute_to_class(self, model, name, **kwargs):
        super().contribute_to_class(model, name, **kwargs)
        django.db.models.signals.class_prepared.connect(
            self.handle_class_prepared,
            sender=model,
        )

    def handle_class_prepared(self, sender, **kwargs):
        django.db.models.signals.pre_delete.connect(
            self.handle_pre_delete,
            sender=sender,
        )

    def handle_pre_delete(self, sender, instance, **kwargs):
        sorl.thumbnail.delete(instance.image)


class BaseImage(django.db.models.Model):
    objects = BaseImageManager()

    image = sorl.thumbnail.ImageField(
        "изображение",
        upload_to=get_path_image,
        help_text="загрузите изображение",
        validators=[
            django.core.validators.FileExtensionValidator(
                ["jpg", "jpeg", "png"]
            ),
        ],
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
        return pathlib.Path(self.image.path).stem
