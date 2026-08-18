"""
Phase 08 Stage 5 — content safety, CSRF, rate limiting, privacy logging, and
scope-boundary enforcement.
"""

import json
import logging

import pytest
from django.test import Client
from helpers import login

from apps.audit.models import AuditEvent
from apps.communication.constants import (
    MESSAGE_MAX_LENGTH,
    MessageValidationError,
    normalize_message_body,
)
from apps.communication.models import Message, Notification, OutboxRecord

pytestmark = pytest.mark.django_db


def thread(client, world):
    login(client, world.coach)
    return client.post(
        "/api/v1/conversations",
        data={"counterpart_user_id": world.athlete.id},
        content_type="application/json",
    ).json()["id"]


# --- Content normalization ------------------------------------------------------- #


XSS_PAYLOADS = [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert(1)>",
    "javascript:alert(document.cookie)",
    "<iframe src='https://evil.test'></iframe>",
    '"><svg/onload=alert(1)>',
    "<a href='javascript:void(0)'>click</a>",
]


@pytest.mark.parametrize("payload", XSS_PAYLOADS)
def test_script_payloads_are_stored_and_returned_as_inert_text(client, world, payload):
    """
    CoachOS stores message bodies as plain text and never renders HTML. The API
    therefore returns the payload verbatim as a JSON string value; the safety
    guarantee is that no HTML is ever interpreted (asserted again in the
    frontend component tests).
    """
    conversation_id = thread(client, world)
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": payload},
        content_type="application/json",
    )
    assert response.status_code == 201

    stored = Message.objects.get()
    assert stored.body == payload

    # The response is JSON, not HTML: angle brackets are escaped by the JSON
    # encoder's string context and there is no HTML content type.
    assert response["Content-Type"].startswith("application/json")
    assert json.loads(response.content)["body"] == payload


def test_control_characters_are_stripped():
    assert normalize_message_body("hel\x00lo\x1b[31m") == "hello[31m"


def test_carriage_returns_are_normalized():
    """Prevents CR-based header/log injection shapes from ever being stored."""
    assert "\r" not in normalize_message_body("line one\r\nline two")


def test_bidi_override_characters_are_removed():
    """RLO/LRO can spoof visual order; isolates used by the UI are preserved."""
    assert normalize_message_body("safe\u202etxet") == "safetxet"
    assert "\u2068" in normalize_message_body("name \u2068Ali\u2069 here")


def test_unicode_is_nfc_normalized():
    decomposed = "cafe\u0301"
    assert normalize_message_body(decomposed) == "caf\u00e9"


def test_excessive_newlines_are_collapsed():
    assert normalize_message_body("a\n\n\n\n\n\nb") == "a\n\nb"


def test_length_is_validated_after_normalization():
    """Padding with control characters must not smuggle content past the bound."""
    padded = "a" * MESSAGE_MAX_LENGTH + "\x00" * 500
    assert len(normalize_message_body(padded)) == MESSAGE_MAX_LENGTH

    with pytest.raises(MessageValidationError):
        normalize_message_body("a" * (MESSAGE_MAX_LENGTH + 1))


def test_whitespace_only_body_is_rejected():
    for value in ("", "   ", "\n\n\t", "\u200b"):
        with pytest.raises(MessageValidationError):
            normalize_message_body(value)


def test_persian_content_is_preserved(client, world):
    conversation_id = thread(client, world)
    persian = "سلام، تمرین امروز عالی بود. لطفاً وزنه را ۲.۵ کیلوگرم افزایش بده."
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": persian},
        content_type="application/json",
    )
    assert response.status_code == 201
    assert json.loads(response.content)["body"] == persian


def test_mixed_bidi_content_is_preserved(client, world):
    conversation_id = thread(client, world)
    mixed = "امروز Bench Press را با ۸۰ kg انجام دادم — https://example.test/plan"
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": mixed},
        content_type="application/json",
    )
    assert response.status_code == 201
    assert json.loads(response.content)["body"] == mixed


# --- CSRF ------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "path_template,payload",
    [
        ("/api/v1/conversations", {"counterpart_user_id": "x"}),
        ("/api/v1/conversations/{cid}/messages", {"body": "csrf attempt"}),
        ("/api/v1/conversations/{cid}/read", {}),
        ("/api/v1/notifications/read-all", {}),
        ("/api/v1/notification-preferences", {}),
    ],
)
def test_mutations_require_csrf(world, path_template, payload):
    """A cookie-session mutation without a CSRF token must be rejected."""
    enforcing = Client(enforce_csrf_checks=True)
    enforcing.force_login(world.coach)

    setup = Client()
    setup.force_login(world.coach)
    conversation_id = setup.post(
        "/api/v1/conversations",
        data={"counterpart_user_id": world.athlete.id},
        content_type="application/json",
    ).json()["id"]

    path = path_template.format(cid=conversation_id)
    method = enforcing.patch if "preferences" in path else enforcing.post
    response = method(path, data=payload, content_type="application/json")
    assert response.status_code == 403


def test_safe_methods_do_not_require_csrf(world):
    enforcing = Client(enforce_csrf_checks=True)
    enforcing.force_login(world.coach)
    assert enforcing.get("/api/v1/conversations").status_code == 200


# --- Rate limiting ------------------------------------------------------------------ #


def test_per_conversation_rate_limit_is_enforced(client, world):
    conversation_id = thread(client, world)
    statuses = []
    for index in range(20):
        response = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            data={"body": f"burst {index}", "client_message_id": f"b{index}"},
            content_type="application/json",
        )
        statuses.append(response.status_code)

    assert 429 in statuses
    limited = next(s for s in statuses if s == 429)
    assert limited == 429
    assert statuses.index(429) >= 15


