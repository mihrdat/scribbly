from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserCreateOutPutSerializer,
    ChangePasswordSerializer,
)
from .pagination import DefaultLimitOffsetPagination

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
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)

        return self.retrieve(request, *args, **kwargs)

    @action(methods=["POST"], detail=False)
    def change_password(self, request, *args, **kwargs):
        current_user = self.get_current_user()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        current_user.set_password(serializer.data["new_password"])
        current_user.save(update_fields=["password"])

        return Response(status=status.HTTP_200_OK)

    def get_current_user(self):
        return self.request.user

    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            self.queryset = self.queryset.filter(pk=user.pk)
        return super().get_queryset()

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            self.serializer_class = UserCreateSerializer
        if self.action == "change_password":
            self.serializer_class = ChangePasswordSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = super().get_success_headers(serializer.data)
        serializer = UserCreateOutPutSerializer(user)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        return serializer.save()
