import django.contrib.auth.backends


import users.models


class EmailUsernameBackend(django.contrib.auth.backends.ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if "@" not in username:
                user = users.models.User.objects.get_by_natural_key(
                    username=username,
                )
            else:
                user = users.models.User.objects.by_email(username)
        except users.models.User.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None
