from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Room

User = get_user_model()


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "participant", "created_at"]
        model = Room
