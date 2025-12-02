# Project modules
from settings.base import *
from settings.conf import POSTGRESQL_URL

# Third-party modules
import dj_database_url


DEBUG = True
ALLOWED_HOSTS = ["localhost:8000", "localhost", "localhost:5173", "165.227.173.159"]

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
    "http://localhost:5173",
    "http://165.227.173.159"
]
CORS_ALLOW_CREDENTIALS = True