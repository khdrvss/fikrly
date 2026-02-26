"""
E2E-specific Django settings
Use: python manage.py runserver --settings=myproject.settings_e2e
"""
from .settings import *


# Stable local DB for browser tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_e2e.sqlite3",
    }
}

# Local in-memory cache (avoid Redis dependency during e2e)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "e2e-cache",
    }
}

REDIS_URL = None

# Keep local e2e over HTTP
USE_HTTPS = False
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Local host support for playwright
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]
