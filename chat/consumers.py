from channels.generic.websocket import WebsocketConsumer
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from json import loads
from .models import *
import json


class Chatroom_consumer(WebsocketConsumer):

    async def connect(self):
        self.accept()

        print(self.user)
        self.chatroom_name = self.scope["url_route"]["kwargs"]["chatroom_name"]

        sender_id, receiver_id = self.chatroom_name.split("_")

        #creating room
        self.chatroom_group_name = (
            f"chat_{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
        )



        self.chatroom = get_object_or_404(Chat, group_name=self.chatroom_name)

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json["body"]  # the body is the message in the data base

        message = Chat.objects.create(body=body, author=self.user)
