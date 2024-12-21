# Generated by Django 4.2.16 on 2024-12-21 11:56

import catalog.models
from django.db import migrations, models
import django.db.models.deletion
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0008_rename_item_garment_alter_garment_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
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
                    "price",
                    models.PositiveIntegerField(
                        default=0, help_text="цена товара", verbose_name="цена"
                    ),
                ),
            ],
            options={
                "verbose_name": "товар",
                "verbose_name_plural": "товары",
            },
        ),
        migrations.AlterModelOptions(
            name="constructorproductimage",
            options={
                "verbose_name": "изображение товара конструктора",
                "verbose_name_plural": "изображения товаров конструктора",
            },
        ),
        migrations.CreateModel(
            name="ProductImage",
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
                    "product",
                    models.OneToOneField(
                        help_text="товар изображения",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="image",
                        related_query_name="image",
                        to="catalog.product",
                        verbose_name="товар",
                    ),
                ),
            ],
            options={
                "verbose_name": "изображение товара",
                "verbose_name_plural": "изображения товаров",
            },
        ),
    ]