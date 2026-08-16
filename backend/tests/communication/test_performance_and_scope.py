"""
Phase 08 Stage 5 — measured query behaviour and scope-boundary enforcement.

Query-count assertions guard against N+1 regressions on the two hot paths
(inbox and message history). Absolute latency numbers are recorded in the phase
report; they are environment-dependent and are NOT presented as SLOs.
"""

import pathlib
import re

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from helpers import login

from apps.communication.models import Conversation, ConversationParticipant, Message

pytestmark = pytest.mark.django_db

BACKEND_ROOT = pathlib.Path(__file__).resolve().parents[2]
COMMUNICATION_APP = BACKEND_ROOT / "apps" / "communication"


def seed_inbox(world, conversations=20, messages_each=20, prefix="seed"):
    from apps.communication.constants import build_preview

    created = []
    for index in range(conversations):
        conversation = Conversation.objects.create(
            organization=world.org,
            participant_key=f"{prefix}-{index}",
            created_by_user=world.coach,
        )
        ConversationParticipant.objects.create(
            conversation=conversation, user=world.coach, role_at_join="coach"
        )
        ConversationParticipant.objects.create(
            conversation=conversation, user=world.athlete, role_at_join="athlete"
        )
        rows = [
            Message(
                conversation=conversation,
                sender_user=world.athlete,
                body=f"seed message {number}",
            )
            for number in range(messages_each)
        ]
        Message.objects.bulk_create(rows)
        last = Message.objects.filter(conversation=conversation).order_by("-created_at").first()
        conversation.last_message_at = last.created_at
        conversation.last_message_preview = build_preview(last.body)
        conversation.save(update_fields=["last_message_at", "last_message_preview"])
        created.append(conversation)
    return created


def test_inbox_query_count_is_bounded_and_independent_of_page_size(client, world):
    """
    The inbox performs a bounded number of queries per page. It grows with page
    size only through the per-row counterpart/unread lookups, which are capped
    by the page-size bound (max 50), never by total inbox size.
    """
    seed_inbox(world, conversations=20, messages_each=20)
    login(client, world.coach)

    with CaptureQueriesContext(connection) as small:
        response = client.get("/api/v1/conversations?limit=5")
        assert response.status_code == 200
        assert len(response.json()["conversations"]) == 5

    seed_inbox(world, conversations=20, messages_each=20, prefix="grown")

    with CaptureQueriesContext(connection) as after_growth:
        response = client.get("/api/v1/conversations?limit=5")
        assert len(response.json()["conversations"]) == 5

    # Doubling the total inbox size must not change the query count for a page.
    assert len(after_growth) == len(small)
    assert len(small) <= 25


def test_message_history_uses_a_constant_number_of_queries(client, world):
    conversations = seed_inbox(world, conversations=1, messages_each=200)
    conversation = conversations[0]
    login(client, world.coach)

    with CaptureQueriesContext(connection) as small_page:
        client.get(f"/api/v1/conversations/{conversation.id}/messages?limit=10")

    with CaptureQueriesContext(connection) as large_page:
        client.get(f"/api/v1/conversations/{conversation.id}/messages?limit=50")

    # select_related on the sender prevents an N+1: the count must not grow
    # with the number of returned messages.
    assert len(large_page) == len(small_page)
    assert len(small_page) <= 10


def test_notification_list_query_count_is_bounded(client, world):
    from apps.communication.models import Notification

    Notification.objects.bulk_create(
        [
            Notification(
                organization=world.org,
                recipient_user=world.athlete,
                event_type="message.sent",
                category="messaging",
                title_key="t",
                body_key="b",
                dedupe_key=f"perf-{index}",
            )
            for index in range(300)
        ]
    )
    login(client, world.athlete)

    with CaptureQueriesContext(connection) as captured:
        response = client.get("/api/v1/notifications?limit=50")
        assert len(response.json()["notifications"]) == 50

    assert len(captured) <= 10


def test_responses_are_never_unbounded(client, world):
    seed_inbox(world, conversations=80, messages_each=5)
    login(client, world.coach)

    inbox = client.get("/api/v1/conversations?limit=1000").json()
    assert len(inbox["conversations"]) == 50
    assert inbox["next_cursor"] is not None


def test_required_indexes_exist():
    """The inbox and history hot paths must be index-backed."""
    conversation_indexes = {tuple(index.fields) for index in Conversation._meta.indexes}
    assert ("organization", "-last_message_at") in conversation_indexes

    message_indexes = {tuple(index.fields) for index in Message._meta.indexes}
    assert ("conversation", "-created_at", "-id") in message_indexes


# --- Scope boundary ------------------------------------------------------------- #


FORBIDDEN_SCOPE_PATTERNS = {
    "nutrition": r"\bnutrition|calorie|macro(?:nutrient)?s?\b|food_log",
    "billing": r"\bstripe|checkout|invoice|subscription_plan|payment_intent\b",
    "ai": r"\bopenai|anthropic|llm|gpt-|prompt_template|ai_summar",
    "durable_offline": r"indexedDB|BackgroundSyncManager|navigator\.sync",
    "sms_whatsapp": r"\btwilio|whatsapp\b|\bsms_",
    "wearable": r"\bhealthkit|google_?fit|garmin|fitbit\b",
    "marketplace": r"\bmarketplace|public_profile\b",
}


def _communication_sources():
    return [path for path in COMMUNICATION_APP.rglob("*.py") if "migrations" not in path.parts]


@pytest.mark.parametrize("label,pattern", sorted(FORBIDDEN_SCOPE_PATTERNS.items()))
def test_no_out_of_scope_domain_leaked_into_phase_08(label, pattern):
    compiled = re.compile(pattern, re.IGNORECASE)
    hits = []
    for path in _communication_sources():
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if compiled.search(line):
                hits.append(f"{path.name}:{number}: {line.strip()[:100]}")
    assert hits == [], f"Out-of-scope '{label}' reference found: {hits}"


def test_no_real_provider_credentials_are_present():
    """Phase 08 must contain no provider keys, VAPID keys, or SMTP credentials."""
    credential_patterns = [
        r"SMTP_PASSWORD\s*=\s*['\"][^'\"]+",
        r"VAPID_PRIVATE_KEY\s*=\s*['\"][^'\"]+",
        r"SG\.[A-Za-z0-9_\-]{20,}",
        r"BEGIN (?:RSA|EC|OPENSSH) PRIVATE KEY",
    ]
    hits = []
    for path in _communication_sources():
        content = path.read_text(encoding="utf-8")
        for pattern in credential_patterns:
            if re.search(pattern, content):
                hits.append(f"{path.name}: {pattern}")
    assert hits == []


def test_no_group_conversation_shortcut_exists():
    """
    Group messaging is not P0 and is not implemented. In particular there must
    be no 'organization-wide room' shortcut that would bypass per-participant
    authorization.
    """
    assert [choice[0] for choice in Conversation.KIND_CHOICES] == ["direct"]

    sources = "\n".join(path.read_text(encoding="utf-8") for path in _communication_sources())
    assert "org_room" not in sources
    assert "broadcast_all" not in sources


def test_no_arabic_resources_in_the_communication_app():
    for path in COMMUNICATION_APP.rglob("*"):
        if path.is_file():
            assert not path.name.startswith("ar-")
            assert path.name not in ("ar.json", "ar.po", "ar.mo")
