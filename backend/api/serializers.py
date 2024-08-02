import django.contrib.auth.models
import rest_framework.serializers


class UserSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = django.contrib.auth.models.User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return django.contrib.auth.models.User.objects.create_user(
            **validated_data
        )
