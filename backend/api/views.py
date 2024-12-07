import django.middleware.csrf
import django.utils.decorators
import django.views.decorators.csrf
import rest_framework.authentication
import rest_framework.generics
import rest_framework.permissions
import rest_framework.response
import rest_framework.status


@django.utils.decorators.method_decorator(
    django.views.decorators.csrf.ensure_csrf_cookie, name="dispatch"
)
class GetCSRFTokenView(rest_framework.generics.GenericAPIView):
    permission_classes = (rest_framework.permissions.AllowAny,)
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        return rest_framework.response.Response({}, status=200)
