import uuid

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=55, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms")
    partner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")

    class Meta:
        unique_together = [
            ["user", "partner"],
        ]


class Message(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    rooms = models.ManyToManyField(Room, related_name="messages")
