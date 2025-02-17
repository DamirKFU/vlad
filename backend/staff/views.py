import django.db.transaction
import django_filters
import rest_framework.generics
import rest_framework.permissions
import rest_framework.status
import rest_framework.views

import catalog.filters
import catalog.models
import catalog.pagination
import catalog.serializers
import core.utils
import staff.documets
import staff.pagination
import staff.serializers
import staff.utils
import support.models
import support.utils


class StaffChatListView(rest_framework.generics.ListAPIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    serializer_class = staff.serializers.ChatStaffSerializer

    def get_queryset(self):
        return support.models.Chat.objects.get_chats_for_staff(
            self.request.user, self.request.query_params.get("chat_type")
        )

    def get(self, request, *args, **kwargs):
        chat_type = request.query_params.get("chat_type")
        allowed_chats = staff.utils.get_allowed_chats(request.user)

        if chat_type not in allowed_chats:
            return core.utils.error_response(message="Недостаточно прав")

        data = {
            "allowed_chats": allowed_chats,
            "chats": super().get(request, *args, **kwargs).data,
        }

        return core.utils.success_response(
            message="Чаты получены",
            data=data,
        )


class StaffChatInviteView(rest_framework.views.APIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    serializer_class = staff.serializers.ChatUserInviteSerializer

    @django.db.transaction.atomic
    def get(self, request, pk, *args, **kwargs):
        chat = support.models.Chat.objects.get(id=pk)

        have_rights = list(chat.responsible_users.all())
        if not have_rights and not request.user.is_superuser:
            return core.utils.error_response(message="Недостаточно прав")

        if request.user.id in have_rights:
            return core.utils.error_response(
                message="Вы уже ответственный за этот чат"
            )

        chat.responsible_users.add(request.user)
        chat.save()

        message = support.models.Message.objects.create(
            chat=chat,
            user=request.user,
            content=f"Сотрудник {request.user.username} присоединился к чату",
            is_system=True,
        )
        support.utils.send_message_to_chat(chat, message)
        return core.utils.success_response(
            message="Вы успешно присоединились к чату"
        )

    @django.db.transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        chat = support.models.Chat.objects.get(id=pk)
        serializer = self.serializer_class(
            data=request.data,
            context={"chat": chat},
        )
        if not serializer.is_valid():
            return core.utils.error_response(
                message="Ошибка валидации",
                serializer_errors=serializer.errors,
            )

        user = serializer.save()

        message = support.models.Message.objects.create(
            chat=chat,
            user=request.user,
            content=(
                f"Сотрудник {request.user.username} "
                f"добавил {user.username} в чат"
            ),
            is_system=True,
        )
        support.utils.send_message_to_chat(chat, message)

        return core.utils.success_response(
            message="Пользователь присоединен к чату",
        )


class StaffOrderListView(rest_framework.generics.ListAPIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    serializer_class = catalog.serializers.OrderSerializer
    queryset = catalog.models.Order.objects.get_orders_with_items_for_staff()
    pagination_class = catalog.pagination.OrderPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = catalog.filters.OrderFilter

    def get(self, request, *args, **kwargs):
        return core.utils.success_response(
            message="Заказы получены",
            data=super().get(request, *args, **kwargs).data,
        )
