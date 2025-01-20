import rest_framework.serializers

import support.models


class ChatListSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = support.models.Chat
        fields = [
            support.models.Chat.id.field.name,
            support.models.Chat.topic.field.name,
            support.models.Chat.created_at.field.name,
            support.models.Chat.is_active.field.name,
        ]


class ChatCreateSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = support.models.Chat
        fields = [support.models.Chat.topic.field.name]

    def create(self, validated_data):
        user = self.context["request"].user
        return support.models.Chat.objects.create(
            user=user,
            **validated_data,
        )
