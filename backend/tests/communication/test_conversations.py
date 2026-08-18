"""
Phase 08 Stage 2 — conversation and message API behaviour.

Covers creation idempotency, pagination boundaries and stable ordering, message
validation bounds, idempotent submission, read-state semantics, and unread
counts. Authorization has its own module (test_authorization.py).
"""

import datetime

import pytest
from django.utils import timezone
from helpers import login, make_session

from apps.communication.constants import MESSAGE_MAX_LENGTH, UNREAD_COUNT_CAP
from apps.communication.models import (
    Conversation,
    ConversationParticipant,
    Message,
    OutboxRecord,
)

pytestmark = pytest.mark.django_db


def open_conversation(client, counterpart):
    return client.post(
        "/api/v1/conversations",
        data={"counterpart_user_id": counterpart.id},
        content_type="application/json",
    )


def test_coach_opens_conversation_with_assigned_athlete(client, world):
    login(client, world.coach)
    response = open_conversation(client, world.athlete)

    assert response.status_code == 201
    body = response.json()
    assert body["kind"] == "direct"
    assert body["organization_id"] == world.org.id
    assert body["counterpart"]["user_id"] == world.athlete.id
    assert body["counterpart"]["display_name"] == "Athlete Neda"
    # Counterpart payloads must never carry an email address.
    assert "email" not in body["counterpart"]
    assert ConversationParticipant.objects.filter(conversation_id=body["id"]).count() == 2


def test_conversation_creation_is_idempotent(client, world):
    login(client, world.coach)
    first = open_conversation(client, world.athlete)
    second = open_conversation(client, world.athlete)

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert Conversation.objects.count() == 1


def test_athlete_can_open_conversation_with_assigned_coach(client, world):
    login(client, world.athlete)
    response = open_conversation(client, world.coach)
    assert response.status_code == 201


def test_workout_context_conversation_is_separate_thread(client, world):
    session = make_session(world)
    login(client, world.coach)

    plain = open_conversation(client, world.athlete)
    contextual = client.post(
        "/api/v1/conversations",
        data={
            "counterpart_user_id": world.athlete.id,
            "context_type": "workout_session",
            "context_id": session.id,
        },
        content_type="application/json",
    )

    assert contextual.status_code == 201
    assert contextual.json()["id"] != plain.json()["id"]
    assert contextual.json()["context_type"] == "workout_session"
    assert contextual.json()["context_id"] == session.id


def test_workout_context_requires_context_id(client, world):
    login(client, world.coach)
    response = client.post(
        "/api/v1/conversations",
        data={"counterpart_user_id": world.athlete.id, "context_type": "workout_session"},
        content_type="application/json",
    )
    assert response.status_code == 400


def test_cross_tenant_workout_context_is_not_found(client, world, other_world):
    foreign_session = make_session(other_world)
    login(client, world.coach)
    response = client.post(
        "/api/v1/conversations",
        data={
            "counterpart_user_id": world.athlete.id,
            "context_type": "workout_session",
            "context_id": foreign_session.id,
        },
        content_type="application/json",
    )
    assert response.status_code == 404


# --- Message send ----------------------------------------------------------- #


def _thread(client, world):
    login(client, world.coach)
    return open_conversation(client, world.athlete).json()["id"]


def test_send_message_creates_message_and_outbox_event(client, world):
    conversation_id = _thread(client, world)

    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "Great depth on set 3, keep the chest tall."},
        content_type="application/json",
    )

    assert response.status_code == 201
    body = response.json()
    assert body["body"] == "Great depth on set 3, keep the chest tall."
    assert body["sender_user_id"] == world.coach.id

    record = OutboxRecord.objects.get(event_type="message.sent")
    assert record.status == "pending"
    assert record.subject_id == body["id"]
    # The event must never carry the message body.
    assert "body" not in record.payload
    assert record.payload["recipient_user_ids"] == [world.athlete.id]

    conversation = Conversation.objects.get(id=conversation_id)
    assert conversation.last_message_at is not None
    assert conversation.last_message_preview.startswith("Great depth")


