import django.conf
import django.contrib.auth
import django.core.signing
import django.utils.timezone
import rest_framework.serializers
import rest_framework.validators

import users.models
import users.validators


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

    def validate_email(self, value):
        normalized_email = users.models.UserManager.normalize_email(value)
        if users.models.User.objects.filter(email=normalized_email).exists():
            raise rest_framework.serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )

        return value

    def create(self, validated_data):
        return users.models.User.objects.create_user(
            **validated_data,
            verified_email=django.conf.settings.DEFAULT_VERIFED_EMAIL,
        )


class LoginSerializer(rest_framework.serializers.Serializer):
    username = rest_framework.serializers.CharField(
        required=True,
        max_length=32,
        min_length=5,
    )
    password = rest_framework.serializers.CharField(
        required=True,
        write_only=True,
        max_length=128,
        min_length=8,
    )

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = django.contrib.auth.authenticate(
            username=username, password=password
        )
        if user is None:
            raise rest_framework.serializers.ValidationError(
                {"non_field_errors": ["Пользователь не найден"]}
            )

        return {"user": user}


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


class PasswordResetRequestSerializer(rest_framework.serializers.Serializer):
    email = rest_framework.serializers.EmailField()

    def validate_email(self, value):
        normalized_email = users.models.UserManager.normalize_email(value)
        try:
            users.models.User.objects.get(email=normalized_email)
        except users.models.User.DoesNotExist:
            raise rest_framework.serializers.ValidationError(
                "Пользователь с таким email не найден."
            )

        return normalized_email


class PasswordResetConfirmSerializer(rest_framework.serializers.Serializer):
    token = rest_framework.serializers.CharField()
    password = rest_framework.serializers.CharField(
        validators=[users.validators.PasswordValidator()]
    )

    def validate_token(self, value):
        try:
            return django.core.signing.loads(value, max_age=3600)
        except (
            django.core.signing.BadSignature,
            django.core.signing.SignatureExpired,
        ):
            raise rest_framework.serializers.ValidationError(
                "Недействительная или просроченная ссылка для сброса пароля."
            )
