from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.core.exceptions import ValidationError
from json import loads
import json


class Chatroom_consumer(WebsocketConsumer):

    def connect(self):
        self.accept()
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        
        # print("connected")
        # self.send(text_data=json.dumps({"message": "WebSocket Connection Successful!"}))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        data = loads(text_data)
        message = data.get("message")
        # print(message,"received")
        pass
