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
    def session(self, request, *args, **kwargs):
        return render(request, "session.html")
