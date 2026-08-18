"""Billing application services: hosted sessions, webhook ingestion and reconciliation."""

import hashlib
import re
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode, urlparse, urlunparse

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from .entitlements import evaluate_entitlements
from .models import (
    BillingAccount,
    BillingAuditEvent,
    BillingDomainEvent,
    CheckoutAttempt,
    InvoiceSummary,
    Price,
    ProviderCustomerReference,
    ReconciliationIssue,
    Subscription,
    WebhookEvent,
)
from .providers import get_provider
from .providers.base import (
    BillingProviderError,
    MalformedProviderEvent,
    MalformedProviderResponse,
)

IDEMPOTENCY_KEY = re.compile(r"^[\x21-\x7E]{16,128}$")
ALLOWED_TRANSITIONS = {
    None: {"trialing", "active", "past_due", "incomplete", "unpaid", "canceled"},
    "trialing": {"trialing", "active", "past_due", "incomplete", "unpaid", "canceled"},
    "active": {"active", "past_due", "incomplete", "unpaid", "canceled"},
    "past_due": {"past_due", "active", "incomplete", "unpaid", "canceled"},
    "incomplete": {"incomplete", "active", "unpaid", "canceled"},
    "unpaid": {"unpaid", "active", "canceled"},
    "canceled": {"canceled"},
}
SUBSCRIPTION_EVENTS = {"subscription.created", "subscription.updated", "subscription.deleted"}
INVOICE_EVENTS = {"invoice.updated", "invoice.paid", "invoice.payment_failed"}
INVOICE_TRANSITIONS = {
    None: {"draft", "open", "paid", "uncollectible", "void"},
    "draft": {"draft", "open", "void"},
    "open": {"open", "paid", "uncollectible", "void"},
    "paid": {"paid", "void"},
    "uncollectible": {"uncollectible", "paid", "void"},
    "void": {"void"},
}


class BillingConflict(Exception):
    code = "billing_conflict"


class BillingConfigurationFailure(Exception):
    code = "billing_configuration_error"


class WebhookProcessingFailure(Exception):
    code = "webhook_processing_failed"

    def __init__(self, code: str, event: WebhookEvent | None = None):
        self.code = code
        self.event = event
        super().__init__(code)


class ReconciliationFailure(Exception):
    code = "reconciliation_failed"

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def validate_idempotency_key(value: str) -> str:
    if not isinstance(value, str) or not IDEMPOTENCY_KEY.fullmatch(value):
        raise BillingConflict("invalid_idempotency_key")
    return value


def _timestamp(value, *, required=False):
    if value is None and not required:
        return None
    if not isinstance(value, int):
        raise MalformedProviderEvent("Expected a Unix timestamp.")
    try:
        return datetime.fromtimestamp(value, tz=UTC)
    except (OverflowError, OSError, ValueError) as exc:
        raise MalformedProviderEvent("Timestamp is outside the supported range.") from exc


def _external_url(url: str, *, invoice=False) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    allowed = set(getattr(settings, "BILLING_HOSTED_URL_ALLOWED_HOSTS", []))
    if parsed.scheme != "https" or not parsed.hostname or parsed.hostname not in allowed:
        raise MalformedProviderResponse("Provider returned a non-allowlisted hosted URL.")
    if parsed.username or parsed.password or parsed.fragment:
        raise MalformedProviderResponse("Provider returned an unsafe hosted URL.")
    if not invoice and parsed.query:
        # Session URLs are bearer-like redirects; fake/reference contract does not need queries.
        raise MalformedProviderResponse("Provider returned an unexpected hosted URL query.")
    return url


def _frontend_url(locale: str, state: str) -> str:
    base = getattr(settings, "BILLING_FRONTEND_BASE_URL", "")
    parsed = urlparse(base)
    local_http = (
        settings.DEBUG and parsed.scheme == "http" and parsed.hostname in {"localhost", "127.0.0.1"}
    )
    if (parsed.scheme != "https" and not local_http) or not parsed.netloc:
        raise BillingConfigurationFailure("billing_frontend_url_invalid")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise BillingConfigurationFailure("billing_frontend_url_invalid")
    path = f"{parsed.path.rstrip('/')}/{locale}/org/billing"
    return urlunparse((parsed.scheme, parsed.netloc, path, "", urlencode({"checkout": state}), ""))


