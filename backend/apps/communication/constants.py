"""
Phase 08 shared constants and content-safety helpers.

Bounded field sizes, rate-limit windows, and message body normalization live here
so that serializers, views, and the outbox dispatcher share one definition.
"""

import unicodedata

# --- Message body bounds -------------------------------------------------- #
MESSAGE_MAX_LENGTH = 2000
MESSAGE_MAX_NEWLINES = 30
MESSAGE_PREVIEW_LENGTH = 140
CLIENT_MESSAGE_ID_MAX_LENGTH = 64

# --- Pagination bounds ---------------------------------------------------- #
CONVERSATION_PAGE_DEFAULT = 20
CONVERSATION_PAGE_MAX = 50
MESSAGE_PAGE_DEFAULT = 30
MESSAGE_PAGE_MAX = 50
NOTIFICATION_PAGE_DEFAULT = 20
NOTIFICATION_PAGE_MAX = 50

# Unread counts are capped so a hostile or very large inbox cannot force an
# unbounded COUNT(*) or leak an exact volume signal.
UNREAD_COUNT_CAP = 99

# --- Rate limits: (max_events, window_seconds) ---------------------------- #
RATE_LIMIT_MESSAGE_PER_USER = (30, 60)
RATE_LIMIT_MESSAGE_PER_CONVERSATION = (15, 60)
RATE_LIMIT_MESSAGE_PER_ORG = (600, 60)
RATE_LIMIT_CONVERSATION_CREATE = (10, 300)
RATE_LIMIT_PREFERENCE_UPDATE = (20, 300)

# --- Outbox retry policy -------------------------------------------------- #
OUTBOX_MAX_ATTEMPTS = 5
OUTBOX_BACKOFF_BASE_SECONDS = 30
OUTBOX_BACKOFF_MAX_SECONDS = 3600
OUTBOX_CLAIM_TIMEOUT_SECONDS = 300

# --- Event contract ------------------------------------------------------- #
EVENT_SCHEMA_VERSION = 1

EVENT_MESSAGE_SENT = "message.sent"
EVENT_WORKOUT_COMPLETED = "workout.completed"
EVENT_FEEDBACK_FLAG_CREATED = "feedback_flag.created"

EVENT_TYPES = (
    EVENT_MESSAGE_SENT,
    EVENT_WORKOUT_COMPLETED,
    EVENT_FEEDBACK_FLAG_CREATED,
)

# --- Notification categories ---------------------------------------------- #
CATEGORY_MESSAGING = "messaging"
CATEGORY_TRAINING = "training"
CATEGORY_SAFETY = "safety"
CATEGORY_ACCOUNT = "account"

# Safety notifications may never have their in-app channel disabled. This is the
# PRD US-NTF-001 rule that training-critical alerts continue to deliver.
NON_SUPPRESSIBLE_CATEGORIES = frozenset({CATEGORY_SAFETY})

EVENT_CATEGORY = {
    EVENT_MESSAGE_SENT: CATEGORY_MESSAGING,
    EVENT_WORKOUT_COMPLETED: CATEGORY_TRAINING,
    EVENT_FEEDBACK_FLAG_CREATED: CATEGORY_SAFETY,
}

CHANNEL_IN_APP = "in_app"
CHANNEL_EMAIL = "email"
CHANNEL_WEB_PUSH = "web_push"
CHANNELS = (CHANNEL_IN_APP, CHANNEL_EMAIL, CHANNEL_WEB_PUSH)

# Email and Web Push default OFF: Phase 08 ships no real provider credentials.
DEFAULT_CHANNEL_ENABLED = {
    CHANNEL_IN_APP: True,
    CHANNEL_EMAIL: False,
    CHANNEL_WEB_PUSH: False,
}

# Channels that quiet hours may defer. In-app notifications are pull-based and
# non-intrusive, so quiet hours never suppress or defer them.
QUIET_HOURS_DEFERRABLE_CHANNELS = frozenset({CHANNEL_EMAIL, CHANNEL_WEB_PUSH})


class MessageValidationError(ValueError):
    """Raised with a stable message_key for message body validation failures."""

    def __init__(self, message_key: str):
        super().__init__(message_key)
        self.message_key = message_key


def normalize_message_body(raw: object) -> str:
    """
    Normalize an untrusted message body.

    - Requires a string (rejects lists/dicts/numbers used for type confusion).
    - Unicode NFC normalization so visually identical bodies compare equal.
    - Strips C0/C1 control characters except newline and tab, which removes
      NUL, escape sequences, and header-injection style CR payloads.
    - Removes BiDi *override* controls (RLO/LRO/PDF) that can be used to spoof
      display order, while preserving legitimate isolate marks used by the
      bilingual UI.
    - Collapses excessive newlines and trims outer whitespace.

    Returns the normalized body. Raises MessageValidationError for empty or
    over-long content. Length is validated AFTER normalization so padding with
    control characters cannot smuggle extra content past the bound.
    """
    if not isinstance(raw, str):
        raise MessageValidationError("errors.messaging.body_empty")

    text = unicodedata.normalize("NFC", raw)

    # Dangerous BiDi override characters (display spoofing).
    for override in ("\u202a", "\u202b", "\u202c", "\u202d", "\u202e"):
        text = text.replace(override, "")

    cleaned_chars = []
    for char in text:
        if char in ("\n", "\t"):
            cleaned_chars.append(char)
            continue
        if char == "\r":
            # Normalize CR / CRLF to a single newline; never keep a bare CR.
            cleaned_chars.append("\n")
            continue
        category = unicodedata.category(char)
        if category in ("Cc", "Cf", "Cs", "Co", "Cn"):
            # Keep directional isolates the UI relies on for mixed BiDi text.
            if char in ("\u2066", "\u2067", "\u2068", "\u2069"):
                cleaned_chars.append(char)
            continue
        cleaned_chars.append(char)

    text = "".join(cleaned_chars)
    text = text.replace("\n\n\n", "\n\n")
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    text = text.strip()

    if not text:
        raise MessageValidationError("errors.messaging.body_empty")
    if len(text) > MESSAGE_MAX_LENGTH:
        raise MessageValidationError("errors.messaging.body_too_long")
    if text.count("\n") > MESSAGE_MAX_NEWLINES:
        raise MessageValidationError("errors.messaging.body_too_long")

    return text


def build_preview(body: str) -> str:
    """
    Build a bounded single-line preview for the inbox list.

    The preview is a truncation of already-normalized content; it is treated
    with the same confidentiality as the body and is only ever returned to an
    authorized participant.
    """
    single_line = " ".join(body.split())
    if len(single_line) <= MESSAGE_PREVIEW_LENGTH:
        return single_line
    return single_line[: MESSAGE_PREVIEW_LENGTH - 1] + "\u2026"


def participant_key(user_id_a: str, user_id_b: str, context_type: str, context_id: str) -> str:
    """Deterministic uniqueness key for a direct conversation."""
    first, second = sorted([str(user_id_a), str(user_id_b)])
    return f"{first}:{second}:{context_type}:{context_id or '-'}"
