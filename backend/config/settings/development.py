"""Development environment settings."""

import os

from .base import *  # noqa: F403

DEBUG = True

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "django-insecure-dev-only-secret-key-phase04-testing-only"
)

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = False
ALLOW_TENANT_HEADER_OVERRIDE = False
