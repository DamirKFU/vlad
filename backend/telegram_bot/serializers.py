import django.core.signing
import rest_framework.exceptions
import rest_framework.serializers

import users.models


class TelegramAuthSerializer(rest_framework.serializers.Serializer):
    token = rest_framework.serializers.CharField()

    def validate_token(self, value):
        try:
            value = django.core.signing.loads(value, max_age=60)
        except (
            django.core.signing.BadSignature,
            django.core.signing.SignatureExpired,
        ):
            raise rest_framework.exceptions.ValidationError(
                "Недействительная или истекшая ссылка"
            )

        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.telegram_id = self.validated_data["token"]
        user.save(update_fields=[users.models.User.telegram_id.field.name])

        return user
