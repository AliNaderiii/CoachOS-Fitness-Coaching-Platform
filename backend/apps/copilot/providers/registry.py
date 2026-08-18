"""Provider selection — configuration driven, fail closed, no silent fallback.

Resolution order:

1. ``settings.COPILOT_PROVIDER`` picks the configured provider slug
   (default: the deterministic fake).
2. The matching :class:`AIProviderAdapterConfig` row must exist **and** be
   enabled, otherwise :class:`ProviderUnavailable` is raised.
3. Only adapters with an implementation in this module can be instantiated;
   a configured-but-unimplemented provider kind fails closed (it never falls
   back to a different provider).
"""

from dataclasses import dataclass

from django.conf import settings

from ..models import AIProviderAdapterConfig
from .base import ProviderUnavailable
from .fake import DeterministicFakeProvider


@dataclass
class ResolvedProvider:
    provider: DeterministicFakeProvider
    config: AIProviderAdapterConfig


def configured_provider_slug() -> str:
    return getattr(settings, "COPILOT_PROVIDER", DeterministicFakeProvider.slug)


def resolve_provider() -> ResolvedProvider:
    slug = configured_provider_slug()
    config = AIProviderAdapterConfig.objects.filter(slug=slug).first()
    if config is None or not config.is_enabled:
        raise ProviderUnavailable("provider_not_configured_or_disabled")
    if config.provider_kind == "fake":
        return ResolvedProvider(provider=DeterministicFakeProvider(), config=config)
    # Declarative kinds (e.g. "http") intentionally have no implementation in
    # this branch; selecting one is a configuration error that fails closed.
    raise ProviderUnavailable("provider_kind_not_implemented")


def provider_capabilities() -> dict:
    """Discovery metadata for the capabilities endpoint (non-secret)."""
    slug = configured_provider_slug()
    config = AIProviderAdapterConfig.objects.filter(slug=slug).first()
    return {
        "provider_slug": slug,
        "provider_enabled": bool(config and config.is_enabled),
        "model_identifier": (config.model_identifier if config else "") or "fake-deterministic-1",
    }
