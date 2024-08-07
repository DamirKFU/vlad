import django.contrib.auth.models
import django.db.models

import users.validators


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
            "unique": "A user with that username already exists.",
        },
    )

    email = django.db.models.EmailField(
        "email address",
        blank=True,
        unique=True,
    )

    verified_email = django.db.models.BooleanField(
        "подтвержденный адрес электронной почты",
        default=False,
    )

    class Meta(django.contrib.auth.models.AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
