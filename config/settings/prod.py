from .common import *

DEBUG = False

ALLOWED_HOSTS = [".vercel.app"]

REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
}

MINIO_STORAGE_USE_HTTPS = True
