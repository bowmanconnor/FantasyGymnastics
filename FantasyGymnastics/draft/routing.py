from django.urls import path
from . import consumers
import os
import socket

websocket_urlpatterns = [
    path('ws/draft/<int:league_pk>/', consumers.DraftConsumer.as_asgi()),
]