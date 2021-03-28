from django.urls import path
from .core import consumers as core_consumers
from .draft import consumers as draft_consumers
import os
import socket

### THE REAL ROUTING FILE

websocket_urlpatterns = [
    path('ws/draft/<int:league_pk>/', draft_consumers.DraftConsumer.as_asgi()),
    path('ws/users/', core_consumers.UserConsumer.as_asgi()),
]
