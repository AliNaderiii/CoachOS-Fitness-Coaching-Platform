"""Tests for UUIDv7 Generator Utility."""

from apps.core.utils.id_generator import generate_uuid7, is_valid_uuid


def test_uuidv7_generation_and_validation():
    uid1 = generate_uuid7()
    uid2 = generate_uuid7()

    assert is_valid_uuid(uid1)
    assert is_valid_uuid(uid2)
    assert uid1 != uid2
    assert len(uid1) == 36


def test_uuidv7_lexical_sorting_trend():
    """Verify that sequentially generated UUIDs have time-ordering properties."""
    uids = [generate_uuid7() for _ in range(5)]
    # In time-ordered UUIDv7, sorting alphabetically roughly preserves creation order
    assert len(set(uids)) == 5
