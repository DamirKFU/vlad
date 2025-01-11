import django.db.transaction
import rest_framework.generics
import rest_framework.permissions
import rest_framework.views

import core.utils
import support.models


class CreateChatView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)
    serializer_class = support.serializers.ChatSerializer

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
