import rest_framework.serializers

import support.models
import users.models


class ChatUserSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = users.models.User
        fields = [
            users.models.User.id.field.name,
            users.models.User.username.field.name,
        ]


class ChatStaffSerializer(rest_framework.serializers.ModelSerializer):
    responsible_users = ChatUserSerializer(many=True)
    user = ChatUserSerializer()

    class Meta:
        model = support.models.Chat
        fields = [
            support.models.Chat.id.field.name,
            support.models.Chat.topic.field.name,
            support.models.Chat.created_at.field.name,
            support.models.Chat.is_active.field.name,
            support.models.Chat.user.field.name,
            support.models.Chat.responsible_users.field.name,
        ]


class ChatUserInviteSerializer(rest_framework.serializers.Serializer):
    user_id = rest_framework.serializers.IntegerField()

    def validate(self, data):
        user = users.models.User.objects.filter(
            id=data["user_id"],
        ).first()
        if not user:
            raise rest_framework.exceptions.ValidationError(
                {"user_id": "Пользователь не найден"}
            )

        if self.context["chat"].responsible_users.filter(id=user.id).exists():
            raise rest_framework.exceptions.ValidationError(
                {"form_error": "Пользователь уже присоединен к чату"}
            )

        data["user"] = user

        return data

    def save(self):
        self.context["chat"].responsible_users.add(self.validated_data["user"])
        self.context["chat"].save()
        return self.validated_data["user"]
