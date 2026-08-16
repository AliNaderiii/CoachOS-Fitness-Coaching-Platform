"""Deterministic no-network billing provider for development and tests."""

import hashlib
import hmac
import json
import re
from datetime import UTC, datetime
from typing import Any

from .base import (
    HostedSession,
    InvalidWebhookSignature,
    MalformedProviderEvent,
    ProviderCustomer,
    ProviderSubscription,
    ProviderUnavailable,
    VerifiedWebhookEvent,
)

PROHIBITED_KEYS = re.compile(
    r"^(?:pan|card_number|cvv|cvc|security_code|bank_account|account_number|routing_number|client_secret|payment_method_data)$",
    re.IGNORECASE,
)
EVENT_ID = re.compile(r"^[A-Za-z0-9_\-]{6,255}$")


def _contains_prohibited_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            PROHIBITED_KEYS.match(str(key)) or _contains_prohibited_key(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_prohibited_key(item) for item in value)
    return False


class FakeBillingProvider:
    name = "fake"

    def __init__(self, *, webhook_secret: str, tolerance_seconds: int = 300):
        if not webhook_secret:
            raise ValueError("The fake webhook verifier requires a test secret.")
        self._secret = webhook_secret.encode()
        self._tolerance_seconds = tolerance_seconds

    @staticmethod
    def _stable(prefix: str, value: str) -> str:
        return f"{prefix}_{hashlib.sha256(value.encode()).hexdigest()[:24]}"

    def create_customer(self, *, account_reference: str, idempotency_key: str) -> ProviderCustomer:
        return ProviderCustomer(id=self._stable("cus", account_reference))

    def create_checkout_session(
        self,
        *,
        customer_ref: str,
        price_ref: str,
        return_url: str,
        cancel_url: str,
        idempotency_key: str,
    ) -> HostedSession:
        session_id = self._stable("cs", f"{customer_ref}:{price_ref}:{idempotency_key}")
        return HostedSession(
            id=session_id,
            url=f"https://payments.test.coachos.invalid/checkout/{session_id}",
        )

    def create_portal_session(
        self, *, customer_ref: str, return_url: str, idempotency_key: str
    ) -> HostedSession:
        session_id = self._stable("bps", f"{customer_ref}:{idempotency_key}")
        return HostedSession(
            id=session_id,
            url=f"https://payments.test.coachos.invalid/portal/{session_id}",
        )

    def verify_webhook(
        self, *, raw_body: bytes, signature_header: str, received_at: datetime
    ) -> VerifiedWebhookEvent:
        parts: dict[str, str] = {}
        for item in signature_header.split(","):
            key, separator, value = item.strip().partition("=")
            if separator and key in {"t", "v1"}:
                parts[key] = value
        try:
            timestamp = int(parts["t"])
            supplied = parts["v1"]
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidWebhookSignature("Missing signature components.") from exc
        if abs(int(received_at.timestamp()) - timestamp) > self._tolerance_seconds:
            raise InvalidWebhookSignature("Webhook timestamp is outside the replay window.")
        expected = hmac.new(
            self._secret, str(timestamp).encode() + b"." + raw_body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, supplied):
            raise InvalidWebhookSignature("Webhook signature does not match.")
        try:
            payload = json.loads(raw_body)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MalformedProviderEvent("Webhook body is not valid JSON.") from exc
        if not isinstance(payload, dict) or _contains_prohibited_key(payload):
            raise MalformedProviderEvent("Webhook event contains a prohibited or invalid shape.")
        event_id = payload.get("id")
        event_type = payload.get("type")
        created = payload.get("created")
        data = payload.get("data")
        if (
            not isinstance(event_id, str)
            or not EVENT_ID.fullmatch(event_id)
            or not isinstance(event_type, str)
            or not 1 <= len(event_type) <= 100
            or not isinstance(created, int)
            or not isinstance(data, dict)
        ):
            raise MalformedProviderEvent("Webhook event is missing required normalized fields.")
        try:
            created_at = datetime.fromtimestamp(created, tz=UTC)
        except (OverflowError, OSError, ValueError) as exc:
            raise MalformedProviderEvent("Webhook event timestamp is invalid.") from exc
        if created_at.timestamp() > received_at.timestamp() + self._tolerance_seconds:
            raise MalformedProviderEvent(
                "Webhook event creation time is implausibly in the future."
            )
        return VerifiedWebhookEvent(
            id=event_id, event_type=event_type, created_at=created_at, data=data
        )

    def retrieve_subscription(self, *, subscription_ref: str) -> ProviderSubscription:
        raise ProviderUnavailable("The deterministic fake provider has no remote state.")
