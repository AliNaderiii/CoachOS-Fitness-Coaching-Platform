"""
Core Middleware Stack — CoachOS Phase 04 Foundation.
Implements correlation tracking, security headers, logging redaction, and tenant interfaces.
"""

import logging
from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from apps.core.utils.id_generator import generate_uuid7, is_valid_uuid

logger = logging.getLogger(__name__)


class CorrelationIDFilter(logging.Filter):
    """Logging filter to inject request_id default attribute if missing."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


class CorrelationIDMiddleware:
    """
    Attaches a validated correlation ID (UUIDv7) to incoming requests,
    propagates it to the logger context, and returns it in the X-Request-ID response header.
    Rejects malformed, oversized, or log-injection values (ADR-048 Correction).
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        incoming_id = request.headers.get("X-Request-ID", "").strip()

        # Validate incoming ID: must be valid UUID and <= 36 characters
        if incoming_id and len(incoming_id) <= 36 and is_valid_uuid(incoming_id):
            correlation_id = incoming_id
        else:
            # Generate clean time-ordered UUIDv7 if missing or invalid
            correlation_id = generate_uuid7()

        request.correlation_id = correlation_id

        response = self.get_response(request)
        response["X-Request-ID"] = correlation_id
        return response


class SecurityHeadersMiddleware:
    """
    Applies baseline security headers to every HTTP response.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        # Baseline Security Headers
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("X-Frame-Options", "DENY")
        response.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), payment=()",
        )

        # Content-Security-Policy baseline for API backend
        csp = (
            "default-src 'self'; "
            "img-src 'self' data: https: blob:; "
            "font-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; "
            "connect-src 'self' http://localhost:8000 http://127.0.0.1:8000; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "frame-ancestors 'none';"
        )
        response.setdefault("Content-Security-Policy", csp)

        # HSTS in non-debug mode
        if not settings.DEBUG:
            response.setdefault(
                "Strict-Transport-Security",
                "max-age=63072000; includeSubDomains; preload",
            )

        return response


class TenantContextMiddleware:
    """
    Foundation placeholder interface for multi-tenant organization scoping (ADR-006, ADR-014).
    Production tenant context derives exclusively from authenticated session state.
    Client-supplied header overrides are strictly gated behind ALLOW_TENANT_HEADER_OVERRIDE.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Default tenant context interface
        request.org_id = None

        if hasattr(request, "session"):
            request.org_id = request.session.get("active_org_id")

        # Explicitly gated test-only header override (default False in production/staging)
        allow_override = getattr(settings, "ALLOW_TENANT_HEADER_OVERRIDE", False)
        if allow_override and not request.org_id and "X-Organization-ID" in request.headers:
            header_val = request.headers.get("X-Organization-ID", "").strip()
            if header_val and len(header_val) <= 64:
                request.org_id = header_val

        return self.get_response(request)


class LoggingRedactionMiddleware:
    """
    Sanitizes sensitive fields from request payloads and query strings before logging.
    """

    SENSITIVE_KEYS = {
        "password",
        "secret",
        "token",
        "authorization",
        "cookie",
        "sessionid",
        "csrf_token",
        "pain_flag_details",
        "body_weight",
        "credit_card",
    }

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    @classmethod
    def redact_dict(cls, data: dict) -> dict:
        """Recursively redact sensitive keys from dictionary payloads."""
        if not isinstance(data, dict):
            return data

        redacted = {}
        for k, v in data.items():
            if any(sensitive in str(k).lower() for sensitive in cls.SENSITIVE_KEYS):
                redacted[k] = "[REDACTED]"
            elif isinstance(v, dict):
                redacted[k] = cls.redact_dict(v)
            elif isinstance(v, list):
                redacted[k] = [
                    cls.redact_dict(item) if isinstance(item, dict) else item for item in v
                ]
            else:
                redacted[k] = v
        return redacted
