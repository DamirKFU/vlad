# Generated by Django 4.2 on 2024-08-07 15:35

import catalog.models
from django.db import migrations, models
import django.db.models.deletion
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Category",
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
                    "name",
                    models.CharField(
                        help_text="напишите название",
                        max_length=150,
                        unique=True,
                        verbose_name="название",
                    ),
                ),
            ],
            options={
                "verbose_name": "категория",
                "verbose_name_plural": "категории",
            },
        ),
        migrations.CreateModel(
            name="Color",
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
                    "name",
                    models.CharField(
                        help_text="напишите название",
                        max_length=150,
                        unique=True,
                        verbose_name="название",
                    ),
                ),
            ],
            options={
                "verbose_name": "цвет",
                "verbose_name_plural": "цвета",
            },
        ),
        migrations.CreateModel(
            name="Embroidery",
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
                    "name",
                    models.CharField(
                        help_text="напишите название",
                        max_length=150,
                        unique=True,
                        verbose_name="название",
                    ),
                ),
                (
                    "main_image",
                    sorl.thumbnail.fields.ImageField(
                        help_text="загрузите изображение",
                        upload_to=catalog.models.get_path_image,
                        verbose_name="главное изображение",
                    ),
                ),
                (
                    "secondary_image",
                    sorl.thumbnail.fields.ImageField(
                        help_text="загрузите изображение",
                        upload_to=catalog.models.get_path_image,
                        verbose_name="вторичное изображение",
                    ),
                ),
            ],
            options={
                "verbose_name": "вышивка",
                "verbose_name_plural": "вышивки",
            },
        ),
        migrations.CreateModel(
            name="TShirt",
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
                    "size",
                    models.CharField(
                        choices=[
                            ("XS", "XS"),
                            ("S", "S"),
                            ("M", "M"),
                            ("L", "L"),
                            ("XL", "XL"),
                            ("XXL", "XXL"),
                        ],
                        help_text="выберите размер",
                        max_length=3,
                        verbose_name="размер",
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
                    "count",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="укажите количество",
                        verbose_name="количество",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        help_text="выберите категорию",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tshirts",
                        related_query_name="tshirts",
                        to="catalog.category",
                        verbose_name="категория",
                    ),
                ),
                (
                    "color",
                    models.ForeignKey(
                        help_text="выберите цвет",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tshirts",
                        related_query_name="tshirts",
                        to="catalog.color",
                        verbose_name="цвет",
                    ),
                ),
            ],
            options={
                "verbose_name": "футболка",
                "verbose_name_plural": "футболки",
                "unique_together": {("category", "color", "size")},
            },
        ),
    ]
