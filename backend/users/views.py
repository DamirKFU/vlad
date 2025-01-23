import django.conf
import django.contrib.auth
import django.core.signing
import django.utils.timezone
import elasticsearch_dsl
import rest_framework.generics
import rest_framework.permissions
import rest_framework.status
import rest_framework.views

import core.tasks
import core.utils
import users.documents
import users.models
import users.serializers


class CrateUserView(rest_framework.generics.CreateAPIView):
    queryset = users.models.User.objects.all()
    serializer_class = users.serializers.UserSerializer
    permission_classes = [rest_framework.permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors,
                message="Ошибка при регистрации",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        users.logs.log_user_event("user_registered", request)
        return core.utils.success_response(
            message="Регистрация успешно завершена",
            http_status=rest_framework.status.HTTP_201_CREATED,
        )


class LoginView(rest_framework.generics.GenericAPIView):
    permission_classes = (rest_framework.permissions.AllowAny,)
    serializer_class = users.serializers.LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors,
                message="Ошибка авторизации",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.validated_data["user"]
        django.contrib.auth.login(request, user)
        return core.utils.success_response(
            message="Вход выполнен успешно",
            http_status=rest_framework.status.HTTP_200_OK,
        )


class LogoutView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        django.contrib.auth.logout(request)
        return core.utils.success_response(
            message="Выход выполнен успешно",
            http_status=rest_framework.status.HTTP_200_OK,
        )


class IsAuthView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        return core.utils.success_response(
            message="Вы авторизованы",
            http_status=rest_framework.status.HTTP_200_OK,
        )


class PasswordResetRequestView(rest_framework.generics.GenericAPIView):
    serializer_class = users.serializers.PasswordResetRequestSerializer
    permission_classes = (rest_framework.permissions.AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors,
                message="Ошибка при запросе сброса пароля",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        user = serializer.validated_data["user"]

        token_data = {"user_id": user.id, "email": user.email}
        token = django.core.signing.dumps(token_data)

        reset_url = f"http://localhost:3000/reset-password/{token}"

        core.tasks.send_email_task.delay(
            subject="Сброс пароля",
            message="",
            html_message=django.template.loader.render_to_string(
                "reset_password_email.html",
                {"reset_url": reset_url, "user": user},
            ),
            from_email=django.conf.settings.EMAIL_ADMIN,
            recipient_list=[email],
        )

        return core.utils.success_response(
            message="Инструкции по сбросу пароля отправлены на вашу почту",
            http_status=rest_framework.status.HTTP_200_OK,
        )


class PasswordResetConfirmView(rest_framework.generics.GenericAPIView):
    serializer_class = users.serializers.PasswordResetConfirmSerializer
    permission_classes = (rest_framework.permissions.AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors,
                message="Ошибка при сбросе пароля",
                http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return core.utils.success_response(
            message="Пароль успешно изменен.",
            http_status=rest_framework.status.HTTP_200_OK,
        )


class UserSearchView(rest_framework.views.APIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    throttle_classes = []

    def get(self, request):
        query = request.query_params.get("query", "")
        if len(query) < 2:
            return core.utils.success_response(data=[])

        query = query.lower()
        search = users.documents.UserDocument.search().query(
            elasticsearch_dsl.Q(
                "bool",
                should=[
                    elasticsearch_dsl.Q(
                        "match",
                        username={
                            "query": query,
                            "fuzziness": 2,
                        },
                    ),
                    elasticsearch_dsl.Q("fuzzy", username=query),
                    elasticsearch_dsl.Q("wildcard", username=f"*{query}*"),
                ],
            )
        )[:3]

        response = search.execute()

        users_data = [
            {
                "id": hit.id,
                "username": hit.username,
            }
            for hit in response
        ]
        return core.utils.success_response(
            message="Пользователи найдены", data=users_data
        )
