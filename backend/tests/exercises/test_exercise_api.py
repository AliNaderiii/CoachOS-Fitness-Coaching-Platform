import pytest
from django.core.exceptions import ValidationError
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.audit.models import AuditEvent
from apps.exercises.models import (
    Exercise,
    ExerciseTranslation,
    MediaAsset,
    MediaRights,
)
from apps.identity.models import User
from apps.organizations.models import Membership, Organization


def make_org(slug="alpha"):
    owner = User.objects.create_user(email=f"owner-{slug}@example.com", password="x")
    org = Organization.objects.create(name=slug.title(), slug=slug, owner_user=owner)
    Membership.objects.create(user=owner, organization=org, role="owner", status="active")
    return org, owner


def exercise_payload(org_id):
    return {
        "org_id": org_id,
        "movement_pattern": "squat",
        "difficulty": "intermediate",
        "primary_muscles": ["quadriceps", "glutes"],
        "secondary_muscles": ["hamstrings"],
        "equipment_required": ["barbell"],
        "translations": [
            {
                "locale": "fa-IR",
                "name": "پرس سینه دمبل",
                "instructions": "وزنه را با کنترل حرکت دهید.",
                "coaching_cues": ["کنترل حرکت"],
                "common_mistakes": ["قوس زیاد"],
            },
            {
                "locale": "en-US",
                "name": "Dumbbell Chest Press",
                "instructions": "Move the weight with control.",
                "coaching_cues": ["Stay controlled"],
                "common_mistakes": ["Excessive arch"],
            },
        ],
        "aliases": [
            {"locale": "fa-IR", "alias": "پرس سينه"},
            {"locale": "en-US", "alias": "DB press"},
        ],
        "media_assets": [
            {
                "media_type": "video_mp4",
                "storage_key": f"org/{org_id}/exercise/demo.mp4",
                "duration_seconds": 30,
                "bytes_size": 1024,
                "checksum_sha256": "a" * 64,
                "rights": {
                    "license_type": "coach_upload",
                    "source_url": "https://example.com/provenance/demo",
                    "creator_attribution": "Synthetic CoachOS test asset",
                    "permitted_commercial_use": True,
                },
            }
        ],
    }


@pytest.mark.django_db
def test_private_exercise_create_is_bilingual_normalized_and_audited(api_client):
    org, owner = make_org()
    api_client.force_authenticate(owner)
    response = api_client.post("/api/v1/exercises", exercise_payload(org.id), format="json")
    assert response.status_code == 201, response.data
    exercise = Exercise.objects.get(id=response.data["id"])
    assert exercise.organization == org
    assert exercise.status == "published"
    assert set(exercise.translations.values_list("locale", flat=True)) == {"fa-IR", "en-US"}
    assert exercise.aliases.get(locale="fa-IR").normalized_alias == "پرس سینه"
    assert exercise.media_assets.get().rights.license_type == "coach_upload"
    assert "storage_key" not in response.data["media_assets"][0]
    assert AuditEvent.objects.filter(action="exercise.created_private", organization=org).exists()


@pytest.mark.django_db
def test_persian_variant_search_exact_alias_and_filters(api_client):
    org, owner = make_org()
    api_client.force_authenticate(owner)
    created = api_client.post("/api/v1/exercises", exercise_payload(org.id), format="json")
    assert created.status_code == 201
    response = api_client.get(
        "/api/v1/exercises",
        {
            "org_id": org.id,
            "q": "پرس سينه",
            "locale": "fa-IR",
            "muscle": "quadriceps",
            "equipment": "barbell",
            "movement_pattern": "squat",
        },
    )
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["exercises"][0]["id"] == created.data["id"]


@pytest.mark.django_db
def test_catalog_visibility_is_canonical_plus_current_tenant_only(api_client):
    org_a, owner_a = make_org("a")
    org_b, owner_b = make_org("b")
    api_client.force_authenticate(owner_a)
    a = api_client.post("/api/v1/exercises", exercise_payload(org_a.id), format="json")
    payload_b = exercise_payload(org_b.id)
    payload_b["media_assets"][0]["storage_key"] = "org/b/demo.mp4"
    api_client.force_authenticate(owner_b)
    b = api_client.post("/api/v1/exercises", payload_b, format="json")
    assert a.status_code == b.status_code == 201

    admin = User.objects.create_user(email="admin@example.com", is_platform_admin=True)
    canonical = Exercise.objects.create(
        organization=None,
        created_by_user=admin,
        movement_pattern="hinge",
        difficulty="beginner",
        primary_muscles=["glutes"],
        status="published",
    )
    ExerciseTranslation.objects.create(
        exercise=canonical, locale="fa-IR", name="ددلیفت", instructions="کنترل"
    )
    ExerciseTranslation.objects.create(
        exercise=canonical, locale="en-US", name="Deadlift", instructions="Control"
    )

    api_client.force_authenticate(owner_a)
    response = api_client.get("/api/v1/exercises", {"org_id": org_a.id})
    ids = {item["id"] for item in response.data["exercises"]}
    assert a.data["id"] in ids
    assert canonical.id in ids
    assert b.data["id"] not in ids

    outsider = User.objects.create_user(email="outsider@example.com")
    api_client.force_authenticate(outsider)
    assert api_client.get("/api/v1/exercises", {"org_id": org_a.id}).status_code == 403


