import rest_framework.status
import rest_framework_simplejwt.views
import rest_framework.response
import rest_framework.permissions


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
