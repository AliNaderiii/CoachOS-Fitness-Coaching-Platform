"""
Phase 08 server-authoritative authorization for conversations and notifications.

Every decision derives from server state only (session user + Membership +
CoachAthleteAssignment + ConversationParticipant). No client-supplied header,
body field, or id ever widens access.

Denial policy: a caller who is not an active participant receives 404 for any
conversation-scoped resource, whether the conversation belongs to another tenant,
belongs to the same tenant, or does not exist at all. That uniformity is what
prevents existence leakage.
"""

from django.utils import timezone

from apps.organizations.models import Membership
from apps.programs.models import CoachAthleteAssignment

from .models import Conversation, ConversationParticipant


def active_roles(user, organization) -> set:
    """Effective active roles for a user in an organization (union of memberships)."""
    if organization is None or not getattr(user, "is_authenticated", False):
        return set()
    return set(
        Membership.objects.filter(
            user=user, organization=organization, status="active"
        ).values_list("role", flat=True)
    )


def has_active_membership(user, organization) -> bool:
    """A suspended, invited, or archived membership is not access."""
    if organization is None or not getattr(user, "is_authenticated", False):
        return False
    return Membership.objects.filter(user=user, organization=organization, status="active").exists()


def coach_assignment_active(coach, athlete, organization) -> bool:
    """Organization-scoped active coach-athlete assignment lookup."""
    return CoachAthleteAssignment.objects.filter(
        organization=organization,
        coach_user=coach,
        athlete_user=athlete,
        is_active=True,
    ).exists()


def get_participant(conversation, user):
    """Return the caller's active participant row, or None."""
    return (
        ConversationParticipant.objects.filter(
            conversation=conversation, user=user, left_at__isnull=True
        )
        .select_related("conversation")
        .first()
    )


def resolve_conversation_for_read(user, conversation_id):
    """
    Resolve a conversation the caller may READ.

    Returns (conversation, participant) or (None, None) for every denial case:
    unknown id, cross-tenant id, non-participant, removed participant, or
    suspended membership. The caller maps (None, None) to a bare 404.
    """
    if not getattr(user, "is_authenticated", False) or not getattr(user, "is_active", False):
        return (None, None)

    conversation = (
        Conversation.objects.select_related("organization").filter(id=conversation_id).first()
    )
    if conversation is None:
        return (None, None)

    # Tenant gate: the caller must currently hold an active membership in the
    # conversation's organization. Losing membership revokes access immediately.
    if not has_active_membership(user, conversation.organization):
        return (None, None)

    participant = get_participant(conversation, user)
    if participant is None:
        # Explicit decision AMD-08-01: an organization owner who is not a
        # participant has NO read path into private message content. Owner
        # oversight is served by audit events, not by a content backdoor.
        return (None, None)

    return (conversation, participant)


def counterpart_participants(conversation, exclude_user_id=None):
    """Active participants other than the given user."""
    queryset = ConversationParticipant.objects.filter(
        conversation=conversation, left_at__isnull=True
    ).select_related("user")
    if exclude_user_id is not None:
        queryset = queryset.exclude(user_id=exclude_user_id)
    return list(queryset)


def can_send_message(user, conversation, participant):
    """
    Decide whether the caller may WRITE to a conversation they can read.

    Returns (allowed, message_key). Read access does not imply write access:
    a coach whose assignment was revoked keeps the history they legitimately
    participated in but loses the ability to send.
    """
    if conversation.is_archived:
        return (False, "errors.messaging.conversation_archived")
    if participant is None or not participant.is_active:
        return (False, "errors.authz.forbidden")

    organization = conversation.organization
    roles = active_roles(user, organization)
    if not roles:
        return (False, "errors.authz.forbidden")

    others = counterpart_participants(conversation, exclude_user_id=user.id)
    if not others:
        return (False, "errors.messaging.participant_inactive")

    for other in others:
        # The counterpart must still be an active member of the tenant.
        if not other.user.is_active or not has_active_membership(other.user, organization):
            return (False, "errors.messaging.participant_inactive")

        other_roles = active_roles(other.user, organization)

        # Coach -> athlete and athlete -> coach both require a live assignment.
        if "coach" in roles and "athlete" in other_roles:
            if not coach_assignment_active(user, other.user, organization):
                return (False, "errors.authz.unassigned_athlete")
        elif "athlete" in roles and "coach" in other_roles:
            if not coach_assignment_active(other.user, user, organization):
                return (False, "errors.authz.unassigned_athlete")

    return (True, "")


def can_open_conversation(user, counterpart, organization):
    """
    Decide whether the caller may CREATE a direct conversation with counterpart.

    Requires: both are active members of the same organization, they are not the
    same person, and an active coach-athlete assignment links them.
    """
    if counterpart is None or not counterpart.is_active:
        return (False, "errors.messaging.participant_inactive")
    if str(counterpart.id) == str(user.id):
        return (False, "errors.authz.forbidden")
    if not has_active_membership(user, organization):
        return (False, "errors.authz.forbidden")
    if not has_active_membership(counterpart, organization):
        return (False, "errors.messaging.participant_inactive")

    caller_roles = active_roles(user, organization)
    other_roles = active_roles(counterpart, organization)

    # Support may never open a private coaching conversation.
    if caller_roles == {"support"} or other_roles == {"support"}:
        return (False, "errors.authz.forbidden")

    if "coach" in caller_roles and "athlete" in other_roles:
        if coach_assignment_active(user, counterpart, organization):
            return (True, "")
        return (False, "errors.authz.unassigned_athlete")

    if "athlete" in caller_roles and "coach" in other_roles:
        if coach_assignment_active(counterpart, user, organization):
            return (True, "")
        return (False, "errors.authz.unassigned_athlete")

    return (False, "errors.authz.forbidden")


def role_for_participant(user, organization):
    """Snapshot role recorded at join time (audit context, not authorization)."""
    roles = active_roles(user, organization)
    for candidate in ("coach", "athlete", "owner"):
        if candidate in roles:
            return candidate
    return "athlete"


def visible_message_queryset(conversation, participant):
    """
    Messages the participant may see.

    Bounded by joined_at so that adding somebody to a conversation never grants
    retroactive access to earlier private content.
    """
    from .models import Message

    return Message.objects.filter(
        conversation=conversation, created_at__gte=participant.joined_at
    ).select_related("sender_user")


def deactivate_participant(participant):
    """Revoke a participant's access immediately (used by tests and admin paths)."""
    participant.left_at = timezone.now()
    participant.save(update_fields=["left_at"])
    return participant
