"""Synthetic-only fixtures for the Copilot evaluation harness.

Every identity here uses the reserved ``.test`` domain and invented values.
No real personal or health data is permitted in evaluation fixtures.
"""

import datetime

from django.utils import timezone

from apps.execution.models import FeedbackFlag, SetLog, WorkoutSession
from apps.exercises.models import Exercise, ExerciseTranslation
from apps.identity.models import User
from apps.organizations.models import Membership, Organization
from apps.programs.models import CoachAthleteAssignment, ProgramAssignment

SYNTH = "synthetic.test"


def make_org(slug: str):
    owner = User.objects.create_user(
        email=f"owner-{slug}@{SYNTH}", password="synthetic-only", display_name=f"Owner {slug}"
    )
    org = Organization.objects.create(name=f"Org {slug}", slug=slug, owner_user=owner)
    Membership.objects.create(user=owner, organization=org, role="owner", status="active")
    coach = User.objects.create_user(
        email=f"coach-{slug}@{SYNTH}", password="synthetic-only", display_name=f"Coach {slug}"
    )
    Membership.objects.create(user=coach, organization=org, role="coach", status="active")
    athlete = User.objects.create_user(
        email=f"athlete-{slug}@{SYNTH}", password="synthetic-only", display_name=f"Saeed {slug}"
    )
    Membership.objects.create(user=athlete, organization=org, role="athlete", status="active")
    support = User.objects.create_user(
        email=f"support-{slug}@{SYNTH}", password="synthetic-only", display_name=f"Support {slug}"
    )
    Membership.objects.create(user=support, organization=org, role="support", status="active")
    return {
        "org": org,
        "owner": owner,
        "coach": coach,
        "athlete": athlete,
        "support": support,
    }


def assign_coach(org, coach, athlete):
    return CoachAthleteAssignment.objects.create(
        organization=org, coach_user=coach, athlete_user=athlete, is_active=True
    )


def make_exercise(org, owner, slug: str, name_en: str, name_fa: str, *, published=True):
    exercise = Exercise.objects.create(
        organization=org,
        created_by_user=owner,
        movement_pattern="horizontal_push",
        difficulty="intermediate",
        primary_muscles=["chest"],
        equipment_required=["barbell"],
        status="published" if published else "draft",
    )
    ExerciseTranslation.objects.create(
        exercise=exercise, locale="en-US", name=name_en, instructions="Synthetic instructions."
    )
    ExerciseTranslation.objects.create(
        exercise=exercise, locale="fa-IR", name=name_fa, instructions="دستورالعمل مصنوعی."
    )
    return exercise


def make_assignment(org, athlete, owner, *, title="Synthetic Block"):
    """Minimal active assignment with a snapshot payload (no Program row needed)."""
    snapshot = {
        "schema_version": 1,
        "program": {
            "id": "synthetic-program",
            "title": title,
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
                                    "title": "Day 1",
                                    "workouts": [
                                        {
                                            "id": "w1",
                                            "title": "Main",
                                            "sequence_order": 1,
                                            "items": [],
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
    from apps.programs.models import Program

    program = Program.objects.create(
        organization=org,
        created_by_user=owner,
        title=title,
        target_goal="strength",
    )
    return ProgramAssignment.objects.create(
        organization=org,
        athlete_user=athlete,
        assigned_by_user=owner,
        source_program=program,
        source_program_version=1,
        start_date=timezone.now().date() - datetime.timedelta(days=7),
        status="active",
        snapshot_payload=snapshot,
    )


def make_session(assignment, athlete, org, *, days_ago=1, status="completed", notes=""):
    session = WorkoutSession.objects.create(
        organization=org,
        program_assignment=assignment,
        athlete_user=athlete,
        scheduled_date=timezone.now().date() - datetime.timedelta(days=days_ago),
        status="scheduled",
    )
    WorkoutSession.objects.filter(id=session.id).update(status=status)
    session.status = status
    if notes:
        WorkoutSession.objects.filter(id=session.id).update(athlete_notes=notes)
        session.athlete_notes = notes
    return session


def make_set_log(session, exercise, *, set_index=1, reps=5, load="100.00", rpe="8.0"):
    return SetLog.objects.create(
        session=session,
        exercise=exercise,
        set_index=set_index,
        actual_reps=reps,
        actual_load_kg=load,
        actual_rpe=rpe,
        is_completed=True,
    )


def make_flag(session, athlete, *, flag_type="severe_fatigue", severity="moderate"):
    return FeedbackFlag.objects.create(
        session=session,
        athlete_user=athlete,
        flag_type=flag_type,
        anatomical_location="synthetic-location",
        severity=severity,
        details="synthetic-details-must-never-leak",
    )
