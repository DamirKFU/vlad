# Generated by Django 4.2 on 2024-08-03 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0005_alter_color_options"),
    ]

    operations = [
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
                    "name",
                    models.CharField(
                        help_text="напишите название",
                        max_length=150,
                        unique=True,
                        verbose_name="название",
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
            },
        ),
        migrations.DeleteModel(
            name="Item",
        ),
    ]
