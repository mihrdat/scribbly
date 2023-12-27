from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Room, Message

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username"]


class RoomSerializers(serializers.ModelSerializer):
    partner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_staff=True)
    )

    class Meta:
        model = Room
        fields = ["id", "name", "user", "partner"]
        read_only_fields = ["name", "user"]

    def validate_partner(self, value):
        user = self.context["request"].user
        if Room.objects.filter(user=user, partner=value).exists():
            raise serializers.ValidationError(
                "There is currently an open chat with this admin."
            )
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)


class MessageSerializers(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "content", "created_at", "sender_id", "recipient_id"]
