from django.core import exceptions
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .utils import decode_uid

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "date_joined", "last_login", "is_active"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs["password"]

        try:
            validate_password(password, user)
        except exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {
                    "password": serializer_error["non_field_errors"],
                }
            )

        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class BaseSerializerMixin(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None


class EmailValidationMixin(BaseSerializerMixin):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user with the given email was found.")

        return value


class UserStateMixin(BaseSerializerMixin):
    def validate(self, attrs):
        if (not self.user.is_active) and (not self.user.has_usable_password()):
            raise serializers.ValidationError("The user account has been disabled.")
        return attrs


class PasswordValidationMixin(BaseSerializerMixin):
    new_password = serializers.CharField(max_length=128)

    def validate_new_password(self, value):
        try:
            validate_password(value, self.user)
        except exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(serializer_error["non_field_errors"])

        return value


class ChangePasswordSerializer(PasswordValidationMixin):
    current_password = serializers.CharField(max_length=128)

    def validate_current_password(self, value):
        self.user = self.context["request"].user
        is_current_password_valid = self.user.check_password(value)
        if not is_current_password_valid:
            raise serializers.ValidationError("Invalid password.")
        return value


class ResetPasswordSerializer(EmailValidationMixin, UserStateMixin):
    pass


class ResetPasswordConfirmSerializer(PasswordValidationMixin):
    uid = serializers.CharField()
    token = serializers.CharField()

    def validate_uid(self, value):
        try:
            uid = decode_uid(value)
            self.user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError):
            raise serializers.ValidationError("Invalid user id or user doesn't exist.")

        return value

    def validate_token(self, value):
        is_valid_token = default_token_generator.check_token(self.user, value)
        if not is_valid_token:
            raise serializers.ValidationError("Invalid token for given user.")
        return value


class ResendActivationSerializer(EmailValidationMixin, UserStateMixin):
    def validate(self, attrs):
        super().validate(attrs)
        if self.user.is_active:
            raise serializers.ValidationError(
                "The user account has already been activated."
            )
        return attrs


class ActivationConfirmSerializer(EmailValidationMixin, UserStateMixin):
    code = serializers.CharField()

    def validate_code(self, value):
        if value != cache.get(key=self.initial_data["email"]):
            raise serializers.ValidationError("The given code is invalid.")
        return value


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source="key")

    class Meta:
        model = Token
        fields = ["token"]


class DeactivateUserSerializer(serializers.Serializer):
    def validate(self, attrs):
        user = self.context["user"]
        if not user.is_active:
            raise serializers.ValidationError(
                "The user account has already been deactivated."
            )
        return attrs


class ActivateUserSerializer(serializers.Serializer):
    def validate(self, attrs):
        user = self.context["user"]
        if user.is_active:
            raise serializers.ValidationError(
                "The user account has already been activated."
            )
        return attrs
