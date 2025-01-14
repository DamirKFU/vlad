import channels.routing
import django.urls

import support.consumers

websocket = channels.routing.URLRouter(
    [
        django.urls.path(
            "ws/support/chat/<int:chat_id>/",
            support.consumers.ChatConsumer.as_asgi(),
            name="chat",
        ),
    ]
)
