"""Tests for custom DRF exception handler (RFC 7807)."""

from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.views import APIView

from apps.core.exceptions import custom_exception_handler


class MockErrorView(APIView):
    def get(self, request):
        raise ValidationError({"field_a": ["Invalid input."]})


def test_custom_exception_handler_validation_error():
    from django.test import RequestFactory

    factory = RequestFactory()
    request = factory.get("/api/v1/test")
    request.correlation_id = "test-corr-id-001"

    exc = ValidationError({"email": ["Invalid email format"]})
    context = {"request": request}

    response = custom_exception_handler(exc, context)
    assert response is not None
    assert response.status_code == 400
    data = response.data

    assert data["type"] == "https://errors.coachos.io/error-validation_failed"
    assert data["title"] == "Validation Error"
    assert data["status"] == 400
    assert data["message_key"] == "error.validation_failed"
    assert data["correlation_id"] == "test-corr-id-001"
    assert "email" in data["field_errors"]


def test_custom_exception_handler_permission_denied():
    from django.test import RequestFactory

    factory = RequestFactory()
    request = factory.get("/api/v1/test")
    request.correlation_id = "test-corr-id-002"

    exc = PermissionDenied("You do not have access to this resource.")
    context = {"request": request}

    response = custom_exception_handler(exc, context)
    assert response is not None
    assert response.status_code == 403
    data = response.data

    assert data["title"] == "Permission Denied"
    assert data["status"] == 403
    assert data["message_key"] == "error.permission_denied"


def test_custom_exception_handler_unhandled_500():
    from django.test import RequestFactory

    factory = RequestFactory()
    request = factory.get("/api/v1/test")
    request.correlation_id = "test-corr-id-003"

    exc = RuntimeError("Unexpected internal crash")
    context = {"request": request}

    response = custom_exception_handler(exc, context)
    assert response is not None
    assert response.status_code == 500
    data = response.data

    assert data["title"] == "Internal Server Error"
    assert data["status"] == 500
    assert data["message_key"] == "error.internal_error"
    assert "Unexpected internal crash" not in data["detail"]
