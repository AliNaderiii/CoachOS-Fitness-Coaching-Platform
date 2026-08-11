"""Tests for GET /healthz liveness endpoint."""

import pytest
from rest_framework import status


@pytest.mark.django_db
def test_healthz_endpoint_returns_200(api_client):
    response = api_client.get("/healthz")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "pass"
    assert "version" in data
    assert "timestamp" in data
    # Ensure no secret keys or database connection info leaked
    assert "secret" not in str(data).lower()
    assert "password" not in str(data).lower()
