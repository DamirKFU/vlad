import django.urls

import staff.views

app_name = "staff"

urlpatterns = [
    django.urls.path(
        "orders/",
        staff.views.StaffOrderListView.as_view(),
        name="orders",
    ),
    django.urls.path(
        "orders/<int:order_id>/",
        staff.views.StaffOrderDetailView.as_view(),
        name="order-detail",
    ),
    django.urls.path(
        "orders/<int:order_id>/logs/",
        staff.views.OrderLogListView.as_view(),
        name="order-logs",
    ),
]
