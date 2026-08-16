"""
Phase 08 synthetic test-world builders.

All content here is synthetic. No real personal, health, or production message
data appears anywhere in the Phase 08 test suite.
"""

import datetime

from apps.exercises.models import Exercise, ExerciseTranslation
from apps.identity.models import User
from apps.organizations.models import Membership, Organization
from apps.programs.models import CoachAthleteAssignment, Program, ProgramAssignment


def make_org(slug):
    owner = User.objects.create_user(
        email=f"owner-{slug}@example.test", password="x", display_name=f"Owner {slug}"
    )
    org = Organization.objects.create(name=slug.title(), slug=slug, owner_user=owner)
    Membership.objects.create(user=owner, organization=org, role="owner", status="active")
    return org, owner


def add_user(org, role, slug, display_name=None, status="active"):
    user = User.objects.create_user(
        email=f"{role}-{slug}@example.test",
        password="x",
        display_name=display_name or f"{role.title()} {slug}",
    )
    Membership.objects.create(user=user, organization=org, role=role, status=status)
    return user


def assign(org, coach, athlete, is_active=True):
    return CoachAthleteAssignment.objects.create(
        organization=org, coach_user=coach, athlete_user=athlete, is_active=is_active
    )


class World:
    def __init__(self, slug):
        self.slug = slug
        self.org, self.owner = make_org(slug)
        self.coach = add_user(self.org, "coach", slug, display_name="Coach Reza")
        self.athlete = add_user(self.org, "athlete", slug, display_name="Athlete Neda")
        self.support = add_user(self.org, "support", slug)
        self.other_coach = add_user(self.org, "coach", f"{slug}2", display_name="Coach Two")
        self.assignment = assign(self.org, self.coach, self.athlete)


def login(client, user):
    client.force_login(user)
    return client


def make_session(world, scheduled_date=None):
    """A minimal Phase 07 WorkoutSession for context and hook tests."""
    from apps.execution.models import WorkoutSession

    exercise = Exercise.objects.create(
        organization=world.org,
        created_by_user=world.owner,
        movement_pattern="squat",
        difficulty="intermediate",
        primary_muscles=["quads"],
        equipment_required=["barbell"],
        status="published",
    )
    ExerciseTranslation.objects.create(
        exercise=exercise, locale="en-US", name="Back Squat", instructions="Brace"
    )
    ExerciseTranslation.objects.create(
        exercise=exercise, locale="fa-IR", name="اسکوات", instructions="کنترل"
    )
    program = Program.objects.create(
        organization=world.org,
        created_by_user=world.coach,
        title="Block A",
        target_goal="strength",
    )
    start = scheduled_date or datetime.date.today()
    assignment = ProgramAssignment.objects.create(
        organization=world.org,
        source_program=program,
        source_program_version=program.version,
        athlete_user=world.athlete,
        assigned_by_user=world.coach,
        start_date=start,
        status="active",
        snapshot_payload={
            "schema_version": 1,
            "program": {
                "id": program.id,
                "title": "Block A",
                "phases": [
                    {
                        "name": "Base",
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
                                                "title": "Lower",
                                                "sequence_order": 1,
                                                "items": [
                                                    {
                                                        "exercise_id": exercise.id,
                                                        "sequence_order": 1,
                                                        "segment": "main",
                                                        "exercise": {
                                                            "translations": [
                                                                {
                                                                    "locale": "en-US",
                                                                    "name": "Back Squat",
                                                                }
                                                            ]
                                                        },
                                                        "prescriptions": [
                                                            {
                                                                "set_index": 1,
                                                                "target_reps": "5",
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
                ],
            },
        },
    )
    session = WorkoutSession.objects.create(
        organization=world.org,
        program_assignment=assignment,
        athlete_user=world.athlete,
        scheduled_date=start,
        status="in_progress",
    )
    session.exercise = exercise
    return session
