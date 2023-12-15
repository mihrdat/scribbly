from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.SerializerMethodField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user with the given email was found.")

        return value

    def validate_password(self, value):
        if self.user:
            if self.is_user_disabled(self.user):
                return

            if not self.user.has_usable_password():
                raise serializers.ValidationError(
                    "No password has been registered for this account."
                )

            is_valid_password = self.user.check_password(value)
            if not is_valid_password:
                raise serializers.ValidationError(
                    "Unable to log in with provided password."
                )

        return value

    def validate(self, attrs):
        if self.is_user_disabled(self.user):
            raise serializers.ValidationError("The user account has been disabled.")

        if not self.user.is_active:
            raise serializers.ValidationError(
                "The user account has not been activated."
            )

        return super().validate(attrs)

    def get_token(self, obj):
        (token, created) = Token.objects.get_or_create(user=self.user)
        return token.key

    def is_user_disabled(self, user):
        return (not user.is_active) and (not user.has_usable_password())
