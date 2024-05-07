from django.urls import path, re_path
from .consumers import *

websocket_urlpatterns = [
    path("ws/chat/", Chatroom_consumer.as_asgi()),
]
