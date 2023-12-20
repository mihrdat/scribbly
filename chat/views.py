from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from .serializers import RoomSerializers, MessageSerializers
from .models import Room, Message


class RoomViewSet(ReadOnlyModelViewSet):
    queryset = Room.objects.select_related("partner").all()
    serializer_class = RoomSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class MessageViewSet(ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room = get_object_or_404(Room, pk=self.kwargs["room_pk"])
        return room.messages.all().order_by("created_at")
