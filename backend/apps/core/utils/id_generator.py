"""
UUIDv7 Identifier Generator Utility.
Phase 04 Foundation - Implements time-ordered 128-bit identifiers (ADR-017).
Note: Entity identifiers must never be used as a substitute for server-side authorization.
"""

import uuid

try:
    import uuid6

    HAS_UUID6 = True
except ImportError:
    HAS_UUID6 = False


def generate_uuid7() -> str:
    """
    Generate a time-ordered UUIDv7 string.
    Falls back to UUIDv4 if uuid6 library is unavailable.
    """
    if HAS_UUID6:
        return str(uuid6.uuid7())
    # Fallback standard UUIDv4
    return str(uuid.uuid4())


def is_valid_uuid(val: str) -> bool:
    """Validate if a string is a valid UUID representation."""
    try:
        uuid_obj = uuid.UUID(str(val))
        return str(uuid_obj) == str(val).lower()
    except (ValueError, AttributeError, TypeError):
        return False
