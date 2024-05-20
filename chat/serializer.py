from .models import *
from .serializer import *
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class UserChatSeralizer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id']



class ChatSerializer(ModelSerializer):
    sender = UserChatSeralizer(read_only=True)
    receiver = UserChatSeralizer(read_only=True)

    class Meta:
        model = Chat
        fields = ["id", "sender", "receiver", "message", "is_read"]
