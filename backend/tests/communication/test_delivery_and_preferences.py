"""
Phase 08 Stage 3 — delivery adapters, preferences, quiet hours, and failure
isolation, all exercised with deterministic local fakes.
"""

import datetime

import pytest
from django.test import override_settings
from django.utils import timezone
from helpers import login

from apps.communication import dispatcher
from apps.communication.adapters import FakeEmailAdapter, FakeWebPushAdapter, registry
from apps.communication.models import (
    DeliveryAttempt,
    Notification,
    NotificationPreference,
    NotificationPreferenceProfile,
    OutboxRecord,
)

pytestmark = pytest.mark.django_db


def send_and_dispatch(client, world):
    login(client, world.coach)
    conversation_id = client.post(
        "/api/v1/conversations",
        data={"counterpart_user_id": world.athlete.id},
        content_type="application/json",
    ).json()["id"]
    client.post(
        f"/api/v1/conversations/{conversation_id}/messages",
        data={"body": "check your form cues"},
        content_type="application/json",
    )
    dispatcher.run_dispatcher()
    return Notification.objects.get(recipient_user=world.athlete)


def enable_channel(user, event_type, channel):
    NotificationPreference.objects.update_or_create(
        user=user, event_type=event_type, channel=channel, defaults={"is_enabled": True}
    )


# --- Channel defaults ----------------------------------------------------------- #


def test_in_app_delivers_and_optional_channels_default_off(client, world):
    notification = send_and_dispatch(client, world)
    attempts = {a.channel: a for a in DeliveryAttempt.objects.filter(notification=notification)}

    assert attempts["in_app"].status == "succeeded"
    assert attempts["email"].status == "suppressed"
    assert attempts["email"].error_code == "preference_disabled"
    assert attempts["web_push"].status == "suppressed"


def test_enabled_email_uses_the_fake_adapter(client, world):
    enable_channel(world.athlete, "message.sent", "email")
    fake = FakeEmailAdapter()
    registry.register("email", fake)

    notification = send_and_dispatch(client, world)
    attempt = DeliveryAttempt.objects.get(notification=notification, channel="email")

    assert attempt.status == "succeeded"
    assert len(fake.sent) == 1
    # Only identifiers are retained by the fake — no address, subject, or body.
    assert set(fake.sent[0]) == {"notification_id", "recipient_id"}
    assert attempt.provider_ref_hash and len(attempt.provider_ref_hash) == 64


@override_settings(COMMUNICATION_FAKE_PROVIDERS_ENABLED=False)
def test_unconfigured_provider_suppresses_rather_than_pretending(client, world):
    enable_channel(world.athlete, "message.sent", "email")
    registry.register("email", FakeEmailAdapter())

    notification = send_and_dispatch(client, world)
    attempt = DeliveryAttempt.objects.get(notification=notification, channel="email")
    assert attempt.status == "suppressed"
    assert attempt.error_code == "provider_not_configured"


# --- Web Push permission -------------------------------------------------------- #


def test_web_push_denied_permission_is_suppressed_not_failed(client, world):
    enable_channel(world.athlete, "message.sent", "web_push")
    NotificationPreferenceProfile.objects.create(
        user=world.athlete, web_push_permission_state="denied"
    )
    registry.register("web_push", FakeWebPushAdapter())

    notification = send_and_dispatch(client, world)
    attempt = DeliveryAttempt.objects.get(notification=notification, channel="web_push")
    assert attempt.status == "suppressed"
    assert attempt.error_code == "push_permission_denied"
    # The durable in-app notification is untouched.
    assert Notification.objects.filter(id=notification.id).exists()


def test_web_push_unknown_permission_is_suppressed(client, world):
    enable_channel(world.athlete, "message.sent", "web_push")
    registry.register("web_push", FakeWebPushAdapter())

    notification = send_and_dispatch(client, world)
    attempt = DeliveryAttempt.objects.get(notification=notification, channel="web_push")
    assert attempt.error_code == "push_permission_unknown"


