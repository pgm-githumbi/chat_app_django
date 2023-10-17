# chat/routing.py
from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    path("ws/<str:room_name>/<str:username>/", consumers.ChatConsumer.as_asgi()),
]