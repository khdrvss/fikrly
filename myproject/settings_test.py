"""
Test-specific Django settings
Use: python manage.py test --settings=myproject.settings_test
"""
from .settings import *

# Use in-memory SQLite for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_e2e.sqlite3",
    }
}

# Use local memory cache instead of Redis for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    }
}

# Disable Redis URL
REDIS_URL = None

# Speed up password hashing in tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable migrations for faster testing (optional)
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# MIGRATION_MODULES = DisableMigrations()

# Keep debug on in test settings so runserver can serve static assets for e2e.
DEBUG = True
TEMPLATE_DEBUG = True

# E2E/local test runner uses plain HTTP; disable HTTPS-only redirects/cookies here.
USE_HTTPS = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Required for test security
SECRET_KEY = "test-secret-key-for-testing-only-do-not-use-in-production"

# Disable external services in tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
