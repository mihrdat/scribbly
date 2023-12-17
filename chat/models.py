import uuid

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats")
    partner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")

    class Meta:
        unique_together = [
            ["user", "partner"],
        ]


class Message(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
