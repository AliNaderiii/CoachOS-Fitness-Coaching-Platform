"""Provider-neutral model adapter contract (Phase 11).

The domain layer depends only on this contract. Production provider selection
is configuration (env + AIProviderAdapterConfig), never hardcoded business
logic, and there is no silent fallback to another provider.
"""

from dataclasses import dataclass
from typing import Protocol


class ProviderError(Exception):
    """Base adapter error. ``code`` is a safe enumerable reason (no payloads)."""

    code = "provider_error"
    transient = False


class ProviderUnavailable(ProviderError):
    code = "provider_unavailable"
    transient = True


class ProviderTimeout(ProviderError):
    code = "provider_timeout"
    transient = True


class ProviderOutputMalformed(ProviderError):
    """Adapter could not produce a structured payload at all."""

    code = "provider_output_malformed"
    transient = False


@dataclass(frozen=True)
class ProviderRequest:
    capability: str
    generation_language: str
    system_directive: str
    context_payload: dict
    output_schema: str
    max_output_tokens: int


@dataclass(frozen=True)
class ProviderResponse:
    payload: dict
    model_identifier: str
    provider_request_id: str
    input_tokens_est: int
    output_tokens_est: int
    cost_micro_usd: int


def estimate_tokens(text: str) -> int:
    """Deterministic rough token estimate (~4 chars/token), min 1."""
    if not text:
        return 0
    return max(1, len(text) // 4)


class ModelProvider(Protocol):
    """Adapter interface every provider must implement."""

    slug: str

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        """Return a structured draft payload for validation (not yet trusted)."""
        ...
