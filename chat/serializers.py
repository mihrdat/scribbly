from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Room, Message

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "participant", "created_at"]
        model = Room


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "content", "user", "recipient", "created_at"]
        model = Message
