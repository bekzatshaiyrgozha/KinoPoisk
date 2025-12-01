# Project modules
from settings.base import *
from settings.conf import POSTGRESQL_URL

# Third-party modules
import dj_database_url


DEBUG = False
ALLOWED_HOSTS = ["localhost:8000", "localhost"]

DATABASES = {
    'default': dj_database_url.config(
        default=POSTGRESQL_URL,
    )
}

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:80",
]
CORS_ALLOW_CREDENTIALS = True