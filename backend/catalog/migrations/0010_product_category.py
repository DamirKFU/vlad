# Generated by Django 4.2.16 on 2024-12-21 12:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "catalog",
            "0009_product_alter_constructorproductimage_options_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="category",
            field=models.ForeignKey(
                default=1,
                help_text="категория товара",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                related_query_name="products",
                to="catalog.category",
                verbose_name="категория",
            ),
            preserve_default=False,
        ),
    ]
