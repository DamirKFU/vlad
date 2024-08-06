import re

import django.core.validators


@django.utils.deconstruct.deconstructible
class UsernameValidator(django.core.validators.RegexValidator):
    regex = r"^(?=.{5,32}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$"
    message = "username_validation_error"
    flags = re.ASCII
