import os
import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import messenger_project.chat_app.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "messenger_project.messenger_project.settings")

django.setup()

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            messenger_project.chat_app.routing.websocket_urlpatterns
        )
    ),
})