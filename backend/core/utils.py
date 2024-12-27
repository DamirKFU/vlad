import rest_framework.response
import rest_framework.status


def success_response(
    data=None,
    message="",
    http_status=rest_framework.status.HTTP_200_OK,
):
    if data is None:
        data = {}

    return rest_framework.response.Response(
        {"data": data, "message": message},
        status=http_status,
    )


def error_response(
    fields=None,
    form_error=None,
    message="",
    http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
):
    if fields is None:
        fields = {}

    return rest_framework.response.Response(
        {
            "errors": {
                "fields": fields,
                "form_error": form_error,
            },
            "message": message,
        },
        status=http_status,
    )
