import django.contrib.admin

import catalog.models
import staff.models


@django.contrib.admin.register(staff.models.OrderLog)
class OrderLogAdmin(django.contrib.admin.ModelAdmin):
    list_display = [
        staff.models.OrderLog.order.field.name,
        staff.models.OrderLog.user.field.name,
        staff.models.OrderLog.from_status.field.name,
        staff.models.OrderLog.to_status.field.name,
        staff.models.OrderLog.created_at.field.name,
    ]
    list_filter = [
        staff.models.OrderLog.from_status.field.name,
        staff.models.OrderLog.to_status.field.name,
        staff.models.OrderLog.user.field.name,
        staff.models.OrderLog.created_at.field.name,
    ]
    search_fields = [
        "{0}__{1}".format(
            staff.models.OrderLog.order.field.name,
            catalog.models.Order.id.field.name,
        )
    ]
    readonly_fields = [
        staff.models.OrderLog.created_at.field.name,
        staff.models.OrderLog.order.field.name,
        staff.models.OrderLog.user.field.name,
        staff.models.OrderLog.from_status.field.name,
        staff.models.OrderLog.to_status.field.name,
        staff.models.OrderLog.error_comment.field.name,
    ]
    ordering = ["-{}".format(staff.models.OrderLog.created_at.field.name)]
