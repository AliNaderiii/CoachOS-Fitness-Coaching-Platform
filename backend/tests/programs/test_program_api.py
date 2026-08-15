from copy import deepcopy

import pytest
from django.core.exceptions import ValidationError
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.audit.models import AuditEvent
from apps.exercises.models import Exercise, ExerciseTranslation
from apps.identity.models import User
from apps.organizations.models import Membership, Organization
from apps.programs.models import Program, ProgramAssignment


def make_org(slug="training"):
    owner = User.objects.create_user(email=f"owner-{slug}@example.com", password="x")
    org = Organization.objects.create(name=slug.title(), slug=slug, owner_user=owner)
    Membership.objects.create(user=owner, organization=org, role="owner", status="active")
    return org, owner


def make_exercise(org, owner):
    exercise = Exercise.objects.create(
        organization=org,
        created_by_user=owner,
        movement_pattern="horizontal_push",
        difficulty="intermediate",
        primary_muscles=["chest"],
        equipment_required=["barbell"],
        status="published",
    )
    ExerciseTranslation.objects.create(
        exercise=exercise, locale="fa-IR", name="پرس سینه", instructions="کنترل"
    )
    ExerciseTranslation.objects.create(
        exercise=exercise, locale="en-US", name="Bench Press", instructions="Control"
    )
    return exercise


