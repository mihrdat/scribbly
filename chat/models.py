import uuid

from django.db import models
from django.contrib.auth import get_user_model

from .utils import generate_random_room_name

User = get_user_model()


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=55, default=generate_random_room_name)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms")
    partner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")

    class Meta:
        unique_together = [
            ["name", "user", "partner"],
        ]


class Message(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    rooms = models.ManyToManyField(Room, related_name="messages")
