from .models import *


class ChatSerializer(ModelSerializer):
    sender = UserChatSeralizer(read_only=True)
    receiver = UserChatSeralizer(read_only=True)

    class Meta:
        model = Chat
        fields = ["id", "sender", "receiver", "message", "date", "is_read"]
