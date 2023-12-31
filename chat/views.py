from django.shortcuts import get_object_or_404, render

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .serializers import RoomSerializers, MessageSerializers
from .models import Room, Message


class RoomViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Room.objects.select_related("partner").all()
    serializer_class = RoomSerializers
    permission_classes = [IsAuthenticated]

    @action(methods=["GET"], detail=True)
    def history(self, request, *args, **kwargs):
        return render(request, "lobby.html")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class MessageViewSet(GenericViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room = get_object_or_404(Room, pk=self.kwargs["room_pk"])
        return room.messages.all().order_by("created_at")
