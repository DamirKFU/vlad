import django.conf
import django.conf.urls.static
import django.contrib.admin
import django.urls

import core.views

app_name = "core"

urlpatterns = [
    django.urls.path(
        "download/",
        core.views.DownloadFileView.as_view(),
        name="download",
    ),
    django.urls.path(
        "task/<str:task_id>/",
        core.views.TaskStatusView.as_view(),
        name="task-status",
    ),
]
