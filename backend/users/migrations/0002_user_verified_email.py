# Generated by Django 4.2 on 2024-08-06 06:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="verified_email",
            field=models.BooleanField(
                default=0,
                verbose_name="подтвержденный адрес электронной почты",
            ),
            preserve_default=False,
        ),
    ]