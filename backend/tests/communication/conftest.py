"""Phase 08 pytest fixtures."""

import pytest
from django.core.cache import cache
from helpers import World

from apps.communication.adapters import registry


@pytest.fixture(autouse=True)
def _reset_state():
    """Rate-limit counters and adapter fakes must not leak between tests."""
    cache.clear()
    registry.reset()
    yield
    cache.clear()
    registry.reset()


@pytest.fixture
def world(db):
    return World("alpha")


@pytest.fixture
def other_world(db):
    return World("beta")
