"""
Phase 08 — communication and notification APIs.

Authorization model (server-authoritative, see authz.py):
- Only active conversation participants may read or write a conversation.
- Sending additionally requires a live coach-athlete assignment.
- Owners are NOT given a private-message backdoor (contract AMD-08-01).
- Every denial for a conversation-scoped resource is a bare 404 so that
  cross-tenant probing cannot distinguish "exists" from "not yours".

Privacy: message bodies are returned only to authorized participants and are
never logged, audited, or copied into events or notification payloads.
"""

import base64
import binascii
import datetime
import logging

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditEvent
from apps.identity.models import User
from apps.identity.permissions import IsAuthenticatedAndActive
from apps.organizations.models import Membership, Organization

from . import authz
from .constants import (
    CHANNELS,
    CONVERSATION_PAGE_DEFAULT,
    CONVERSATION_PAGE_MAX,
    DEFAULT_CHANNEL_ENABLED,
    EVENT_CATEGORY,
    EVENT_TYPES,
    MESSAGE_PAGE_DEFAULT,
    MESSAGE_PAGE_MAX,
    NON_SUPPRESSIBLE_CATEGORIES,
    NOTIFICATION_PAGE_DEFAULT,
    NOTIFICATION_PAGE_MAX,
    RATE_LIMIT_CONVERSATION_CREATE,
    RATE_LIMIT_MESSAGE_PER_CONVERSATION,
    RATE_LIMIT_MESSAGE_PER_ORG,
    RATE_LIMIT_MESSAGE_PER_USER,
    RATE_LIMIT_PREFERENCE_UPDATE,
    UNREAD_COUNT_CAP,
    build_preview,
    participant_key,
)
from .events import emit_message_sent
from .models import (
    Conversation,
    ConversationParticipant,
    Message,
    Notification,
    NotificationPreference,
    NotificationPreferenceProfile,
)
from .ratelimit import RateLimitExceeded, enforce
from .serializers import (
    ConversationSerializer,
    CreateConversationInputSerializer,
    CreateMessageInputSerializer,
    MarkReadInputSerializer,
    MessageSerializer,
    NotificationSerializer,
    UpdatePreferencesInputSerializer,
)

logger = logging.getLogger(__name__)


# --- Shared helpers --------------------------------------------------------- #


def _problem(status_code, message_key, detail="Request could not be completed."):
    """RFC 7807 shaped body consistent with apps.core.exceptions."""
    return Response(
        {
            "type": f"https://errors.coachos.io/{message_key.replace('.', '-')}",
            "title": detail,
            "status": status_code,
            "detail": detail,
            "message_key": message_key,
        },
        status=status_code,
    )


def _not_found():
    """Uniform denial: no existence leakage across tenants or participants."""
    return Response(
        {
            "type": "https://errors.coachos.io/error-not-found",
            "title": "Resource Not Found",
            "status": 404,
            "detail": "The requested resource does not exist or is not accessible.",
            "message_key": "errors.not_found",
        },
        status=status.HTTP_404_NOT_FOUND,
    )


def _audit(request, organization, action, target_type, target_id, metadata=None):
    """
    Append an immutable audit event.

    Metadata carries identifiers, keys and counts only. Message bodies and
    previews are never audited.
    """
    AuditEvent.objects.create(
        actor_user=request.user,
        organization=organization,
        action=action,
        target_entity_type=target_type,
        target_entity_id=str(target_id),
        metadata=metadata or {},
        request_id=getattr(request, "correlation_id", ""),
    )


def _bounded_limit(request, default, maximum):
    raw = request.query_params.get("limit")
    if raw is None:
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return max(1, min(value, maximum))


