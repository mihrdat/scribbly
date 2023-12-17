from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Chat

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username"]


class ChatSerializers(serializers.ModelSerializer):
    partner = UserSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = ["id", "partner"]