def program_payload(org, exercise, title="Hypertrophy Block", is_template=True):
    return {
        "org_id": org.id,
        "title": title,
        "description": "Synthetic program data",
        "target_goal": "hypertrophy",
        "is_template": is_template,
        "phases": [
            {
                "name": "Accumulation",
                "sequence_order": 1,
                "duration_weeks": 1,
                "weeks": [
                    {
                        "week_number": 1,
                        "focus_note": "Technique",
                        "days": [
                            {
                                "day_number": 1,
                                "title": "Upper body",
                                "workouts": [
                                    {
                                        "title": "Push and pull",
                                        "estimated_minutes": 60,
                                        "sequence_order": 1,
                                        "items": [
                                            {
                                                "exercise_id": exercise.id,
                                                "sequence_order": 1,
                                                "group_key": "A1",
                                                "segment": "main",
                                                "rest_seconds_between_sets": 90,
                                                "coach_notes": "Controlled reps",
                                                "prescriptions": [
                                                    {
                                                        "set_index": 1,
                                                        "target_reps": "8",
                                                        "target_load": "80 kg",
                                                        "target_rpe": "8.0",
                                                        "target_rir": 2,
                                                        "tempo": "3-1-1-0",
                                                    },
                                                    {
                                                        "set_index": 2,
                                                        "target_reps": "8",
                                                        "target_load": "80 kg",
                                                        "target_rpe": "8.0",
                                                        "target_rir": 2,
                                                        "tempo": "3-1-1-0",
                                                    },
                                                ],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ],
    }


@pytest.mark.django_db
def test_create_hierarchical_program_and_prescriptions_atomically(api_client):
    org, owner = make_org()
    exercise = make_exercise(org, owner)
    api_client.force_authenticate(owner)
    response = api_client.post("/api/v1/programs", program_payload(org, exercise), format="json")
    assert response.status_code == 201, response.data
    program = Program.objects.get(id=response.data["id"])
    phase = program.phases.get()
    item = phase.weeks.get().days.get().workouts.get().items.get()
    assert item.group_key == "A1"
    assert item.prescriptions.count() == 2
    assert str(item.prescriptions.first().target_rpe) == "8.0"
    assert AuditEvent.objects.filter(action="program.created", organization=org).exists()

    invalid = program_payload(org, exercise, title="Invalid")
    invalid["phases"][0]["weeks"][0]["days"][0]["workouts"][0]["items"][0]["exercise_id"] = (
        "00000000-0000-0000-0000-000000000000"
    )
    denied = api_client.post("/api/v1/programs", invalid, format="json")
    assert denied.status_code == 400
    assert not Program.objects.filter(title="Invalid").exists()


@pytest.mark.django_db
def test_template_clone_is_deep_and_independent(api_client):
    org, owner = make_org()
    exercise = make_exercise(org, owner)
    api_client.force_authenticate(owner)
    source_response = api_client.post(
        "/api/v1/programs", program_payload(org, exercise), format="json"
    )
    clone_response = api_client.post(
        f"/api/v1/programs/{source_response.data['id']}/clone",
        {"title": "Athlete copy", "is_template": False},
        format="json",
    )
    assert clone_response.status_code == 201, clone_response.data
    source = Program.objects.get(id=source_response.data["id"])
    clone = Program.objects.get(id=clone_response.data["id"])
    assert source.id != clone.id
    assert source.phases.get().id != clone.phases.get().id
    clone_phase = clone.phases.get()
    clone_phase.name = "Changed copy"
    clone_phase.save()
    source.phases.get().refresh_from_db()
    assert source.phases.get().name == "Accumulation"
    assert AuditEvent.objects.filter(action="template.cloned", target_entity_id=clone.id).exists()


@pytest.mark.django_db
def test_assignment_snapshot_is_frozen_after_program_update(api_client):
    org, owner = make_org()
    exercise = make_exercise(org, owner)
    athlete = User.objects.create_user(email="athlete@example.com")
    Membership.objects.create(user=athlete, organization=org, role="athlete", status="active")
    api_client.force_authenticate(owner)
    program_response = api_client.post(
        "/api/v1/programs", program_payload(org, exercise), format="json"
    )
    assignment_response = api_client.post(
        "/api/v1/program-assignments",
        {
            "org_id": org.id,
            "athlete_user_id": athlete.id,
            "source_program_id": program_response.data["id"],
            "start_date": "2026-08-17",
        },
        format="json",
    )
    assert assignment_response.status_code == 201, assignment_response.data
    assignment = ProgramAssignment.objects.get(id=assignment_response.data["id"])
    frozen = deepcopy(assignment.snapshot_payload)
    assert frozen["program"]["title"] == "Hypertrophy Block"
    assert (
        frozen["program"]["phases"][0]["weeks"][0]["days"][0]["workouts"][0]["items"][0][
            "prescriptions"
        ][0]["tempo"]
        == "3-1-1-0"
    )

    updated = api_client.patch(
        f"/api/v1/programs/{program_response.data['id']}",
        {"title": "Updated Draft"},
        format="json",
    )
    assert updated.status_code == 200
    assert updated.data["version"] == 2
    assignment.refresh_from_db()
    assert assignment.snapshot_payload == frozen
    assignment.snapshot_payload = {"tampered": True}
    with pytest.raises(ValidationError):
        assignment.save()


@pytest.mark.django_db
def test_coach_can_assign_only_linked_tenant_athlete(api_client):
    org, owner = make_org()
    exercise = make_exercise(org, owner)
    coach = User.objects.create_user(email="coach@example.com")
    linked = User.objects.create_user(email="linked@example.com")
    unlinked = User.objects.create_user(email="unlinked@example.com")
    Membership.objects.create(user=coach, organization=org, role="coach", status="active")
    Membership.objects.create(user=linked, organization=org, role="athlete", status="active")
    Membership.objects.create(user=unlinked, organization=org, role="athlete", status="active")
    api_client.force_authenticate(owner)
    program = api_client.post("/api/v1/programs", program_payload(org, exercise), format="json")
    relation = api_client.post(
        "/api/v1/coach-athlete-assignments",
        {"org_id": org.id, "coach_user_id": coach.id, "athlete_user_id": linked.id},
        format="json",
    )
    assert relation.status_code == 201
    api_client.force_authenticate(coach)
    base = {
        "org_id": org.id,
        "source_program_id": program.data["id"],
        "start_date": "2026-08-18",
    }
    denied = api_client.post(
        "/api/v1/program-assignments",
        {**base, "athlete_user_id": unlinked.id},
        format="json",
    )
    assert denied.status_code == 403
    allowed = api_client.post(
        "/api/v1/program-assignments",
        {**base, "athlete_user_id": linked.id},
        format="json",
    )
    assert allowed.status_code == 201


@pytest.mark.django_db
def test_program_rejects_private_exercise_from_another_tenant(api_client):
    org_a, owner_a = make_org("program-a")
    org_b, owner_b = make_org("program-b")
    foreign_exercise = make_exercise(org_b, owner_b)
    api_client.force_authenticate(owner_a)
    response = api_client.post(
        "/api/v1/programs", program_payload(org_a, foreign_exercise), format="json"
    )
    assert response.status_code == 400
    assert not Program.objects.filter(organization=org_a).exists()


@pytest.mark.django_db
def test_owner_role_precedes_coach_role_for_unlinked_assignment(api_client):
    org, owner = make_org("multi-role")
    Membership.objects.create(user=owner, organization=org, role="coach", status="active")
    athlete = User.objects.create_user(email="multi-role-athlete@example.com")
    Membership.objects.create(user=athlete, organization=org, role="athlete", status="active")
    exercise = make_exercise(org, owner)
    api_client.force_authenticate(owner)
    program = api_client.post("/api/v1/programs", program_payload(org, exercise), format="json")
    response = api_client.post(
        "/api/v1/program-assignments",
        {
            "org_id": org.id,
            "source_program_id": program.data["id"],
            "athlete_user_id": athlete.id,
            "start_date": "2026-08-20",
        },
        format="json",
    )
    assert response.status_code == 201


@pytest.mark.django_db
def test_program_tenant_role_and_suspension_controls(api_client):
    org_a, owner_a = make_org("orga")
    org_b, owner_b = make_org("orgb")
    exercise = make_exercise(org_a, owner_a)
    athlete = User.objects.create_user(email="athlete-role@example.com")
    suspended = User.objects.create_user(email="suspended@example.com")
    Membership.objects.create(user=athlete, organization=org_a, role="athlete", status="active")
    Membership.objects.create(user=suspended, organization=org_a, role="coach", status="suspended")
    api_client.force_authenticate(owner_a)
    program = api_client.post("/api/v1/programs", program_payload(org_a, exercise), format="json")
    assert program.status_code == 201
    for user in (owner_b, athlete, suspended):
        api_client.force_authenticate(user)
        assert api_client.get(f"/api/v1/programs/{program.data['id']}").status_code == 404
        create = api_client.post(
            "/api/v1/programs", program_payload(org_a, exercise), format="json"
        )
        assert create.status_code == 403
    assert org_b.id != org_a.id


@pytest.mark.django_db
def test_program_detail_query_count_is_bounded(api_client):
    org, owner = make_org()
    exercise = make_exercise(org, owner)
    api_client.force_authenticate(owner)
    created = api_client.post("/api/v1/programs", program_payload(org, exercise), format="json")
    with CaptureQueriesContext(connection) as queries:
        response = api_client.get(f"/api/v1/programs/{created.data['id']}")
    assert response.status_code == 200
    assert len(queries) <= 15