def test_rate_limited_response_carries_a_stable_message_key(client, world):
    conversation_id = thread(client, world)
    last = None
    for index in range(20):
        last = client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            data={"body": f"x{index}", "client_message_id": f"r{index}"},
            content_type="application/json",
        )
    assert last.status_code == 429
    assert last.json()["message_key"] == "errors.messaging.rate_limited"


def test_rate_limit_cannot_be_bypassed_with_spoofed_headers(client, world):
    """Counters key on server-derived identity, so client headers are irrelevant."""
    conversation_id = thread(client, world)
    for index in range(16):
        client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            data={"body": f"x{index}", "client_message_id": f"h{index}"},
            content_type="application/json",
            HTTP_X_FORWARDED_FOR=f"10.0.0.{index}",
            HTTP_X_ORGANIZATION_ID=f"spoofed-{index}",
            HTTP_X_REQUEST_ID=f"01999999-0000-7000-8000-00000000{index:04d}",
        )

    blocked = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "final", "client_message_id": "h-final"},
        content_type="application/json",
        HTTP_X_FORWARDED_FOR="203.0.113.9",
    )
    assert blocked.status_code == 429


def test_rate_limit_counters_are_isolated_per_user(client, world):
    conversation_id = thread(client, world)
    for index in range(16):
        client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            data={"body": f"x{index}", "client_message_id": f"u{index}"},
            content_type="application/json",
        )

    # The athlete's own quota is untouched by the coach exhausting theirs.
    login(client, world.athlete)
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "my first message"},
        content_type="application/json",
    )
    assert response.status_code == 201


def test_conversation_creation_is_rate_limited(client, world):
    login(client, world.coach)
    statuses = []
    for _index in range(14):
        response = client.post(
            "/api/v1/conversations",
            data={"counterpart_user_id": world.athlete.id},
            content_type="application/json",
        )
        statuses.append(response.status_code)
    assert 429 in statuses


def test_rate_limit_fails_closed_when_the_cache_errors(client, world, monkeypatch):
    from apps.communication import ratelimit

    conversation_id = thread(client, world)

    def broken_add(*_args, **_kwargs):
        raise RuntimeError("cache down")

    monkeypatch.setattr(ratelimit.cache, "add", broken_add)
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "should be refused"},
        content_type="application/json",
    )
    assert response.status_code == 429


# --- Privacy: logs, audit, and errors -------------------------------------------- #


SECRET_BODY = "CONFIDENTIAL-BODY-MARKER-9f3ac1 my knee hurt during squats"


def test_message_body_never_appears_in_logs(client, world, caplog):
    conversation_id = thread(client, world)
    with caplog.at_level(logging.DEBUG):
        client.post(
            f"/api/v1/conversations/{conversation_id}/messages",
            data={"body": SECRET_BODY},
            content_type="application/json",
        )
        from apps.communication import dispatcher

        dispatcher.run_dispatcher()

    log_text = "\n".join(record.getMessage() for record in caplog.records)
    assert "CONFIDENTIAL-BODY-MARKER" not in log_text
    assert "knee hurt" not in log_text


def test_message_body_never_appears_in_audit_metadata(client, world):
    conversation_id = thread(client, world)
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": SECRET_BODY},
        content_type="application/json",
    )
    event = AuditEvent.objects.get(action="message.sent")
    serialized = json.dumps(event.metadata)
    assert "CONFIDENTIAL-BODY-MARKER" not in serialized
    assert event.metadata["body_length"] == len(SECRET_BODY)


def test_message_body_never_appears_in_outbox_or_notification(client, world):
    from apps.communication import dispatcher

    conversation_id = thread(client, world)
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": SECRET_BODY},
        content_type="application/json",
    )
    dispatcher.run_dispatcher()

    assert "CONFIDENTIAL-BODY-MARKER" not in json.dumps(OutboxRecord.objects.get().payload)
    assert "CONFIDENTIAL-BODY-MARKER" not in json.dumps(Notification.objects.get().payload)


def test_email_addresses_are_never_returned_by_the_api(client, world):
    conversation_id = thread(client, world)
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "hello"},
        content_type="application/json",
    )

    for path in (
        "/api/v1/conversations",
        f"/api/v1/conversations/{conversation_id}",
        f"/api/v1/conversations/{conversation_id}/messages",
        "/api/v1/notifications",
    ):
        content = client.get(path).content.decode()
        assert "@example.test" not in content


def test_model_repr_does_not_leak_the_body(client, world):
    conversation_id = thread(client, world)
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": SECRET_BODY},
        content_type="application/json",
    )
    message = Message.objects.get()
    assert "CONFIDENTIAL-BODY-MARKER" not in str(message)
    assert "CONFIDENTIAL-BODY-MARKER" not in repr(message)


def test_error_responses_do_not_echo_the_body(client, world):
    conversation_id = thread(client, world)
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "x" * (MESSAGE_MAX_LENGTH + 50)},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert "xxxxxxxxxx" not in response.content.decode()


def test_no_provider_secret_is_present_in_delivery_records(client, world):
    from apps.communication import dispatcher
    from apps.communication.models import DeliveryAttempt

    conversation_id = thread(client, world)
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "hello"},
        content_type="application/json",
    )
    dispatcher.run_dispatcher()

    for attempt in DeliveryAttempt.objects.all():
        # Only a SHA-256 hash, never a raw provider reference or endpoint.
        assert attempt.provider_ref_hash == "" or len(attempt.provider_ref_hash) == 64
        assert "http" not in attempt.provider_ref_hash
        assert "@" not in attempt.provider_ref_hash