def test_message_send_is_idempotent_by_client_message_id(client, world):
    conversation_id = _thread(client, world)
    payload = {"body": "Same message", "client_message_id": "client-abc-1"}

    first = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data=payload,
        content_type="application/json",
    )
    second = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data=payload,
        content_type="application/json",
    )

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json()["id"] == second.json()["id"]
    assert Message.objects.count() == 1
    # A replay must not emit a second event either.
    assert OutboxRecord.objects.filter(event_type="message.sent").count() == 1


def test_empty_body_rejected_with_message_key(client, world):
    conversation_id = _thread(client, world)
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "   \n\t  "},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.json()["message_key"] == "errors.messaging.body_empty"


def test_oversized_body_rejected(client, world):
    conversation_id = _thread(client, world)
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "a" * (MESSAGE_MAX_LENGTH + 1)},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.json()["message_key"] == "errors.messaging.body_too_long"


def test_maximum_length_body_accepted(client, world):
    conversation_id = _thread(client, world)
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "a" * MESSAGE_MAX_LENGTH},
        content_type="application/json",
    )
    assert response.status_code == 201


def test_non_string_body_rejected(client, world):
    conversation_id = _thread(client, world)
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": {"nested": "object"}},
        content_type="application/json",
    )
    assert response.status_code == 422


def test_message_body_is_immutable(client, world):
    conversation_id = _thread(client, world)
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "original"},
        content_type="application/json",
    )
    message = Message.objects.get()
    message.body = "tampered"
    with pytest.raises(ValueError):
        message.save()


# --- Pagination -------------------------------------------------------------- #


def test_message_history_pagination_is_stable_and_bounded(client, world):
    conversation_id = _thread(client, world)
    for index in range(12):
        client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            data={"body": f"message {index}", "client_message_id": f"c{index}"},
            content_type="application/json",
        )

    first = client.get(f"/api/v1/conversations/{conversation_id}/messages?limit=5").json()
    assert len(first["messages"]) == 5
    assert first["has_more"] is True
    assert first["messages"][0]["body"] == "message 11"

    second = client.get(
        f"/api/v1/conversations/{conversation_id}/messages?limit=5&before={first['next_cursor']}"
    ).json()
    assert len(second["messages"]) == 5
    assert second["messages"][0]["body"] == "message 6"

    first_ids = {m["id"] for m in first["messages"]}
    second_ids = {m["id"] for m in second["messages"]}
    assert first_ids.isdisjoint(second_ids)


def test_message_page_size_is_capped(client, world):
    conversation_id = _thread(client, world)
    for index in range(60):
        Message.objects.create(
            conversation_id=conversation_id, sender_user=world.coach, body=f"m{index}"
        )
    response = client.get(f"/api/v1/conversations/{conversation_id}/messages?limit=9999").json()
    assert len(response["messages"]) == 50


def test_malformed_cursor_is_ignored_safely(client, world):
    conversation_id = _thread(client, world)
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "hello"},
        content_type="application/json",
    )
    response = client.get(
        f"/api/v1/conversations/{conversation_id}/messages?before=%%%not-base64%%%"
    )
    assert response.status_code == 200
    assert len(response.json()["messages"]) == 1


def test_inbox_orders_by_recent_activity(client, world):
    login(client, world.coach)
    first_id = open_conversation(client, world.athlete).json()["id"]

    from apps.communication.models import Conversation as ConversationModel
    from apps.organizations.models import Membership

    second_athlete = world.athlete
    # Second thread with workout context to get a distinct conversation.
    session = make_session(world)
    second_id = client.post(
        "/api/v1/conversations",
        data={
            "counterpart_user_id": second_athlete.id,
            "context_type": "workout_session",
            "context_id": session.id,
        },
        content_type="application/json",
    ).json()["id"]

    assert Membership.objects.filter(user=world.coach, status="active").exists()

    ConversationModel.objects.filter(id=first_id).update(
        last_message_at=timezone.now() - datetime.timedelta(hours=2)
    )
    ConversationModel.objects.filter(id=second_id).update(last_message_at=timezone.now())

    inbox = client.get("/api/v1/conversations").json()["conversations"]
    assert [c["id"] for c in inbox] == [second_id, first_id]


