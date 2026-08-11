"""Tests for Security Headers Middleware."""

from django.http import HttpResponse
from django.test import RequestFactory

from apps.core.middleware import SecurityHeadersMiddleware


def test_security_headers_applied():
    factory = RequestFactory()
    request = factory.get("/healthz")

    middleware = SecurityHeadersMiddleware(lambda req: HttpResponse("OK"))
    response = middleware(request)

    assert response["X-Content-Type-Options"] == "nosniff"
    assert response["X-Frame-Options"] == "DENY"
    assert response["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in response["Permissions-Policy"]
    assert "Content-Security-Policy" in response
    assert "default-src 'self'" in response["Content-Security-Policy"]
