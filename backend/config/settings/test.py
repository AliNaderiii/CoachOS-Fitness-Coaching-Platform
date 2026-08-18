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

# Enable test seam to capture raw reset tokens so actual forgot-password path is exercised
# (raw token never appears in prod responses/logs/audit)
TEST_CAPTURE_RESET_TOKENS = True

# Phase 08: enable the deterministic local fake providers for tests only.
# No real credentials exist anywhere in the repository.
COMMUNICATION_FAKE_PROVIDERS_ENABLED = True
# Deterministic, network-free Phase 10 billing test provider.
BILLING_DEFAULT_PROVIDER = "fake"
BILLING_ALLOW_FAKE_PROVIDER = True
BILLING_FAKE_WEBHOOK_SECRET = "phase10-test-webhook-secret"
BILLING_FRONTEND_BASE_URL = "https://app.test.coachos.invalid"
BILLING_HOSTED_URL_ALLOWED_HOSTS = [
    "payments.test.coachos.invalid",
    "invoices.test.coachos.invalid",
]
BILLING_WEBHOOK_TOLERANCE_SECONDS = 300
# Phase 11: enable the Copilot in the test environment (production default is OFF).
# Tests override these values per-case to exercise kill-switch and budget paths.
COPILOT_ENABLED = True
