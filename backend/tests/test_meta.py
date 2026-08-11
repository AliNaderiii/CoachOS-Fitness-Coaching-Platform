"""Tests for GET /api/v1/meta system metadata endpoint."""

import pytest
from rest_framework import status


@pytest.mark.django_db
def test_meta_endpoint_structure(api_client):
    response = api_client.get("/api/v1/meta")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["app_name"] == "CoachOS"
    assert data["api_version"] == "v1"
    assert "fa-IR" in data["locales"]
    assert "en-US" in data["locales"]
    assert "ar" not in str(data["locales"]).lower()
    assert data["default_locale"] == "fa-IR"
    assert data["auth_strategy"] == "cookie_session"
    assert "pwa_shell" in data["capabilities"]
