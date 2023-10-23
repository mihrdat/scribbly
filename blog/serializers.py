from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Author

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "date_joined", "last_login", "is_active"]


class AuthorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Author
        fields = [
            "id",
            "phone_number",
            "avatar",
            "user",
        ]