def _encode_cursor(moment, identifier):
    raw = f"{moment.isoformat()}|{identifier}".encode()
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode_cursor(cursor):
    """Decode an opaque keyset cursor. Returns None for anything malformed."""
    if not cursor or len(cursor) > 200:
        return None
    try:
        padding = "=" * (-len(cursor) % 4)
        raw = base64.urlsafe_b64decode(cursor + padding).decode("utf-8")
        moment_text, identifier = raw.split("|", 1)
        moment = datetime.datetime.fromisoformat(moment_text)
        if timezone.is_naive(moment):
            moment = timezone.make_aware(moment, datetime.UTC)
        return (moment, identifier)
    except (ValueError, binascii.Error, UnicodeDecodeError):
        return None


def _user_organizations(user):
    return Organization.objects.filter(
        memberships__user=user, memberships__status="active"
    ).distinct()


def _counterpart_payload(conversation, user_id):
    participant = (
        ConversationParticipant.objects.filter(conversation=conversation)
        .exclude(user_id=user_id)
        .select_related("user")
        .first()
    )
    if participant is None:
        return None
    return {
        "user_id": participant.user_id,
        # Display name only — never the counterpart's email address.
        "display_name": participant.user.display_name or "",
        "role": participant.role_at_join,
        "is_active": participant.left_at is None and participant.user.is_active,
    }


def _unread_count(conversation, participant):
    """Bounded unread count: capped so a huge backlog cannot cost an unbounded scan."""
    queryset = Message.objects.filter(conversation=conversation).exclude(
        sender_user_id=participant.user_id
    )
    queryset = queryset.filter(created_at__gte=participant.joined_at)
    if participant.last_read_at is not None:
        queryset = queryset.filter(created_at__gt=participant.last_read_at)
    # Count at most CAP+1 rows: the exact size of a very large backlog is
    # neither useful to the UI nor worth an unbounded scan.
    bounded_ids = list(queryset.order_by("id").values_list("id", flat=True)[:UNREAD_COUNT_CAP])
    return len(bounded_ids)


# --- Conversations ---------------------------------------------------------- #


