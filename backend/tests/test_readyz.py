"""Tests for GET /readyz readiness endpoint."""

import pytest
from rest_framework import status


@pytest.mark.django_db
def test_readyz_endpoint_database_check(api_client):
    response = api_client.get("/readyz")
    assert response.status_code in (status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE)
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "database" in data["checks"]
    assert data["checks"]["database"] == "pass"
