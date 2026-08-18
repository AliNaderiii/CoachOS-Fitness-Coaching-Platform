from django.conf import settings

from .base import ProviderConfigurationError
from .fake import FakeBillingProvider


def get_provider(name: str):
    """Return an explicitly enabled provider; unknown/live providers fail closed."""
    if (
        name == "fake"
        and getattr(settings, "BILLING_ALLOW_FAKE_PROVIDER", False)
        and getattr(settings, "BILLING_FAKE_WEBHOOK_SECRET", "")
    ):
        return FakeBillingProvider(
            webhook_secret=settings.BILLING_FAKE_WEBHOOK_SECRET,
            tolerance_seconds=settings.BILLING_WEBHOOK_TOLERANCE_SECONDS,
        )
    raise ProviderConfigurationError("Billing provider is not configured.")


__all__ = ["get_provider", "ProviderConfigurationError"]