@pytest.mark.django_db
def test_private_detail_and_org_id_mutation_cannot_cross_tenants(api_client):
    org_a, owner_a = make_org("detail-a")
    org_b, owner_b = make_org("detail-b")
    api_client.force_authenticate(owner_a)
    created = api_client.post("/api/v1/exercises", exercise_payload(org_a.id), format="json")
    assert created.status_code == 201

    api_client.force_authenticate(owner_b)
    hidden = api_client.get(f"/api/v1/exercises/{created.data['id']}", {"org_id": org_b.id})
    assert hidden.status_code == 404

    payload = exercise_payload(org_a.id)
    payload["media_assets"][0]["storage_key"] = "org/cross-tenant/demo.mp4"
    denied = api_client.post("/api/v1/exercises", payload, format="json")
    assert denied.status_code == 403


@pytest.mark.django_db
def test_athlete_cannot_create_and_suspended_coach_cannot_read(api_client):
    org, owner = make_org()
    athlete = User.objects.create_user(email="athlete@example.com")
    coach = User.objects.create_user(email="coach@example.com")
    Membership.objects.create(user=athlete, organization=org, role="athlete", status="active")
    Membership.objects.create(user=coach, organization=org, role="coach", status="suspended")
    for user in (athlete, coach):
        api_client.force_authenticate(user)
        response = api_client.post("/api/v1/exercises", exercise_payload(org.id), format="json")
        assert response.status_code == 403
    api_client.force_authenticate(coach)
    assert api_client.get("/api/v1/exercises", {"org_id": org.id}).status_code == 403


@pytest.mark.django_db
def test_private_exercise_rejects_media_without_commercial_permission(api_client):
    org, owner = make_org("rights")
    payload = exercise_payload(org.id)
    payload["media_assets"][0]["rights"]["permitted_commercial_use"] = False
    api_client.force_authenticate(owner)
    response = api_client.post("/api/v1/exercises", payload, format="json")
    assert response.status_code == 400
    assert Exercise.objects.filter(organization=org).count() == 0


@pytest.mark.django_db
def test_media_rights_validation_requires_source_and_reviewer_pair():
    org, owner = make_org()
    exercise = Exercise.objects.create(
        organization=org,
        created_by_user=owner,
        movement_pattern="other",
        difficulty="beginner",
        primary_muscles=[],
    )
    asset = MediaAsset.objects.create(
        exercise=exercise,
        media_type="video_mp4",
        storage_key="private/test.mp4",
        bytes_size=1,
        checksum_sha256="b" * 64,
    )
    rights = MediaRights(
        media_asset=asset,
        license_type="commercial_license",
        creator_attribution="Owner",
        permitted_commercial_use=True,
    )
    with pytest.raises(ValidationError):
        rights.full_clean()


@pytest.mark.django_db
def test_moderation_is_admin_only_and_refuses_unlicensed_media(api_client):
    org, owner = make_org()
    pending = Exercise.objects.create(
        organization=org,
        created_by_user=owner,
        movement_pattern="lunge",
        difficulty="intermediate",
        primary_muscles=["quadriceps"],
        status="pending_review",
    )
    for locale, name in (("fa-IR", "لانج"), ("en-US", "Lunge")):
        ExerciseTranslation.objects.create(
            exercise=pending, locale=locale, name=name, instructions="Instruction"
        )
    asset = MediaAsset.objects.create(
        exercise=pending,
        media_type="video_mp4",
        storage_key="pending/lunge.mp4",
        bytes_size=100,
        checksum_sha256="c" * 64,
    )
    MediaRights.objects.create(
        media_asset=asset,
        license_type="coach_upload",
        source_url="https://example.com/source",
        creator_attribution="Coach",
        permitted_commercial_use=False,
    )
    api_client.force_authenticate(owner)
    assert api_client.get("/api/v1/admin/exercises/moderation").status_code == 403

    admin = User.objects.create_user(email="platform@example.com", is_platform_admin=True)
    api_client.force_authenticate(admin)
    queue = api_client.get("/api/v1/admin/exercises/moderation")
    assert queue.status_code == 200
    denied = api_client.post(
        "/api/v1/admin/exercises/moderation",
        {"exercise_id": pending.id, "decision": "approve"},
        format="json",
    )
    assert denied.status_code == 409
    asset.rights.permitted_commercial_use = True
    asset.rights.save()
    approved = api_client.post(
        "/api/v1/admin/exercises/moderation",
        {"exercise_id": pending.id, "decision": "approve"},
        format="json",
    )
    assert approved.status_code == 200
    pending.refresh_from_db()
    asset.rights.refresh_from_db()
    assert pending.status == "published"
    assert asset.rights.reviewed_by_user == admin
    assert AuditEvent.objects.filter(action="exercise.published").exists()


@pytest.mark.django_db
def test_catalog_query_count_is_bounded(api_client):
    org, owner = make_org()
    for number in range(5):
        exercise = Exercise.objects.create(
            organization=org,
            created_by_user=owner,
            movement_pattern="other",
            difficulty="beginner",
            primary_muscles=[],
            status="published",
        )
        ExerciseTranslation.objects.create(
            exercise=exercise, locale="fa-IR", name=f"حرکت {number}", instructions="توضیح"
        )
        ExerciseTranslation.objects.create(
            exercise=exercise, locale="en-US", name=f"Move {number}", instructions="Info"
        )
    api_client.force_authenticate(owner)
    with CaptureQueriesContext(connection) as queries:
        response = api_client.get("/api/v1/exercises", {"org_id": org.id})
    assert response.status_code == 200
    assert len(queries) <= 9
