import re

import django.core.exceptions
import django.core.validators


@django.utils.deconstruct.deconstructible
class UsernameValidator:
    def __call__(self, username):
        if len(username) < 5 or len(username) > 32:
            raise django.core.exceptions.ValidationError(
                "Имя пользователя должно быть от 5 до 32 символов.",
                code="username_length",
            )

        if not re.match("^[a-zA-Z0-9_]+$", username):
            raise django.core.exceptions.ValidationError(
                (
                    "Имя пользователя может содержать только латинские буквы, "
                    "цифры и нижнее подчеркивание."
                ),
                code="username_invalid_chars",
            )


@django.utils.deconstruct.deconstructible
class PasswordValidator:
    def __call__(self, password):
        if len(password) < 8 or len(password) > 128:
            raise django.core.exceptions.ValidationError(
                "Пароль должен быть от 8 до 128 символов.",
                code="password_length",
            )

        if not re.match("^[a-zA-Z0-9_]+$", password):
            raise django.core.exceptions.ValidationError(
                (
                    "Пароль может содержать только латинские буквы, "
                    "цифры и нижнее подчеркивание."
                ),
                code="password_invalid_chars",
            )

        if not re.findall("[A-Z]", password):
            raise django.core.exceptions.ValidationError(
                "Пароль должен содержать хотя бы одну прописную букву.",
                code="password_uppercase",
            )

        if not re.findall("[a-z]", password):
            raise django.core.exceptions.ValidationError(
                "Пароль должен содержать хотя бы одну строчную букву.",
                code="password_lowercase",
            )

        if not re.findall("[0-9]", password):
            raise django.core.exceptions.ValidationError(
                "Пароль должен содержать хотя бы одну цифру.",
                code="password_digit",
            )
