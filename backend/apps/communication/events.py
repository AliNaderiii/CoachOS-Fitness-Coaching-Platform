"""
Phase 08 — versioned domain event emission (transactional outbox producer side).

`emit_event` must be called from inside the same `transaction.atomic()` block as
the source domain mutation. It performs a single INSERT; no network I/O, no
provider call, and no notification creation happens on the request path.

Payload rule: identifiers, counts and routing metadata only. A `message.sent`
event never carries `Message.body`.
"""

import logging

from django.utils import timezone

from apps.core.utils.id_generator import generate_uuid7

from .constants import (
    EVENT_FEEDBACK_FLAG_CREATED,
    EVENT_MESSAGE_SENT,
    EVENT_SCHEMA_VERSION,
    EVENT_TYPES,
    EVENT_WORKOUT_COMPLETED,
)
from .models import OutboxRecord

logger = logging.getLogger(__name__)

# Keys that must never appear in an event payload. Enforced at emit time so a
# future contributor cannot accidentally widen the blast radius of an event.
FORBIDDEN_PAYLOAD_KEYS = frozenset(
    {
        "body",
        "message_body",
        "content",
        "text",
        "email",
        "email_address",
        "password",
        "token",
        "secret",
        "authorization",
        "push_endpoint",
        "preview",
        "last_message_preview",
    }
)


class EventPayloadError(ValueError):
    """Raised when an event payload violates the privacy contract."""


def _assert_safe_payload(payload):
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise EventPayloadError("Event payload must be a mapping.")
    for key, value in payload.items():
        if str(key).lower() in FORBIDDEN_PAYLOAD_KEYS:
            raise EventPayloadError(f"Forbidden key in event payload: {key}")
        if isinstance(value, dict):
            _assert_safe_payload(value)
    return payload


def emit_event(
    *,
    event_type,
    organization,
    actor_user,
    subject_type,
    subject_id,
    payload=None,
    correlation_id="",
    occurred_at=None,
):
    """
    Append a durable outbox record inside the caller's transaction.

    Returns the created OutboxRecord. Raises EventPayloadError if the payload
    violates the privacy contract, and ValueError for unknown event types.
    """
    if event_type not in EVENT_TYPES:
        raise ValueError(f"Unknown event type: {event_type}")

    safe_payload = _assert_safe_payload(payload)

    record = OutboxRecord.objects.create(
        event_id=generate_uuid7(),
        event_type=event_type,
        schema_version=EVENT_SCHEMA_VERSION,
        organization=organization,
        actor_user=actor_user,
        subject_type=subject_type,
        subject_id=str(subject_id),
        correlation_id=(correlation_id or "")[:36],
        occurred_at=occurred_at or timezone.now(),
        payload=safe_payload,
        status="pending",
        next_attempt_at=timezone.now(),
    )

    # Structured log carries identifiers only — no payload, no body.
    logger.info(
        "outbox.enqueued event_type=%s event_id=%s subject=%s",
        record.event_type,
        record.event_id,
        record.subject_type,
    )
    return record


# --- Convenience producers used by the domain --------------------------------- #


def emit_message_sent(*, message, conversation, recipient_user_ids, correlation_id=""):
    return emit_event(
        event_type=EVENT_MESSAGE_SENT,
        organization=conversation.organization,
        actor_user=message.sender_user,
        subject_type="Message",
        subject_id=message.id,
        correlation_id=correlation_id,
        payload={
            "conversation_id": conversation.id,
            "recipient_user_ids": list(recipient_user_ids),
            "context_type": conversation.context_type,
            "context_id": conversation.context_id,
        },
    )


def emit_workout_completed(*, session, recipient_user_ids, correlation_id=""):
    return emit_event(
        event_type=EVENT_WORKOUT_COMPLETED,
        organization=session.organization,
        actor_user=session.athlete_user,
        subject_type="WorkoutSession",
        subject_id=session.id,
        correlation_id=correlation_id,
        payload={
            "workout_session_id": session.id,
            "athlete_user_id": session.athlete_user_id,
            "recipient_user_ids": list(recipient_user_ids),
            "scheduled_date": str(session.scheduled_date),
        },
    )


def emit_feedback_flag_created(*, flag, session, recipient_user_ids, correlation_id=""):
    """
    Safety event.

    Carries severity and flag type — clinical detail text is deliberately
    excluded. CoachOS makes no medical claim; this is a subjective athlete
    report routed to the assigned coach.
    """
    return emit_event(
        event_type=EVENT_FEEDBACK_FLAG_CREATED,
        organization=session.organization,
        actor_user=session.athlete_user,
        subject_type="FeedbackFlag",
        subject_id=flag.id,
        correlation_id=correlation_id,
        payload={
            "feedback_flag_id": flag.id,
            "workout_session_id": session.id,
            "athlete_user_id": session.athlete_user_id,
            "recipient_user_ids": list(recipient_user_ids),
            "flag_type": flag.flag_type,
            "severity": flag.severity,
        },
    )
