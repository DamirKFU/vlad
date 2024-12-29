import django.contrib.admin

import payments.models


@django.contrib.admin.register(payments.models.Payment)
class PaymentAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "payment_id",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("order__id", "payment_id")
    ordering = ("-created_at",)
    readonly_fields = (
        "order",
        "payment_id",
        "status",
        "created_at",
        "confirmation_url",
    )
