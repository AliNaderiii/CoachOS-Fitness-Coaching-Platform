"""
Phase 08 — versioned event-to-notification mapping.

Each mapper turns one event envelope into zero or more notification specs. The
mapping is keyed by (event_type, schema_version) so a future schema revision can
be added without silently changing the behaviour of already-queued events.

Recipient safety rule: a mapper must re-verify, at mapping time, that each
candidate recipient may still access the subject. An event queued before an
access revocation must not produce a notification after it.
"""

from dataclasses import dataclass, field

from apps.identity.models import User
from apps.organizations.models import Organization

from .authz import coach_assignment_active, get_participant, has_active_membership
from .constants import (
    EVENT_CATEGORY,
    EVENT_FEEDBACK_FLAG_CREATED,
    EVENT_MESSAGE_SENT,
    EVENT_WORKOUT_COMPLETED,
)


@dataclass
class NotificationSpec:
    recipient: object
    event_type: str
    category: str
    title_key: str
    body_key: str
    payload: dict = field(default_factory=dict)
    dedupe_key: str = ""


def _dedupe_key(event_type, event_id, recipient_id):
    """Stable event identity per recipient — the deduplication anchor."""
    return f"{event_type}:{event_id}:{recipient_id}"


def _organization(envelope):
    tenant_id = envelope.get("tenant_id")
    if not tenant_id:
        return None
    return Organization.objects.filter(id=tenant_id).first()


def _actor_display_name(envelope):
    """Display name only. Never the actor's email address."""
    actor_id = envelope.get("actor_user_id")
    if not actor_id:
        return ""
    actor = User.objects.filter(id=actor_id).first()
    if actor is None:
        return ""
    return (actor.display_name or "").strip()[:80]


def map_message_sent(envelope):
    from .models import Conversation

    payload = envelope.get("payload") or {}
    conversation = (
        Conversation.objects.select_related("organization")
        .filter(id=payload.get("conversation_id"))
        .first()
    )
    if conversation is None:
        return []

    organization = conversation.organization
    actor_name = _actor_display_name(envelope)
    specs = []

    for recipient_id in payload.get("recipient_user_ids") or []:
        recipient = User.objects.filter(id=recipient_id, is_active=True).first()
        if recipient is None:
            continue
        # Re-verify access at mapping time: revoked access must not notify.
        if not has_active_membership(recipient, organization):
            continue
        participant = get_participant(conversation, recipient)
        if participant is None or participant.is_muted:
            continue

        specs.append(
            NotificationSpec(
                recipient=recipient,
                event_type=EVENT_MESSAGE_SENT,
                category=EVENT_CATEGORY[EVENT_MESSAGE_SENT],
                title_key="notifications.message_sent.title",
                body_key="notifications.message_sent.body",
                payload={
                    # Metadata only. The message body is deliberately absent so
                    # a notification can never leak private content.
                    "conversation_id": conversation.id,
                    "actor_display_name": actor_name,
                    "route": f"/messages/{conversation.id}",
                },
                dedupe_key=_dedupe_key(EVENT_MESSAGE_SENT, envelope["event_id"], recipient.id),
            )
        )
    return specs


def map_workout_completed(envelope):
    payload = envelope.get("payload") or {}
    organization = _organization(envelope)
    if organization is None:
        return []

    athlete = User.objects.filter(id=payload.get("athlete_user_id")).first()
    actor_name = _actor_display_name(envelope)
    specs = []

    for recipient_id in payload.get("recipient_user_ids") or []:
        recipient = User.objects.filter(id=recipient_id, is_active=True).first()
        if recipient is None or athlete is None:
            continue
        if not has_active_membership(recipient, organization):
            continue
        # A coach unassigned after the event was queued must not be notified.
        if not coach_assignment_active(recipient, athlete, organization):
            continue

        specs.append(
            NotificationSpec(
                recipient=recipient,
                event_type=EVENT_WORKOUT_COMPLETED,
                category=EVENT_CATEGORY[EVENT_WORKOUT_COMPLETED],
                title_key="notifications.workout_completed.title",
                body_key="notifications.workout_completed.body",
                payload={
                    "workout_session_id": payload.get("workout_session_id"),
                    "athlete_user_id": payload.get("athlete_user_id"),
                    "actor_display_name": actor_name,
                    "route": f"/coach/sessions/{payload.get('workout_session_id')}",
                },
                dedupe_key=_dedupe_key(EVENT_WORKOUT_COMPLETED, envelope["event_id"], recipient.id),
            )
        )
    return specs


def map_feedback_flag_created(envelope):
    payload = envelope.get("payload") or {}
    organization = _organization(envelope)
    if organization is None:
        return []

    athlete = User.objects.filter(id=payload.get("athlete_user_id")).first()
    actor_name = _actor_display_name(envelope)
    specs = []

    for recipient_id in payload.get("recipient_user_ids") or []:
        recipient = User.objects.filter(id=recipient_id, is_active=True).first()
        if recipient is None or athlete is None:
            continue
        if not has_active_membership(recipient, organization):
            continue
        if not coach_assignment_active(recipient, athlete, organization):
            continue

        specs.append(
            NotificationSpec(
                recipient=recipient,
                event_type=EVENT_FEEDBACK_FLAG_CREATED,
                category=EVENT_CATEGORY[EVENT_FEEDBACK_FLAG_CREATED],
                title_key="notifications.feedback_flag.title",
                body_key="notifications.feedback_flag.body",
                payload={
                    # Severity and type only. Free-text clinical detail stays in
                    # the source record behind its own authorization check.
                    "feedback_flag_id": payload.get("feedback_flag_id"),
                    "workout_session_id": payload.get("workout_session_id"),
                    "athlete_user_id": payload.get("athlete_user_id"),
                    "flag_type": payload.get("flag_type"),
                    "severity": payload.get("severity"),
                    "actor_display_name": actor_name,
                    "route": f"/coach/sessions/{payload.get('workout_session_id')}",
                },
                dedupe_key=_dedupe_key(
                    EVENT_FEEDBACK_FLAG_CREATED, envelope["event_id"], recipient.id
                ),
            )
        )
    return specs


MAPPERS = {
    (EVENT_MESSAGE_SENT, 1): map_message_sent,
    (EVENT_WORKOUT_COMPLETED, 1): map_workout_completed,
    (EVENT_FEEDBACK_FLAG_CREATED, 1): map_feedback_flag_created,
}


class UnsupportedEventVersion(Exception):
    """Raised for an event whose (type, schema_version) has no mapper."""


def map_envelope(envelope):
    """Resolve and run the mapper for an envelope."""
    key = (envelope.get("event_type"), envelope.get("schema_version"))
    mapper = MAPPERS.get(key)
    if mapper is None:
        raise UnsupportedEventVersion(f"No mapper for {key}")
    return mapper(envelope)
