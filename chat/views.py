from django.shortcuts import render

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
)
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import Room
from .serializers import RoomSerializer


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
        participant_id = request.query_params.get("participant_id", default=0)
        return render(request, "lobby.html", {"participant_id": participant_id})