class ConversationListCreateView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        user = request.user
        organizations = list(_user_organizations(user).values_list("id", flat=True))
        if not organizations:
            return Response({"conversations": [], "next_cursor": None})

        participant_rows = ConversationParticipant.objects.filter(user=user, left_at__isnull=True)
        conversation_ids = list(participant_rows.values_list("conversation_id", flat=True))
        if not conversation_ids:
            return Response({"conversations": [], "next_cursor": None})

        queryset = (
            Conversation.objects.filter(id__in=conversation_ids, organization_id__in=organizations)
            .select_related("organization")
            .order_by("-last_message_at", "-created_at", "-id")
        )

        cursor = _decode_cursor(request.query_params.get("cursor"))
        if cursor is not None:
            moment, identifier = cursor
            queryset = queryset.filter(
                Q(last_message_at__lt=moment) | Q(last_message_at=moment, id__lt=identifier)
            )

        limit = _bounded_limit(request, CONVERSATION_PAGE_DEFAULT, CONVERSATION_PAGE_MAX)
        page = list(queryset[: limit + 1])
        has_more = len(page) > limit
        page = page[:limit]

        participants_by_conversation = {
            row.conversation_id: row
            for row in participant_rows.filter(conversation_id__in=[c.id for c in page])
        }
        counterparts = {c.id: _counterpart_payload(c, user.id) for c in page}
        unread = {
            c.id: _unread_count(c, participants_by_conversation[c.id])
            for c in page
            if c.id in participants_by_conversation
        }

        serializer = ConversationSerializer(
            page,
            many=True,
            context={"counterparts": counterparts, "unread_counts": unread},
        )
        next_cursor = None
        if has_more and page:
            last = page[-1]
            next_cursor = _encode_cursor(last.last_message_at or last.created_at, last.id)

        return Response({"conversations": serializer.data, "next_cursor": next_cursor})

    @transaction.atomic
    def post(self, request):
        user = request.user
        serializer = CreateConversationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            enforce(
                [
                    (
                        "conversation_create",
                        user.id,
                        RATE_LIMIT_CONVERSATION_CREATE,
                    )
                ]
            )
        except RateLimitExceeded:
            return _problem(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "errors.messaging.rate_limited",
                "Too many conversation attempts. Try again shortly.",
            )

        counterpart = User.objects.filter(id=data["counterpart_user_id"]).first()
        if counterpart is None:
            return _not_found()

        # The organization is the one both users share an active membership in.
        organization = (
            Organization.objects.filter(memberships__user=user, memberships__status="active")
            .filter(memberships__user=counterpart, memberships__status="active")
            .distinct()
            .first()
        )
        if organization is None:
            # Cross-tenant or non-shared: indistinguishable from "does not exist".
            return _not_found()

        allowed, message_key = authz.can_open_conversation(user, counterpart, organization)
        if not allowed:
            if message_key == "errors.messaging.participant_inactive":
                return _problem(
                    status.HTTP_403_FORBIDDEN,
                    message_key,
                    "The other participant is not currently active.",
                )
            return _problem(
                status.HTTP_403_FORBIDDEN, message_key, "You cannot open this conversation."
            )

        context_type = data.get("context_type", "none")
        context_id = data.get("context_id")

        if context_type == "workout_session":
            from apps.execution.models import WorkoutSession

            session = WorkoutSession.objects.filter(
                id=context_id, organization=organization
            ).first()
            if session is None:
                return _not_found()

        key = participant_key(user.id, counterpart.id, context_type, context_id or "")

        existing = Conversation.objects.filter(
            organization=organization, kind="direct", participant_key=key
        ).first()
        if existing is not None:
            # Idempotent creation: return the existing thread rather than a 409.
            return Response(
                ConversationSerializer(
                    existing,
                    context={
                        "counterparts": {existing.id: _counterpart_payload(existing, user.id)},
                        "unread_counts": {},
                    },
                ).data,
                status=status.HTTP_200_OK,
            )

        try:
            conversation = Conversation.objects.create(
                organization=organization,
                kind="direct",
                context_type=context_type,
                context_id=context_id,
                participant_key=key,
                created_by_user=user,
            )
        except IntegrityError:
            existing = Conversation.objects.get(
                organization=organization, kind="direct", participant_key=key
            )
            return Response(
                ConversationSerializer(
                    existing,
                    context={
                        "counterparts": {existing.id: _counterpart_payload(existing, user.id)},
                        "unread_counts": {},
                    },
                ).data,
                status=status.HTTP_200_OK,
            )

        ConversationParticipant.objects.create(
            conversation=conversation,
            user=user,
            role_at_join=authz.role_for_participant(user, organization),
        )
        ConversationParticipant.objects.create(
            conversation=conversation,
            user=counterpart,
            role_at_join=authz.role_for_participant(counterpart, organization),
        )

        _audit(
            request,
            organization,
            "conversation.created",
            "Conversation",
            conversation.id,
            {"context_type": context_type, "participant_count": 2},
        )

        return Response(
            ConversationSerializer(
                conversation,
                context={
                    "counterparts": {conversation.id: _counterpart_payload(conversation, user.id)},
                    "unread_counts": {conversation.id: 0},
                },
            ).data,
            status=status.HTTP_201_CREATED,
        )


class ConversationDetailView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, conversation_id):
        conversation, participant = authz.resolve_conversation_for_read(
            request.user, conversation_id
        )
        if conversation is None:
            return _not_found()

        can_send, send_block_key = authz.can_send_message(request.user, conversation, participant)
        data = ConversationSerializer(
            conversation,
            context={
                "counterparts": {
                    conversation.id: _counterpart_payload(conversation, request.user.id)
                },
                "unread_counts": {conversation.id: _unread_count(conversation, participant)},
            },
        ).data
        data["can_send"] = can_send
        data["send_block_key"] = "" if can_send else send_block_key
        data["last_read_at"] = participant.last_read_at
        data["is_muted"] = participant.is_muted
        return Response(data)


