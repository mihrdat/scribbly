from django.contrib.auth import get_user_model, authenticate

from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source="key")

    class Meta:
        model = Token
        fields = ["token"]


class TokenCreateSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.fields[User.USERNAME_FIELD] = serializers.CharField(max_length=55)

    def validate(self, attrs):
        password = attrs.get("password")
        params = {
            User.USERNAME_FIELD: attrs.get(User.USERNAME_FIELD),
        }
        self.user = authenticate(
            request=self.context["request"], **params, password=password
        )

        if self.user is None:
            raise serializers.ValidationError(
                "Unable to log in with provided credentials."
            )

        if not self.user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        return attrs
