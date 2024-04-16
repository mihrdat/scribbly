from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/socket-server/<int:contact_id>/", consumers.ChatConsumer.as_asgi()),
]
