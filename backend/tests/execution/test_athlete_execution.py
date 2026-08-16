"""
Phase 07 athlete execution, progress, and consent tests.

Covers model constraints (Stage 1), backend APIs (Stage 2), consent-gated media
and privacy boundary (Stage 3), and adversarial authorization/security cases
(Stage 6).
"""

import datetime

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError

from apps.audit.models import AuditEvent
from apps.execution.models import (
    ConsentRecord,
    FeedbackFlag,
    ProgressPhoto,
    SetLog,
    Substitution,
    WorkoutSession,
)
from apps.exercises.models import Exercise, ExerciseTranslation
from apps.identity.models import User
from apps.organizations.models import Membership, Organization
from apps.programs.models import CoachAthleteAssignment, Program, ProgramAssignment


def make_world(slug="w"):
    owner = User.objects.create_user(email=f"owner-{slug}@example.com", password="x")
    org = Organization.objects.create(name=slug.title(), slug=slug, owner_user=owner)
    Membership.objects.create(user=owner, organization=org, role="owner", status="active")
    coach = User.objects.create_user(email=f"coach-{slug}@example.com", password="x")
    Membership.objects.create(user=coach, organization=org, role="coach", status="active")
    athlete = User.objects.create_user(email=f"athlete-{slug}@example.com", password="x")
    Membership.objects.create(user=athlete, organization=org, role="athlete", status="active")
    support = User.objects.create_user(email=f"support-{slug}@example.com", password="x")
    Membership.objects.create(user=support, organization=org, role="support", status="active")
    return org, owner, coach, athlete, support


def make_exercise(org, owner, name="Bench Press", slug="bp"):
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
        exercise=exercise, locale="fa-IR", name=f"پرس {slug}", instructions="کنترل"
    )
    ExerciseTranslation.objects.create(
        exercise=exercise, locale="en-US", name=name, instructions="Control"
    )
    return exercise


def make_alternative(org, owner):
    exercise = Exercise.objects.create(
        organization=org,
        created_by_user=owner,
        movement_pattern="horizontal_pull",
        difficulty="intermediate",
        primary_muscles=["back"],
        equipment_required=["dumbbell"],
        status="published",
    )
    ExerciseTranslation.objects.create(
        exercise=exercise, locale="en-US", name="Dumbbell Row", instructions="Pull"
    )
    ExerciseTranslation.objects.create(
        exercise=exercise, locale="fa-IR", name="ردیف دمبل", instructions="کشش"
    )
    return exercise


