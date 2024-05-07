from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.core.exceptions import ValidationError
from json import loads

class Chatroom_consumer(WebsocketConsumer):

    def connect(self):
        self.accept()
        print("connected")
        self.send(text_data="WebSocket Connection Successful!")

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = loads(text_data)
        message = data.get('message')
        print(message,"received")
        pass
