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
        username = data["username"]
        password = data["password"]

        user = django.contrib.auth.authenticate(
            username=username, password=password
        )
        if user is None:
            raise rest_framework.serializers.ValidationError(
                {"form_error": "Пользователь не найден"}
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
                {"token": "Токен недействителен"}
            )

        user = users.models.User.objects.filter(
            id=token_data.get("user_id")
        ).first()

        if user is None:
            raise rest_framework.validators.ValidationError(
                {"form_error": "Пользователь не найден"}
            )

        data["user_id"] = token_data.get("user_id")
        return data

    def create(self, validated_data):
        users.models.User.objects.filter(
            id=validated_data.get("user_id")
        ).update(verified_email=True)


class PasswordResetRequestSerializer(rest_framework.serializers.Serializer):
    email = rest_framework.serializers.EmailField()

    def validate(self, data):
        normalized_email = users.models.UserManager.normalize_email(
            data.get("email")
        )

        user = users.models.User.objects.filter(email=normalized_email).first()
        if user is None:
            raise rest_framework.serializers.ValidationError(
                {"form_error": "Пользователь с таким email не найден."}
            )

        data["email"] = normalized_email
        data["user"] = user

        return data


class PasswordResetConfirmSerializer(rest_framework.serializers.Serializer):
    token = rest_framework.serializers.CharField()
    password = rest_framework.serializers.CharField(
        validators=[users.validators.PasswordValidator()]
    )

    def validate(self, data):
        token = data.get("token")
        try:
            token_data = django.core.signing.loads(token, max_age=3600)

        except (
            django.core.signing.BadSignature,
            django.core.signing.SignatureExpired,
        ):
            raise rest_framework.serializers.ValidationError(
                {
                    "token": (
                        "Недействительная или просроченная ссылка для сброса "
                        "пароля."
                    )
                }
            )

        user = users.models.User.objects.filter(
            id=token_data["user_id"], email=token_data["email"]
        ).first()
        if user is None:
            raise rest_framework.serializers.ValidationError(
                {"form_error": "Пользователь не найден"}
            )

        return {"user": user, "password": data.get("password")}

    def save(self):
        user = self.validated_data.get("user")
        password = self.validated_data.get("password")
        user.set_password(password)
        user.save()
