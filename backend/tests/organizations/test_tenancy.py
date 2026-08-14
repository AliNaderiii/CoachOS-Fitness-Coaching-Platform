import pytest

from apps.organizations.models import Invitation, Membership, Organization


@pytest.mark.django_db
def test_create_org_creates_owner_membership_and_primary_location(api_client):
    # Register + login
    api_client.post(
        "/api/v1/auth/register",
        {"email": "owner@example.com", "password": "SecurePass123!", "display_name": "Owner"},
        format="json",
    )

    resp = api_client.post(
        "/api/v1/organizations/",
        {
            "name": "Alborz Fitness",
            "slug": "alborz-fitness",
            "primary_location": {"name": "Main Gym", "city": "Tehran"},
        },
        format="json",
    )

    assert resp.status_code == 201
    org_id = resp.data["id"]
    org = Organization.objects.get(id=org_id)
    assert org.owner_user.email == "owner@example.com"
    assert org.locations.filter(is_primary=True).exists()
    assert (
        Membership.objects.filter(
            user=org.owner_user, organization=org, role="owner", status="active"
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_cross_tenant_org_access_denied(api_client):
    # Owner 1 creates org
    api_client.post(
        "/api/v1/auth/register",
        {"email": "owner1@ex.com", "password": "SecurePass123!", "display_name": "O1"},
        format="json",
    )
    create1 = api_client.post(
        "/api/v1/organizations/", {"name": "Org1", "slug": "org1"}, format="json"
    )
    assert create1.status_code == 201
    org1_id = create1.data["id"]

    # Owner 2 registers + creates separate org
    api_client.post("/api/v1/auth/logout", {}, format="json")
    api_client.post(
        "/api/v1/auth/register",
        {"email": "owner2@ex.com", "password": "SecurePass123!", "display_name": "O2"},
        format="json",
    )
    create2 = api_client.post(
        "/api/v1/organizations/", {"name": "Org2", "slug": "org2"}, format="json"
    )
    assert create2.status_code == 201

    # Owner2 must NOT be able to access Org1 (real cross-tenant)
    resp = api_client.get(f"/api/v1/organizations/{org1_id}")
    assert resp.status_code in (403, 404)

    # Also verify member list cross-tenant denied
    resp_members = api_client.get(f"/api/v1/organizations/{org1_id}/members")
    assert resp_members.status_code in (403, 404)


@pytest.mark.django_db
def test_member_list_role_visibility(api_client):
    # Owner creates org + invites coach + athlete
    api_client.post(
        "/api/v1/auth/register",
        {"email": "owner@org.com", "password": "SecurePass123!", "display_name": "Owner"},
        format="json",
    )
    create_resp = api_client.post(
        "/api/v1/organizations/", {"name": "RoleTestOrg", "slug": "roletest"}, format="json"
    )
    assert create_resp.status_code == 201
    org_id = create_resp.data["id"]

    # Create coach user via register (simulate invite flow with token later)
    # For test: create users directly in DB + memberships
    from apps.identity.models import User

    coach = User.objects.create_user(
        email="coach@org.com", password="SecurePass123!", display_name="Coach"
    )
    athlete = User.objects.create_user(
        email="athlete@org.com", password="SecurePass123!", display_name="Athlete"
    )

    org = Organization.objects.get(id=org_id)
    Membership.objects.create(user=coach, organization=org, role="coach", status="active")
    Membership.objects.create(user=athlete, organization=org, role="athlete", status="active")

    # Login as coach
    api_client.post("/api/v1/auth/logout", {}, format="json")
    login_resp = api_client.post(
        "/api/v1/auth/login",
        {"email": "coach@org.com", "password": "SecurePass123!"},
        format="json",
    )
    assert login_resp.status_code == 200

    # Coach should see only self (assignment deferred)
    members_resp = api_client.get(f"/api/v1/organizations/{org_id}/members")
    assert members_resp.status_code == 200
    # Coach sees only own membership (per current implementation)
    assert len(members_resp.data.get("members", [])) == 1
    assert coach.id in [m.get("user_id") for m in members_resp.data.get("members", [])]

    # Login as owner
    api_client.post("/api/v1/auth/logout", {}, format="json")
    api_client.post(
        "/api/v1/auth/login",
        {"email": "owner@org.com", "password": "SecurePass123!"},
        format="json",
    )
    owner_members = api_client.get(f"/api/v1/organizations/{org_id}/members")
    assert owner_members.status_code == 200
    assert len(owner_members.data.get("members", [])) >= 3  # owner + coach + athlete

    # Athlete sees self only
    api_client.post("/api/v1/auth/logout", {}, format="json")
    api_client.post(
        "/api/v1/auth/login",
        {"email": "athlete@org.com", "password": "SecurePass123!"},
        format="json",
    )
    ath_members = api_client.get(f"/api/v1/organizations/{org_id}/members")
    assert ath_members.status_code == 200
    assert len(ath_members.data.get("members", [])) == 1


@pytest.mark.django_db
def test_owner_cannot_suspend_only_active_owner(api_client):
    api_client.post(
        "/api/v1/auth/register",
        {"email": "soleowner@org.com", "password": "SecurePass123!", "display_name": "Sole"},
        format="json",
    )
    create = api_client.post(
        "/api/v1/organizations/", {"name": "SoleOrg", "slug": "soleorg"}, format="json"
    )
    assert create.status_code == 201
    org_id = create.data["id"]
    org = Organization.objects.get(id=org_id)

    # Find owner membership
    owner_mem = Membership.objects.get(organization=org, role="owner", status="active")

    # Attempt to suspend the only owner
    resp = api_client.patch(
        f"/api/v1/organizations/{org_id}/members/{owner_mem.id}",
        {"status": "suspended"},
        format="json",
    )
    assert resp.status_code == 409
    assert "owner" in str(resp.data).lower() or "transfer" in str(resp.data).lower()


@pytest.mark.django_db
def test_invitation_email_binding_and_status_transition(api_client):
    import hashlib
    import secrets
    from datetime import timedelta as py_timedelta

    from django.utils import timezone as dj_tz

    from apps.identity.models import User as IdentityUser

    # Owner creates org
    api_client.post(
        "/api/v1/auth/register",
        {"email": "invowner@ex.com", "password": "SecurePass123!", "display_name": "InvOwner"},
        format="json",
    )
    org_create = api_client.post(
        "/api/v1/organizations/", {"name": "InvOrg", "slug": "invorg"}, format="json"
    )
    assert org_create.status_code == 201
    org_id = org_create.data["id"]
    org = Organization.objects.get(id=org_id)

    # Create a fresh invitation directly (bypass view to obtain raw token for test)
    raw_token = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    inv = Invitation.objects.create(
        organization=org,
        invited_by=org.owner_user,
        email="invited2@ex.com",
        role="athlete",
        token_hash=token_hash,
        expires_at=dj_tz.now() + py_timedelta(days=7),
    )

    # Register the target user supplying the raw invitation_token
    api_client.post("/api/v1/auth/logout", {}, format="json")
    reg_resp = api_client.post(
        "/api/v1/auth/register",
        {
            "email": "invited2@ex.com",
            "password": "SecurePass123!",
            "display_name": "Invited",
            "invitation_token": raw_token,
        },
        format="json",
    )
    assert reg_resp.status_code == 201

    # Verify membership was created with active status (transitioned from invited if existed)
    user = IdentityUser.objects.get(email="invited2@ex.com")
    mem = Membership.objects.filter(user=user, organization=org, role="athlete").first()
    assert mem is not None
    assert mem.status == "active"

    # Invitation should be marked accepted
    inv.refresh_from_db()
    assert inv.accepted_at is not None
