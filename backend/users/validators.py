import re

import django.core.validators


@django.utils.deconstruct.deconstructible
class UsernameValidator(django.core.validators.RegexValidator):
    regex = r"^[\w_]{5,32}"
    message = "username_validation_error"
    flags = re.ASCII
