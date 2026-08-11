"""Staging environment settings — Strict fail-closed validation."""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

DEBUG = False

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY or "insecure" in SECRET_KEY.lower() or len(SECRET_KEY) < 20:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY environment variable is mandatory and cannot be an insecure default in staging."
    )

if not os.environ.get("DATABASE_URL"):
    raise ImproperlyConfigured(
        "DATABASE_URL environment variable is mandatory in staging. SQLite fallback is prohibited."
    )

raw_hosts = os.environ.get("ALLOWED_HOSTS", "")
if not raw_hosts or "*" in raw_hosts:
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS must be explicitly configured without wildcards in staging."
    )
ALLOWED_HOSTS = [h.strip() for h in raw_hosts.split(",") if h.strip()]

raw_cors = os.environ.get("CORS_ALLOWED_ORIGINS", "")
if not raw_cors:
    raise ImproperlyConfigured("CORS_ALLOWED_ORIGINS must be explicitly configured in staging.")
CORS_ALLOWED_ORIGINS = [o.strip() for o in raw_cors.split(",") if o.strip()]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

ALLOW_TENANT_HEADER_OVERRIDE = False
