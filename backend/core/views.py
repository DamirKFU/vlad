import pathlib

import celery
import django.conf
import django.http
import rest_framework.permissions
import rest_framework.response
import rest_framework.status as status
import rest_framework.views

import core.utils


class DownloadFileView(rest_framework.views.APIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]

    def get(self, request):
        file_path = request.query_params.get("path")
        if not file_path:
            return core.utils.error_response(
                message="No path provided",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        media_root = pathlib.Path(django.conf.settings.MEDIA_ROOT)
        absolute_path = media_root / file_path.removeprefix("/media/")
        if not str(absolute_path).startswith(str(media_root)):
            return core.utils.error_response(
                message="Invalid path",
                http_status=status.HTTP_403_FORBIDDEN,
            )

        if absolute_path.exists():
            return django.http.FileResponse(
                absolute_path.open("rb"),
                as_attachment=True,
                filename=absolute_path.name,
            )

        return core.utils.error_response(
            message="File not found",
            http_status=status.HTTP_404_NOT_FOUND,
        )


class TaskStatusView(rest_framework.views.APIView):
    def get(self, request, task_id):
        task = celery.result.AsyncResult(task_id)
        if task.state == celery.states.PENDING and not task.task_id:
            return core.utils.error_response(
                message="Задача не найдена",
                errors={"form_error": "task_id не найден"},
                http_status=status.HTTP_404_NOT_FOUND,
            )

        if task.state == celery.states.PENDING:
            return core.utils.success_response(
                message="Задача еще не выполнена",
            )

        if task.state == celery.states.FAILURE:
            return core.utils.error_response(
                message="Ошибка выполнения задачи",
                http_status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        result = task.get()
        if "serializer_errors" in result:
            return core.utils.error_response(
                **result,
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        return core.utils.success_response(
            **result,
            http_status=status.HTTP_201_CREATED,
        )
