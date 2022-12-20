"""
ASGI config for FantasyGymnastics project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
import socket
from django.urls import path

from django.core.asgi import get_asgi_application
a = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from draft import consumers as draft_consumers
from core import consumers as core_consumers

if 'django' in socket.gethostname():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FantasyGymnastics.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FantasyGymnastics.settings.development')

application = ProtocolTypeRouter({
    'http': a,
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('ws/draft/<int:league_pk>/', draft_consumers.DraftConsumer.as_asgi()),
            path('ws/users/', core_consumers.UserConsumer.as_asgi()),
        ])
    )
})