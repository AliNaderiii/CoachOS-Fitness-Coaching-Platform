import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_register_creates_user_and_session(api_client):
    url = "/api/v1/auth/register"
    payload = {
        "email": "coach.reza@example.com",
        "password": "SecurePass123!",
        "display_name": "Reza Rahimi",
        "preferred_locale": "fa-IR",
    }
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 201
    assert "user" in resp.data
    assert resp.data["user"]["email"] == "coach.reza@example.com"
    assert User.objects.filter(email="coach.reza@example.com").exists()


@pytest.mark.django_db
def test_login_success(api_client):
    User.objects.create_user(email="test@example.com", password="testpass123", display_name="Test")
    resp = api_client.post(
        "/api/v1/auth/login",
        {"email": "test@example.com", "password": "testpass123"},
        format="json",
    )
    assert resp.status_code == 200
    assert "user" in resp.data


@pytest.mark.django_db
def test_login_invalid(api_client):
    resp = api_client.post(
        "/api/v1/auth/login", {"email": "no@one.com", "password": "wrong"}, format="json"
    )
    assert resp.status_code == 401


@pytest.mark.django_db
def test_me_requires_auth(api_client):
    resp = api_client.get("/api/v1/auth/me")
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_forgot_password_non_enumerating(api_client):
    resp = api_client.post(
        "/api/v1/auth/forgot-password", {"email": "missing@coachos.com"}, format="json"
    )
    assert resp.status_code == 202
    assert "message_key" in resp.data