def test_web_push_granted_permission_delivers_via_fake(client, world):
    enable_channel(world.athlete, "message.sent", "web_push")
    NotificationPreferenceProfile.objects.create(
        user=world.athlete, web_push_permission_state="granted"
    )
    fake = FakeWebPushAdapter()
    registry.register("web_push", fake)

    notification = send_and_dispatch(client, world)
    attempt = DeliveryAttempt.objects.get(notification=notification, channel="web_push")
    assert attempt.status == "succeeded"
    assert len(fake.sent) == 1


# --- Failure isolation ------------------------------------------------------------ #


def test_provider_failure_never_deletes_the_in_app_notification(client, world):
    enable_channel(world.athlete, "message.sent", "email")
    fake = FakeEmailAdapter()
    fake.fail_next = True
    registry.register("email", fake)

    notification = send_and_dispatch(client, world)
    email_attempt = DeliveryAttempt.objects.get(notification=notification, channel="email")
    in_app_attempt = DeliveryAttempt.objects.get(notification=notification, channel="in_app")

    assert email_attempt.status == "failed"
    assert email_attempt.error_code == "provider_unavailable"
    assert in_app_attempt.status == "succeeded"
    assert Notification.objects.filter(id=notification.id).exists()
    # The source event still completed: a channel failure is not an event failure.
    assert OutboxRecord.objects.get().status == "processed"


def test_adapter_exception_is_contained(client, world):
    class ExplodingAdapter:
        channel = "email"

        def is_configured(self):
            return True

        def send(self, **_kwargs):
            raise RuntimeError("provider client crashed")

    enable_channel(world.athlete, "message.sent", "email")
    registry.register("email", ExplodingAdapter())

    notification = send_and_dispatch(client, world)
    attempt = DeliveryAttempt.objects.get(notification=notification, channel="email")
    assert attempt.status == "failed"
    assert attempt.error_code == "adapter_exception"
    assert Notification.objects.filter(id=notification.id).exists()


# --- Quiet hours -------------------------------------------------------------------- #


def test_quiet_hours_defer_push_channels_but_never_in_app(client, world):
    enable_channel(world.athlete, "message.sent", "email")
    world.athlete.timezone = "UTC"
    world.athlete.save(update_fields=["timezone"])
    NotificationPreferenceProfile.objects.create(
        user=world.athlete,
        quiet_hours_enabled=True,
        quiet_hours_start="00:00",
        quiet_hours_end="23:59",
    )
    registry.register("email", FakeEmailAdapter())

    notification = send_and_dispatch(client, world)
    email_attempt = DeliveryAttempt.objects.get(notification=notification, channel="email")
    in_app_attempt = DeliveryAttempt.objects.get(notification=notification, channel="in_app")

    assert email_attempt.status == "scheduled"
    assert email_attempt.error_code == "quiet_hours_deferred"
    assert email_attempt.scheduled_for is not None
    # In-app is pull-based and is never deferred.
    assert in_app_attempt.status == "succeeded"


def test_quiet_hours_wrapping_midnight_is_evaluated_correctly(world):
    world.athlete.timezone = "UTC"
    world.athlete.save(update_fields=["timezone"])
    NotificationPreferenceProfile.objects.create(
        user=world.athlete,
        quiet_hours_enabled=True,
        quiet_hours_start="22:00",
        quiet_hours_end="07:00",
    )

    inside_late = datetime.datetime(2026, 8, 16, 23, 30, tzinfo=datetime.UTC)
    inside_early = datetime.datetime(2026, 8, 16, 3, 0, tzinfo=datetime.UTC)
    outside = datetime.datetime(2026, 8, 16, 12, 0, tzinfo=datetime.UTC)

    assert dispatcher.in_quiet_hours(world.athlete, inside_late) is True
    assert dispatcher.in_quiet_hours(world.athlete, inside_early) is True
    assert dispatcher.in_quiet_hours(world.athlete, outside) is False


def test_quiet_hours_respect_the_user_timezone(world):
    world.athlete.timezone = "Asia/Tehran"
    world.athlete.save(update_fields=["timezone"])
    NotificationPreferenceProfile.objects.create(
        user=world.athlete,
        quiet_hours_enabled=True,
        quiet_hours_start="22:00",
        quiet_hours_end="07:00",
    )
    # 20:00 UTC is 23:30 in Tehran (+3:30) => inside quiet hours locally.
    moment = datetime.datetime(2026, 8, 16, 20, 0, tzinfo=datetime.UTC)
    assert dispatcher.in_quiet_hours(world.athlete, moment) is True


