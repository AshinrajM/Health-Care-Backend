from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from json import loads
from .models import *
import json


class Chatroom_consumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        print("connected")
        print("connected")

        self.chatroom_name = self.scope["url_route"]["kwargs"]["room_name"]

        sender_id, recipient_id = self.chatroom_name.split("_")
        print(sender_id, recipient_id)

        # creating room  room_group_name is the permanent name
        self.room_group_name = (
            f"chat_{min(sender_id, recipient_id)}_{max(sender_id, recipient_id)}"
        )

        # join the room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print("disconnected")
        print("disconnected")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await super().disconnect(code)


    async def receive(self, text_data):

        text_data_json = json.loads(text_data)
        text = text_data_json["text"]  
        sender = text_data_json["sender"]
        recipient_id = self.room_name.split("_")[1]
        chat_message = await self.save_chat_message(text, sender, recipient_id)

        if chat_message and not chat_message.is_read:
            chat_message.mark_as_read()

        messages = await self.get_messages(sender, recipient_id)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "messages": messages,
                "sender": sender,
                "message": text,
            },
        )

    async def chat_message(self, event):

        # Receive message from room group
        messages = event["messages"]
        sender = event["sender"]
        message = event["message"]

        # Send message to WebSocket
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
    def save_chat_message(self, message, sender, recipient_id):
        Chat.objects.create(
            message=message,
            sender_id=sender_id,
            receiver_id=recipient_id,
        )

    @database_sync_to_async
    def get_messages(self, sender, recipient_id):
        messages = []

        for instance in Chat.objects.filter(
            sender__in=[sender, recipient_id], receiver__in=[sender, recipient_id]
        ):
            messages = ChatSerializer(instance).data

        return messages
