from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Room(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms")
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    content = models.TextField()
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
    created_at = models.DateTimeField(auto_now_add=True)
