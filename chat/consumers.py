from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from .serializer import *
from json import loads
from .models import *
import json


# import ast


class Chatroom_consumer(AsyncJsonWebsocketConsumer):
    async def connect(self):

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        sender_id, recipient_id = self.room_name.split("_")

        # creating room  room_group_name is the permanent name
        self.room_group_name = (
            f"chat_{min(sender_id, recipient_id)}_{max(sender_id, recipient_id)}"
        )

        # Join room group  self.channel_name: A unique name assigned to the WebSocket connection by Django Channels. This name is used to identify the specific connection instance when messages are sent to or received from the WebSocket.
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await super().disconnect(close_code)

    async def receive(self, text_data):

        text_data_json = json.loads(text_data)
        text = text_data_json["text"]

        sender_id = self.room_name.split("_")[0]
        recipient_id = self.room_name.split("_")[1]
        chat_message = await self.save_chat_message(text, sender_id, recipient_id)

        if text:
            print("received", {text})

        messages = await self.get_messages(sender_id, recipient_id)

        # here chat_message method will be send to the group and later it will be triggered
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "messages": messages,
                "sender": sender_id,
                "message": text,
            },
        )

    @database_sync_to_async
    def get_messages(self, sender_id, recipient_id):

        messages = []
        for i in Chat.objects.filter(
            author__in=[sender_id, recipient_id], receiver__in=[sender_id, recipient_id]
        ):
            messages.append(ChatSerializer(i).data)

        print(messages, "check in get")

        return messages

    async def chat_message(self, event):
        messages = event["messages"]
        sender = event["sender"]
        message = event["message"]

        await self.send(
            text_data=json.dumps(
                {
                    "messages": messages,
                    "sender": sender,
                    "message": message,
                }
            )
        )

    @database_sync_to_async
    def save_chat_message(self, message, sender_id, recipient_id):
        Chat.objects.create(
            message=message, author_id=sender_id, receiver_id=recipient_id
        )
