from django.urls import path, re_path
from .consumers import *

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_name>[\w_]+)/$', ChatConsumer.as_asgi()),
]

    # path("ws/chat/<room_name>/", Chatroom_consumer.as_asgi()),