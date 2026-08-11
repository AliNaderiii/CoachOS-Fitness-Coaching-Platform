"""Tests for Core Middleware Pipeline."""

from django.test import RequestFactory

from apps.core.middleware import (
    CorrelationIDMiddleware,
    LoggingRedactionMiddleware,
    TenantContextMiddleware,
)


def test_correlation_id_middleware_generates_header():
    factory = RequestFactory()
    request = factory.get("/healthz")

    middleware = CorrelationIDMiddleware(lambda req: req)
    # Simulate view returning response
    from django.http import HttpResponse

    def mock_view(req):
        return HttpResponse("OK")

    middleware = CorrelationIDMiddleware(mock_view)
    response = middleware(request)

    assert "X-Request-ID" in response
    assert len(response["X-Request-ID"]) > 10
    assert hasattr(request, "correlation_id")


def test_correlation_id_middleware_preserves_existing_header():
    factory = RequestFactory()
    custom_id = "test-request-id-12345"
    request = factory.get("/healthz", HTTP_X_REQUEST_ID=custom_id)

    from django.http import HttpResponse

    middleware = CorrelationIDMiddleware(lambda req: HttpResponse("OK"))
    response = middleware(request)

    assert response["X-Request-ID"] == custom_id
    assert request.correlation_id == custom_id


def test_tenant_context_middleware_extracts_org():
    factory = RequestFactory()
    request = factory.get("/healthz", HTTP_X_ORGANIZATION_ID="org-tenant-001")

    from django.http import HttpResponse

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
