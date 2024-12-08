import re

import django.core.exceptions
import django.core.validators


@django.utils.deconstruct.deconstructible
class UsernameValidator(django.core.validators.RegexValidator):
    regex = r"^(?=.{5,32}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$"
    message = "username_validation_error"
    flags = re.ASCII


class PasswordValidator:
    def __call__(self, password):
        if len(password) < 8 or len(password) > 128:
            raise django.core.exceptions.ValidationError(
                "Пароль должен быть от 8 до 128 символов.",
                code="password_length",
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

        if " " in password:
            raise django.core.exceptions.ValidationError(
                "Пароль не должен содержать пробелы.",
                code="password_no_spaces",
            )
