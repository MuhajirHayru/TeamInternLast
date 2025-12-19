import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import Teamworkapp.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Teamworkproject.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(Teamworkapp.routing.websocket_urlpatterns)
    ),
})
