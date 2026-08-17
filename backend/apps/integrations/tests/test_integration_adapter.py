import pytest
from apps.integrations.adapters.mock_adapter import MockFitnessProviderAdapter


def test_mock_adapter_generates_events():
    adapter = MockFitnessProviderAdapter()
    events = adapter.generate_events(3)
    assert len(events) == 3
    assert all("provider_event_id" in e for e in events)


def test_mock_adapter_duplicate_detection():
    adapter = MockFitnessProviderAdapter()
    assert adapter.check_duplicate("mock_event_001", "ref_001") is False


def test_mock_adapter_rate_limit():
    adapter = MockFitnessProviderAdapter()
    assert adapter.simulate_rate_limit(3) is True
    assert adapter.simulate_rate_limit(5) is False
    assert adapter.rate_limit_remaining == 0


def test_mock_adapter_outage_simulation():
    adapter = MockFitnessProviderAdapter()
    assert adapter.simulate_outage(enabled=False) is True
    assert adapter.simulate_outage(enabled=True) is False
