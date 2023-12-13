from django.core import exceptions
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
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "token"]

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

    def get_token(self, user):
        return Token.objects.create(user=user).key


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]


class EmailValidationMixin(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            self.user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user with the given email was found.")

        return value


class UserActivationMixin(serializers.Serializer):
    def validate(self, attrs):
        if (not self.user.is_active) and (not self.user.has_usable_password()):
            raise serializers.ValidationError("User account is disabled.")

        return attrs


class PasswordValidationMixin:
    def is_valid_password(self, value, user, raise_exception=False):
        try:
            validate_password(value, user)
        except exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            if raise_exception:
                raise serializers.ValidationError(serializer_error["non_field_errors"])
            return False

        return True


class ChangePasswordSerializer(PasswordValidationMixin, serializers.Serializer):
    current_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)

    def validate_current_password(self, value):
        is_current_password_valid = self.context["request"].user.check_password(value)
        if not is_current_password_valid:
            raise serializers.ValidationError("Invalid password.")

        return value

    def validate_new_password(self, value):
        user = self.context["request"].user
        self.is_valid_password(value, user, raise_exception=True)
        return value


class ResetPasswordConfirmSerializer(PasswordValidationMixin, serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(max_length=128)

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

    def validate_new_password(self, value):
        self.is_valid_password(value, self.user, raise_exception=True)
        return value


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source="key")

    class Meta:
        model = Token
        fields = ["token"]


class ResendActivationSerializer(EmailValidationMixin, UserActivationMixin):
    def validate(self, attrs):
        super().validate(attrs)

        if self.user.is_active:
            raise serializers.ValidationError("User account is already active.")

        return attrs


class ResetPasswordSerializer(EmailValidationMixin, UserActivationMixin):
    pass
