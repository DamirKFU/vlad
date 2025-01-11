import rest_framework.serializers

import support.models


class ChatSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = support.models.Chat
        fields = ["topic"]

    def create(self, validated_data):
        user = self.context["request"].user
        return support.models.Chat.objects.create(user=user, **validated_data)
