import django.middleware.csrf
import django.utils.decorators
import django.views.decorators.csrf
import rest_framework.authentication
import rest_framework.generics
import rest_framework.permissions
import rest_framework.response
import rest_framework.status
import rest_framework_simplejwt.views


@django.utils.decorators.method_decorator(
    django.views.decorators.csrf.csrf_protect, name="dispatch"
)
class CustomTokenObtainPairView(
    rest_framework_simplejwt.views.TokenObtainPairView
):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == rest_framework.status.HTTP_200_OK:
            access_token = response.data.pop("access")
            refresh_token = response.data.pop("refresh")
            response.set_cookie("access_token", access_token, samesite="Lax")
            response.set_cookie("refresh_token", refresh_token, samesite="Lax")

        return response


class CustomTokenRefreshView(rest_framework_simplejwt.views.TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == rest_framework.status.HTTP_200_OK:
            access_token = response.data.pop("access")
            response.set_cookie("access_token", access_token, samesite="Lax")

        return response


@django.utils.decorators.method_decorator(
    django.views.decorators.csrf.ensure_csrf_cookie, name="dispatch"
)
class GetCSRFTokenView(rest_framework.generics.GenericAPIView):
    permission_classes = (rest_framework.permissions.AllowAny,)
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        return rest_framework.response.Response({}, status=200)
