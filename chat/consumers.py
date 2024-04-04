import json
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Room
from .constants import Messages

User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        user = self.scope["user"]

        if not user.is_authenticated:
            self.send_message("Error", Messages.ERROR_AUTHENTICATION_FAILED)
            self.close()
            return

        username = self.scope["url_route"]["kwargs"]["username"]
        if username == "support":
            # Randomly assign an admin to supervise
            self.room_group_name = self.get_room_name(
                user=user, participant=self.get_random_admin()
            )
        else:
            try:
                self.room_group_name = self.get_room_name(
                    user=user, participant=User.objects.get(username=username)
                )
            except User.DoesNotExist:
                self.send_message("Error", Messages.ERROR_NO_USER_FOUND)
                self.close()
                return

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )
        self.send_message("Connected", Messages.CONNECTION_SUCCESS_MESSAGE)

    def get_room_name(self, user, participant):
        (room, created) = Room.objects.get_or_create(user=user, participant=participant)
        return room.name

    def get_random_admin(self):
        return User.objects.filter(is_staff=True).order_by("?").first()

    def send_message(self, type, message):
        self.send(text_data=json.dumps({"type": type, "message": message}))

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
