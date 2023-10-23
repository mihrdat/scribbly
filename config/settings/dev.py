from .common import *

DEBUG = True

INSTALLED_APPS += [
    "debug_toolbar",
    "drf_spectacular",
    "django_extensions",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# To fix django-debug-toolbar disappearing when running application using Docker.
DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda request: True}

# Swagger
SPECTACULAR_SETTINGS = {
    "TITLE": "scribbly API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp4dev"
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_PORT = 25
