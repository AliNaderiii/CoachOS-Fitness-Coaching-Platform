"""Tests for Core Middleware Pipeline (Correlation ID validation & Tenant Context Safety)."""

import uuid

from django.http import HttpResponse
from django.test import RequestFactory, override_settings

from apps.core.middleware import (
    CorrelationIDMiddleware,
    LoggingRedactionMiddleware,
    TenantContextMiddleware,
)


def test_correlation_id_middleware_generates_header_when_missing():
    factory = RequestFactory()
    request = factory.get("/healthz")

    middleware = CorrelationIDMiddleware(lambda req: HttpResponse("OK"))
    response = middleware(request)

    assert "X-Request-ID" in response
    assert len(response["X-Request-ID"]) > 10
    assert hasattr(request, "correlation_id")


def test_correlation_id_middleware_preserves_valid_uuid():
    factory = RequestFactory()
    valid_uuid = str(uuid.uuid4())
    request = factory.get("/healthz", HTTP_X_REQUEST_ID=valid_uuid)

    middleware = CorrelationIDMiddleware(lambda req: HttpResponse("OK"))
    response = middleware(request)

    assert response["X-Request-ID"] == valid_uuid
    assert request.correlation_id == valid_uuid


def test_correlation_id_middleware_replaces_invalid_malformed_id():
    factory = RequestFactory()
    # Malformed XSS / injection payload
    malformed_id = "<script>alert(1)</script>"
    request = factory.get("/healthz", HTTP_X_REQUEST_ID=malformed_id)

    middleware = CorrelationIDMiddleware(lambda req: HttpResponse("OK"))
    response = middleware(request)

    # Must NOT use malformed ID
    assert response["X-Request-ID"] != malformed_id
    assert "<script>" not in response["X-Request-ID"]
    assert len(response["X-Request-ID"]) == 36


def test_correlation_id_middleware_replaces_overly_long_id():
    factory = RequestFactory()
    long_id = "a" * 200
    request = factory.get("/healthz", HTTP_X_REQUEST_ID=long_id)

    middleware = CorrelationIDMiddleware(lambda req: HttpResponse("OK"))
    response = middleware(request)

    assert response["X-Request-ID"] != long_id
    assert len(response["X-Request-ID"]) == 36


@override_settings(ALLOW_TENANT_HEADER_OVERRIDE=False)
def test_tenant_context_middleware_rejects_header_override_in_production_mode():
    """Verify arbitrary client X-Organization-ID is ignored when override is disabled."""
    factory = RequestFactory()
    request = factory.get("/healthz", HTTP_X_ORGANIZATION_ID="rogue-tenant-999")

    middleware = TenantContextMiddleware(lambda req: HttpResponse("OK"))
    middleware(request)

    # In production mode (ALLOW_TENANT_HEADER_OVERRIDE=False), header cannot set org_id
    assert request.org_id is None


@override_settings(ALLOW_TENANT_HEADER_OVERRIDE=True)
def test_tenant_context_middleware_allows_header_in_explicit_test_mode():
    factory = RequestFactory()
    request = factory.get("/healthz", HTTP_X_ORGANIZATION_ID="org-tenant-001")

    middleware = TenantContextMiddleware(lambda req: HttpResponse("OK"))
    middleware(request)

    assert request.org_id == "org-tenant-001"


def test_logging_redaction_middleware_scrubs_secrets():
    payload = {
        "user": "athlete1",
        "password": "super-secret-password-123",
        "nested": {
            "token": "secret-token-abc",
            "safe_field": "public_name",
        },
    }
    redacted = LoggingRedactionMiddleware.redact_dict(payload)
    assert redacted["password"] == "[REDACTED]"
    assert redacted["nested"]["token"] == "[REDACTED]"
    assert redacted["nested"]["safe_field"] == "public_name"
