"""
Phase 08 — outbox dispatcher and notification delivery pipeline.

Responsibilities:
1. Claim pending outbox records safely (at most one worker per record).
2. Map each event envelope to notification specs (versioned mapping).
3. Create durable in-app notifications idempotently.
4. Fan out to channel adapters honouring preferences and quiet hours.
5. Apply bounded exponential backoff and dead-letter exhausted work.

Guarantees:
- Duplicate events never produce duplicate visible notifications
  (unique (recipient_user, dedupe_key)).
- A downstream channel failure never deletes a committed in-app notification.
- No message body, notification body, email address, push endpoint, or provider
  secret is written to logs.
"""

import datetime
import logging
import zoneinfo

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.core.utils.id_generator import generate_uuid7

from .adapters import registry
from .constants import (
    CHANNEL_EMAIL,
    CHANNEL_IN_APP,
    CHANNEL_WEB_PUSH,
    DEFAULT_CHANNEL_ENABLED,
    NON_SUPPRESSIBLE_CATEGORIES,
    OUTBOX_BACKOFF_BASE_SECONDS,
    OUTBOX_BACKOFF_MAX_SECONDS,
    OUTBOX_CLAIM_TIMEOUT_SECONDS,
    OUTBOX_MAX_ATTEMPTS,
    QUIET_HOURS_DEFERRABLE_CHANNELS,
)
from .mapping import UnsupportedEventVersion, map_envelope
from .models import (
    DeliveryAttempt,
    Notification,
    NotificationPreference,
    NotificationPreferenceProfile,
    OutboxRecord,
)

logger = logging.getLogger(__name__)


def backoff_seconds(attempt_number: int) -> int:
    """Bounded exponential backoff: 30s, 60s, 120s, 240s, ... capped at 1h."""
    if attempt_number < 1:
        attempt_number = 1
    delay = OUTBOX_BACKOFF_BASE_SECONDS * (2 ** (attempt_number - 1))
    return min(delay, OUTBOX_BACKOFF_MAX_SECONDS)


def claim_records(limit=20):
    """
    Atomically claim up to `limit` due outbox records.

    Uses SELECT ... FOR UPDATE SKIP LOCKED where the backend supports it
    (PostgreSQL). On SQLite the same at-most-one-claimer guarantee is achieved
    with a conditional UPDATE that only succeeds for rows still in `pending`.
    Both paths are exercised by the test suite.
    """
    now = timezone.now()
    stale_cutoff = now - datetime.timedelta(seconds=OUTBOX_CLAIM_TIMEOUT_SECONDS)
    token = generate_uuid7()

    with transaction.atomic():
        # Recover records whose claim went stale (worker crash).
        OutboxRecord.objects.filter(status="claimed", claimed_at__lt=stale_cutoff).update(
            status="pending", claim_token=""
        )

        base = OutboxRecord.objects.filter(status="pending", next_attempt_at__lte=now).order_by(
            "next_attempt_at", "created_at"
        )

        try:
            candidate_ids = list(
                base.select_for_update(skip_locked=True).values_list("id", flat=True)[:limit]
            )
        except Exception:  # pragma: no cover - backend without SKIP LOCKED
            candidate_ids = list(base.values_list("id", flat=True)[:limit])

        if not candidate_ids:
            return []

        # Conditional update: only rows still pending are claimed, so a racing
        # worker that already claimed a row cannot claim it a second time.
        OutboxRecord.objects.filter(id__in=candidate_ids, status="pending").update(
            status="claimed", claimed_at=now, claim_token=token
        )

    return list(OutboxRecord.objects.filter(claim_token=token, status="claimed"))


def _preference_enabled(user, event_type, channel, category):
    """Resolve the effective opt-in for (user, event_type, channel)."""
    if channel == CHANNEL_IN_APP and category in NON_SUPPRESSIBLE_CATEGORIES:
        return True
    preference = NotificationPreference.objects.filter(
        user=user, event_type=event_type, channel=channel
    ).first()
    if preference is None:
        return DEFAULT_CHANNEL_ENABLED.get(channel, False)
    return preference.is_enabled


