"""
Phase 08 Stage 5 — adversarial authorization and tenant-isolation tests.

Every denial path is asserted for BOTH the outcome and the absence of an
existence signal: a caller who is not entitled must not be able to distinguish
"this conversation belongs to another tenant" from "this id does not exist".
"""

import pytest
from django.utils import timezone
from helpers import login

from apps.communication.models import (
    Conversation,
    ConversationParticipant,
    Message,
    Notification,
)
from apps.organizations.models import Membership

pytestmark = pytest.mark.django_db


def thread_for(client, world):
    login(client, world.coach)
    response = client.post(
        "/api/v1/conversations",
        data={"counterpart_user_id": world.athlete.id},
        content_type="application/json",
    )
    conversation_id = response.json()["id"]
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "private coaching content"},
        content_type="application/json",
    )
    client.logout()
    return conversation_id


ENDPOINTS = [
    ("get", "/api/v1/conversations/{cid}"),
    ("get", "/api/v1/conversations/{cid}/messages"),
    ("post", "/api/v1/conversations/{cid}/messages"),
    ("post", "/api/v1/conversations/{cid}/read"),
    ("post", "/api/v1/conversations/{cid}/mute"),
]


def call(client, method, path):
    if method == "get":
        return client.get(path)
    return client.post(
        path, data={"body": "intrusion", "is_muted": True}, content_type="application/json"
    )


# --- Unauthenticated --------------------------------------------------------- #


@pytest.mark.parametrize("method,template", ENDPOINTS)
def test_anonymous_is_denied_everywhere(client, world, method, template):
    conversation_id = thread_for(client, world)
    response = call(client, method, template.format(cid=conversation_id))
    assert response.status_code in (401, 403)


def test_anonymous_cannot_list_conversations_or_notifications(client, world):
    assert client.get("/api/v1/conversations").status_code in (401, 403)
    assert client.get("/api/v1/notifications").status_code in (401, 403)
    assert client.get("/api/v1/notification-preferences").status_code in (401, 403)


# --- Cross-tenant ------------------------------------------------------------ #


@pytest.mark.parametrize("method,template", ENDPOINTS)
def test_cross_tenant_user_gets_404(client, world, other_world, method, template):
    conversation_id = thread_for(client, world)
    login(client, other_world.coach)
    response = call(client, method, template.format(cid=conversation_id))
    assert response.status_code == 404


def test_cross_tenant_enumeration_is_indistinguishable(client, world, other_world):
    """A real foreign id and a fabricated id must produce identical responses."""
    conversation_id = thread_for(client, world)
    login(client, other_world.coach)

    real = client.get(f"/api/v1/conversations/{conversation_id}")
    fake = client.get("/api/v1/conversations/01999999-0000-7000-8000-000000000000")

    assert real.status_code == fake.status_code == 404
    assert real.json() == fake.json()


def test_cross_tenant_conversation_creation_is_404(client, world, other_world):
    login(client, world.coach)
    response = client.post(
        "/api/v1/conversations",
        data={"counterpart_user_id": other_world.athlete.id},
        content_type="application/json",
    )
    assert response.status_code == 404


def test_inbox_never_lists_other_tenant_threads(client, world, other_world):
    thread_for(client, world)
    login(client, other_world.coach)
    assert client.get("/api/v1/conversations").json()["conversations"] == []


# --- Non-participants in the same tenant ------------------------------------- #


@pytest.mark.parametrize("method,template", ENDPOINTS)
def test_unassigned_coach_same_org_gets_404(client, world, method, template):
    conversation_id = thread_for(client, world)
    login(client, world.other_coach)
    response = call(client, method, template.format(cid=conversation_id))
    assert response.status_code == 404


@pytest.mark.parametrize("method,template", ENDPOINTS)
def test_support_role_gets_404(client, world, method, template):
    conversation_id = thread_for(client, world)
    login(client, world.support)
    response = call(client, method, template.format(cid=conversation_id))
    assert response.status_code == 404


@pytest.mark.parametrize("method,template", ENDPOINTS)
def test_owner_has_no_private_message_backdoor(client, world, method, template):
    """
    Contract AMD-08-01: an owner who is not a participant has no read path into
    private coach-athlete message content, audited or otherwise.
    """
    conversation_id = thread_for(client, world)
    login(client, world.owner)
    response = call(client, method, template.format(cid=conversation_id))
    assert response.status_code == 404


def test_support_cannot_open_a_conversation(client, world):
    login(client, world.support)
    response = client.post(
        "/api/v1/conversations",
        data={"counterpart_user_id": world.athlete.id},
        content_type="application/json",
    )
    assert response.status_code == 403


def test_unassigned_coach_cannot_open_a_conversation(client, world):
    login(client, world.other_coach)
    response = client.post(
        "/api/v1/conversations",
        data={"counterpart_user_id": world.athlete.id},
        content_type="application/json",
    )
    assert response.status_code == 403
    assert response.json()["message_key"] == "errors.authz.unassigned_athlete"


# --- Suspension and revocation ------------------------------------------------ #


@pytest.mark.parametrize("method,template", ENDPOINTS)
def test_suspended_membership_loses_all_access(client, world, method, template):
    conversation_id = thread_for(client, world)
    Membership.objects.filter(user=world.athlete, organization=world.org).update(status="suspended")
    login(client, world.athlete)
    response = call(client, method, template.format(cid=conversation_id))
    assert response.status_code == 404


def test_archived_membership_loses_access(client, world):
    conversation_id = thread_for(client, world)
    Membership.objects.filter(user=world.athlete, organization=world.org).update(status="archived")
    login(client, world.athlete)
    assert client.get(f"/api/v1/conversations/{conversation_id}").status_code == 404


