"""
Phase 08 — Communication and Notifications domain models.

Design notes (see docs/reports/PHASE-08-COMMUNICATION-NOTIFICATIONS-CONTRACTS.md):
- Every record that can carry user content is organization-scoped.
- Message bodies are Tier-3 personal content: append-only, never logged, never
  copied into domain events, audit metadata, or notification payloads.
- Read state is a monotonic per-participant cursor, not a per-message receipt.
- Notifications are deduplicated on stable event identity so outbox retries can
  never produce a second user-visible notification.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.utils.id_generator import generate_uuid7
from apps.identity.models import User
from apps.organizations.models import Organization

from .constants import (
    CATEGORY_ACCOUNT,
    CATEGORY_MESSAGING,
    CATEGORY_SAFETY,
    CATEGORY_TRAINING,
    CHANNELS,
    CLIENT_MESSAGE_ID_MAX_LENGTH,
    EVENT_TYPES,
    MESSAGE_MAX_LENGTH,
    MESSAGE_PREVIEW_LENGTH,
)


class Conversation(models.Model):
    """A tenant-scoped direct (1:1) conversation, optionally bound to a workout."""

    KIND_CHOICES = [("direct", "Direct")]
    CONTEXT_CHOICES = [("none", "None"), ("workout_session", "Workout Session")]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="conversations"
    )
    kind = models.CharField(max_length=16, choices=KIND_CHOICES, default="direct")
    context_type = models.CharField(max_length=32, choices=CONTEXT_CHOICES, default="none")
    context_id = models.CharField(max_length=36, null=True, blank=True)
    participant_key = models.CharField(max_length=160, db_index=True)
    created_by_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_conversations"
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    last_message_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_message_preview = models.CharField(max_length=MESSAGE_PREVIEW_LENGTH, blank=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        verbose_name = "conversation"
        verbose_name_plural = "conversations"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "kind", "participant_key"],
                name="unique_direct_conversation_per_pair",
            )
        ]
        indexes = [
            models.Index(fields=["organization", "-last_message_at"]),
            models.Index(fields=["organization", "context_type", "context_id"]),
        ]

    def __str__(self):
        return f"Conversation {self.id} ({self.kind})"

    def clean(self):
        if self.context_type == "workout_session" and not self.context_id:
            raise ValidationError({"context_id": "Workout context requires a context_id."})
        if self.context_type == "none" and self.context_id:
            raise ValidationError({"context_id": "context_id requires a context_type."})


class ConversationParticipant(models.Model):
    """
    Membership of a user in a conversation.

    `joined_at` bounds historic visibility: a participant never sees messages
    written before they joined. `left_at` revokes access immediately.
    """

    ROLE_CHOICES = [("coach", "Coach"), ("athlete", "Athlete"), ("owner", "Owner")]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="participants"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="conversation_memberships"
    )
    role_at_join = models.CharField(max_length=20, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(default=timezone.now)
    left_at = models.DateTimeField(null=True, blank=True)
    last_read_at = models.DateTimeField(null=True, blank=True)
    is_muted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "conversation participant"
        verbose_name_plural = "conversation participants"
        constraints = [
            models.UniqueConstraint(
                fields=["conversation", "user"], name="unique_participant_per_conversation"
            )
        ]
        indexes = [
            models.Index(fields=["user", "left_at"]),
            models.Index(fields=["conversation", "left_at"]),
        ]

    def __str__(self):
        return f"Participant {self.user_id} in {self.conversation_id}"

    @property
    def is_active(self):
        return self.left_at is None


class Message(models.Model):
    """
    An append-only message.

    Bodies are plain text. No HTML is stored or rendered. No edit or delete path
    exists in Phase 08; `save()` refuses to mutate an existing body.
    """

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="sent_messages")
    body = models.TextField(max_length=MESSAGE_MAX_LENGTH)
    client_message_id = models.CharField(
        max_length=CLIENT_MESSAGE_ID_MAX_LENGTH, null=True, blank=True
    )
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "message"
        verbose_name_plural = "messages"
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["conversation", "sender_user", "client_message_id"],
                condition=models.Q(client_message_id__isnull=False),
                name="unique_client_message_id_per_sender",
            )
        ]
        indexes = [
            models.Index(fields=["conversation", "-created_at", "-id"]),
            models.Index(fields=["sender_user", "-created_at"]),
        ]

    def __str__(self):
        # Never include the body in a repr: it is Tier-3 personal content.
        return f"Message {self.id} in {self.conversation_id}"

    def save(self, *args, **kwargs):
        if self.pk:
            existing = Message.objects.filter(pk=self.pk).values("body").first()
            if existing is not None and existing["body"] != self.body:
                raise ValueError("Message bodies are immutable in Phase 08.")
        super().save(*args, **kwargs)


class Notification(models.Model):
    """A durable in-app notification for one recipient."""

    CATEGORY_CHOICES = [
        (CATEGORY_MESSAGING, "Messaging"),
        (CATEGORY_TRAINING, "Training"),
        (CATEGORY_SAFETY, "Safety"),
        (CATEGORY_ACCOUNT, "Account"),
    ]
    EVENT_TYPE_CHOICES = [(value, value) for value in EVENT_TYPES]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    recipient_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    event_type = models.CharField(max_length=48, choices=EVENT_TYPE_CHOICES, db_index=True)
    category = models.CharField(max_length=24, choices=CATEGORY_CHOICES, db_index=True)
    title_key = models.CharField(max_length=64)
    body_key = models.CharField(max_length=64)
    # Metadata only: ids, counts, actor display name, deep-link route.
    # Never message bodies, email addresses, tokens, or provider references.
    payload = models.JSONField(default=dict, blank=True)
    dedupe_key = models.CharField(max_length=128)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "notification"
        verbose_name_plural = "notifications"
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["recipient_user", "dedupe_key"],
                name="unique_notification_per_recipient_event",
            )
        ]
        indexes = [
            models.Index(fields=["recipient_user", "read_at", "-created_at"]),
            models.Index(fields=["recipient_user", "-created_at", "-id"]),
        ]

    def __str__(self):
        return f"Notification {self.id} ({self.event_type})"


class NotificationPreferenceProfile(models.Model):
    """User-level quiet hours and browser push permission state."""

    PERMISSION_CHOICES = [
        ("unknown", "Unknown"),
        ("granted", "Granted"),
        ("denied", "Denied"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="notification_profile")
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.CharField(max_length=5, default="22:00")
    quiet_hours_end = models.CharField(max_length=5, default="07:00")
    web_push_permission_state = models.CharField(
        max_length=16, choices=PERMISSION_CHOICES, default="unknown"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "notification preference profile"
        verbose_name_plural = "notification preference profiles"

    def __str__(self):
        return f"Notification profile for {self.user_id}"

    def clean(self):
        for field in ("quiet_hours_start", "quiet_hours_end"):
            value = getattr(self, field)
            parts = str(value).split(":")
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                raise ValidationError({field: "Use HH:MM 24-hour format."})
            hour, minute = int(parts[0]), int(parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValidationError({field: "Use a valid 24-hour time."})


class NotificationPreference(models.Model):
    """Per-(user, event_type, channel) opt-in state."""

    CHANNEL_CHOICES = [(value, value) for value in CHANNELS]
    EVENT_TYPE_CHOICES = [(value, value) for value in EVENT_TYPES]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    event_type = models.CharField(max_length=48, choices=EVENT_TYPE_CHOICES)
    channel = models.CharField(max_length=16, choices=CHANNEL_CHOICES)
    is_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "notification preference"
        verbose_name_plural = "notification preferences"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "event_type", "channel"],
                name="unique_preference_per_user_event_channel",
            )
        ]
        indexes = [models.Index(fields=["user", "event_type"])]

    def __str__(self):
        return f"{self.user_id} {self.event_type}/{self.channel}={self.is_enabled}"


class OutboxRecord(models.Model):
    """
    Transactional outbox row.

    Written inside the same atomic block as the source domain mutation. If the
    domain write rolls back, the event never exists. Payloads carry identifiers
    and counts only — never message bodies.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("claimed", "Claimed"),
        ("processed", "Processed"),
        ("failed", "Failed"),
        ("dead_letter", "Dead Letter"),
    ]
    EVENT_TYPE_CHOICES = [(value, value) for value in EVENT_TYPES]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    event_id = models.CharField(max_length=36, unique=True, default=generate_uuid7)
    event_type = models.CharField(max_length=48, choices=EVENT_TYPE_CHOICES, db_index=True)
    schema_version = models.PositiveSmallIntegerField(default=1)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True, related_name="outbox_records"
    )
    actor_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="emitted_events"
    )
    subject_type = models.CharField(max_length=64)
    subject_id = models.CharField(max_length=36)
    correlation_id = models.CharField(max_length=36, blank=True)
    occurred_at = models.DateTimeField(default=timezone.now)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    attempts = models.PositiveSmallIntegerField(default=0)
    next_attempt_at = models.DateTimeField(default=timezone.now, db_index=True)
    claimed_at = models.DateTimeField(null=True, blank=True)
    claim_token = models.CharField(max_length=36, blank=True)
    last_error_code = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "outbox record"
        verbose_name_plural = "outbox records"
        indexes = [
            models.Index(fields=["status", "next_attempt_at"]),
            models.Index(fields=["event_type", "-created_at"]),
        ]

    def __str__(self):
        return f"Outbox {self.event_type} {self.event_id} ({self.status})"

    def envelope(self):
        """Return the versioned event envelope for consumers."""
        return {
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "tenant_id": self.organization_id,
            "actor_user_id": self.actor_user_id,
            "subject_type": self.subject_type,
            "subject_id": self.subject_id,
            "correlation_id": self.correlation_id,
            "payload": self.payload or {},
        }


class DeliveryAttempt(models.Model):
    """
    One attempt to deliver a notification over a channel.

    Provider references are stored only as SHA-256 hashes. Recipient email
    addresses and push endpoints are never persisted here.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("scheduled", "Scheduled"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("suppressed", "Suppressed"),
        ("dead_letter", "Dead Letter"),
    ]
    CHANNEL_CHOICES = [(value, value) for value in CHANNELS]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    notification = models.ForeignKey(
        Notification, on_delete=models.CASCADE, related_name="delivery_attempts"
    )
    channel = models.CharField(max_length=16, choices=CHANNEL_CHOICES)
    attempt_number = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    scheduled_for = models.DateTimeField(null=True, blank=True)
    error_code = models.CharField(max_length=64, blank=True)
    provider_ref_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "delivery attempt"
        verbose_name_plural = "delivery attempts"
        constraints = [
            models.UniqueConstraint(
                fields=["notification", "channel", "attempt_number"],
                name="unique_delivery_attempt_per_channel",
            )
        ]
        indexes = [models.Index(fields=["notification", "channel"])]

    def __str__(self):
        return f"Delivery {self.channel} #{self.attempt_number} ({self.status})"
