import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = get_asgi_application()

app = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
    }
)
