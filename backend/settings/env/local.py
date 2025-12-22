# Project modules
from settings.base import REST_FRAMEWORK
from settings.base import *  # noqa F401

DEBUG = True
ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    REST_FRAMEWORK.setdefault(
        "DEFAULT_RENDERER_CLASSES", ["rest_framework.renderers.JSONRenderer"]
    )
    if (
        "rest_framework.renderers.BrowsableAPIRenderer"
        not in REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"]
    ):
        REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].append(
            "rest_framework.renderers.BrowsableAPIRenderer"
        )
