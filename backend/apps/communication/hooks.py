"""
Phase 08 — additive event hooks for existing Phase 07 coaching behaviour.

These helpers are called from inside the Phase 07 view transactions. They are
deliberately thin and defensive: Phase 07 semantics are not rewritten, and a
notification concern must never be able to fail an athlete's workout write.

Recipient resolution happens here (assigned coaches only) rather than in the
dispatcher so that the event payload records exactly who was entitled at the
moment the domain change committed. The mapper re-verifies entitlement again at
delivery time, so a revocation between commit and dispatch still suppresses.
"""

import logging

from apps.programs.models import CoachAthleteAssignment

from .events import emit_feedback_flag_created, emit_workout_completed

logger = logging.getLogger(__name__)


def assigned_coach_ids(athlete, organization):
    """Active coaches for this athlete in this organization."""
    return list(
        CoachAthleteAssignment.objects.filter(
            organization=organization, athlete_user=athlete, is_active=True
        ).values_list("coach_user_id", flat=True)
    )


def on_workout_completed(session, correlation_id=""):
    """Emit `workout.completed` inside the caller's transaction."""
    try:
        recipients = assigned_coach_ids(session.athlete_user, session.organization)
        if not recipients:
            return None
        return emit_workout_completed(
            session=session,
            recipient_user_ids=recipients,
            correlation_id=correlation_id,
        )
    except Exception:
        # Identifier-only log. A notification concern must never break the
        # athlete's completion write.
        logger.warning("hooks.workout_completed_failed session_id=%s", session.id)
        return None


def on_feedback_flag_created(flag, session, correlation_id=""):
    """Emit `feedback_flag.created` (safety category) inside the transaction."""
    try:
        recipients = assigned_coach_ids(session.athlete_user, session.organization)
        if not recipients:
            return None
        return emit_feedback_flag_created(
            flag=flag,
            session=session,
            recipient_user_ids=recipients,
            correlation_id=correlation_id,
        )
    except Exception:
        logger.warning("hooks.feedback_flag_failed flag_id=%s", flag.id)
        return None
