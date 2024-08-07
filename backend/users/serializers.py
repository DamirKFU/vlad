import django.conf
import django.core.signing
import django.utils.timezone
import rest_framework.serializers
import rest_framework.validators

import users.models


class UserSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = users.models.User
        fields = [
            users.models.User.id.field.name,
            users.models.User.username.field.name,
            users.models.User.email.field.name,
            users.models.User.password.field.name,
        ]
        extra_kwargs = {
            users.models.User.password.field.name: {
                "write_only": True,
            },
        }

    def create(self, validated_data):
        return users.models.User.objects.create_user(
            **validated_data,
            verified_email=django.conf.settings.DEFAULT_VERIFED_EMAIL,
        )


class EmailTokenSerializer(rest_framework.serializers.Serializer):
    token = rest_framework.serializers.CharField(
        max_length=256,
        min_length=40,
    )

    def validate(self, data):
        token_data = django.core.signing.loads(data.get("token"))
        dt = django.utils.timezone.datetime.fromordinal(token_data.get("exp"))
        td = django.utils.timezone.timedelta(seconds=3600)
        if dt + td > django.utils.timezone.datetime.now():
            raise rest_framework.validators.ValidationError(
                "token not validate"
            )

        return data