class MessageListCreateView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, conversation_id):
        conversation, participant = authz.resolve_conversation_for_read(
            request.user, conversation_id
        )
        if conversation is None:
            return _not_found()

        queryset = authz.visible_message_queryset(conversation, participant).order_by(
            "-created_at", "-id"
        )

        cursor = _decode_cursor(request.query_params.get("before"))
        if cursor is not None:
            moment, identifier = cursor
            queryset = queryset.filter(
                Q(created_at__lt=moment) | Q(created_at=moment, id__lt=identifier)
            )

        limit = _bounded_limit(request, MESSAGE_PAGE_DEFAULT, MESSAGE_PAGE_MAX)
        page = list(queryset[: limit + 1])
        has_more = len(page) > limit
        page = page[:limit]

        next_cursor = (
            _encode_cursor(page[-1].created_at, page[-1].id) if has_more and page else None
        )

        return Response(
            {
                "messages": MessageSerializer(page, many=True).data,
                "next_cursor": next_cursor,
                "has_more": has_more,
            }
        )

    def post(self, request, conversation_id):
        user = request.user
        conversation, participant = authz.resolve_conversation_for_read(user, conversation_id)
        if conversation is None:
            return _not_found()

        can_send, message_key = authz.can_send_message(user, conversation, participant)
        if not can_send:
            if message_key == "errors.messaging.conversation_archived":
                return _problem(
                    status.HTTP_409_CONFLICT, message_key, "This conversation is archived."
                )
            return _problem(
                status.HTTP_403_FORBIDDEN, message_key, "You cannot send in this conversation."
            )

        serializer = CreateMessageInputSerializer(data=request.data)
        if not serializer.is_valid():
            body_errors = serializer.errors.get("body") or []
            for error in body_errors:
                text = str(error)
                if text.startswith("errors.messaging."):
                    return _problem(
                        status.HTTP_422_UNPROCESSABLE_ENTITY,
                        text,
                        "The message could not be accepted.",
                    )
            return _problem(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "errors.validation_failed",
                "The submitted payload contained validation errors.",
            )

        body = serializer.validated_data["body"]
        client_message_id = serializer.validated_data.get("client_message_id")

        # Idempotent replay: return the original message rather than a duplicate.
        if client_message_id:
            existing = Message.objects.filter(
                conversation=conversation,
                sender_user=user,
                client_message_id=client_message_id,
            ).first()
            if existing is not None:
                return Response(MessageSerializer(existing).data, status=status.HTTP_200_OK)

        try:
            enforce(
                [
                    ("message_user", user.id, RATE_LIMIT_MESSAGE_PER_USER),
                    (
                        "message_conversation",
                        f"{user.id}:{conversation.id}",
                        RATE_LIMIT_MESSAGE_PER_CONVERSATION,
                    ),
                    (
                        "message_org",
                        conversation.organization_id,
                        RATE_LIMIT_MESSAGE_PER_ORG,
                    ),
                ]
            )
        except RateLimitExceeded:
            return _problem(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "errors.messaging.rate_limited",
                "You are sending messages too quickly. Try again shortly.",
            )

        recipients = [
            row.user_id
            for row in authz.counterpart_participants(conversation, exclude_user_id=user.id)
        ]

        try:
            # Domain write and outbox event share one transaction: if either
            # fails, neither the message nor the event exists.
            with transaction.atomic():
                message = Message.objects.create(
                    conversation=conversation,
                    sender_user=user,
                    body=body,
                    client_message_id=client_message_id,
                )
                Conversation.objects.filter(id=conversation.id).update(
                    last_message_at=message.created_at,
                    last_message_preview=build_preview(body),
                )
                emit_message_sent(
                    message=message,
                    conversation=conversation,
                    recipient_user_ids=recipients,
                    correlation_id=getattr(request, "correlation_id", ""),
                )
                _audit(
                    request,
                    conversation.organization,
                    "message.sent",
                    "Message",
                    message.id,
                    {
                        "conversation_id": conversation.id,
                        "body_length": len(body),
                        "recipient_count": len(recipients),
                    },
                )
        except IntegrityError:
            # Concurrent idempotent replay landed first.
            existing = Message.objects.filter(
                conversation=conversation,
                sender_user=user,
                client_message_id=client_message_id,
            ).first()
            if existing is not None:
                return Response(MessageSerializer(existing).data, status=status.HTTP_200_OK)
            raise

        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)