def ensure_account(organization) -> BillingAccount:
    provider_name = getattr(settings, "BILLING_DEFAULT_PROVIDER", "")
    if not provider_name:
        raise BillingConfigurationFailure("billing_provider_not_configured")
    account, _ = BillingAccount.objects.get_or_create(
        organization=organization, defaults={"default_provider": provider_name}
    )
    if account.status != "active":
        raise BillingConflict("billing_account_not_active")
    return account


def _customer_reference(account: BillingAccount, provider, idempotency_key: str):
    existing = ProviderCustomerReference.objects.filter(
        billing_account=account, provider=provider.name
    ).first()
    if existing:
        return existing
    customer = provider.create_customer(
        account_reference=account.id, idempotency_key=f"customer:{idempotency_key}"
    )
    if not customer.id or len(customer.id) > 255:
        raise MalformedProviderResponse("Provider customer reference is invalid.")
    try:
        return ProviderCustomerReference.objects.create(
            billing_account=account,
            provider=provider.name,
            external_customer_id=customer.id,
        )
    except IntegrityError:
        return ProviderCustomerReference.objects.get(
            billing_account=account, provider=provider.name
        )


def create_hosted_session(
    *, organization, actor, kind: str, idempotency_key: str, locale: str, price: Price | None = None
):
    validate_idempotency_key(idempotency_key)
    if kind not in {"checkout", "portal"}:
        raise BillingConflict("invalid_session_kind")
    account = ensure_account(organization)
    provider = get_provider(account.default_provider)
    if price and (
        not price.is_active
        or not price.plan.is_active
        or price.provider != provider.name
        or not price.provider_price_id
    ):
        raise BillingConflict("price_not_available")
    if kind == "checkout" and price is None:
        raise BillingConflict("price_required")

    with transaction.atomic():
        locked = BillingAccount.objects.select_for_update().get(pk=account.pk)
        attempt, created = CheckoutAttempt.objects.get_or_create(
            billing_account=locked,
            idempotency_key=idempotency_key,
            defaults={
                "price": price,
                "provider": provider.name,
                "kind": kind,
                "created_by": actor,
            },
        )
        if not created:
            same_payload = (
                attempt.kind == kind
                and attempt.provider == provider.name
                and attempt.price_id == (price.id if price else None)
            )
            if not same_payload:
                raise BillingConflict("idempotency_payload_conflict")
            if attempt.status == "created":
                return attempt
            attempt.status = "pending"
            attempt.error_code = ""
            attempt.save(update_fields=["status", "error_code", "updated_at"])

    try:
        if kind == "portal":
            customer_ref = ProviderCustomerReference.objects.filter(
                billing_account=account, provider=provider.name
            ).first()
            if customer_ref is None:
                raise BillingConflict("provider_customer_required")
        else:
            customer_ref = _customer_reference(account, provider, idempotency_key)
        return_url = _frontend_url(locale, "return" if kind == "checkout" else "portal-return")
        if kind == "checkout":
            session = provider.create_checkout_session(
                customer_ref=customer_ref.external_customer_id,
                price_ref=price.provider_price_id,
                return_url=return_url,
                cancel_url=_frontend_url(locale, "cancelled"),
                idempotency_key=idempotency_key,
            )
        else:
            session = provider.create_portal_session(
                customer_ref=customer_ref.external_customer_id,
                return_url=return_url,
                idempotency_key=idempotency_key,
            )
        hosted_url = _external_url(session.url)
        if not session.id or len(session.id) > 255:
            raise MalformedProviderResponse("Provider session reference is invalid.")
    except (BillingProviderError, BillingConfigurationFailure, BillingConflict) as exc:
        error_code = getattr(exc, "code", None) or str(exc.args[0])
        CheckoutAttempt.objects.filter(pk=attempt.pk).update(
            status="failed", error_code=error_code[:80]
        )
        raise

    with transaction.atomic():
        attempt = CheckoutAttempt.objects.select_for_update().get(pk=attempt.pk)
        attempt.status = "created"
        attempt.external_session_id = session.id
        attempt.hosted_url = hosted_url
        attempt.error_code = ""
        attempt.save()
        BillingAuditEvent.objects.create(
            billing_account=account,
            actor_user=actor,
            source="actor",
            action=f"billing.{kind}_session_created",
            target_type="CheckoutAttempt",
            target_id=attempt.id,
            metadata={"provider": provider.name, "price_id": price.id if price else None},
        )
    return attempt


