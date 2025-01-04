import rest_framework.permissions
import rest_framework.response
import rest_framework.status as status
import rest_framework.views

import core.utils
import telegram_bot.serializers


class TelegramAuthView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def post(self, request):
        serializer = telegram_bot.serializers.TelegramAuthSerializer(
            data=request.data,
            context={"request": request},
        )
        if not serializer.is_valid():
            return rest_framework.response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return core.utils.success_response(
            message="Telegram успешно привязан к аккаунту",
        )
