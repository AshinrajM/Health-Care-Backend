from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.core.exceptions import ValidationError


class Chatroom_consumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self):
        pass
