from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "token"]

    def get_token(self, user):
        return Token.objects.get_or_create(user=user).key


class GoogleAuthSerializer(serializers.Serializer):
    code = serializers.CharField()
    state = serializers.CharField()
    error = serializers.CharField(required=False)

    def validate(self, attrs):
        error = attrs.get("error")
        if error is not None:
            raise serializers.ValidationError({"error": error})

        return super().validate(attrs)
