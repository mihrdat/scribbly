from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token

from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    ResetPasswordConfirmSerializer,
    TokenSerializer,
    ResendActivationSerializer,
)
from .pagination import DefaultLimitOffsetPagination
from .email import PasswordResetEmail, ActivationEmail
from .utils import generate_random_code
from .constants import CacheTimeouts

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultLimitOffsetPagination

    @action(methods=["GET", "PUT", "PATCH"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_current_user
        if request.method == "PUT":
            return self.update(request, *args, **kwargs)
        if request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)

    @transaction.atomic
    @action(methods=["POST"], detail=False)
    def change_password(self, request, *args, **kwargs):
        user = self.get_current_user()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        # Log out user from other systems
        Token.objects.get(user=user).delete()

        new_token = Token.objects.create(user=user)
        serializer = TokenSerializer(new_token)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data["email"])
        context = {"user": user}

        PasswordResetEmail(request, context).send(to=[user.email])

        return Response(status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        user.set_password(serializer.validated_data["new_password"])
        user.last_login = timezone.now()
        user.save(update_fields=["password", "last_login"])

        return Response(status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def resend_activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        code = generate_random_code()
        cache.set(key=user.pk, value=code, timeout=CacheTimeouts.WEEK)

        context = {"username": user.username, "code": code}
        ActivationEmail(request, context).send(to=[user.email])

        return Response(status=status.HTTP_200_OK)

    def get_current_user(self):
        return self.request.user

    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            self.queryset = self.queryset.filter(pk=user.pk)
        return super().get_queryset()

    def get_permissions(self):
        if self.action in [
            "create",
            "reset_password",
            "reset_password_confirm",
            "resend_activation",
        ]:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            self.serializer_class = UserCreateSerializer
        if self.action in ["update", "partial_update"]:
            self.serializer_class = UserUpdateSerializer
        if self.action == "change_password":
            self.serializer_class = ChangePasswordSerializer
        if self.action == "reset_password":
            self.serializer_class = ResetPasswordSerializer
        if self.action == "reset_password_confirm":
            self.serializer_class = ResetPasswordConfirmSerializer
        if self.action == "resend_activation":
            self.serializer_class = ResendActivationSerializer
        return super().get_serializer_class()
