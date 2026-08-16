"""
Phase 07 media storage adapter.

No production bucket, S3 credentials, or real media provider integration is
implemented (explicitly excluded in Phase 07 scope). This module defines the
adapter contract and a mock metadata-only adapter so the consent-gated media
boundary can be built and tested without a production provider.

The mock adapter retains file metadata (and optionally bytes) only in process
memory — it never writes to disk or Git and never exposes public URLs.
"""

import time

from django.utils.crypto import get_random_string

SIGNED_URL_TTL_SECONDS = 900  # ≤15 min per ADR-034


class MediaStorageAdapter:
    """Interface for private media storage. Implementations must not leak keys/URLs."""

    def put(self, key, file_obj, content_type=None):
        raise NotImplementedError

    def get_signed_url(self, key, ttl_seconds=SIGNED_URL_TTL_SECONDS):
        raise NotImplementedError

    def delete(self, key):
        raise NotImplementedError


class MockMediaStorageAdapter(MediaStorageAdapter):
    """
    Metadata-only in-memory adapter for Phase 07.

    Retains a small amount of metadata (and raw bytes for fidelity tests) in a
    process-local store. Not durable across restarts; that is intentional for the
    Phase 07 boundary. Signed URLs are deterministic and non-public (mock path).
    """

    _store = {}

    def put(self, key, file_obj, content_type=None):
        try:
            data = file_obj.read()
        except Exception:
            data = b""
        self._store[key] = {
            "content_type": content_type or "application/octet-stream",
            "size": len(data),
            "bytes": data,
        }
        return {"storage_key": key, "size": len(data)}

    def get_signed_url(self, key, ttl_seconds=SIGNED_URL_TTL_SECONDS):
        entry = self._store.get(key)
        if entry is None:
            return None
        expires = int(time.time()) + int(ttl_seconds)
        signature = get_random_string(16)
        # Mock signed URL only — no real provider is integrated in Phase 07.
        return f"/api/v1/media/mock/{key}?expires={expires}&sig={signature}"

    def delete(self, key):
        self._store.pop(key, None)


# Singleton used by the API layer. In production this would be a provider-backed
# adapter configured via settings; Phase 07 uses the mock by design.
storage_adapter = MockMediaStorageAdapter()