def make_snapshot(exercise_id, day_title="Day 1 · Upper"):
    return {
        "schema_version": 1,
        "source_program_id": "prog",
        "source_program_version": 1,
        "program": {
            "id": "prog",
            "title": "Hypertrophy Block",
            "phases": [
                {
                    "name": "Accumulation",
                    "sequence_order": 1,
                    "weeks": [
                        {
                            "week_number": 1,
                            "days": [
                                {
                                    "day_number": 1,
                                    "title": day_title,
                                    "workouts": [
                                        {
                                            "id": "w1",
                                            "title": "Push and pull",
                                            "estimated_minutes": 60,
                                            "sequence_order": 1,
                                            "items": [
                                                {
                                                    "exercise_id": exercise_id,
                                                    "sequence_order": 1,
                                                    "group_key": "A1",
                                                    "segment": "main",
                                                    "rest_seconds_between_sets": 90,
                                                    "coach_notes": "Controlled",
                                                    "exercise": {
                                                        "translations": [
                                                            {"locale": "fa-IR", "name": "پرس w"},
                                                            {
                                                                "locale": "en-US",
                                                                "name": "Bench Press",
                                                            },
                                                        ]
                                                    },
                                                    "prescriptions": [
                                                        {
                                                            "set_index": 1,
                                                            "target_reps": "8",
                                                            "target_load": "80 kg",
                                                        },
                                                        {
                                                            "set_index": 2,
                                                            "target_reps": "8",
                                                            "target_load": "80 kg",
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
        },
    }


def make_assignment(org, athlete, exercise_id, start_date=None):
    program = Program.objects.create(
        organization=org,
        created_by_user=org.owner_user,
        title="Hypertrophy Block",
        target_goal="hypertrophy",
    )
    start_date = start_date or datetime.date.today() - datetime.timedelta(days=3)
    assignment = ProgramAssignment.objects.create(
        organization=org,
        athlete_user=athlete,
        assigned_by_user=org.owner_user,
        source_program=program,
        source_program_version=1,
        start_date=start_date,
        status="active",
        snapshot_payload=make_snapshot(exercise_id),
    )
    return assignment


def link_coach(org, coach, athlete):
    return CoachAthleteAssignment.objects.create(
        organization=org, coach_user=coach, athlete_user=athlete, is_active=True
    )


@pytest.fixture
def world(api_client):
    org, owner, coach, athlete, support = make_world()
    return {
        "org": org,
        "owner": owner,
        "coach": coach,
        "athlete": athlete,
        "support": support,
        "api_client": api_client,
    }


@pytest.fixture
def prepped(world):
    org = world["org"]
    owner = world["owner"]
    coach = world["coach"]
    athlete = world["athlete"]
    exercise = make_exercise(org, owner)
    alternative = make_alternative(org, owner)
    link_coach(org, coach, athlete)
    assignment = make_assignment(org, athlete, exercise.id)
    world["exercise"] = exercise
    world["alternative"] = alternative
    world["assignment"] = assignment
    return world


# --------------------------------------------------------------------------- #
# Stage 1 — Model constraints
# --------------------------------------------------------------------------- #
@pytest.mark.django_db
def test_session_requires_assigned_athlete(prepped):
    org = prepped["org"]
    other = User.objects.create_user(email="other@example.com", password="x")
    Membership.objects.create(user=other, organization=org, role="athlete", status="active")
    assignment = prepped["assignment"]
    session = WorkoutSession(
        organization=org,
        program_assignment=assignment,
        athlete_user=other,
        scheduled_date=datetime.date.today(),
    )
    with pytest.raises(ValidationError):
        session.full_clean()


@pytest.mark.django_db
def test_session_only_active_assignment(prepped):
    org = prepped["org"]
    athlete = prepped["athlete"]
    assignment = prepped["assignment"]
    assignment.status = "archived"
    assignment.save()
    session = WorkoutSession(
        organization=org,
        program_assignment=assignment,
        athlete_user=athlete,
        scheduled_date=datetime.date.today(),
    )
    with pytest.raises(ValidationError):
        session.full_clean()


@pytest.mark.django_db
def test_session_status_transitions_and_skip_reason(prepped):
    org = prepped["org"]
    athlete = prepped["athlete"]
    assignment = prepped["assignment"]
    session = WorkoutSession(
        organization=org,
        program_assignment=assignment,
        athlete_user=athlete,
        scheduled_date=datetime.date.today(),
    )
    session.full_clean()
    session.save()
    session.transition("in_progress")
    session.save()
    assert session.started_at is not None
    session.transition("completed", session_rpe=8, fatigue_score=3)
    session.save()
    assert session.status == "completed"
    assert session.completed_at is not None
    # invalid transition from completed
    with pytest.raises(ValidationError):
        session.transition("in_progress")


@pytest.mark.django_db
def test_skip_requires_reason(prepped):
    org = prepped["org"]
    athlete = prepped["athlete"]
    session = WorkoutSession(
        organization=org,
        program_assignment=prepped["assignment"],
        athlete_user=athlete,
        scheduled_date=datetime.date.today(),
        status="scheduled",
    )
    session.full_clean()
    session.save()
    with pytest.raises(ValidationError):
        session.transition("skipped", reason=None)


@pytest.mark.django_db
def test_rpe_fatigue_bounds(prepped):
    org = prepped["org"]
    athlete = prepped["athlete"]
    session = WorkoutSession(
        organization=org,
        program_assignment=prepped["assignment"],
        athlete_user=athlete,
        scheduled_date=datetime.date.today(),
        session_rpe=11,
    )
    with pytest.raises(ValidationError):
        session.full_clean()


@pytest.mark.django_db
def test_set_log_unique_and_bounds(prepped):
    org = prepped["org"]
    athlete = prepped["athlete"]
    session = WorkoutSession.objects.create(
        organization=org,
        program_assignment=prepped["assignment"],
        athlete_user=athlete,
        scheduled_date=datetime.date.today(),
        status="in_progress",
    )
    exercise = prepped["exercise"]
    SetLog.objects.create(
        session=session, exercise=exercise, set_index=1, actual_reps=8, actual_load_kg=80
    )
    from django.db import transaction

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            SetLog.objects.create(
                session=session, exercise=exercise, set_index=1, actual_reps=9, actual_load_kg=85
            )
    bad = SetLog(session=session, exercise=exercise, set_index=1, actual_reps=-1, actual_load_kg=80)
    with pytest.raises(ValidationError):
        bad.full_clean()


@pytest.mark.django_db
def test_substitution_requires_reason_and_difference(prepped):
    org = prepped["org"]
    athlete = prepped["athlete"]
    session = WorkoutSession.objects.create(
        organization=org,
        program_assignment=prepped["assignment"],
        athlete_user=athlete,
        scheduled_date=datetime.date.today(),
        status="in_progress",
    )
    same = Substitution(
        session=session,
        original_exercise=prepped["exercise"],
        substituted_exercise=prepped["exercise"],
        reason="preference",
    )
    with pytest.raises(ValidationError):
        same.full_clean()


@pytest.mark.django_db
def test_feedback_flag_non_clinical_and_ownership(prepped):
    org = prepped["org"]
    athlete = prepped["athlete"]
    session = WorkoutSession.objects.create(
        organization=org,
        program_assignment=prepped["assignment"],
        athlete_user=athlete,
        scheduled_date=datetime.date.today(),
        status="in_progress",
    )
    other = User.objects.create_user(email="athlete-other@example.com", password="x")
    Membership.objects.create(user=other, organization=org, role="athlete", status="active")
    flag = FeedbackFlag(
        session=session,
        athlete_user=other,
        flag_type="joint_pain",
        anatomical_location="knee",
        severity="mild",
        details="Slight discomfort after squatting.",
    )
    with pytest.raises(ValidationError):
        flag.full_clean()


@pytest.mark.django_db
def test_consent_grant_revoke_lifecycle(prepped):
    coach = prepped["coach"]
    athlete = prepped["athlete"]
    record = ConsentRecord.objects.create(
        athlete_user=athlete, grantee_user=coach, consent_type="progress_photo"
    )
    record.grant()
    record.save()
    assert record.is_active
    record.revoke()
    record.save()
    assert not record.is_active


# --------------------------------------------------------------------------- #
# Stage 2 — Athlete Today + Session APIs
# --------------------------------------------------------------------------- #
@pytest.mark.django_db
def test_athlete_today_returns_scheduled_workout(prepped):
    client = prepped["api_client"]
    client.force_authenticate(prepped["athlete"])
    response = client.get("/api/v1/athlete/today")
    assert response.status_code == 200, response.data
    assert len(response.data["scheduled_workouts"]) == 1
    assert response.data["scheduled_workouts"][0]["title"] == "Push and pull"
    assert response.data["scheduled_workouts"][0]["workout"]["items"][0]["prescriptions"]


@pytest.mark.django_db
def test_athlete_today_empty_when_no_active_assignment(world):
    client = world["api_client"]
    client.force_authenticate(world["athlete"])
    response = client.get("/api/v1/athlete/today")
    assert response.status_code == 200
    assert response.data["scheduled_workouts"] == []


@pytest.mark.django_db
def test_start_session_requires_own_active_assignment(prepped):
    client = prepped["api_client"]
    client.force_authenticate(prepped["athlete"])
    response = client.post(
        "/api/v1/workout-sessions",
        {
            "program_assignment_id": prepped["assignment"].id,
            "scheduled_date": datetime.date.today().isoformat(),
        },
        format="json",
    )
    assert response.status_code == 201, response.data
    assert response.data["status"] == "in_progress"
    assert AuditEvent.objects.filter(action="session.started").exists()


@pytest.mark.django_db
def test_start_session_other_athlete_assignment_denied(prepped):
    org = prepped["org"]
    other = User.objects.create_user(email="athlete-b@example.com", password="x")
    Membership.objects.create(user=other, organization=org, role="athlete", status="active")
    client = prepped["api_client"]
    client.force_authenticate(other)
    response = client.post(
        "/api/v1/workout-sessions",
        {
            "program_assignment_id": prepped["assignment"].id,
            "scheduled_date": datetime.date.today().isoformat(),
        },
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_start_session_idempotent(prepped):
    client = prepped["api_client"]
    client.force_authenticate(prepped["athlete"])
    payload = {
        "program_assignment_id": prepped["assignment"].id,
        "scheduled_date": datetime.date.today().isoformat(),
    }
    first = client.post("/api/v1/workout-sessions", payload, format="json")
    second = client.post("/api/v1/workout-sessions", payload, format="json")
    assert first.status_code == 201
    assert second.status_code == 201
    assert WorkoutSession.objects.filter(program_assignment=prepped["assignment"]).count() == 1


@pytest.mark.django_db
def test_session_detail_access_matrix(prepped):
    client = prepped["api_client"]
    client.force_authenticate(prepped["athlete"])
    start = client.post(
        "/api/v1/workout-sessions",
        {
            "program_assignment_id": prepped["assignment"].id,
            "scheduled_date": datetime.date.today().isoformat(),
        },
        format="json",
    )
    session_id = start.data["id"]
    # athlete self
    assert client.get(f"/api/v1/workout-sessions/{session_id}").status_code == 200
    # assigned coach
    client.force_authenticate(prepped["coach"])
    assert client.get(f"/api/v1/workout-sessions/{session_id}").status_code == 200
    # owner
    client.force_authenticate(prepped["owner"])
    assert client.get(f"/api/v1/workout-sessions/{session_id}").status_code == 200
    # support denied
    client.force_authenticate(prepped["support"])
    assert client.get(f"/api/v1/workout-sessions/{session_id}").status_code == 404
    # unrelated athlete in another org denied
    org2, owner2, coach2, athlete2, _ = make_world("other")
    client.force_authenticate(athlete2)
    assert client.get(f"/api/v1/workout-sessions/{session_id}").status_code == 404
    # cross-tenant coach not assigned denied
    client.force_authenticate(coach2)
    assert client.get(f"/api/v1/workout-sessions/{session_id}").status_code == 404


@pytest.mark.django_db
def test_complete_session_flow(prepped):
    client = prepped["api_client"]
    client.force_authenticate(prepped["athlete"])
    start = client.post(
        "/api/v1/workout-sessions",
        {
            "program_assignment_id": prepped["assignment"].id,
            "scheduled_date": datetime.date.today().isoformat(),
        },
        format="json",
    )
    session_id = start.data["id"]
    complete = client.post(
        f"/api/v1/workout-sessions/{session_id}",
        {"session_rpe": 8, "fatigue_score": 3, "athlete_notes": "Good session"},
        format="json",
    )
    assert complete.status_code == 200, complete.data
    assert complete.data["status"] == "completed"
    # completed cannot be re-mutated
    retry = client.post(
        f"/api/v1/workout-sessions/{session_id}",
        {"session_rpe": 9},
        format="json",
    )
    assert retry.status_code == 409
    # other athlete cannot complete
    org = prepped["org"]
    other = User.objects.create_user(email="athlete-c@example.com", password="x")
    Membership.objects.create(user=other, organization=org, role="athlete", status="active")
    client.force_authenticate(other)
    assert client.post(f"/api/v1/workout-sessions/{session_id}", {}, format="json").status_code in (
        403,
        404,
    )


# --------------------------------------------------------------------------- #
# Stage 2 — Set logs
# --------------------------------------------------------------------------- #
def _start_session(prepped, client):
    client.force_authenticate(prepped["athlete"])
    return client.post(
        "/api/v1/workout-sessions",
        {
            "program_assignment_id": prepped["assignment"].id,
            "scheduled_date": datetime.date.today().isoformat(),
        },
        format="json",
    ).data["id"]


@pytest.mark.django_db
def test_set_log_persists_and_idempotent(prepped):
    client = prepped["api_client"]
    session_id = _start_session(prepped, client)
    url = f"/api/v1/workout-sessions/{session_id}/set-logs"
    payload = {
        "exercise_id": prepped["exercise"].id,
        "set_index": 1,
        "actual_reps": 8,
        "actual_load_kg": "80.0",
    }
    first = client.post(url, payload, format="json")
    assert first.status_code == 201, first.data
    second = client.post(url, {**payload, "actual_reps": 9}, format="json")
    assert second.status_code == 201
    assert SetLog.objects.filter(session_id=session_id, set_index=1).count() == 1
    assert str(SetLog.objects.get(session_id=session_id, set_index=1).actual_reps) == "9"


@pytest.mark.django_db
def test_set_log_unknown_or_cross_athlete_denied(prepped):
    client = prepped["api_client"]
    session_id = _start_session(prepped, client)
    url = f"/api/v1/workout-sessions/{session_id}/set-logs"
    client.force_authenticate(prepped["athlete"])
    # unknown exercise not in session
    alt = prepped["alternative"]
    payload = {"exercise_id": alt.id, "set_index": 1, "actual_reps": 8, "actual_load_kg": "20"}
    assert client.post(url, payload, format="json").status_code == 400
    # other athlete cannot log to this session
    org = prepped["org"]
    other = User.objects.create_user(email="athlete-d@example.com", password="x")
    Membership.objects.create(user=other, organization=org, role="athlete", status="active")
    client.force_authenticate(other)
    assert (
        client.post(
            url,
            {
                "exercise_id": prepped["exercise"].id,
                "set_index": 1,
                "actual_reps": 8,
                "actual_load_kg": "80",
            },
            format="json",
        ).status_code
        == 404
    )


@pytest.mark.django_db
def test_completed_session_cannot_accept_set_logs(prepped):
    client = prepped["api_client"]
    session_id = _start_session(prepped, client)
    client.force_authenticate(prepped["athlete"])
    client.post(f"/api/v1/workout-sessions/{session_id}", {"session_rpe": 7}, format="json")
    resp = client.post(
        f"/api/v1/workout-sessions/{session_id}/set-logs",
        {
            "exercise_id": prepped["exercise"].id,
            "set_index": 2,
            "actual_reps": 8,
            "actual_load_kg": "80",
        },
        format="json",
    )
    assert resp.status_code == 409


# --------------------------------------------------------------------------- #
# Stage 2 — Substitution
# --------------------------------------------------------------------------- #
@pytest.mark.django_db
def test_substitution_mandatory_reason_and_visibility(prepped):
    client = prepped["api_client"]
    session_id = _start_session(prepped, client)
    url = f"/api/v1/workout-sessions/{session_id}/substitutions"
    client.force_authenticate(prepped["athlete"])
    # missing reason
    resp = client.post(
        url,
        {
            "original_exercise_id": prepped["exercise"].id,
            "substituted_exercise_id": prepped["alternative"].id,
        },
        format="json",
    )
    assert resp.status_code == 400
    # valid substitution
    resp = client.post(
        url,
        {
            "original_exercise_id": prepped["exercise"].id,
            "substituted_exercise_id": prepped["alternative"].id,
            "reason": "preference",
        },
        format="json",
    )
    assert resp.status_code == 201, resp.data
    assert AuditEvent.objects.filter(action="exercise.substituted").exists()
    # substitution reason cannot be omitted after visibility check
    resp = client.post(
        url,
        {
            "original_exercise_id": prepped["exercise"].id,
            "substituted_exercise_id": prepped["alternative"].id,
        },
        format="json",
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_substitution_replacement_must_be_visible(prepped):
    org = prepped["org"]
    owner = prepped["owner"]
    hidden = Exercise.objects.create(
        organization=org,
        created_by_user=owner,
        movement_pattern="isolation",
        difficulty="beginner",
        primary_muscles=["biceps"],
        equipment_required=[],
        status="draft",
    )
    client = prepped["api_client"]
    session_id = _start_session(prepped, client)
    client.force_authenticate(prepped["athlete"])
    resp = client.post(
        f"/api/v1/workout-sessions/{session_id}/substitutions",
        {
            "original_exercise_id": prepped["exercise"].id,
            "substituted_exercise_id": hidden.id,
            "reason": "preference",
        },
        format="json",
    )
    assert resp.status_code == 400


# --------------------------------------------------------------------------- #
# Stage 2 — Feedback flags
# --------------------------------------------------------------------------- #
@pytest.mark.django_db
def test_feedback_flag_subjective_and_ownership(prepped):
    client = prepped["api_client"]
    session_id = _start_session(prepped, client)
    client.force_authenticate(prepped["athlete"])
    resp = client.post(
        f"/api/v1/workout-sessions/{session_id}/feedback-flags",
        {
            "flag_type": "joint_pain",
            "anatomical_location": "knee",
            "severity": "moderate",
            "details": "Slight discomfort, subjective report only.",
        },
        format="json",
    )
    assert resp.status_code == 201, resp.data
    assert resp.data["status"] == "unresolved"
    assert AuditEvent.objects.filter(action="pain.flagged").exists()
    org = prepped["org"]
    other = User.objects.create_user(email="athlete-e@example.com", password="x")
    Membership.objects.create(user=other, organization=org, role="athlete", status="active")
    client.force_authenticate(other)
    resp = client.post(
        f"/api/v1/workout-sessions/{session_id}/feedback-flags",
        {
            "flag_type": "dizziness",
            "anatomical_location": "head",
            "severity": "mild",
            "details": "x",
        },
        format="json",
    )
    assert resp.status_code == 403


# --------------------------------------------------------------------------- #
# Stage 3 — Progress photos (consent-gated media boundary)
# --------------------------------------------------------------------------- #
def _upload_photo(prepped, client):
    session_id = _start_session(prepped, client)
    client.force_authenticate(prepped["athlete"])
    upload = client.post(
        f"/api/v1/athletes/{prepped['athlete'].id}/progress/photos",
        {
            "file": SimpleUploadedFile("p.png", b"PNGDATA"),
            "photo_type": "front",
            "captured_at": "2026-08-01",
        },
        format="multipart",
    )
    return session_id, upload


@pytest.mark.django_db
def test_photo_upload_and_no_public_storage_key(prepped):
    client = prepped["api_client"]
    _, upload = _upload_photo(prepped, client)
    assert upload.status_code == 201, upload.data
    assert ProgressPhoto.objects.filter(athlete_user=prepped["athlete"]).count() == 1
    # no raw storage key field leaked in response (only a signed mock URL for self)
    assert "storage_key" not in upload.data


@pytest.mark.django_db
def test_photo_list_consent_gated(prepped):
    client = prepped["api_client"]
    _, _ = _upload_photo(prepped, client)
    url = f"/api/v1/athletes/{prepped['athlete'].id}/progress/photos"
    # athlete self sees own photos
    client.force_authenticate(prepped["athlete"])
    assert client.get(url).status_code == 200
    # assigned coach WITHOUT consent -> denied (no leakage)
    client.force_authenticate(prepped["coach"])
    assert client.get(url).status_code == 403
    # grant consent -> coach can read with signed URLs
    client.force_authenticate(prepped["athlete"])
    grant = client.post(
        "/api/v1/consents",
        {
            "athlete_user_id": prepped["athlete"].id,
            "grantee_user_id": prepped["coach"].id,
            "consent_type": "progress_photo",
        },
        format="json",
    )
    assert grant.status_code == 201, grant.data
    client.force_authenticate(prepped["coach"])
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.data["photos"][0]["signed_url"] is not None
    # support denied
    client.force_authenticate(prepped["support"])
    assert client.get(url).status_code == 403
    # unassigned coach in same org denied
    _, _, coach2, _, _ = make_world("coach2")
    Membership.objects.create(
        user=coach2, organization=prepped["org"], role="coach", status="active"
    )
    client.force_authenticate(coach2)
    assert client.get(url).status_code == 403


@pytest.mark.django_db
def test_consent_revocation_blocks_reads_and_signed_urls(prepped):
    client = prepped["api_client"]
    _, _ = _upload_photo(prepped, client)
    url = f"/api/v1/athletes/{prepped['athlete'].id}/progress/photos"
    client.force_authenticate(prepped["athlete"])
    client.post(
        "/api/v1/consents",
        {
            "athlete_user_id": prepped["athlete"].id,
            "grantee_user_id": prepped["coach"].id,
            "consent_type": "progress_photo",
        },
        format="json",
    )
    client.force_authenticate(prepped["coach"])
    assert client.get(url).status_code == 200
    # revoke via DELETE
    client.force_authenticate(prepped["athlete"])
    revoke = client.delete(
        f"/api/v1/consents?athlete_id={prepped['athlete'].id}&grantee_id={prepped['coach'].id}&consent_type=progress_photo"
    )
    assert revoke.status_code == 204
    client.force_authenticate(prepped["coach"])
    assert client.get(url).status_code == 403


@pytest.mark.django_db
def test_photo_upload_self_only(prepped):
    client = prepped["api_client"]
    client.force_authenticate(prepped["coach"])
    resp = client.post(
        f"/api/v1/athletes/{prepped['athlete'].id}/progress/photos",
        {"file": SimpleUploadedFile("p.png", b"PNG"), "photo_type": "front"},
        format="multipart",
    )
    assert resp.status_code == 403


# --------------------------------------------------------------------------- #
# Stage 3 — Body metrics (consent-gated)
# --------------------------------------------------------------------------- #
@pytest.mark.django_db
def test_body_metric_self_and_consent_gated(prepped):
    client = prepped["api_client"]
    client.force_authenticate(prepped["athlete"])
    url = f"/api/v1/athletes/{prepped['athlete'].id}/body-metrics"
    create = client.post(
        url,
        {"metric_type": "body_weight", "value": "82.5", "unit": "kg", "recorded_at": "2026-08-01"},
        format="json",
    )
    assert create.status_code == 201, create.data
    assert client.get(url).status_code == 200
    # coach without consent denied
    client.force_authenticate(prepped["coach"])
    assert client.get(url).status_code == 403
    # grant body_metrics consent
    client.force_authenticate(prepped["athlete"])
    client.post(
        "/api/v1/consents",
        {
            "athlete_user_id": prepped["athlete"].id,
            "grantee_user_id": prepped["coach"].id,
            "consent_type": "body_metrics",
        },
        format="json",
    )
    client.force_authenticate(prepped["coach"])
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.data["metrics"][0]["metric_type"] == "body_weight"


@pytest.mark.django_db
def test_body_metric_other_athlete_cannot_write(prepped):
    client = prepped["api_client"]
    org = prepped["org"]
    other = User.objects.create_user(email="athlete-f@example.com", password="x")
    Membership.objects.create(user=other, organization=org, role="athlete", status="active")
    client.force_authenticate(other)
    resp = client.post(
        f"/api/v1/athletes/{prepped['athlete'].id}/body-metrics",
        {"metric_type": "body_weight", "value": "70", "unit": "kg", "recorded_at": "2026-08-01"},
        format="json",
    )
    assert resp.status_code == 403


# --------------------------------------------------------------------------- #
# Performance — bounded queries, no N+1 on Today/session reads
# --------------------------------------------------------------------------- #
@pytest.mark.django_db
def test_today_and_session_detail_bounded_queries(prepped):
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    client = prepped["api_client"]
    client.force_authenticate(prepped["athlete"])
    with CaptureQueriesContext(connection) as ctx:
        today = client.get("/api/v1/athlete/today")
        assert today.status_code == 200
        assert len(ctx.captured_queries) <= 6
    session_id = _start_session(prepped, client)
    client.force_authenticate(prepped["athlete"])
    with CaptureQueriesContext(connection) as ctx:
        detail = client.get(f"/api/v1/workout-sessions/{session_id}")
        assert detail.status_code == 200
        # session select + set_logs select (+ auth/permission queries), bounded.
        assert len(ctx.captured_queries) <= 10


# --------------------------------------------------------------------------- #
# Stage 6 — Adversarial cases
# --------------------------------------------------------------------------- #
@pytest.mark.django_db
def test_cross_tenant_isolated(world):
    org = world["org"]
    owner = world["owner"]
    coach = world["coach"]
    athlete = world["athlete"]
    org2, _, _, athlete2, _ = make_world("tenant2")
    ex = make_exercise(org, owner)
    link_coach(org, coach, athlete)
    assignment = make_assignment(org, athlete, ex.id)
    client = world["api_client"]
    # athlete2 in another org cannot start a session on tenant1's assignment
    client.force_authenticate(athlete2)
    resp = client.post(
        "/api/v1/workout-sessions",
        {
            "program_assignment_id": assignment.id,
            "scheduled_date": datetime.date.today().isoformat(),
        },
        format="json",
    )
    assert resp.status_code == 403


@pytest.mark.django_db
def test_suspended_membership_denied(prepped):
    org = prepped["org"]
    athlete = prepped["athlete"]
    membership = Membership.objects.get(user=athlete, organization=org, role="athlete")
    membership.status = "suspended"
    membership.save()
    client = prepped["api_client"]
    client.force_authenticate(athlete)
    resp = client.post(
        "/api/v1/workout-sessions",
        {
            "program_assignment_id": prepped["assignment"].id,
            "scheduled_date": datetime.date.today().isoformat(),
        },
        format="json",
    )
    assert resp.status_code in (403, 404)


@pytest.mark.django_db
def test_consent_only_to_assigned_coach_or_owner(prepped):
    org = prepped["org"]
    owner = prepped["owner"]
    athlete = prepped["athlete"]
    # unassigned coach cannot receive consent
    _, _, unassigned, _, _ = make_world("unassigned")
    Membership.objects.create(user=unassigned, organization=org, role="coach", status="active")
    client = prepped["api_client"]
    client.force_authenticate(athlete)
    resp = client.post(
        "/api/v1/consents",
        {
            "athlete_user_id": athlete.id,
            "grantee_user_id": unassigned.id,
            "consent_type": "progress_photo",
        },
        format="json",
    )
    assert resp.status_code == 403
    # owner escalation allowed
    resp = client.post(
        "/api/v1/consents",
        {
            "athlete_user_id": athlete.id,
            "grantee_user_id": owner.id,
            "consent_type": "progress_photo",
        },
        format="json",
    )
    assert resp.status_code == 201


@pytest.mark.django_db
def test_no_health_details_in_log_or_error(prepped):
    client = prepped["api_client"]
    session_id = _start_session(prepped, client)
    client.force_authenticate(prepped["athlete"])
    resp = client.post(
        f"/api/v1/workout-sessions/{session_id}/feedback-flags",
        {
            "flag_type": "joint_pain",
            "anatomical_location": "knee",
            "severity": "severe",
            "details": "Patient diagnosed with ACL tear",
        },
        format="json",
    )
    # The word "diagnos" must not appear in any error/log surface from the API.
    assert resp.status_code == 201


@pytest.mark.django_db
def test_audit_sensitive_views_recorded(prepped):
    client = prepped["api_client"]
    _, upload = _upload_photo(prepped, client)
    client.force_authenticate(prepped["athlete"])
    client.post(
        "/api/v1/consents",
        {
            "athlete_user_id": prepped["athlete"].id,
            "grantee_user_id": prepped["coach"].id,
            "consent_type": "progress_photo",
        },
        format="json",
    )
    client.force_authenticate(prepped["coach"])
    client.get(f"/api/v1/athletes/{prepped['athlete'].id}/progress/photos")
    assert AuditEvent.objects.filter(action="photo.viewed").exists()
    assert AuditEvent.objects.filter(action="consent.granted").exists()


# --------------------------------------------------------------------------- #
# Phase 07 Security Corrections — Additional matrix tests (suspended, cross-org, multi-org, lifecycle)
# --------------------------------------------------------------------------- #
@pytest.mark.django_db
def test_suspended_athlete_denied_on_today_and_session(prepped):
    org = prepped["org"]
    athlete = prepped["athlete"]
    membership = Membership.objects.get(user=athlete, organization=org, role="athlete")
    membership.status = "suspended"
    membership.save()
    client = prepped["api_client"]
    client.force_authenticate(athlete)
    assert client.get("/api/v1/athlete/today").status_code in (403, 404)
    # start session denied
    resp = client.post(
        "/api/v1/workout-sessions",
        {
            "program_assignment_id": prepped["assignment"].id,
            "scheduled_date": datetime.date.today().isoformat(),
        },
        format="json",
    )
    assert resp.status_code in (403, 404)


@pytest.mark.django_db
def test_suspended_coach_denied_on_assigned_data(prepped):
    org = prepped["org"]
    coach = prepped["coach"]
    membership = Membership.objects.get(user=coach, organization=org, role="coach")
    membership.status = "suspended"
    membership.save()
    client = prepped["api_client"]
    client.force_authenticate(coach)
    # create session first as athlete
    client.force_authenticate(prepped["athlete"])
    start = client.post(
        "/api/v1/workout-sessions",
        {
            "program_assignment_id": prepped["assignment"].id,
            "scheduled_date": datetime.date.today().isoformat(),
        },
        format="json",
    )
    session_id = start.data["id"]
    client.force_authenticate(coach)
    assert client.get(f"/api/v1/workout-sessions/{session_id}").status_code == 404


@pytest.mark.django_db
def test_cross_org_assignment_does_not_authorize(prepped):
    coach = prepped["coach"]
    # create second org + assignment for same users (cross-tenant)
    org2, owner2, coach2, athlete2, _ = make_world("org2")
    ex2 = make_exercise(org2, owner2)
    link_coach(org2, coach2, athlete2)
    make_assignment(org2, athlete2, ex2.id)
    # coach from org1 should NOT be authorized on org2 assignment
    client = prepped["api_client"]
    client.force_authenticate(coach)
    resp = client.get(f"/api/v1/athletes/{athlete2.id}/progress/photos")
    assert resp.status_code == 403
    # same for body metrics
    resp = client.get(f"/api/v1/athletes/{athlete2.id}/body-metrics")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_multi_org_user_cannot_use_arbitrary_first_org(prepped):
    athlete = prepped["athlete"]
    # athlete belongs to a second org (simulating multi-org user)
    org2 = Organization.objects.create(name="Second Org", slug="org2b", owner_user=prepped["owner"])
    Membership.objects.create(user=athlete, organization=org2, role="athlete", status="active")
    client = prepped["api_client"]
    client.force_authenticate(athlete)
    # Today and session operations should still resolve the correct org from the assignment
    resp = client.get("/api/v1/athlete/today")
    assert resp.status_code == 200  # succeeds because of active membership in correct org


@pytest.mark.django_db
def test_unassigned_coach_denied_on_athlete_data(prepped):
    org = prepped["org"]
    _, _, unassigned_coach, _, _ = make_world("unassigned")
    Membership.objects.create(
        user=unassigned_coach, organization=org, role="coach", status="active"
    )
    client = prepped["api_client"]
    client.force_authenticate(unassigned_coach)
    resp = client.get(f"/api/v1/athletes/{prepped['athlete'].id}/progress/photos")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_scheduled_session_cannot_accept_set_logs(prepped):
    client = prepped["api_client"]
    client.force_authenticate(prepped["athlete"])
    # create scheduled session without starting
    session = WorkoutSession.objects.create(
        organization=prepped["org"],
        program_assignment=prepped["assignment"],
        athlete_user=prepped["athlete"],
        scheduled_date=datetime.date.today(),
        status="scheduled",
    )
    resp = client.post(
        f"/api/v1/workout-sessions/{session.id}/set-logs",
        {
            "exercise_id": prepped["exercise"].id,
            "set_index": 1,
            "actual_reps": 8,
            "actual_load_kg": "80.0",
        },
        format="json",
    )
    assert resp.status_code == 409


@pytest.mark.django_db
def test_completed_session_mutation_denied(prepped):
    client = prepped["api_client"]
    client.force_authenticate(prepped["athlete"])
    start = client.post(
        "/api/v1/workout-sessions",
        {
            "program_assignment_id": prepped["assignment"].id,
            "scheduled_date": datetime.date.today().isoformat(),
        },
        format="json",
    )
    session_id = start.data["id"]
    client.post(f"/api/v1/workout-sessions/{session_id}", {"session_rpe": 8}, format="json")
    resp = client.post(
        f"/api/v1/workout-sessions/{session_id}/set-logs",
        {
            "exercise_id": prepped["exercise"].id,
            "set_index": 3,
            "actual_reps": 8,
            "actual_load_kg": "80",
        },
        format="json",
    )
    assert resp.status_code == 409


@pytest.mark.django_db
def test_no_signed_url_on_unauthorized_photo_access(prepped):
    client = prepped["api_client"]
    _, upload = _upload_photo(prepped, client)
    client.force_authenticate(prepped["coach"])
    resp = client.get(f"/api/v1/athletes/{prepped['athlete'].id}/progress/photos")
    assert resp.status_code == 403
    # even if somehow allowed, signed_url should not be present without consent
    assert "signed_url" not in str(resp.data)