def _issue(*, account, provider, event_id, code, detail_key):
    return ReconciliationIssue.objects.create(
        billing_account=account,
        provider=provider,
        provider_event_id=event_id,
        issue_code=code,
        safe_detail_key=detail_key,
    )


def _required_string(value, field: str, max_length=255):
    if not isinstance(value, str) or not value or len(value) > max_length:
        raise MalformedProviderEvent(f"Invalid {field} reference.")
    return value


def _required_int(value, field: str, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise MalformedProviderEvent(f"Invalid {field} value.")
    return value


def _required_bool(value, field: str):
    if not isinstance(value, bool):
        raise MalformedProviderEvent(f"Invalid {field} value.")
    return value


def _customer_account(provider_name: str, data: dict):
    customer_id = _required_string(data.get("customer_id"), "customer")
    reference = (
        ProviderCustomerReference.objects.select_related("billing_account")
        .filter(provider=provider_name, external_customer_id=customer_id)
        .first()
    )
    return reference.billing_account if reference else None


def _subscription_payload(data: dict, event_type: str):
    payload = data.get("subscription")
    if not isinstance(payload, dict):
        raise MalformedProviderEvent("Subscription event has no normalized subscription.")
    status_value = "canceled" if event_type == "subscription.deleted" else payload.get("status")
    if status_value not in dict(Subscription.STATUS_CHOICES):
        raise MalformedProviderEvent("Unknown normalized subscription status.")
    quantity = _required_int(payload.get("quantity", 1), "quantity", minimum=1)
    requires_period = status_value in {"trialing", "active", "past_due"}
    period_start = _timestamp(payload.get("current_period_start"), required=requires_period)
    period_end = _timestamp(payload.get("current_period_end"), required=requires_period)
    trial_end = _timestamp(payload.get("trial_end"), required=status_value == "trialing")
    if period_start and period_end and period_end <= period_start:
        raise MalformedProviderEvent("Subscription period end must be after its start.")
    if status_value == "trialing" and trial_end and period_start and trial_end <= period_start:
        raise MalformedProviderEvent("Trial end must be after the subscription period start.")
    return {
        "external_id": _required_string(payload.get("id"), "subscription"),
        "status": status_value,
        "price_ref": _required_string(payload.get("price_id"), "price"),
        "quantity": quantity,
        "current_period_start": period_start,
        "current_period_end": period_end,
        "trial_end": trial_end,
        "cancel_at_period_end": _required_bool(
            payload.get("cancel_at_period_end", False), "cancel_at_period_end"
        ),
        "canceled_at": _timestamp(payload.get("canceled_at"), required=status_value == "canceled"),
    }


def _subscription_matches(subscription, normalized, price):
    return (
        subscription.status == normalized["status"]
        and subscription.price_id == price.id
        and subscription.quantity == normalized["quantity"]
        and subscription.current_period_start == normalized["current_period_start"]
        and subscription.current_period_end == normalized["current_period_end"]
        and subscription.trial_end == normalized["trial_end"]
        and subscription.cancel_at_period_end == normalized["cancel_at_period_end"]
        and subscription.canceled_at == normalized["canceled_at"]
    )


def _apply_subscription_projection(
    *,
    account: BillingAccount,
    provider_name: str,
    normalized: dict,
    provider_created_at: datetime,
    source_id: str,
    request_id: str,
) -> str:
    price = (
        Price.objects.select_related("plan")
        .filter(
            provider=provider_name,
            provider_price_id=normalized["price_ref"],
        )
        .first()
    )
    if price is None:
        raise WebhookProcessingFailure("unknown_price")
    subscription = (
        Subscription.objects.select_for_update()
        .filter(
            provider=provider_name,
            external_subscription_id=normalized["external_id"],
        )
        .first()
    )
    previous = subscription.status if subscription else None
    if subscription and subscription.billing_account_id != account.id:
        raise WebhookProcessingFailure("cross_account_subscription_reference")
    if subscription and provider_created_at < subscription.last_provider_event_created_at:
        _issue(
            account=account,
            provider=provider_name,
            event_id=source_id,
            code="stale_subscription_event",
            detail_key="billing.reconciliation.stale_event",
        )
        return "ignored"
    if (
        subscription
        and provider_created_at == subscription.last_provider_event_created_at
        and not _subscription_matches(subscription, normalized, price)
    ):
        raise WebhookProcessingFailure("conflicting_event_timestamp")
    if normalized["status"] not in ALLOWED_TRANSITIONS[previous]:
        raise WebhookProcessingFailure("illegal_subscription_transition")

    if subscription is None:
        subscription = Subscription(
            billing_account=account,
            provider=provider_name,
            external_subscription_id=normalized["external_id"],
            plan=price.plan,
            price=price,
            status=normalized["status"],
            last_provider_event_created_at=provider_created_at,
        )
    subscription.plan = price.plan
    subscription.price = price
    subscription.status = normalized["status"]
    subscription.quantity = normalized["quantity"]
    subscription.current_period_start = normalized["current_period_start"]
    subscription.current_period_end = normalized["current_period_end"]
    subscription.trial_end = normalized["trial_end"]
    subscription.cancel_at_period_end = normalized["cancel_at_period_end"]
    subscription.canceled_at = normalized["canceled_at"]
    subscription.last_provider_event_created_at = provider_created_at
    if normalized["status"] == "past_due":
        if previous != "past_due":
            subscription.grace_period_ends_at = (
                provider_created_at + timedelta(days=price.grace_period_days)
                if price.grace_period_days
                else None
            )
    else:
        subscription.grace_period_ends_at = None
    subscription.save()
    evaluate_entitlements(account, persist=True)
    if previous != normalized["status"]:
        BillingAuditEvent.objects.create(
            billing_account=account,
            source="provider",
            action="billing.subscription_state_changed",
            target_type="Subscription",
            target_id=subscription.id,
            previous_state=previous or "none",
            next_state=subscription.status,
            metadata={"provider_event_id": source_id},
            request_id=request_id,
        )
        BillingDomainEvent.objects.get_or_create(
            event_key=f"{provider_name}:{source_id}:subscription-state",
            defaults={
                "billing_account": account,
                "event_type": "billing.subscription_state_changed",
                "payload": {
                    "subscription_id": subscription.id,
                    "previous_state": previous,
                    "next_state": subscription.status,
                },
            },
        )
    return "processed"


def _process_subscription(event_record: WebhookEvent, event) -> str:
    account = _customer_account(event_record.provider, event.data)
    if account is None:
        _issue(
            account=None,
            provider=event_record.provider,
            event_id=event.id,
            code="unknown_customer",
            detail_key="billing.reconciliation.unknown_customer",
        )
        return "ignored"
    event_record.billing_account = account
    event_record.save(update_fields=["billing_account"])
    normalized = _subscription_payload(event.data, event.event_type)
    try:
        return _apply_subscription_projection(
            account=account,
            provider_name=event_record.provider,
            normalized=normalized,
            provider_created_at=event.created_at,
            source_id=event.id,
            request_id=event_record.request_id,
        )
    except WebhookProcessingFailure as exc:
        exc.event = event_record
        raise


def _process_invoice(event_record: WebhookEvent, event) -> str:
    account = _customer_account(event_record.provider, event.data)
    if account is None:
        _issue(
            account=None,
            provider=event_record.provider,
            event_id=event.id,
            code="unknown_customer",
            detail_key="billing.reconciliation.unknown_customer",
        )
        return "ignored"
    event_record.billing_account = account
    event_record.save(update_fields=["billing_account"])
    invoice = event.data.get("invoice")
    if not isinstance(invoice, dict):
        raise MalformedProviderEvent("Invoice event has no normalized invoice.")
    status_value = invoice.get("status")
    if status_value not in dict(InvoiceSummary.STATUS_CHOICES):
        raise MalformedProviderEvent("Unknown normalized invoice status.")
    currency = invoice.get("currency")
    if not isinstance(currency, str) or not re.fullmatch(r"[A-Z]{3}", currency):
        raise MalformedProviderEvent("Invoice currency must be uppercase ISO format.")
    external_id = _required_string(invoice.get("id"), "invoice")
    subscription = None
    subscription_ref = invoice.get("subscription_id")
    if subscription_ref:
        subscription = Subscription.objects.filter(
            provider=event_record.provider,
            external_subscription_id=_required_string(subscription_ref, "subscription"),
            billing_account=account,
        ).first()
    invoice_number = invoice.get("number")
    if invoice_number is not None and not isinstance(invoice_number, str):
        raise MalformedProviderEvent("Invoice number must be a string.")
    exponent = _required_int(invoice.get("currency_exponent"), "currency_exponent")
    if exponent > 4:
        raise MalformedProviderEvent("Invoice currency exponent is outside the supported range.")
    hosted_url = invoice.get("hosted_invoice_url")
    receipt_url = invoice.get("receipt_url")
    if hosted_url is not None and not isinstance(hosted_url, str):
        raise MalformedProviderEvent("Hosted invoice URL must be a string.")
    if receipt_url is not None and not isinstance(receipt_url, str):
        raise MalformedProviderEvent("Receipt URL must be a string.")
    defaults = {
        "billing_account": account,
        "subscription": subscription,
        "invoice_number": (invoice_number or "")[:100],
        "status": status_value,
        "currency": currency,
        "currency_exponent": exponent,
        "amount_due_minor": _required_int(invoice.get("amount_due_minor", 0), "amount_due"),
        "amount_paid_minor": _required_int(invoice.get("amount_paid_minor", 0), "amount_paid"),
        "hosted_invoice_url": _external_url(hosted_url or "", invoice=True) or None,
        "receipt_url": _external_url(receipt_url or "", invoice=True) or None,
        "issued_at": _timestamp(invoice.get("issued_at")),
        "due_at": _timestamp(invoice.get("due_at")),
        "paid_at": _timestamp(invoice.get("paid_at")),
        "last_provider_event_created_at": event.created_at,
    }
    existing = (
        InvoiceSummary.objects.select_for_update()
        .filter(provider=event_record.provider, external_invoice_id=external_id)
        .first()
    )
    if existing and existing.billing_account_id != account.id:
        raise WebhookProcessingFailure("cross_account_invoice_reference", event_record)
    if existing and event.created_at < existing.last_provider_event_created_at:
        _issue(
            account=account,
            provider=event_record.provider,
            event_id=event.id,
            code="stale_invoice_event",
            detail_key="billing.reconciliation.stale_invoice_event",
        )
        return "ignored"
    if existing and event.created_at == existing.last_provider_event_created_at:
        comparable = {
            key: defaults[key]
            for key in [
                "subscription",
                "invoice_number",
                "status",
                "currency",
                "currency_exponent",
                "amount_due_minor",
                "amount_paid_minor",
                "hosted_invoice_url",
                "receipt_url",
                "issued_at",
                "due_at",
                "paid_at",
            ]
        }
        current = {key: getattr(existing, key) for key in comparable}
        if current != comparable:
            raise WebhookProcessingFailure("conflicting_invoice_timestamp", event_record)
    previous_status = existing.status if existing else None
    if status_value not in INVOICE_TRANSITIONS[previous_status]:
        raise WebhookProcessingFailure("illegal_invoice_transition", event_record)
    InvoiceSummary.objects.update_or_create(
        provider=event_record.provider, external_invoice_id=external_id, defaults=defaults
    )
    return "processed"


def _reconciliation_datetime(value, field: str, *, required=False):
    if value is None and not required:
        return None
    if not isinstance(value, datetime) or timezone.is_naive(value):
        raise ReconciliationFailure(f"invalid_{field}")
    return value.astimezone(UTC)


def _reconcile_subscription_state(
    *, account: BillingAccount, subscription: Subscription, retrieved, actor, request_id: str
) -> str:
    """Validate and apply a provider retrieval through the webhook projection rules."""

    try:
        external_id = _required_string(retrieved.id, "subscription")
        customer_id = _required_string(retrieved.customer_id, "customer")
        status_value = retrieved.status
        if status_value not in dict(Subscription.STATUS_CHOICES):
            raise ReconciliationFailure("unknown_subscription_status")
        normalized = {
            "external_id": external_id,
            "status": status_value,
            "price_ref": _required_string(retrieved.price_id, "price"),
            "quantity": _required_int(retrieved.quantity, "quantity", minimum=1),
            "current_period_start": _reconciliation_datetime(
                retrieved.current_period_start,
                "current_period_start",
                required=status_value in {"trialing", "active", "past_due"},
            ),
            "current_period_end": _reconciliation_datetime(
                retrieved.current_period_end,
                "current_period_end",
                required=status_value in {"trialing", "active", "past_due"},
            ),
            "trial_end": _reconciliation_datetime(
                retrieved.trial_end, "trial_end", required=status_value == "trialing"
            ),
            "cancel_at_period_end": _required_bool(
                retrieved.cancel_at_period_end, "cancel_at_period_end"
            ),
            "canceled_at": _reconciliation_datetime(
                retrieved.canceled_at, "canceled_at", required=status_value == "canceled"
            ),
        }
        provider_updated_at = _reconciliation_datetime(
            retrieved.updated_at, "provider_updated_at", required=True
        )
    except (AttributeError, MalformedProviderEvent) as exc:
        raise ReconciliationFailure("malformed_provider_response") from exc

    if external_id != subscription.external_subscription_id:
        raise ReconciliationFailure("subscription_reference_mismatch")
    customer_matches = ProviderCustomerReference.objects.filter(
        billing_account=account,
        provider=subscription.provider,
        external_customer_id=customer_id,
    ).exists()
    if not customer_matches:
        raise ReconciliationFailure("customer_reference_mismatch")
    period_start = normalized["current_period_start"]
    period_end = normalized["current_period_end"]
    if period_start and period_end and period_end <= period_start:
        raise ReconciliationFailure("invalid_subscription_period")
    if status_value == "trialing" and normalized["trial_end"] <= period_start:
        raise ReconciliationFailure("invalid_trial_period")
    tolerance = int(getattr(settings, "BILLING_WEBHOOK_TOLERANCE_SECONDS", 300))
    if provider_updated_at > timezone.now() + timedelta(seconds=tolerance):
        raise ReconciliationFailure("future_provider_timestamp")

    source_digest = hashlib.sha256(
        f"{subscription.provider}:{external_id}:{provider_updated_at.isoformat()}".encode()
    ).hexdigest()[:32]
    source_id = f"reconciliation_{source_digest}"
    try:
        with transaction.atomic():
            locked_account = BillingAccount.objects.select_for_update().get(pk=account.pk)
            outcome = _apply_subscription_projection(
                account=locked_account,
                provider_name=subscription.provider,
                normalized=normalized,
                provider_created_at=provider_updated_at,
                source_id=source_id,
                request_id=request_id,
            )
            current = Subscription.objects.get(
                provider=subscription.provider, external_subscription_id=external_id
            )
            BillingAuditEvent.objects.create(
                billing_account=locked_account,
                actor_user=actor,
                source="system",
                action="billing.subscription_reconciled",
                target_type="Subscription",
                target_id=current.id,
                metadata={"provider": subscription.provider, "outcome": outcome},
                request_id=request_id,
            )
    except WebhookProcessingFailure as exc:
        raise ReconciliationFailure(exc.code) from exc
    return outcome


def reconcile_subscription_state(
    *, account: BillingAccount, subscription: Subscription, retrieved, actor, request_id: str
) -> str:
    """Apply retrieved state and retain a safe operational issue on any conflict."""

    attempt_digest = hashlib.sha256(
        f"{subscription.provider}:{subscription.external_subscription_id}:{request_id}:{timezone.now().isoformat()}".encode()
    ).hexdigest()[:32]
    try:
        return _reconcile_subscription_state(
            account=account,
            subscription=subscription,
            retrieved=retrieved,
            actor=actor,
            request_id=request_id,
        )
    except ReconciliationFailure as exc:
        _issue(
            account=account,
            provider=subscription.provider,
            event_id=f"reconciliation_attempt_{attempt_digest}",
            code=exc.code,
            detail_key=f"billing.reconciliation.{exc.code}",
        )
        raise


def ingest_webhook(*, provider_name: str, raw_body: bytes, signature_header: str, request_id: str):
    provider = get_provider(provider_name)
    verified = provider.verify_webhook(
        raw_body=raw_body, signature_header=signature_header, received_at=timezone.now()
    )
    digest = hashlib.sha256(raw_body).hexdigest()
    try:
        record, created = WebhookEvent.objects.get_or_create(
            provider=provider_name,
            provider_event_id=verified.id,
            defaults={
                "event_type": verified.event_type,
                "status": "received",
                "payload_sha256": digest,
                "provider_created_at": verified.created_at,
                "request_id": request_id,
            },
        )
    except IntegrityError:
        record = WebhookEvent.objects.get(provider=provider_name, provider_event_id=verified.id)
        created = False
    if not created:
        if record.payload_sha256 != digest or record.event_type != verified.event_type:
            _issue(
                account=record.billing_account,
                provider=provider_name,
                event_id=verified.id,
                code="event_identity_collision",
                detail_key="billing.reconciliation.event_collision",
            )
            raise WebhookProcessingFailure("event_identity_collision", record)
        WebhookEvent.objects.filter(pk=record.pk).update(attempt_count=record.attempt_count + 1)
        record.refresh_from_db()
        if record.status in {"processed", "ignored"}:
            return record, True

    try:
        with transaction.atomic():
            record = WebhookEvent.objects.select_for_update().get(pk=record.pk)
            record.status = "verified"
            record.error_code = ""
            record.save(update_fields=["status", "error_code"])
            if verified.event_type in SUBSCRIPTION_EVENTS:
                outcome = _process_subscription(record, verified)
            elif verified.event_type in INVOICE_EVENTS:
                outcome = _process_invoice(record, verified)
            else:
                outcome = "ignored"
            record.status = outcome
            record.processed_at = timezone.now()
            record.save(update_fields=["status", "processed_at"])
    except WebhookProcessingFailure as exc:
        WebhookEvent.objects.filter(pk=record.pk).update(status="failed", error_code=exc.code)
        _issue(
            account=record.billing_account,
            provider=provider_name,
            event_id=verified.id,
            code=exc.code,
            detail_key=f"billing.reconciliation.{exc.code}",
        )
        raise
    except (MalformedProviderEvent, MalformedProviderResponse) as exc:
        code = getattr(exc, "code", "malformed_provider_event")
        WebhookEvent.objects.filter(pk=record.pk).update(status="failed", error_code=code)
        _issue(
            account=record.billing_account,
            provider=provider_name,
            event_id=verified.id,
            code=code,
            detail_key="billing.reconciliation.malformed_event",
        )
        raise WebhookProcessingFailure(code, record) from exc
    except Exception as exc:
        WebhookEvent.objects.filter(pk=record.pk).update(
            status="failed", error_code="transaction_failure"
        )
        _issue(
            account=record.billing_account,
            provider=provider_name,
            event_id=verified.id,
            code="transaction_failure",
            detail_key="billing.reconciliation.processing_failed",
        )
        raise WebhookProcessingFailure("transaction_failure", record) from exc
    record.refresh_from_db()
    return record, False
