import os

import channels.auth
import channels.routing
import channels.security.websocket
import django.core.asgi


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

django_asgi_app = django.core.asgi.get_asgi_application()

import support.routing  # noqa

application = channels.routing.ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": (
            channels.security.websocket.AllowedHostsOriginValidator(
                channels.auth.AuthMiddlewareStack(support.routing.websocket)
            )
        ),
    }
)
