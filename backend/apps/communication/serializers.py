"""Phase 08 serializers — bounded input validation and safe output shaping."""

from rest_framework import serializers

from .constants import (
    CHANNELS,
    CLIENT_MESSAGE_ID_MAX_LENGTH,
    EVENT_TYPES,
    MESSAGE_MAX_LENGTH,
    MessageValidationError,
    normalize_message_body,
)
from .models import Conversation, Message, Notification


class CreateConversationInputSerializer(serializers.Serializer):
    counterpart_user_id = serializers.CharField(max_length=36)
    context_type = serializers.ChoiceField(
        choices=["none", "workout_session"], required=False, default="none"
    )
    context_id = serializers.CharField(max_length=36, required=False, allow_null=True)

    def validate(self, attrs):
        if attrs.get("context_type") == "workout_session" and not attrs.get("context_id"):
            raise serializers.ValidationError(
                {"context_id": "context_id is required for a workout_session context."}
            )
        if attrs.get("context_type", "none") == "none":
            attrs["context_id"] = None
        return attrs


class CreateMessageInputSerializer(serializers.Serializer):
    # A generous raw bound guards against memory abuse; the precise bound is
    # applied after Unicode normalization in normalize_message_body.
    body = serializers.CharField(max_length=MESSAGE_MAX_LENGTH * 2, trim_whitespace=False)
    client_message_id = serializers.CharField(
        max_length=CLIENT_MESSAGE_ID_MAX_LENGTH, required=False, allow_null=True
    )

    def validate_body(self, value):
        try:
            return normalize_message_body(value)
        except MessageValidationError as exc:
            error = serializers.ValidationError(str(exc.message_key))
            error.message_key = exc.message_key
            raise error from exc

    def validate_client_message_id(self, value):
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        if not all(ch.isalnum() or ch in "-_:" for ch in value):
            raise serializers.ValidationError("Use only alphanumerics, dash, underscore, colon.")
        return value


class MarkReadInputSerializer(serializers.Serializer):
    read_at = serializers.DateTimeField(required=False)


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "conversation_id", "sender_user_id", "body", "created_at"]
        read_only_fields = fields


class ConversationSerializer(serializers.ModelSerializer):
    """
    Inbox row.

    `counterpart` carries a display name only. Email addresses are never
    included: they are not needed by the UI and would widen the blast radius of
    any accidental exposure.
    """

    counterpart = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "organization_id",
            "kind",
            "context_type",
            "context_id",
            "last_message_at",
            "last_message_preview",
            "is_archived",
            "created_at",
            "counterpart",
            "unread_count",
        ]
        read_only_fields = fields

    def get_counterpart(self, obj):
        data = (self.context.get("counterparts") or {}).get(obj.id)
        if not data:
            return None
        return data

    def get_unread_count(self, obj):
        return (self.context.get("unread_counts") or {}).get(obj.id, 0)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "organization_id",
            "event_type",
            "category",
            "title_key",
            "body_key",
            "payload",
            "read_at",
            "created_at",
        ]
        read_only_fields = fields


class UpdatePreferencesInputSerializer(serializers.Serializer):
    preferences = serializers.ListField(child=serializers.DictField(), required=False)
    quiet_hours_enabled = serializers.BooleanField(required=False)
    quiet_hours_start = serializers.RegexField(r"^([01]\d|2[0-3]):[0-5]\d$", required=False)
    quiet_hours_end = serializers.RegexField(r"^([01]\d|2[0-3]):[0-5]\d$", required=False)
    web_push_permission_state = serializers.ChoiceField(
        choices=["unknown", "granted", "denied"], required=False
    )

    def validate_preferences(self, value):
        cleaned = []
        for entry in value:
            event_type = entry.get("event_type")
            channel = entry.get("channel")
            is_enabled = entry.get("is_enabled")
            if event_type not in EVENT_TYPES:
                raise serializers.ValidationError(f"Unknown event_type: {event_type}")
            if channel not in CHANNELS:
                raise serializers.ValidationError(f"Unknown channel: {channel}")
            if not isinstance(is_enabled, bool):
                raise serializers.ValidationError("is_enabled must be a boolean.")
            cleaned.append({"event_type": event_type, "channel": channel, "is_enabled": is_enabled})
        return cleaned
