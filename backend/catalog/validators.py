import re

import django.core.exceptions
import django.core.validators
import django.utils.deconstruct
from rest_framework import serializers


@django.utils.deconstruct.deconstructible
class HexColorValidator(django.core.validators.RegexValidator):
    regex = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    message = "Enter a valid HEX color."
    flags = re.ASCII


def validate_file_size(file):
    max_file_size = 5 * 1024 * 1024
    if file.size > max_file_size:
        raise serializers.ValidationError(
            f"Максимальный размер файла не должен превышать "
            f"{max_file_size / (1024 * 1024)}MB"
        )

    return file
