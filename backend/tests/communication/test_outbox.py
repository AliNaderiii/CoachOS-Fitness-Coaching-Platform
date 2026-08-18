"""
Phase 08 Stage 3 — transactional outbox, event mapping, dedupe, and retries.
"""

import datetime

import pytest
from django.db import transaction
from django.utils import timezone
from helpers import login, make_session

from apps.communication import dispatcher
from apps.communication.constants import OUTBOX_MAX_ATTEMPTS
from apps.communication.events import EventPayloadError, emit_event
from apps.communication.mapping import UnsupportedEventVersion, map_envelope
from apps.communication.models import (
    Conversation,
    ConversationParticipant,
    Message,
    Notification,
    OutboxRecord,
)

pytestmark = pytest.mark.django_db


def send_one(client, world, body="hello there"):
    login(client, world.coach)
    conversation_id = client.post(
        "/api/v1/conversations",
        data={"counterpart_user_id": world.athlete.id},
        content_type="application/json",
    ).json()["id"]
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": body},
        content_type="application/json",
    )
    return conversation_id


# --- Transactionality --------------------------------------------------------- #


def test_event_rolls_back_with_the_domain_write(world):
    """If the source transaction aborts, the outbox record must not survive."""
    conversation = Conversation.objects.create(
        organization=world.org,
        participant_key="k",
        created_by_user=world.coach,
    )
    ConversationParticipant.objects.create(
        conversation=conversation, user=world.coach, role_at_join="coach"
    )

    class Boom(Exception):
        pass

    with pytest.raises(Boom):
        with transaction.atomic():
            message = Message.objects.create(
                conversation=conversation, sender_user=world.coach, body="doomed"
            )
            emit_event(
                event_type="message.sent",
                organization=world.org,
                actor_user=world.coach,
                subject_type="Message",
                subject_id=message.id,
                payload={"conversation_id": conversation.id, "recipient_user_ids": []},
            )
            raise Boom()

    assert Message.objects.filter(body="doomed").count() == 0
    assert OutboxRecord.objects.count() == 0


def test_event_payload_rejects_forbidden_keys(world):
    with pytest.raises(EventPayloadError):
        emit_event(
            event_type="message.sent",
            organization=world.org,
            actor_user=world.coach,
            subject_type="Message",
            subject_id="m1",
            payload={"body": "secret content"},
        )


def test_event_payload_rejects_nested_forbidden_keys(world):
    with pytest.raises(EventPayloadError):
        emit_event(
            event_type="message.sent",
            organization=world.org,
            actor_user=world.coach,
            subject_type="Message",
            subject_id="m1",
            payload={"meta": {"email": "leak@example.test"}},
        )


def test_unknown_event_type_is_rejected(world):
    with pytest.raises(ValueError):
        emit_event(
            event_type="nutrition.logged",
            organization=world.org,
            actor_user=world.coach,
            subject_type="X",
            subject_id="1",
        )


def test_envelope_shape_is_versioned_and_complete(client, world):
    send_one(client, world)
    envelope = OutboxRecord.objects.get(event_type="message.sent").envelope()

    for field in (
        "schema_version",
        "event_id",
        "event_type",
        "occurred_at",
        "tenant_id",
        "actor_user_id",
        "subject_type",
        "subject_id",
        "correlation_id",
        "payload",
    ):
        assert field in envelope
    assert envelope["schema_version"] == 1
    assert envelope["tenant_id"] == world.org.id


# --- Dispatch and dedupe -------------------------------------------------------- #


def test_dispatcher_creates_durable_notification(client, world):
    send_one(client, world)
    summaries = dispatcher.run_dispatcher()

    assert summaries == [
        {
            "event_id": OutboxRecord.objects.get().event_id,
            "created": 1,
            "status": "processed",
        }
    ]
    notification = Notification.objects.get()
    assert notification.recipient_user_id == world.athlete.id
    assert notification.event_type == "message.sent"
    assert notification.category == "messaging"
    assert notification.read_at is None
    # Payload carries routing metadata only — never the message body.
    assert "body" not in notification.payload
    assert notification.payload["actor_display_name"] == "Coach Reza"
    assert notification.payload["route"].startswith("/messages/")


def test_reprocessing_the_same_event_creates_no_duplicate(client, world):
    send_one(client, world)
    dispatcher.run_dispatcher()

    record = OutboxRecord.objects.get()
    record.status = "pending"
    record.next_attempt_at = timezone.now()
    record.save(update_fields=["status", "next_attempt_at"])

    dispatcher.run_dispatcher()
    assert Notification.objects.count() == 1


def test_two_distinct_events_create_two_notifications(client, world):
    conversation_id = send_one(client, world, body="first")
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "second"},
        content_type="application/json",
    )
    dispatcher.run_dispatcher()
    assert Notification.objects.count() == 2


def test_claim_is_exclusive(client, world):
    send_one(client, world)
    first = dispatcher.claim_records()
    second = dispatcher.claim_records()

    assert len(first) == 1
    assert second == []


def test_stale_claim_is_recovered(client, world):
    send_one(client, world)
    dispatcher.claim_records()

    OutboxRecord.objects.update(claimed_at=timezone.now() - datetime.timedelta(hours=2))
    recovered = dispatcher.claim_records()
    assert len(recovered) == 1