def _parse_hhmm(value, fallback):
    try:
        hour, minute = str(value).split(":")
        return datetime.time(int(hour), int(minute))
    except (ValueError, TypeError):
        return fallback


def in_quiet_hours(user, at=None):
    """
    Is the user currently inside their quiet-hours window?

    Evaluated in the user's own IANA timezone. Handles windows that wrap
    midnight (for example 22:00 -> 07:00). An unknown timezone falls back to UTC
    rather than silently using server-local time.
    """
    profile = NotificationPreferenceProfile.objects.filter(user=user).first()
    if profile is None or not profile.quiet_hours_enabled:
        return False

    moment = at or timezone.now()
    try:
        tz = zoneinfo.ZoneInfo(user.timezone or "UTC")
    except Exception:
        tz = datetime.UTC

    local_time = moment.astimezone(tz).time()
    start = _parse_hhmm(profile.quiet_hours_start, datetime.time(22, 0))
    end = _parse_hhmm(profile.quiet_hours_end, datetime.time(7, 0))

    if start == end:
        return False
    if start < end:
        return start <= local_time < end
    # Wrapping window.
    return local_time >= start or local_time < end


def quiet_hours_end_at(user, at=None):
    """UTC datetime at which the user's current quiet window ends."""
    profile = NotificationPreferenceProfile.objects.filter(user=user).first()
    moment = at or timezone.now()
    if profile is None:
        return moment
    try:
        tz = zoneinfo.ZoneInfo(user.timezone or "UTC")
    except Exception:
        tz = datetime.UTC

    local = moment.astimezone(tz)
    end = _parse_hhmm(profile.quiet_hours_end, datetime.time(7, 0))
    candidate = local.replace(hour=end.hour, minute=end.minute, second=0, microsecond=0)
    if candidate <= local:
        candidate = candidate + datetime.timedelta(days=1)
    return candidate.astimezone(datetime.UTC)


def create_notification(spec, organization):
    """
    Create a durable in-app notification idempotently.

    Returns (notification, created). A duplicate dedupe_key returns the existing
    row with created=False, which is what makes outbox retries safe.
    """
    existing = Notification.objects.filter(
        recipient_user=spec.recipient, dedupe_key=spec.dedupe_key
    ).first()
    if existing is not None:
        return (existing, False)

    try:
        with transaction.atomic():
            notification = Notification.objects.create(
                organization=organization,
                recipient_user=spec.recipient,
                event_type=spec.event_type,
                category=spec.category,
                title_key=spec.title_key,
                body_key=spec.body_key,
                payload=spec.payload,
                dedupe_key=spec.dedupe_key,
            )
        return (notification, True)
    except IntegrityError:
        # Concurrent worker won the race; converge on its row.
        return (
            Notification.objects.get(recipient_user=spec.recipient, dedupe_key=spec.dedupe_key),
            False,
        )


