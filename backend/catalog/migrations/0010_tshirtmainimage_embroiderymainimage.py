# Generated by Django 4.2 on 2024-08-03 15:45

import catalog.models
from django.db import migrations, models
import django.db.models.deletion
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0009_embroidery"),
    ]

    operations = [
        migrations.CreateModel(
            name="TShirtMainImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    sorl.thumbnail.fields.ImageField(
                        help_text="загрузите изображение",
                        upload_to=catalog.models.get_path_image,
                        verbose_name="изображение",
                    ),
                ),
                (
                    "tshirt",
                    models.OneToOneField(
                        help_text="изображение футболки",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="main_image",
                        related_query_name="main_image",
                        to="catalog.tshirt",
                        verbose_name="футболка",
                    ),
                ),
            ],
            options={
                "verbose_name": "главное изображение",
                "verbose_name_plural": "главные изображения",
            },
        ),
        migrations.CreateModel(
            name="EmbroideryMainImage",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "image",
                    sorl.thumbnail.fields.ImageField(
                        help_text="загрузите изображение",
                        upload_to=catalog.models.get_path_image,
                        verbose_name="изображение",
                    ),
                ),
                (
                    "embroidery",
                    models.OneToOneField(
                        help_text="изображение футболки",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="main_image",
                        related_query_name="main_image",
                        to="catalog.embroidery",
                        verbose_name="футболка",
                    ),
                ),
            ],
            options={
                "verbose_name": "главное изображение",
                "verbose_name_plural": "главные изображения",
            },
        ),
    ]
