import django.contrib.auth.models
import rest_framework.generics
import rest_framework.permissions

import api.serializers


class CrateUserView(rest_framework.generics.CreateAPIView):
    queryset = django.contrib.auth.models.User.objects
    serializer_class = api.serializers.UserSerializer
    permission_classes = [rest_framework.permissions.AllowAny]
