from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import ChatSerializers, MessageSerializers
from .models import Chat, Message


class ChatViewSet(ReadOnlyModelViewSet):
    queryset = Chat.objects.select_related("partner").all()
    serializer_class = ChatSerializers

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class MessageViewSet(ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializers

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(chat=self.kwargs["chat_pk"])
            .order_by("created_at")
        )
