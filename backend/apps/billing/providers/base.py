"""Provider-neutral hosted billing boundary."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


class BillingProviderError(Exception):
    code = "provider_error"


class ProviderUnavailable(BillingProviderError):
    code = "provider_unavailable"


class ProviderConfigurationError(BillingProviderError):
    code = "provider_not_configured"


class InvalidWebhookSignature(BillingProviderError):
    code = "invalid_webhook_signature"


class MalformedProviderEvent(BillingProviderError):
    code = "malformed_provider_event"


class MalformedProviderResponse(BillingProviderError):
    code = "malformed_provider_response"


@dataclass(frozen=True)
class ProviderCustomer:
    id: str


@dataclass(frozen=True)
class HostedSession:
    id: str
    url: str


@dataclass(frozen=True)
class VerifiedWebhookEvent:
    id: str
    event_type: str
    created_at: datetime
    data: dict[str, Any]


@dataclass(frozen=True)
class ProviderSubscription:
    id: str
    customer_id: str
    status: str
    price_id: str
    quantity: int
    current_period_start: datetime | None
    current_period_end: datetime | None
    trial_end: datetime | None
    cancel_at_period_end: bool
    canceled_at: datetime | None
    updated_at: datetime


class BillingProvider(Protocol):
    name: str

    def create_customer(
        self, *, account_reference: str, idempotency_key: str
    ) -> ProviderCustomer: ...

    def create_checkout_session(
        self,
        *,
        customer_ref: str,
        price_ref: str,
        return_url: str,
        cancel_url: str,
        idempotency_key: str,
    ) -> HostedSession: ...

    def create_portal_session(
        self, *, customer_ref: str, return_url: str, idempotency_key: str
    ) -> HostedSession: ...

    def verify_webhook(
        self, *, raw_body: bytes, signature_header: str, received_at: datetime
    ) -> VerifiedWebhookEvent: ...

    def retrieve_subscription(self, *, subscription_ref: str) -> ProviderSubscription: ...
