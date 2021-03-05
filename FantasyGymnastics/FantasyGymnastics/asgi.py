"""
ASGI config for FantasyGymnastics project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
import socket

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

import draft.routing

if 'django' in socket.gethostname():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FantasyGymnastics.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FantasyGymnastics.settings.development')

#application = get_asgi_application()

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            draft.routing.websocket_urlpatterns
        )
    )
})