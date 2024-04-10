import json

from django.conf import settings
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

        user = self.scope["user"]
        if not user.is_authenticated:
            detail = {
                "type": "error",
                "message": Messages.ERROR_AUTHENTICATION_FAILED,
            }
            self.send(json.dumps(detail))
            self.close()
            return

        participant_id = self.scope["url_route"]["kwargs"]["participant_id"]
        if participant_id == 0:
            self.participant = self.get_random_admin()
        else:
            try:
                self.participant = self.get_participant(participant_id)
            except User.DoesNotExist:
                detail = {
                    "type": "error",
                    "message": Messages.ERROR_NO_USER_FOUND,
                }
                self.send(json.dumps(detail))
                self.close()
                return

        self.room_group_name = self.get_shared_room_name(user, self.participant)

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        participant_avatar = self.participant.author.avatar
        detail = {
            "type": "connection_established",
            "message": Messages.CONNECTION_SUCCESS_MESSAGE,
            "participant": {
                "username": self.participant.username,
                "avatar": (
                    settings.BASE_BACKEND_URL + str(participant_avatar.url)
                    if participant_avatar
                    else None
                ),
            },
            "history": [
                {
                    "sender_id": message.sender_id,
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                }
                for message in self.get_history(user, self.participant)
            ],
        }
        self.send(json.dumps(detail))

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        content = text_data_json["content"]

        user = self.scope["user"]
        message = Message.objects.create(
            content=content, sender=user, recipient=self.participant
        )

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "chat_message",
                "content": content,
                "sender_id": self.scope["user"].id,
                "created_at": message.created_at.isoformat(),
            },
        )

        self.create_room_with_shared_name(user, self.participant, self.room_group_name)
        self.create_room_with_shared_name(self.participant, user, self.room_group_name)

    def chat_message(self, event):
        detail = {
            "type": "chat",
            "content": event["content"],
            "sender_id": event["sender_id"],
            "created_at": event["created_at"],
        }
        self.send(json.dumps(detail))

    def get_random_admin(self):
        return User.objects.filter(is_staff=True).order_by("?").first()

    def get_participant(self, pk):
        return User.objects.select_related("author").get(pk=pk)

    def get_shared_room_name(self, user, participant):
        room = Room.objects.filter(
            Q(user=user, participant=participant)
            | Q(user=participant, participant=user)
        ).first()
        return room.name if room else generate_random_room_name()

    def get_history(self, user, participant):
        try:
            room = Room.objects.get(user=user, participant=participant)
            return (
                Message.objects.filter(
                    Q(sender=user, recipient=participant)
                    | Q(sender=participant, recipient=user)
                )
                .filter(created_at__gte=room.created_at)
                .order_by("created_at")
            )
        except Room.DoesNotExist:
            return []

    def create_room_with_shared_name(self, user, participant, name):
        if not Room.objects.filter(user=user, participant=participant).exists():
            Room.objects.create(name=name, user=user, participant=participant)
