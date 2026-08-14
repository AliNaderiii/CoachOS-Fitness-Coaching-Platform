import hashlib

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone as dj_timezone

from apps.identity.models import PasswordResetToken

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
    User.objects.create_user(
        email="test@example.com", password="SecurePass123!", display_name="Test"
    )
    resp = api_client.post(
        "/api/v1/auth/login",
        {"email": "test@example.com", "password": "SecurePass123!"},
        format="json",
    )
    assert resp.status_code == 200
    assert "user" in resp.data


@pytest.mark.django_db
def test_login_invalid(api_client):
    resp = api_client.post(
        "/api/v1/auth/login", {"email": "no@one.com", "password": "wrongpass"}, format="json"
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


@pytest.mark.django_db
def test_password_reset_full_lifecycle(api_client):
    # Register user
    api_client.post(
        "/api/v1/auth/register",
        {
            "email": "resetuser@example.com",
            "password": "SecurePass123!",
            "display_name": "ResetUser",
        },
        format="json",
    )
    user = User.objects.get(email="resetuser@example.com")

    # Request reset
    resp = api_client.post(
        "/api/v1/auth/forgot-password", {"email": "resetuser@example.com"}, format="json"
    )
    assert resp.status_code == 202

    # Simulate token (in real flow email would contain it; here we create)
    raw = "testtoken12345678901234567890123456789012345678"
    th = hashlib.sha256(raw.encode()).hexdigest()
    prt = PasswordResetToken.objects.create(
        user=user,
        token_hash=th,
        expires_at=dj_timezone.now() + dj_timezone.timedelta(minutes=15),
    )

    # Valid reset
    resp = api_client.post(
        f"/api/v1/auth/reset-password/{raw}", {"new_password": "NewSecurePass456!"}, format="json"
    )
    assert resp.status_code == 200
    prt.refresh_from_db()
    assert prt.used_at is not None
    user.refresh_from_db()
    assert user.check_password("NewSecurePass456!")

    # Replay should fail
    resp = api_client.post(
        f"/api/v1/auth/reset-password/{raw}", {"new_password": "AnotherPass789!"}, format="json"
    )
    assert resp.status_code == 400

    # Invalid token
    resp = api_client.post(
        "/api/v1/auth/reset-password/badtoken", {"new_password": "x"}, format="json"
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_logout_invalidates_session(api_client):
    api_client.post(
        "/api/v1/auth/register",
        {"email": "logout@example.com", "password": "SecurePass123!", "display_name": "L"},
        format="json",
    )
    # Login already happened in register
    resp = api_client.post("/api/v1/auth/logout", {}, format="json")
    assert resp.status_code == 204
    # Subsequent me should be unauthorized
    resp = api_client.get("/api/v1/auth/me")
    assert resp.status_code in (401, 403)
