# Project modules
from settings.base import *
from settings.conf import POSTGRESQL_URL

# Third-party modules
import dj_database_url


DEBUG = False
ALLOWED_HOSTS = ["localhost:8000"]

DATABASES = {
    'default': dj_database_url.config(
        default=POSTGRESQL_URL,
    )
}

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'