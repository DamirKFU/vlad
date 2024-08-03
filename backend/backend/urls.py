from django.conf import settings
from django.conf.urls.static import static
import django.contrib.admin
import django.urls


urlpatterns = [
    django.urls.path(
        "admin/",
        django.contrib.admin.site.urls,
        name="admin",
    ),
    django.urls.path(
        "api/",
        django.urls.include("api.urls"),
        name="api",
    ),
    django.urls.path(
        "api-auth/",
        django.urls.include("rest_framework.urls"),
        name="rest_framework-auth",
    ),
]


if settings.DEBUG:
    if settings.MEDIA_ROOT:
        urlpatterns += static(
            settings.MEDIA_URL,
            document_root=settings.MEDIA_ROOT,
        )
