from django.shortcuts import render
from django.db.models import Q

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Room, Message
from .serializers import RoomSerializer, MessageSerializer


class RoomViewSet(
    ListModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    @action(methods=["GET"], detail=False)
    def lobby(self, request, *args, **kwargs):
        username = request.query_params.get("username", default="support")
        return render(request, "lobby.html", {"username": username})


class MessageViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room = Room.objects.get(pk=self.kwargs["room_pk"])
        return (
            super()
            .get_queryset()
            .filter(
                Q(user=self.request.user) & Q(recipient=room.participant)
                | Q(user=room.participant) & Q(recipient=self.request.user)
            )
            .filter(created_at__gte=room.created_at)
            .order_by("created_at")
        )