class ConversationReadView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    @transaction.atomic
    def post(self, request, conversation_id):
        conversation, participant = authz.resolve_conversation_for_read(
            request.user, conversation_id
        )
        if conversation is None:
            return _not_found()

        serializer = MarkReadInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        requested = serializer.validated_data.get("read_at") or timezone.now()
        # Never accept a future cursor and never move the cursor backwards.
        now = timezone.now()
        if requested > now:
            requested = now
        if participant.last_read_at is None or requested > participant.last_read_at:
            participant.last_read_at = requested
            participant.save(update_fields=["last_read_at"])

        _audit(
            request,
            conversation.organization,
            "conversation.read",
            "Conversation",
            conversation.id,
            {"read_at": participant.last_read_at.isoformat()},
        )

        return Response(
            {
                "conversation_id": conversation.id,
                "last_read_at": participant.last_read_at,
                "unread_count": _unread_count(conversation, participant),
            }
        )


# --- Notifications ---------------------------------------------------------- #


class NotificationListView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        user = request.user
        queryset = Notification.objects.filter(recipient_user=user).order_by("-created_at", "-id")

        if request.query_params.get("unread") == "true":
            queryset = queryset.filter(read_at__isnull=True)

        category = request.query_params.get("category")
        if category in dict(Notification.CATEGORY_CHOICES):
            queryset = queryset.filter(category=category)

        cursor = _decode_cursor(request.query_params.get("cursor"))
        if cursor is not None:
            moment, identifier = cursor
            queryset = queryset.filter(
                Q(created_at__lt=moment) | Q(created_at=moment, id__lt=identifier)
            )

        limit = _bounded_limit(request, NOTIFICATION_PAGE_DEFAULT, NOTIFICATION_PAGE_MAX)
        page = list(queryset[: limit + 1])
        has_more = len(page) > limit
        page = page[:limit]

        unread_total = min(
            Notification.objects.filter(recipient_user=user, read_at__isnull=True).count(),
            UNREAD_COUNT_CAP,
        )
        next_cursor = (
            _encode_cursor(page[-1].created_at, page[-1].id) if has_more and page else None
        )

        return Response(
            {
                "notifications": NotificationSerializer(page, many=True).data,
                "unread_count": unread_total,
                "next_cursor": next_cursor,
            }
        )


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, notification_id):
        # Scoped to the caller: another user's id is a 404, not a 403, so the
        # endpoint cannot be used to enumerate notification identifiers.
        notification = Notification.objects.filter(
            id=notification_id, recipient_user=request.user
        ).first()
        if notification is None:
            return _not_found()

        if notification.read_at is None:
            notification.read_at = timezone.now()
            notification.save(update_fields=["read_at"])

        return Response(NotificationSerializer(notification).data)


class NotificationReadAllView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    @transaction.atomic
    def post(self, request):
        now = timezone.now()
        updated = Notification.objects.filter(
            recipient_user=request.user, read_at__isnull=True
        ).update(read_at=now)

        if updated:
            _audit(
                request,
                None,
                "notification.read_all",
                "Notification",
                request.user.id,
                {"updated": updated},
            )

        return Response({"updated": updated, "read_at": now})