def test_muted_participant_receives_no_notification(client, world):
    conversation_id = send_one(client, world)
    ConversationParticipant.objects.filter(
        conversation_id=conversation_id, user=world.athlete
    ).update(is_muted=True)

    OutboxRecord.objects.update(status="pending", next_attempt_at=timezone.now())
    dispatcher.run_dispatcher()
    assert Notification.objects.count() == 0


def test_revoked_membership_between_emit_and_dispatch_suppresses_notification(client, world):
    """An event queued before revocation must not notify after revocation."""
    from apps.organizations.models import Membership

    send_one(client, world)
    Membership.objects.filter(user=world.athlete, organization=world.org).update(status="suspended")

    dispatcher.run_dispatcher()
    assert Notification.objects.count() == 0


# --- Retry and dead-letter -------------------------------------------------------- #


def test_backoff_is_bounded_and_exponential():
    assert dispatcher.backoff_seconds(1) == 30
    assert dispatcher.backoff_seconds(2) == 60
    assert dispatcher.backoff_seconds(3) == 120
    assert dispatcher.backoff_seconds(50) == 3600


def test_mapping_failure_schedules_a_retry(client, world, monkeypatch):
    send_one(client, world)

    def boom(_envelope):
        raise RuntimeError("mapper exploded")

    monkeypatch.setattr(dispatcher, "map_envelope", boom)
    dispatcher.run_dispatcher()

    record = OutboxRecord.objects.get()
    assert record.status == "pending"
    assert record.attempts == 1
    assert record.last_error_code == "mapping_error"
    assert record.next_attempt_at > timezone.now()
    # Error codes only: no exception text is persisted.
    assert "exploded" not in record.last_error_code


def test_exhausted_retries_dead_letter(client, world, monkeypatch):
    send_one(client, world)

    def boom(_envelope):
        raise RuntimeError("still broken")

    monkeypatch.setattr(dispatcher, "map_envelope", boom)

    for _ in range(OUTBOX_MAX_ATTEMPTS):
        OutboxRecord.objects.filter(status="pending").update(next_attempt_at=timezone.now())
        dispatcher.run_dispatcher()

    record = OutboxRecord.objects.get()
    assert record.status == "dead_letter"
    assert record.attempts >= OUTBOX_MAX_ATTEMPTS


def test_unsupported_schema_version_dead_letters_immediately(client, world):
    send_one(client, world)
    OutboxRecord.objects.update(schema_version=99)
    dispatcher.run_dispatcher()

    record = OutboxRecord.objects.get()
    assert record.status == "dead_letter"
    assert record.last_error_code == "unsupported_event_version"


def test_map_envelope_raises_for_unknown_version():
    with pytest.raises(UnsupportedEventVersion):
        map_envelope(
            {"event_type": "message.sent", "schema_version": 42, "event_id": "e", "payload": {}}
        )


# --- Phase 07 hooks ------------------------------------------------------------- #


def test_workout_completion_emits_event_and_notifies_assigned_coach(client, world):
    session = make_session(world)
    login(client, world.athlete)

    response = client.post(
        f"/api/v1/workout-sessions/{session.id}",
        data={"session_rpe": 7},
        content_type="application/json",
    )
    assert response.status_code == 200

    record = OutboxRecord.objects.get(event_type="workout.completed")
    assert record.payload["recipient_user_ids"] == [world.coach.id]

    dispatcher.run_dispatcher()
    notification = Notification.objects.get(event_type="workout.completed")
    assert notification.recipient_user_id == world.coach.id
    assert notification.category == "training"


def test_feedback_flag_emits_safety_event(client, world):
    session = make_session(world)
    login(client, world.athlete)

    response = client.post(
        f"/api/v1/workout-sessions/{session.id}/feedback-flags",
        data={
            "flag_type": "joint_pain",
            "anatomical_location": "left shoulder",
            "severity": "moderate",
            "details": "discomfort during pressing",
        },
        content_type="application/json",
    )
    assert response.status_code == 201

    record = OutboxRecord.objects.get(event_type="feedback_flag.created")
    assert record.payload["severity"] == "moderate"
    # Free-text clinical detail must never enter the event payload.
    assert "details" not in record.payload
    assert "discomfort" not in str(record.payload)

    dispatcher.run_dispatcher()
    notification = Notification.objects.get(event_type="feedback_flag.created")
    assert notification.category == "safety"
    assert notification.recipient_user_id == world.coach.id
    assert "discomfort" not in str(notification.payload)


def test_unassigned_coach_receives_no_workout_event(client, world):
    session = make_session(world)
    world.assignment.is_active = False
    world.assignment.save(update_fields=["is_active"])

    login(client, world.athlete)
    client.post(
        f"/api/v1/workout-sessions/{session.id}",
        data={"session_rpe": 6},
        content_type="application/json",
    )
    assert OutboxRecord.objects.filter(event_type="workout.completed").count() == 0


def test_coach_unassigned_after_event_is_not_notified(client, world):
    session = make_session(world)
    login(client, world.athlete)
    client.post(
        f"/api/v1/workout-sessions/{session.id}",
        data={"session_rpe": 6},
        content_type="application/json",
    )
    assert OutboxRecord.objects.filter(event_type="workout.completed").exists()

    world.assignment.is_active = False
    world.assignment.save(update_fields=["is_active"])

    dispatcher.run_dispatcher()
    assert Notification.objects.filter(event_type="workout.completed").count() == 0
