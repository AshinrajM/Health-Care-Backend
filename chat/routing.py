from django.urls import path, re_path
from .consumers import *

websocket_urlpatterns = [
    # path("ws/chat/<room_name>/", Chatroom_consumer.as_asgi()),
    re_path(r'^ws/chat/(?P<room_name>[\w_]+)/$', Chatroom_consumer.as_asgi()),
]
