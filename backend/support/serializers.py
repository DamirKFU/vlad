import rest_framework.serializers

import support.models


class ChatSerializer(rest_framework.serializers.ModelSerializer):
    responsible_users = rest_framework.serializers.SerializerMethodField()
    user = rest_framework.serializers.SerializerMethodField()

    class Meta:
        model = support.models.Chat
        fields = [
            "id",
            "topic",
            "created_at",
            "is_active",
            "user",
            "responsible_users",
        ]

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
        }

    def get_responsible_users(self, obj):
        return [
            {
                "id": user.id,
                "username": user.username,
            }
            for user in obj.responsible_users.all()
        ]


class ChatListSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = support.models.Chat
        fields = ["id", "topic", "created_at", "is_active"]


class ChatCreateSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = support.models.Chat
        fields = ["topic"]

    def create(self, validated_data):
        user = self.context["request"].user
        return support.models.Chat.objects.create(user=user, **validated_data)
