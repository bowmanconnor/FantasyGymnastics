"""
ASGI config for FantasyGymnastics project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
import socket

from django.core.asgi import get_asgi_application
a = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import draft.routing

if 'django' in socket.gethostname():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FantasyGymnastics.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FantasyGymnastics.settings.development')

application = ProtocolTypeRouter({
    'http': a,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            draft.routing.websocket_urlpatterns
        )
    )
})