"""
Mock fitness provider adapter for Phase 12 deterministic vertical slice.
No real provider credentials; uses deterministic mock events and fake vault references.
"""

import uuid
from datetime import datetime, timezone, timedelta


class MockFitnessProviderAdapter:
    """Deterministic mock adapter — no real provider integration."""

    EVENT_TEMPLATE = {
        "provider_event_id": None,
        "provider_timestamp": None,
        "data_type": "workout",
        "payload": {"duration_minutes": 45, "calories": 250},
    }

    def __init__(self):
        self.event_sequence = 0
        self.rate_limit_remaining = 100
        self.rate_limit_reset = None

    def generate_events(self, count=3):
        events = []
        base_time = datetime.now(timezone.utc) - timedelta(days=7)
        for i in range(count):
            event = dict(self.EVENT_TEMPLATE)
            event["provider_event_id"] = f"mock_event_{self.event_sequence:03d}"
            event["provider_timestamp"] = (base_time + timedelta(days=i * 3)).isoformat()
            events.append(event)
            self.event_sequence += 1
        return events

    def check_duplicate(self, event_id, account_ref):
        return False  # Simplified: real dedup handled server-side by event ID

    def simulate_rate_limit(self, trigger_count):
        if trigger_count >= 5:
            self.rate_limit_remaining = 0
            self.rate_limit_reset = (datetime.now(timezone.utc) + timedelta(seconds=60)).isoformat()
        return self.rate_limit_remaining > 0

    def simulate_outage(self, enabled=False):
        return not enabled
