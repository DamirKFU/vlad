import rest_framework.exceptions
import rest_framework.status
import rest_framework.views

import core.utils


def custom_exception_handler(exc, context):
    response = rest_framework.views.exception_handler(exc, context)
    if isinstance(exc, rest_framework.exceptions.ValidationError):
        new_response_data = core.utils.error_response(
            serializer_errors=response.data,
            message="Ошибка валидации",
        ).data
        response.data = new_response_data
        return response

    if isinstance(exc, rest_framework.exceptions.NotAuthenticated):
        return core.utils.error_response(
            message="Вы не авторизованы",
            http_status=rest_framework.status.HTTP_401_UNAUTHORIZED,
        )

    if isinstance(exc, rest_framework.exceptions.Throttled):
        new_response_data = core.utils.error_response(
            message=response.data["detail"],
        ).data
        response.data = new_response_data
        return response

    return response
