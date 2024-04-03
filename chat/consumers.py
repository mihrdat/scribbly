import json
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Room

User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def get_room_name(self, user, participant):
        room_name = Room.objects.get_or_create(user=user, participant=participant).name

        # Create a mutually room for participant if it doesn't exist
        Room.objects.get_or_create(user=participant, participant=user, name=room_name)

        return room_name

    def connect(self):
        user = self.scope["user"]
        user_name = self.scope["url_route"]["kwargs"]["user_name"]

        if user_name is "admin":
            # Randomly assign an admin to supervise
            admin = User.objects.filter(is_staff=True).order_by("?").first()

            self.room_group_name = self.get_room_name(user=user, participant=admin)
        else:
            try:
                participant = User.objects.get(username=user_name)
                self.room_group_name = self.get_room_name(
                    user=user, participant=participant
                )
            except User.DoesNotExist:
                self.send(
                    text_data=json.dumps(
                        {"error": "No user with the given username was found."}
                    )
                )
                self.close()

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )
        self.accept()
        print(self.scope["user"])
        self.send(
            text_data=json.dumps(
                {
                    "type": "connection_established.",
                    "message": "You are now connected",
                }
            )
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
            },
        )

    def chat_message(self, event):
        message = event["message"]
        self.send(
            text_data=json.dumps(
                {
                    "type": "chat",
                    "message": message,
                }
            )
        )
