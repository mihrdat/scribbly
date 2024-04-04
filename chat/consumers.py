import json
from django.db.models import Q
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Room, Message
from .constants import Messages
from .utils import generate_random_room_name

User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        if not self.authenticate_user():
            return

        self.assign_participant()
        self.assign_room()

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name,
        )
        self.send_message("connection_established", Messages.CONNECTION_SUCCESS_MESSAGE)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

        user = self.scope["user"]
        Room.objects.get_or_create(
            user=user,
            participant=self.participant,
            defaults={"name": self.room_group_name},
        )
        Room.objects.get_or_create(
            user=self.participant,
            participant=user,
            defaults={"name": self.room_group_name},
        )

        Message.objects.create(content=message, user=user, recipient=self.participant)

    def chat_message(self, event):
        message = event["message"]
        self.send_message("chat", message)

    def authenticate_user(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            self.send_message("error", Messages.ERROR_AUTHENTICATION_FAILED)
            self.close()
            return False
        return True

    def assign_participant(self):
        username = self.scope["url_route"]["kwargs"]["username"]
        self.participant = User.objects.filter(username=username).first()
        if (username != "support") and (not self.participant):
            self.send_message("error", Messages.ERROR_NO_USER_FOUND)
            self.close()
            return
        elif username == "support":
            self.participant = self.get_random_admin()

    def assign_room(self):
        user = self.scope["user"]
        room = Room.objects.filter(
            (Q(user=user) & Q(participant=self.participant))
            | (Q(user=self.participant) & Q(participant=user))
        ).first()
        self.room_group_name = room.name if room else generate_random_room_name()

    def get_random_admin(self):
        return User.objects.filter(is_staff=True).order_by("?").first()

    def send_message(self, type, message):
        self.send(text_data=json.dumps({"type": type, "message": message}))
