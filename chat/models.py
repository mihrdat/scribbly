from django.db import models
from django.contrib.auth import get_user_model
from .utils import generate_random_room_name

User = get_user_model()


class Room(models.Model):
    name = models.CharField(max_length=55, default=generate_random_room_name)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rooms")
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    content = models.TextField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
    created_at = models.DateTimeField(auto_now_add=True)
