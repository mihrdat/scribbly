from datetime import timedelta
from .common import *
from config.email.dev import *

DEBUG = True

INSTALLED_APPS += [
    "debug_toolbar",
    "django_extensions",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# To fix django-debug-toolbar disappearing when running application using Docker.
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda request: True,
}

SIMPLE_JWT = {
    **SIMPLE_JWT,
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=14),
}

MINIO_STORAGE_USE_HTTPS = False

BASE_BACKEND_URL = "http://127.0.0.1:8000"
