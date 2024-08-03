# Generated by Django 4.2 on 2024-08-03 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0008_alter_tshirt_unique_together"),
    ]

    operations = [
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
            ],
            options={
                "verbose_name": "вышивка",
                "verbose_name_plural": "вышивки",
            },
        ),
    ]
