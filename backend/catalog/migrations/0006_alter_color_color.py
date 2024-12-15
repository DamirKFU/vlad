# Generated by Django 4.2.16 on 2024-12-14 21:40

import catalog.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0005_alter_item_count"),
    ]

    operations = [
        migrations.AlterField(
            model_name="color",
            name="color",
            field=models.CharField(
                help_text="напишите hex цвета иммет формат #008000",
                max_length=7,
                validators=[catalog.validators.HexColorValidator()],
                verbose_name="hex цвета",
            ),
        ),
    ]