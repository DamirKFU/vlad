# Generated by Django 4.2 on 2024-08-03 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_alter_item_options_alter_item_size"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="count",
            field=models.PositiveIntegerField(
                default=0,
                help_text="укажите количество",
                verbose_name="количество",
            ),
        ),
    ]