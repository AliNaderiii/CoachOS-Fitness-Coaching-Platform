"""Phase 11 — Copilot policy gates: flags, allowlist, screening, limits.

All decisions are recorded via :class:`AIPolicyDecision` by the service layer.
Nothing here reads or writes user content beyond the screened request
parameters, and nothing echoes untrusted text back to clients.
"""

from django.conf import settings as django_settings
from django.core.cache import cache
from django.utils import timezone

from .constants import (
    CAPABILITIES,
    DEFAULT_CONTEXT_RETENTION_DAYS,
    DEFAULT_DAILY_COST_CAP_MICRO_USD,
    DEFAULT_DAILY_RUN_QUOTA_PER_ACTOR,
    DEFAULT_DAILY_RUN_QUOTA_PER_ORG,
    DEFAULT_MAX_ATTEMPTS,
    DEFAULT_RATE_LIMIT_PER_MINUTE,
    PROHIBITED_INTENT_PATTERNS,
    REASON_CAPABILITY_DISABLED,
    REASON_CAPABILITY_UNKNOWN,
    REASON_FEATURE_DISABLED,
    REASON_PROHIBITED_INTENT,
)


def _setting(name, default):
    return getattr(django_settings, name, default)


def copilot_enabled() -> bool:
    """Global kill switch (default: OFF unless explicitly enabled)."""
    return bool(_setting("COPILOT_ENABLED", False))


def retention_days() -> int:
    return int(_setting("COPILOT_CONTEXT_RETENTION_DAYS", DEFAULT_CONTEXT_RETENTION_DAYS))


def max_attempts() -> int:
    return int(_setting("COPILOT_MAX_ATTEMPTS", DEFAULT_MAX_ATTEMPTS))


def rate_limit_per_minute() -> int:
    return int(_setting("COPILOT_RATE_LIMIT_PER_MINUTE", DEFAULT_RATE_LIMIT_PER_MINUTE))


def daily_quota_per_actor() -> int:
    return int(_setting("COPILOT_DAILY_RUN_QUOTA_PER_ACTOR", DEFAULT_DAILY_RUN_QUOTA_PER_ACTOR))


def daily_quota_per_org() -> int:
    return int(_setting("COPILOT_DAILY_RUN_QUOTA_PER_ORG", DEFAULT_DAILY_RUN_QUOTA_PER_ORG))


def daily_cost_cap_micro_usd() -> int:
    return int(_setting("COPILOT_DAILY_COST_CAP_MICRO_USD", DEFAULT_DAILY_COST_CAP_MICRO_USD))


def feature_state(organization) -> tuple[bool, str]:
    """Global flag + per-organization override. Returns (enabled, reason_code)."""
    if not copilot_enabled():
        return False, REASON_FEATURE_DISABLED
    if organization is not None:
        org_settings = getattr(organization, "settings", None) or {}
        if org_settings.get("copilot_disabled") is True:
            return False, REASON_FEATURE_DISABLED
    return True, ""


def capability_state(capability: str) -> tuple[bool, str]:
    """Capability allowlist + optional per-capability kill list from settings."""
    if capability not in CAPABILITIES:
        return False, REASON_CAPABILITY_UNKNOWN
    disabled = set(_setting("COPILOT_DISABLED_CAPABILITIES", []))
    if capability in disabled:
        return False, REASON_CAPABILITY_DISABLED
    return True, ""


def screen_free_text(value) -> tuple[bool, str]:
    """Screen coach-supplied request parameters for prohibited intent.

    Returns ``(allowed, reason_code)``. Matches are normalized-substring based
    and only ever *narrow* scope (deny); they never authorize anything.
    """
    if not value:
        return True, ""
    normalized = str(value).casefold()
    for pattern in PROHIBITED_INTENT_PATTERNS:
        if pattern.casefold() in normalized:
            return False, REASON_PROHIBITED_INTENT
    return True, ""


def rate_limit_hit(actor_user_id: str) -> bool:
    """Rolling per-minute, per-actor rate limit. Returns True if over limit.

    Uses the configured cache (Redis in deployed envs, locmem in tests). A
    cache outage fails *open* for rate limiting only; quota and cost caps are
    database-enforced and still fail closed.
    """
    limit = rate_limit_per_minute()
    minute_bucket = timezone.now().strftime("%Y%m%d%H%M")
    key = f"copilot:rl:{actor_user_id}:{minute_bucket}"
    try:
        current = cache.get(key)
        if current is None:
            cache.set(key, 1, timeout=120)
            return False
        current = int(current) + 1
        cache.set(key, current, timeout=120)
        return current > limit
    except Exception:  # noqa: BLE001 - cache backend failure degrades to DB quota
        return False
