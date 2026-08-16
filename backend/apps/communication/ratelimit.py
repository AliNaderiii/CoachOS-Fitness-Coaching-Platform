"""
Phase 08 abuse prevention — fixed-window rate limiting.

Keys are derived exclusively from server-side state (authenticated user id,
organization id resolved from the database, conversation id resolved from the
database). No client-supplied header or body value participates in the key, so
rotating headers or sending to several endpoints cannot reset a counter.

Fail-closed: if the cache backend errors, the request is denied rather than
silently un-limited.
"""

import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_PREFIX = "p08rl"


class RateLimitExceeded(Exception):
    def __init__(self, scope, retry_after):
        super().__init__(scope)
        self.scope = scope
        self.retry_after = retry_after


def _hit(scope: str, identity: str, limit: int, window_seconds: int):
    """Increment one fixed-window counter. Returns True when within the limit."""
    key = f"{CACHE_PREFIX}:{scope}:{identity}"
    try:
        added = cache.add(key, 1, window_seconds)
        if added:
            return True
        try:
            current = cache.incr(key)
        except ValueError:
            # Key expired between add() and incr(); start a fresh window.
            cache.set(key, 1, window_seconds)
            return True
        return current <= limit
    except Exception:
        logger.warning("ratelimit.backend_error scope=%s", scope)
        return False


def enforce(checks):
    """
    Apply an ordered list of (scope, identity, (limit, window)) checks.

    Raises RateLimitExceeded for the first scope that is exhausted.
    """
    for scope, identity, (limit, window) in checks:
        if not _hit(scope, str(identity), limit, window):
            raise RateLimitExceeded(scope, window)


def reset_all():
    """Test helper: clear the whole cache namespace."""
    cache.clear()
