# Generated by Django 4.2 on 2024-08-03 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_item_count"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="size",
            field=models.CharField(
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
    ]