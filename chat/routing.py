from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/socket-server/<int:participant_id>/", consumers.ChatConsumer.as_asgi()),
]
