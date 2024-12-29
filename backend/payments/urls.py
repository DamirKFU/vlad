import django.urls

import payments.views

app_name = "payments"

urlpatterns = [
    django.urls.path(
        "webhook/yookassa/",
        payments.views.YooKassaWebhookView.as_view(),
        name="yookassa-webhook",
    ),
]