def test_deactivated_user_is_denied(client, world):
    conversation_id = thread_for(client, world)
    login(client, world.athlete)
    world.athlete.is_active = False
    world.athlete.save(update_fields=["is_active"])
    assert client.get(f"/api/v1/conversations/{conversation_id}").status_code in (401, 403, 404)


def test_removed_participant_loses_access_immediately(client, world):
    conversation_id = thread_for(client, world)
    ConversationParticipant.objects.filter(
        conversation_id=conversation_id, user=world.athlete
    ).update(left_at=timezone.now())

    login(client, world.athlete)
    assert client.get(f"/api/v1/conversations/{conversation_id}").status_code == 404
    assert client.get("/api/v1/conversations").json()["conversations"] == []


def test_reassignment_revokes_send_but_preserves_legitimate_history(client, world):
    """
    A coach whose assignment is revoked keeps the history they legitimately
    participated in, but may no longer send. Revocation never widens access.
    """
    conversation_id = thread_for(client, world)
    world.assignment.is_active = False
    world.assignment.save(update_fields=["is_active"])

    login(client, world.coach)
    read = client.get(f"/api/v1/conversations/{conversation_id}/messages")
    assert read.status_code == 200
    assert len(read.json()["messages"]) == 1

    send = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "still coaching?"},
        content_type="application/json",
    )
    assert send.status_code == 403
    assert send.json()["message_key"] == "errors.authz.unassigned_athlete"

    detail = client.get(f"/api/v1/conversations/{conversation_id}").json()
    assert detail["can_send"] is False
    assert detail["send_block_key"] == "errors.authz.unassigned_athlete"


def test_athlete_cannot_send_after_coach_assignment_revoked(client, world):
    conversation_id = thread_for(client, world)
    world.assignment.is_active = False
    world.assignment.save(update_fields=["is_active"])

    login(client, world.athlete)
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "are you there"},
        content_type="application/json",
    )
    assert response.status_code == 403


def test_send_blocked_when_counterpart_membership_suspended(client, world):
    conversation_id = thread_for(client, world)
    Membership.objects.filter(user=world.athlete, organization=world.org).update(status="suspended")
    login(client, world.coach)
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "hello"},
        content_type="application/json",
    )
    assert response.status_code == 403
    assert response.json()["message_key"] == "errors.messaging.participant_inactive"


def test_archived_conversation_is_read_only(client, world):
    conversation_id = thread_for(client, world)
    Conversation.objects.filter(id=conversation_id).update(is_archived=True)

    login(client, world.coach)
    assert client.get(f"/api/v1/conversations/{conversation_id}/messages").status_code == 200
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "reopening"},
        content_type="application/json",
    )
    assert response.status_code == 409
    assert response.json()["message_key"] == "errors.messaging.conversation_archived"


def test_user_cannot_message_self(client, world):
    login(client, world.coach)
    response = client.post(
        "/api/v1/conversations",
        data={"counterpart_user_id": world.coach.id},
        content_type="application/json",
    )
    assert response.status_code in (403, 404)


# --- Notification scoping ------------------------------------------------------ #


def test_notifications_are_self_scoped(client, world):
    coach_notification = Notification.objects.create(
        organization=world.org,
        recipient_user=world.coach,
        event_type="message.sent",
        category="messaging",
        title_key="notifications.message_sent.title",
        body_key="notifications.message_sent.body",
        dedupe_key="message.sent:evt-1:coach",
    )

    login(client, world.athlete)
    listing = client.get("/api/v1/notifications").json()
    assert listing["notifications"] == []

    # Another user's notification id must 404, not 403: no enumeration oracle.
    read = client.post(f"/api/v1/notifications/{coach_notification.id}/read")
    assert read.status_code == 404
    fake = client.post("/api/v1/notifications/01999999-0000-7000-8000-000000000000/read")
    assert read.json() == fake.json()


def test_read_all_only_touches_own_notifications(client, world):
    Notification.objects.create(
        organization=world.org,
        recipient_user=world.coach,
        event_type="message.sent",
        category="messaging",
        title_key="t",
        body_key="b",
        dedupe_key="d-coach",
    )
    Notification.objects.create(
        organization=world.org,
        recipient_user=world.athlete,
        event_type="message.sent",
        category="messaging",
        title_key="t",
        body_key="b",
        dedupe_key="d-athlete",
    )

    login(client, world.athlete)
    response = client.post("/api/v1/notifications/read-all")
    assert response.json()["updated"] == 1
    assert Notification.objects.get(recipient_user=world.coach).read_at is None


def test_suspended_user_cannot_read_notifications(client, world):
    Notification.objects.create(
        organization=world.org,
        recipient_user=world.athlete,
        event_type="message.sent",
        category="messaging",
        title_key="t",
        body_key="b",
        dedupe_key="d1",
    )
    login(client, world.athlete)
    world.athlete.is_active = False
    world.athlete.save(update_fields=["is_active"])
    assert client.get("/api/v1/notifications").status_code in (401, 403)


def test_message_visibility_requires_participation_not_just_tenancy(client, world):
    """A same-tenant Message row must never be reachable without participation."""
    conversation_id = thread_for(client, world)
    assert Message.objects.filter(conversation_id=conversation_id).exists()

    login(client, world.other_coach)
    response = client.get(f"/api/v1/conversations/{conversation_id}/messages")
    assert response.status_code == 404
    assert "private coaching content" not in response.content.decode()
