import django.conf
import django.contrib.messages
import django.core.mail
import django.core.signing
import django.shortcuts
import django.utils.timezone
import rest_framework.generics
import rest_framework.permissions
import rest_framework.response
import rest_framework.status
import rest_framework.views

import users.models
import users.serializers


class CrateUserView(rest_framework.generics.CreateAPIView):
    queryset = users.models.User.objects.all()
    serializer_class = users.serializers.UserSerializer
    permission_classes = [rest_framework.permissions.AllowAny]


class VerifedEmailTokenView(rest_framework.views.APIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]

    def post(self, request):
        token_user_email = request.user.email
        exp = django.utils.timezone.datetime.now().toordinal()
        token = django.core.signing.dumps(
            {
                "exp": exp,
                "user_id": request.user.id,
            }
        )
        django.core.mail.send_mail(
            subject="Activate your account",
            message=django.template.loader.render_to_string(
                "verifed_email.html",
                {"token": token},
            ),
            from_email=django.conf.settings.EMAIL_ADMIN,
            recipient_list=[token_user_email],
        )

        return rest_framework.response.Response(
            status=rest_framework.status.HTTP_201_CREATED,
        )


class CheckEmailTokenView(rest_framework.views.APIView):
    serializer_class = users.serializers.EmailTokenSerializer
    permission_classes = [rest_framework.permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            token_data = django.core.signing.loads(
                serializer.data.get("token")
            )
            user_id = token_data.get("user_id")
            user = django.shortcuts.get_object_or_404(
                users.models.User, id=user_id
            )
            user.verified_email = True
            user.save()
            return rest_framework.response.Response(
                serializer.data,
                status=rest_framework.status.HTTP_202_ACCEPTED,
            )

        return rest_framework.response.Response(
            serializer.data,
            status=rest_framework.status.HTTP_406_NOT_ACCEPTABLE,
        )
