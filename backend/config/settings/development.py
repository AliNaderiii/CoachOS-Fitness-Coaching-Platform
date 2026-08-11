"""Development environment settings."""

from .base import *  # noqa: F403

DEBUG = True

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = False
