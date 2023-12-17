from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import ChatSerializers
from .models import Chat


class ChatViewSet(ReadOnlyModelViewSet):
    queryset = Chat.objects.select_related("partner").all()
    serializer_class = ChatSerializers

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
