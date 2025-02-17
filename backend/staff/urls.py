import django.urls

import staff.views

app_name = "staff"

urlpatterns = [
    django.urls.path(
        "support/chats/",
        staff.views.StaffChatListView.as_view(),
        name="staff_chats",
    ),
    django.urls.path(
        "support/chats/<int:pk>/invite/",
        staff.views.StaffChatInviteView.as_view(),
        name="staff_chat_invite",
    ),
    django.urls.path(
        "orders/",
        staff.views.StaffOrderListView.as_view(),
        name="staff_orders",
    ),
]
