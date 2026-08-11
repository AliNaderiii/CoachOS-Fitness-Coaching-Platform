"""Tests for RFC 7807 error envelopes and sanitization."""

import pytest
from rest_framework import status


@pytest.mark.django_db
def test_404_error_envelope_format(api_client):
    response = api_client.get("/api/v1/non-existent-path")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "type" in data
    assert "title" in data
    assert "status" in data
    assert data["status"] == 404
    assert "detail" in data
    assert "instance" in data
    assert "message_key" in data
    assert data["message_key"] == "error.not_found"
    assert "correlation_id" in data
    # Ensure no internal server file paths or tracebacks leaked
    assert "traceback" not in str(data).lower()
    assert 'file "' not in str(data).lower()
