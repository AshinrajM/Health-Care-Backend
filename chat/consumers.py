from channels.generic.websocket import WebsocketConsumer


class Chatroom_consumer(WebsocketConsumer):
    def connect(self):
        self.accept()
