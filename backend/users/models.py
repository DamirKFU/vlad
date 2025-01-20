import django.contrib.auth.models
import django.db.models

import users.validators


class Role(django.db.models.TextChoices):
    MODERATOR = "moderator", "Модератор"
    DESIGNER = "designer", "Дизайнер"
    EMBROIDERER = "embroiderer", "Вышивальщик"
    CURIER = "courier", "Курьер"
    DEVELOPER = "developer", "Разработчик"


class UserRole(django.db.models.Model):
    role = django.db.models.CharField(
        max_length=32,
        unique=True,
        choices=Role.choices,
    )

    def __str__(self):
        return self.get_role_display()


class UserManager(django.contrib.auth.models.UserManager):
    CONONICAL_DOMAINS = {
        "yandex.ru": "ya.ru",
    }
    DOTS = {
        "ya.ry": "-",
        "gmail.com": "",
    }

    @classmethod
    def normalize_email(cls, email):
        email = super().normalize_email(email).lower()
        try:
            email_name, domain_part = email.rsplit("@", 1)
            email_name, *_ = email_name.split("+", 1)
            domain_part = cls.CONONICAL_DOMAINS.get(domain_part, domain_part)
            email_name = email_name.replace(
                ".",
                cls.DOTS.get(domain_part, "."),
            )
        except ValueError:
            pass
        else:
            email = f"{email_name}@{domain_part}"

        return email

    def by_email(self, email):
        return self.get_queryset().get(email=self.normalize_email(email))


class User(django.contrib.auth.models.AbstractUser):
    objects = UserManager()

    username = django.db.models.CharField(
        "username",
        max_length=32,
        unique=True,
        help_text="username_field_help",
        validators=[
            users.validators.UsernameValidator(),
        ],
        error_messages={
            "unique": "Пользователь с таким именем уже существует.",
        },
    )
    password = django.db.models.CharField(
        "password",
        max_length=128,
        validators=[
            users.validators.PasswordValidator(),
        ],
    )

    email = django.db.models.EmailField(
        "email address",
        unique=True,
        null=False,
        error_messages={
            "unique": "Пользователь с таким email уже существует.",
        },
    )

    verified_email = django.db.models.BooleanField(
        "подтвержденный адрес электронной почты",
        default=False,
    )
    roles = django.db.models.ManyToManyField(
        UserRole,
        verbose_name="роли",
        related_name="users",
    )
    telegram_id = django.db.models.CharField(
        "ID в Telegram",
        max_length=100,
        help_text="ID в Telegram",
        null=True,
        blank=True,
    )

    class Meta(django.contrib.auth.models.AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
