import django.urls

import support.views

app_name = "support"

urlpatterns = [
    django.urls.path("chats/", support.views.ChatListView.as_view()),
]
