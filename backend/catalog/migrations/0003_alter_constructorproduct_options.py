# Generated by Django 4.2.16 on 2024-12-14 06:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_constructorproduct_alter_item_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="constructorproduct",
            options={
                "verbose_name": "товар конструктора",
                "verbose_name_plural": "товары конструктора",
            },
        ),
    ]
