"""
Test-specific Django settings
Use: python manage.py test --settings=myproject.settings_test
"""
from .settings import *

# Use in-memory SQLite for faster tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
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

# Keep debug off in tests
DEBUG = False
TEMPLATE_DEBUG = False

# Required for test security
SECRET_KEY = "test-secret-key-for-testing-only-do-not-use-in-production"

# Disable external services in tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
