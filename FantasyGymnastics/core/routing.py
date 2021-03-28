'''
from django.urls import path
from django.conf.urls import url
from . import consumers

websocket_urlpatterns = [
    path('ws/users/', consumers.UserConsumer.as_asgi()),
    # url(r'^ws/users/', consumers.UserConsumer.as_asgi()),
]

# from django.urls import re_path

# from . import consumers

# websocket_urlpatterns = [
#     re_path(r'ws/users/$', consumers.UserConsumer.as_asgi()),
# ]
'''