def deliver_channels(notification, recipient):
    """
    Fan out a committed notification to the non-in-app channels.

    Never raises: a provider failure is recorded on the DeliveryAttempt and the
    durable in-app notification is untouched.
    """
    results = []
    quiet = in_quiet_hours(recipient)

    for channel in (CHANNEL_IN_APP, CHANNEL_EMAIL, CHANNEL_WEB_PUSH):
        if not _preference_enabled(
            recipient, notification.event_type, channel, notification.category
        ):
            results.append(
                DeliveryAttempt.objects.create(
                    notification=notification,
                    channel=channel,
                    attempt_number=_next_attempt_number(notification, channel),
                    status="suppressed",
                    error_code="preference_disabled",
                )
            )
            continue

        if quiet and channel in QUIET_HOURS_DEFERRABLE_CHANNELS:
            results.append(
                DeliveryAttempt.objects.create(
                    notification=notification,
                    channel=channel,
                    attempt_number=_next_attempt_number(notification, channel),
                    status="scheduled",
                    scheduled_for=quiet_hours_end_at(recipient),
                    error_code="quiet_hours_deferred",
                )
            )
            continue

        adapter = registry.get(channel)
        if adapter is None:
            continue

        try:
            result = adapter.send(notification=notification, recipient=recipient)
        except Exception:
            # Adapter blew up: record a failure code, never the exception text,
            # which could contain provider or recipient detail.
            logger.warning(
                "delivery.adapter_error channel=%s notification_id=%s",
                channel,
                notification.id,
            )
            result = None

        if result is None:
            results.append(
                DeliveryAttempt.objects.create(
                    notification=notification,
                    channel=channel,
                    attempt_number=_next_attempt_number(notification, channel),
                    status="failed",
                    error_code="adapter_exception",
                )
            )
            continue

        results.append(
            DeliveryAttempt.objects.create(
                notification=notification,
                channel=channel,
                attempt_number=_next_attempt_number(notification, channel),
                status=result.status,
                error_code=result.error_code,
                provider_ref_hash=result.provider_ref_hash,
            )
        )

    return results


def _next_attempt_number(notification, channel):
    last = (
        DeliveryAttempt.objects.filter(notification=notification, channel=channel)
        .order_by("-attempt_number")
        .values_list("attempt_number", flat=True)
        .first()
    )
    return (last or 0) + 1


def process_record(record):
    """
    Process one claimed outbox record.

    Returns a summary dict. Marks the record processed on success, or schedules
    a retry / dead-letters it on failure.
    """
    try:
        specs = map_envelope(record.envelope())
    except UnsupportedEventVersion:
        record.status = "dead_letter"
        record.last_error_code = "unsupported_event_version"
        record.attempts += 1
        record.claim_token = ""
        record.save(update_fields=["status", "last_error_code", "attempts", "claim_token"])
        logger.warning(
            "outbox.dead_letter event_id=%s reason=unsupported_event_version",
            record.event_id,
        )
        return {"event_id": record.event_id, "created": 0, "status": "dead_letter"}
    except Exception:
        return _schedule_retry(record, "mapping_error")

    created_count = 0
    try:
        for spec in specs:
            notification, created = create_notification(spec, record.organization)
            if created:
                created_count += 1
                deliver_channels(notification, spec.recipient)
    except Exception:
        return _schedule_retry(record, "dispatch_error")

    record.status = "processed"
    record.attempts += 1
    record.claim_token = ""
    record.last_error_code = ""
    record.save(update_fields=["status", "attempts", "claim_token", "last_error_code"])
    logger.info(
        "outbox.processed event_id=%s notifications_created=%s",
        record.event_id,
        created_count,
    )
    return {"event_id": record.event_id, "created": created_count, "status": "processed"}


def _schedule_retry(record, error_code):
    record.attempts += 1
    record.last_error_code = error_code
    record.claim_token = ""
    if record.attempts >= OUTBOX_MAX_ATTEMPTS:
        record.status = "dead_letter"
        logger.warning(
            "outbox.dead_letter event_id=%s attempts=%s error_code=%s",
            record.event_id,
            record.attempts,
            error_code,
        )
    else:
        record.status = "pending"
        record.next_attempt_at = timezone.now() + datetime.timedelta(
            seconds=backoff_seconds(record.attempts)
        )
    record.save(
        update_fields=[
            "attempts",
            "last_error_code",
            "claim_token",
            "status",
            "next_attempt_at",
        ]
    )
    return {"event_id": record.event_id, "created": 0, "status": record.status}


def run_dispatcher(limit=20):
    """Claim and process a batch. Safe to call repeatedly and concurrently."""
    summaries = []
    for record in claim_records(limit=limit):
        summaries.append(process_record(record))
    return summaries
