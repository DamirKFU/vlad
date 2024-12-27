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
    serializer_errors=None,
    message="",
    http_status=rest_framework.status.HTTP_400_BAD_REQUEST,
):
    if fields and serializer_errors:
        raise ValueError(
            "Both fields and serializer_errors cannot be provided"
        )

    if fields is None and serializer_errors is None:
        fields = {}
    elif serializer_errors:
        fields = {
            k: v[0] for k, v in serializer_errors.items() if k != "form_error"
        }
        form_error = serializer_errors.get("form_error", [None])[0]

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
