"""
Phase 08 — provider-neutral notification delivery adapters.

Phase 08 ships NO real email or Web Push provider credentials. The concrete
adapters below are deterministic local fakes suitable for tests and local
development only. They exist to prove the delivery boundary, retry policy, and
failure handling — not to claim production delivery.

Security rules honoured by every adapter:
- No secret is read from, stored in, or logged by this module.
- Recipient email addresses and push endpoints are never logged or persisted;
  only a SHA-256 hash of a provider reference is retained.
- Notification bodies are never passed to a logger.
"""

import hashlib
import logging
from dataclasses import dataclass, field

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class DeliveryResult:
    """Outcome of a single provider call."""

    status: str  # succeeded | failed | suppressed
    error_code: str = ""
    provider_ref: str = ""
    retryable: bool = False

    @property
    def provider_ref_hash(self) -> str:
        if not self.provider_ref:
            return ""
        return hashlib.sha256(self.provider_ref.encode("utf-8")).hexdigest()


class NotificationChannelAdapter:
    """Interface every channel adapter implements."""

    channel = "unset"

    def is_configured(self) -> bool:
        raise NotImplementedError

    def send(self, *, notification, recipient) -> DeliveryResult:
        raise NotImplementedError


class InAppAdapter(NotificationChannelAdapter):
    """
    In-app channel.

    The durable Notification row IS the delivery. This adapter therefore always
    succeeds once the row is committed; it never performs network I/O and can
    never be the reason a user loses an important notification.
    """

    channel = "in_app"

    def is_configured(self) -> bool:
        return True

    def send(self, *, notification, recipient) -> DeliveryResult:
        return DeliveryResult(status="succeeded", provider_ref=f"in_app:{notification.id}")


@dataclass
class FakeEmailAdapter(NotificationChannelAdapter):
    """
    Deterministic local email fake.

    Records that a send WOULD have happened. It never contacts an SMTP server,
    never reads credentials, and never records the recipient address.
    """

    channel: str = "email"
    fail_next: bool = False
    fail_error_code: str = "provider_unavailable"
    sent: list = field(default_factory=list)

    def is_configured(self) -> bool:
        # Explicitly false in production-like settings: Phase 08 has no provider.
        return bool(getattr(settings, "COMMUNICATION_FAKE_PROVIDERS_ENABLED", False))

    def send(self, *, notification, recipient) -> DeliveryResult:
        if not self.is_configured():
            return DeliveryResult(status="suppressed", error_code="provider_not_configured")
        if self.fail_next:
            self.fail_next = False
            logger.warning(
                "delivery.email.failed notification_id=%s error_code=%s",
                notification.id,
                self.fail_error_code,
            )
            return DeliveryResult(status="failed", error_code=self.fail_error_code, retryable=True)
        # Only identifiers are retained. No address, no subject, no body.
        self.sent.append({"notification_id": notification.id, "recipient_id": recipient.id})
        return DeliveryResult(status="succeeded", provider_ref=f"fake-email:{notification.id}")


@dataclass
class FakeWebPushAdapter(NotificationChannelAdapter):
    """
    Deterministic local Web Push fake.

    Phase 08 registers no push subscription and holds no VAPID keys. When the
    recorded browser permission state is not `granted`, the attempt is recorded
    as `suppressed` with a permission error code rather than pretending to send.
    """

    channel: str = "web_push"
    fail_next: bool = False
    fail_error_code: str = "provider_unavailable"
    sent: list = field(default_factory=list)

    def is_configured(self) -> bool:
        return bool(getattr(settings, "COMMUNICATION_FAKE_PROVIDERS_ENABLED", False))

    def send(self, *, notification, recipient) -> DeliveryResult:
        if not self.is_configured():
            return DeliveryResult(status="suppressed", error_code="provider_not_configured")

        profile = getattr(recipient, "notification_profile", None)
        permission = getattr(profile, "web_push_permission_state", "unknown")
        if permission != "granted":
            return DeliveryResult(status="suppressed", error_code=f"push_permission_{permission}")

        if self.fail_next:
            self.fail_next = False
            logger.warning(
                "delivery.web_push.failed notification_id=%s error_code=%s",
                notification.id,
                self.fail_error_code,
            )
            return DeliveryResult(status="failed", error_code=self.fail_error_code, retryable=True)

        self.sent.append({"notification_id": notification.id, "recipient_id": recipient.id})
        return DeliveryResult(status="succeeded", provider_ref=f"fake-push:{notification.id}")


class AdapterRegistry:
    """Channel -> adapter lookup, swappable in tests."""

    def __init__(self):
        self._adapters = {
            "in_app": InAppAdapter(),
            "email": FakeEmailAdapter(),
            "web_push": FakeWebPushAdapter(),
        }

    def get(self, channel):
        return self._adapters.get(channel)

    def register(self, channel, adapter):
        self._adapters[channel] = adapter

    def reset(self):
        self.__init__()


registry = AdapterRegistry()