def test_invalid_timezone_falls_back_to_utc_not_server_local(world):
    world.athlete.timezone = "Not/AZone"
    world.athlete.save(update_fields=["timezone"])
    NotificationPreferenceProfile.objects.create(
        user=world.athlete,
        quiet_hours_enabled=True,
        quiet_hours_start="00:00",
        quiet_hours_end="23:59",
    )
    moment = datetime.datetime(2026, 8, 16, 12, 0, tzinfo=datetime.UTC)
    assert dispatcher.in_quiet_hours(world.athlete, moment) is True


def test_quiet_hours_disabled_by_default(world):
    assert dispatcher.in_quiet_hours(world.athlete) is False


def test_quiet_hours_end_is_in_the_future(world):
    world.athlete.timezone = "UTC"
    world.athlete.save(update_fields=["timezone"])
    NotificationPreferenceProfile.objects.create(
        user=world.athlete,
        quiet_hours_enabled=True,
        quiet_hours_start="22:00",
        quiet_hours_end="07:00",
    )
    assert dispatcher.quiet_hours_end_at(world.athlete) > timezone.now()


# --- Preference API ------------------------------------------------------------------ #


def test_preferences_default_matrix_is_explicit(client, world):
    login(client, world.athlete)
    body = client.get("/api/v1/notification-preferences").json()

    rows = {(r["event_type"], r["channel"]): r for r in body["preferences"]}
    assert rows[("message.sent", "in_app")]["is_enabled"] is True
    assert rows[("message.sent", "email")]["is_enabled"] is False
    assert rows[("message.sent", "web_push")]["is_enabled"] is False
    # The API states plainly that optional channels are unavailable in Phase 08.
    assert body["channels_available"] == {"in_app": True, "email": False, "web_push": False}


def test_safety_in_app_channel_is_locked(client, world):
    login(client, world.athlete)
    body = client.get("/api/v1/notification-preferences").json()
    row = next(
        r
        for r in body["preferences"]
        if r["event_type"] == "feedback_flag.created" and r["channel"] == "in_app"
    )
    assert row["is_locked"] is True
    assert row["is_enabled"] is True


