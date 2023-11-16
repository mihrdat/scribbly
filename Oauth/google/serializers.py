from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    jwt = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "jwt"]

    def get_jwt(self, user):
        refresh = RefreshToken.for_user(user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}


class GoogleAuthSerializer(serializers.Serializer):
    code = serializers.CharField()
    state = serializers.CharField()
    error = serializers.CharField(required=False)

    def validate(self, attrs):
        error = attrs.get("error")
        if error is not None:
            raise serializers.ValidationError({"error": error})

        return super().validate(attrs)
