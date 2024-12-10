import re

import django.core.exceptions
import django.core.validators
import django.utils.deconstruct


@django.utils.deconstruct.deconstructible
class HexColorValidator(django.core.validators.RegexValidator):
    regex = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    message = "Enter a valid HEX color."
    flags = re.ASCII
