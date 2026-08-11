"""Test environment settings."""

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "django-insecure-test-key-for-pytest-execution-only"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
