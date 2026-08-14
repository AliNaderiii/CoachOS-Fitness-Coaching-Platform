from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from apps.identity.models import PasswordResetToken
from apps.organizations.models import Invitation, Membership, Organization

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
    # Minimal memberships returned (full effective-permissions + active-org context deferred)
    assert "memberships" in resp.data
    assert isinstance(resp.data["memberships"], list)


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
    from apps.identity import views as identity_views

    # Clear capture deterministically
    identity_views._captured_reset_tokens.clear()

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

    # Request reset using real forgot-password path (exercises token generation)
    resp = api_client.post(
        "/api/v1/auth/forgot-password", {"email": "resetuser@example.com"}, format="json"
    )
    assert resp.status_code == 202

    # Deterministic capture seam: exactly one token must have been generated
    assert len(identity_views._captured_reset_tokens) == 1, (
        "Exactly one reset token must be captured from forgot-password"
    )
    raw = identity_views._captured_reset_tokens[-1]
    assert raw is not None and len(raw) > 20  # cryptographically sized

    # Valid reset using the *captured* generated token (no manufactured tokens)
    resp = api_client.post(
        f"/api/v1/auth/reset-password/{raw}", {"new_password": "NewSecurePass456!"}, format="json"
    )
    assert resp.status_code == 200

    # Verify token was marked used
    prt = (
        PasswordResetToken.objects.filter(user=user, used_at__isnull=False)
        .order_by("-used_at")
        .first()
    )
    assert prt is not None and prt.used_at is not None
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

    # Cleanup
    identity_views._captured_reset_tokens.clear()


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


@pytest.mark.django_db
def test_password_reset_invalidates_all_sessions(api_client):

    from rest_framework.test import APIClient

    from apps.identity import views as identity_views

    # Clear deterministically
    identity_views._captured_reset_tokens.clear()

    # Register user (establishes first session)
    api_client.post(
        "/api/v1/auth/register",
        {"email": "multi@example.com", "password": "SecurePass123!", "display_name": "Multi"},
        format="json",
    )

    # Create second client (second session) and login
    client2 = APIClient()
    resp2 = client2.post(
        "/api/v1/auth/login",
        {"email": "multi@example.com", "password": "SecurePass123!"},
        format="json",
    )
    assert resp2.status_code == 200

    # Verify both can access /me (authenticated)
    me1 = api_client.get("/api/v1/auth/me")
    me2 = client2.get("/api/v1/auth/me")
    assert me1.status_code == 200
    assert me2.status_code == 200

    # Request reset using the real forgot-password path (exercises generation + test seam)
    resp_fp = api_client.post(
        "/api/v1/auth/forgot-password", {"email": "multi@example.com"}, format="json"
    )
    assert resp_fp.status_code == 202

    # Deterministic: assert exactly one captured token
    assert len(identity_views._captured_reset_tokens) == 1, (
        "Exactly one reset token must be captured"
    )
    raw = identity_views._captured_reset_tokens[-1]
    assert raw is not None

    # Perform reset using the captured (real generated) token only
    resp = api_client.post(
        f"/api/v1/auth/reset-password/{raw}", {"new_password": "NewSecurePass999!"}, format="json"
    )
    assert resp.status_code == 200

    # Old sessions should be dead (both clients)
    me1_after = api_client.get("/api/v1/auth/me")
    me2_after = client2.get("/api/v1/auth/me")
    assert me1_after.status_code in (401, 403)
    assert me2_after.status_code in (401, 403)

    # New login with new password succeeds
    new_client = APIClient()
    login_resp = new_client.post(
        "/api/v1/auth/login",
        {"email": "multi@example.com", "password": "NewSecurePass999!"},
        format="json",
    )
    assert login_resp.status_code == 200
    me_new = new_client.get("/api/v1/auth/me")
    assert me_new.status_code == 200

    # Cleanup
    identity_views._captured_reset_tokens.clear()


@pytest.mark.django_db
def test_register_with_invitation_is_atomic_rollback_on_membership_failure(api_client):
    """Prove that when invitation binding fails after user creation starts,
    the entire registration tx rolls back (no user, no membership, invitation untouched).
    """

    import hashlib

    from django.utils import timezone as dj_tz

    # Owner creates org + invitation for a specific email
    api_client.post(
        "/api/v1/auth/register",
        {"email": "orgowner@ex.com", "password": "SecurePass123!", "display_name": "Owner"},
        format="json",
    )
    create = api_client.post(
        "/api/v1/organizations/", {"name": "AtomicOrg", "slug": "atomicorg"}, format="json"
    )
    assert create.status_code == 201
    org_id = create.data["id"]
    org = Organization.objects.get(id=org_id)

    raw_token = "atomic-inv-token-1234567890123456789012345678901234"
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    inv = Invitation.objects.create(
        organization=org,
        invited_by=org.owner_user,
        email="inviteduser@ex.com",
        role="athlete",
        token_hash=token_hash,
        expires_at=dj_tz.now() + dj_tz.timedelta(days=1),
    )

    # Simulate failure inside the invitation binding block (after user create but before commit)
    with patch("apps.organizations.models.Membership.objects.get_or_create") as mock_get_create:
        mock_get_create.side_effect = Exception("Simulated DB failure during membership")

        resp = api_client.post(
            "/api/v1/auth/register",
            {
                "email": "inviteduser@ex.com",
                "password": "SecurePass123!",
                "display_name": "Invited",
                "invitation_token": raw_token,
            },
            format="json",
        )
        # The view should surface the error, but crucially: no partial state
        assert resp.status_code >= 400

    # Rollback verification: no user created for the invited email
    assert not User.objects.filter(email="inviteduser@ex.com").exists()

    # Invitation must remain un-accepted (no partial commit)
    inv.refresh_from_db()
    assert inv.accepted_at is None

    # No membership for that user
    assert not Membership.objects.filter(
        organization=org, user__email="inviteduser@ex.com"
    ).exists()

    # Happy path still works (no side effects from failed attempt)
    resp2 = api_client.post(
        "/api/v1/auth/register",
        {
            "email": "inviteduser@ex.com",
            "password": "SecurePass123!",
            "display_name": "Invited",
            "invitation_token": raw_token,
        },
        format="json",
    )
    assert resp2.status_code == 201
    user = User.objects.get(email="inviteduser@ex.com")
    mem = Membership.objects.filter(user=user, organization=org, role="athlete").first()
    assert mem is not None
    assert mem.status == "active"
    inv.refresh_from_db()
    assert inv.accepted_at is not None
