from .base import *  # noqa: F403  (test settings deliberately inherit everything)

DEBUG = True
SECRET_KEY = "test-secret-key-only-for-tests"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Use in-memory cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Disable rate limiting enforcement in tests unless explicit
ALLOW_TENANT_HEADER_OVERRIDE = True

# Faster password hasher for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable CSRF for API test client where needed
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