def test_cannot_disable_safety_in_app_notifications(client, world):
    login(client, world.coach)
    response = client.patch(
        "/api/v1/notification-preferences",
        data={
            "preferences": [
                {
                    "event_type": "feedback_flag.created",
                    "channel": "in_app",
                    "is_enabled": False,
                }
            ]
        },
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.json()["message_key"] == "errors.notifications.category_not_suppressible"


def test_safety_notification_delivers_even_if_a_preference_row_says_otherwise(client, world):
    """Defence in depth: a forged/legacy DB row must not suppress a safety alert."""
    NotificationPreference.objects.create(
        user=world.coach,
        event_type="feedback_flag.created",
        channel="in_app",
        is_enabled=False,
    )
    assert (
        dispatcher._preference_enabled(world.coach, "feedback_flag.created", "in_app", "safety")
        is True
    )


def test_disabling_messaging_in_app_suppresses_that_channel_only(client, world):
    login(client, world.athlete)
    response = client.patch(
        "/api/v1/notification-preferences",
        data={
            "preferences": [
                {"event_type": "message.sent", "channel": "in_app", "is_enabled": False}
            ]
        },
        content_type="application/json",
    )
    assert response.status_code == 200

    notification = send_and_dispatch(client, world)
    attempt = DeliveryAttempt.objects.get(notification=notification, channel="in_app")
    assert attempt.status == "suppressed"
    # The durable record still exists so the user can find it in the centre.
    assert Notification.objects.filter(id=notification.id).exists()


def test_quiet_hours_can_be_configured_through_the_api(client, world):
    login(client, world.athlete)
    response = client.patch(
        "/api/v1/notification-preferences",
        data={
            "quiet_hours_enabled": True,
            "quiet_hours_start": "23:00",
            "quiet_hours_end": "06:30",
        },
        content_type="application/json",
    )
    assert response.status_code == 200
    body = response.json()
    assert body["quiet_hours_enabled"] is True
    assert body["quiet_hours_start"] == "23:00"


def test_invalid_quiet_hours_are_rejected(client, world):
    login(client, world.athlete)
    response = client.patch(
        "/api/v1/notification-preferences",
        data={"quiet_hours_start": "25:99"},
        content_type="application/json",
    )
    assert response.status_code == 400


def test_unknown_event_or_channel_is_rejected(client, world):
    login(client, world.athlete)
    for payload in (
        {
            "preferences": [
                {"event_type": "nutrition.logged", "channel": "in_app", "is_enabled": True}
            ]
        },
        {"preferences": [{"event_type": "message.sent", "channel": "sms", "is_enabled": True}]},
    ):
        response = client.patch(
            "/api/v1/notification-preferences", data=payload, content_type="application/json"
        )
        assert response.status_code == 400


def test_push_permission_state_can_be_recorded(client, world):
    login(client, world.athlete)
    response = client.patch(
        "/api/v1/notification-preferences",
        data={"web_push_permission_state": "denied"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json()["web_push_permission_state"] == "denied"


def test_preference_change_is_audited_without_leaking_values(client, world):
    from apps.audit.models import AuditEvent

    login(client, world.athlete)
    client.patch(
        "/api/v1/notification-preferences",
        data={
            "preferences": [{"event_type": "message.sent", "channel": "email", "is_enabled": True}]
        },
        content_type="application/json",
    )
    event = AuditEvent.objects.get(action="notification.preferences_updated")
    assert event.actor_user_id == world.athlete.id
    assert event.metadata["changed"] == ["message.sent/email"]


# --- Notification centre --------------------------------------------------------------- #


def test_notification_list_filters_and_unread_count(client, world):
    send_and_dispatch(client, world)
    login(client, world.athlete)

    listing = client.get("/api/v1/notifications").json()
    assert listing["unread_count"] == 1
    assert len(listing["notifications"]) == 1

    notification_id = listing["notifications"][0]["id"]
    client.post(f"/api/v1/notifications/{notification_id}/read")

    listing = client.get("/api/v1/notifications?unread=true").json()
    assert listing["notifications"] == []
    assert listing["unread_count"] == 0


def test_marking_notification_read_is_idempotent(client, world):
    notification = send_and_dispatch(client, world)
    login(client, world.athlete)

    first = client.post(f"/api/v1/notifications/{notification.id}/read").json()
    second = client.post(f"/api/v1/notifications/{notification.id}/read").json()
    assert first["read_at"] == second["read_at"]


def test_notification_page_size_is_capped(client, world):
    Notification.objects.bulk_create(
        [
            Notification(
                organization=world.org,
                recipient_user=world.athlete,
                event_type="message.sent",
                category="messaging",
                title_key="t",
                body_key="b",
                dedupe_key=f"d{i}",
            )
            for i in range(70)
        ]
    )
    login(client, world.athlete)
    listing = client.get("/api/v1/notifications?limit=500").json()
    assert len(listing["notifications"]) == 50


def test_notification_category_filter(client, world):
    send_and_dispatch(client, world)
    Notification.objects.create(
        organization=world.org,
        recipient_user=world.athlete,
        event_type="workout.completed",
        category="training",
        title_key="t",
        body_key="b",
        dedupe_key="d-training",
    )

    login(client, world.athlete)
    training = client.get("/api/v1/notifications?category=training").json()
    assert len(training["notifications"]) == 1
    assert training["notifications"][0]["category"] == "training"


def test_marking_notification_read_does_not_mutate_source_domain(client, world):
    """Reading a notification must never touch the message or session it refers to."""
    from apps.communication.models import Message

    notification = send_and_dispatch(client, world)
    before = list(Message.objects.values("id", "body", "created_at"))

    login(client, world.athlete)
    client.post(f"/api/v1/notifications/{notification.id}/read")

    assert list(Message.objects.values("id", "body", "created_at")) == before