def test_empty_inbox_returns_empty_list(client, world):
    login(client, world.athlete)
    response = client.get("/api/v1/conversations")
    assert response.status_code == 200
    assert response.json() == {"conversations": [], "next_cursor": None}


# --- Read state -------------------------------------------------------------- #


def test_unread_count_and_mark_read(client, world):
    conversation_id = _thread(client, world)
    for index in range(3):
        client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            data={"body": f"coach note {index}", "client_message_id": f"k{index}"},
            content_type="application/json",
        )

    login(client, world.athlete)
    inbox = client.get("/api/v1/conversations").json()["conversations"]
    assert inbox[0]["unread_count"] == 3

    read = client.post(
        f"/api/v1/conversations/{conversation_id}/read",
        data={},
        content_type="application/json",
    )
    assert read.status_code == 200
    assert read.json()["unread_count"] == 0

    inbox = client.get("/api/v1/conversations").json()["conversations"]
    assert inbox[0]["unread_count"] == 0


def test_own_messages_never_count_as_unread(client, world):
    conversation_id = _thread(client, world)
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "my own message"},
        content_type="application/json",
    )
    inbox = client.get("/api/v1/conversations").json()["conversations"]
    assert inbox[0]["unread_count"] == 0


def test_read_cursor_only_moves_forward(client, world):
    conversation_id = _thread(client, world)
    login(client, world.athlete)

    client.post(
        f"/api/v1/conversations/{conversation_id}/read",
        data={},
        content_type="application/json",
    )
    participant = ConversationParticipant.objects.get(
        conversation_id=conversation_id, user=world.athlete
    )
    forward_cursor = participant.last_read_at

    stale = (timezone.now() - datetime.timedelta(days=1)).isoformat()
    client.post(
        f"/api/v1/conversations/{conversation_id}/read",
        data={"read_at": stale},
        content_type="application/json",
    )
    participant.refresh_from_db()
    assert participant.last_read_at == forward_cursor


def test_future_read_cursor_is_clamped_to_now(client, world):
    conversation_id = _thread(client, world)
    login(client, world.athlete)
    future = (timezone.now() + datetime.timedelta(days=365)).isoformat()
    client.post(
        f"/api/v1/conversations/{conversation_id}/read",
        data={"read_at": future},
        content_type="application/json",
    )
    participant = ConversationParticipant.objects.get(
        conversation_id=conversation_id, user=world.athlete
    )
    assert participant.last_read_at <= timezone.now()


def test_marking_read_does_not_mutate_messages(client, world):
    conversation_id = _thread(client, world)
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "unchanged"},
        content_type="application/json",
    )
    before = list(Message.objects.values("id", "body", "created_at"))

    login(client, world.athlete)
    client.post(
        f"/api/v1/conversations/{conversation_id}/read",
        data={},
        content_type="application/json",
    )
    assert list(Message.objects.values("id", "body", "created_at")) == before


def test_unread_count_is_capped(client, world):
    conversation_id = _thread(client, world)
    Message.objects.bulk_create(
        [
            Message(conversation_id=conversation_id, sender_user=world.coach, body=f"m{i}")
            for i in range(UNREAD_COUNT_CAP + 25)
        ]
    )
    login(client, world.athlete)
    inbox = client.get("/api/v1/conversations").json()["conversations"]
    assert inbox[0]["unread_count"] == UNREAD_COUNT_CAP


def test_history_bounded_by_join_time(client, world):
    """Adding a participant must not grant retroactive access."""
    conversation_id = _thread(client, world)
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "before the owner joined"},
        content_type="application/json",
    )

    later = timezone.now() + datetime.timedelta(seconds=1)
    ConversationParticipant.objects.create(
        conversation_id=conversation_id,
        user=world.owner,
        role_at_join="owner",
        joined_at=later,
    )

    login(client, world.owner)
    response = client.get(f"/api/v1/conversations/{conversation_id}/messages")
    assert response.status_code == 200
    assert response.json()["messages"] == []
