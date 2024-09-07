"""ASGI config for dsbd project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.core.handlers.asgi import ASGIHandler


class ASGIHandlerTmp(ASGIHandler):
    def __init__(self):
        self.load_middleware(is_async=False)
        super().__init__()


django_asgi_app = get_asgi_application()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dsbd.settings")

from custom_admin import routing as custom_admin_routing
from ticket import routing

url = []
url += routing.urlpatterns
url += custom_admin_routing.urlpatterns

application = ProtocolTypeRouter(
    {"http": django_asgi_app, "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(url)))}
)
