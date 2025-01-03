import django.conf
import django.db
import rest_framework.response
import rest_framework.status


def success_response(
    data=None,
    message="",
    http_status=rest_framework.status.HTTP_200_OK,
):
    if data is None:
        data = {}

    response_data = {"data": data, "message": message}

    if django.conf.settings.DEBUG:
        response_data["queries_info"] = {
            "count": len(django.db.connection.queries),
            "total_time": sum(
                float(q["time"]) for q in django.db.connection.queries
            ),
            "queries": [
                {"sql": q["sql"], "time": q["time"]}
                for q in django.db.connection.queries
            ],
        }

    return rest_framework.response.Response(
        response_data,
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
        fields = {}
        for key, value in serializer_errors.items():
            if key == "form_error":
                continue

            if isinstance(value[0], str):
                fields[key] = value[0]
            else:
                fields[key] = {k: v[0] for k, v in value[0].items()}

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