class NotificationPreferenceView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def _profile(self, user):
        profile, _ = NotificationPreferenceProfile.objects.get_or_create(user=user)
        return profile

    def _matrix(self, user):
        stored = {
            (p.event_type, p.channel): p.is_enabled
            for p in NotificationPreference.objects.filter(user=user)
        }
        rows = []
        for event_type in EVENT_TYPES:
            category = EVENT_CATEGORY[event_type]
            for channel in CHANNELS:
                forced = channel == "in_app" and category in NON_SUPPRESSIBLE_CATEGORIES
                enabled = stored.get(
                    (event_type, channel), DEFAULT_CHANNEL_ENABLED.get(channel, False)
                )
                rows.append(
                    {
                        "event_type": event_type,
                        "category": category,
                        "channel": channel,
                        "is_enabled": True if forced else enabled,
                        "is_locked": forced,
                    }
                )
        return rows

    def _payload(self, user):
        profile = self._profile(user)
        return {
            "preferences": self._matrix(user),
            "quiet_hours_enabled": profile.quiet_hours_enabled,
            "quiet_hours_start": profile.quiet_hours_start,
            "quiet_hours_end": profile.quiet_hours_end,
            "web_push_permission_state": profile.web_push_permission_state,
            "timezone": user.timezone,
            # Explicit, non-inflated capability statement for the UI.
            "channels_available": {
                "in_app": True,
                "email": False,
                "web_push": False,
            },
        }

    def get(self, request):
        return Response(self._payload(request.user))

    @transaction.atomic
    def patch(self, request):
        user = request.user

        try:
            enforce([("preference_update", user.id, RATE_LIMIT_PREFERENCE_UPDATE)])
        except RateLimitExceeded:
            return _problem(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "errors.messaging.rate_limited",
                "Too many preference updates. Try again shortly.",
            )

        serializer = UpdatePreferencesInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        for entry in data.get("preferences", []):
            category = EVENT_CATEGORY[entry["event_type"]]
            if (
                entry["channel"] == "in_app"
                and category in NON_SUPPRESSIBLE_CATEGORIES
                and entry["is_enabled"] is False
            ):
                return _problem(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "errors.notifications.category_not_suppressible",
                    "Safety-critical in-app alerts cannot be disabled.",
                )

        changed_keys = []
        for entry in data.get("preferences", []):
            NotificationPreference.objects.update_or_create(
                user=user,
                event_type=entry["event_type"],
                channel=entry["channel"],
                defaults={"is_enabled": entry["is_enabled"]},
            )
            changed_keys.append(f"{entry['event_type']}/{entry['channel']}")

        profile = self._profile(user)
        profile_fields = []
        for field in (
            "quiet_hours_enabled",
            "quiet_hours_start",
            "quiet_hours_end",
            "web_push_permission_state",
        ):
            if field in data:
                setattr(profile, field, data[field])
                profile_fields.append(field)
                changed_keys.append(field)
        if profile_fields:
            profile.save(update_fields=profile_fields + ["updated_at"])

        if changed_keys:
            organization = _user_organizations(user).first()
            _audit(
                request,
                organization,
                "notification.preferences_updated",
                "NotificationPreference",
                user.id,
                {"changed": sorted(set(changed_keys))[:40]},
            )

        return Response(self._payload(user))


class ConversationMuteView(APIView):
    """Per-conversation mute: a low-noise control that never blocks safety alerts."""

    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, conversation_id):
        conversation, participant = authz.resolve_conversation_for_read(
            request.user, conversation_id
        )
        if conversation is None:
            return _not_found()

        desired = request.data.get("is_muted")
        if not isinstance(desired, bool):
            return _problem(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "errors.validation_failed",
                "is_muted must be a boolean.",
            )

        participant.is_muted = desired
        participant.save(update_fields=["is_muted"])
        return Response({"conversation_id": conversation.id, "is_muted": participant.is_muted})


# Membership import kept for module-level authorization readability in reviews.
__all__ = [
    "ConversationDetailView",
    "ConversationListCreateView",
    "ConversationMuteView",
    "ConversationReadView",
    "MessageListCreateView",
    "NotificationListView",
    "NotificationPreferenceView",
    "NotificationReadAllView",
    "NotificationReadView",
    "Membership",
]
