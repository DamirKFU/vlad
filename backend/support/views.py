import django.db.transaction
import rest_framework.generics
import rest_framework.permissions
import rest_framework.views

import core.utils
import support.models
import support.serializers


class CreateChatView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)
    serializer_class = support.serializers.ChatCreateSerializer

    @django.db.transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return core.utils.response_error(
                message="Ошибка валидации",
                data=serializer.errors,
            )

        serializer.save()
        return core.utils.response_success(
            message="Чат создан",
            data=serializer.data,
        )


class ChatListView(rest_framework.generics.ListAPIView):
    permission_classes = (rest_framework.permissions.AllowAny,)
    serializer_class = support.serializers.ChatListSerializer

    def get_queryset(self):
        return support.models.Chat.objects.filter(user_id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        data = super().get(request, *args, **kwargs).data

        return core.utils.success_response(
            message="Чаты",
            data=data,
        )

    def post(self, request):
        serializer = support.serializers.ChatCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        if not serializer.is_valid(raise_exception=True):
            return core.utils.error_response(
                message="Ошибка валидации",
                data=serializer.errors,
            )

        chat = serializer.save()
        return core.utils.success_response(
            message="Чат создан",
            data={"id": chat.id},
        )
