import json

from django.conf import settings
from django.db.models import Q
from django.contrib.auth import get_user_model

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Room, Message
from .constants import Messages

User = get_user_model()


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        user = self.scope["user"]
        contact_id = self.scope["url_route"]["kwargs"]["contact_id"]

        if not user.is_authenticated:
            self.send_error(Messages.ERROR_UNAUTHENTICATED)
            return
        elif user.pk == contact_id:
            self.send_error(Messages.ERROR_SELF_CHAT)
            return

        if contact_id == 0:
            self.contact = self.get_random_admin()
        else:
            try:
                self.contact = self.get_contact(contact_id)
            except User.DoesNotExist:
                self.send_error(Messages.ERROR_NO_USER_FOUND)
                return

        self.room_group_name = self.get_room_name(user.pk, self.contact.pk)

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.user_room = self.get_room_or_none(user, self.contact)
        self.contact_room = self.get_room_or_none(self.contact, user)

        detail = {
            "type": "connection_established",
            "message": Messages.CONNECTION_SUCCESS_MESSAGE,
            "contact": {
                "username": self.contact.username,
                "avatar": self.get_avatar_url(self.contact.author.avatar),
            },
            "history": [
                {
                    "content": message.content,
                    "sender_id": message.sender_id,
                    "created_at": message.created_at.isoformat(),
                }
                for message in self.get_history(user, self.contact)
            ],
        }
        self.send(json.dumps(detail))

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        content = text_data_json["content"]
        user = self.scope["user"]

        if not self.user_room:
            self.user_room = Room.objects.create(user=user, contact=self.contact)
        if not self.contact_room:
            self.contact_room = Room.objects.create(user=self.contact, contact=user)

        message = Message.objects.create(
            content=content, sender=user, recipient=self.contact
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

    def chat_message(self, event):
        detail = {
            "type": "chat",
            "content": event["content"],
            "sender_id": event["sender_id"],
            "created_at": event["created_at"],
        }
        self.send(json.dumps(detail))

    def get_room_name(self, user_id, contact_id):
        sorted_ids = sorted([user_id, contact_id])
        return f"Room-{sorted_ids[0]}-{sorted_ids[1]}"

    def get_room_or_none(self, user, contact):
        try:
            return Room.objects.get(user=user, contact=contact)
        except Room.DoesNotExist:
            return None

    def send_error(self, message):
        detail = {"type": "error", "message": message}
        self.send(json.dumps(detail))
        self.close()

    def get_history(self, user, contact):
        if not self.user_room:
            return []

        return (
            Message.objects.filter(
                Q(sender=user, recipient=contact) | Q(sender=contact, recipient=user)
            )
            .filter(created_at__gte=self.user_room.created_at)
            .order_by("created_at")
        )

    def get_random_admin(self):
        return User.objects.filter(is_staff=True).order_by("?").first()

    def get_contact(self, pk):
        return User.objects.select_related("author").get(pk=pk)

    def get_avatar_url(self, avatar):
        return f"{settings.BASE_BACKEND_URL}{avatar.url}" if avatar else None
