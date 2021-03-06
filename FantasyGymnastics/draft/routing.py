from django.urls import path
from . import consumers
import os
import socket

if 'django' in socket.gethostname():
    websocket_urlpatterns = [
        path('wss/draft/<int:league_pk>/', consumers.DraftConsumer.as_asgi()),
    ]
else:
    websocket_urlpatterns = [
        path('ws/draft/<int:league_pk>/', consumers.DraftConsumer.as_asgi()),
    ]