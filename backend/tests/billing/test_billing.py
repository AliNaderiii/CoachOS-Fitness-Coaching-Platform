import hashlib
import hmac
import json
import time
from datetime import UTC, datetime, timedelta

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.billing.entitlements import (
    CapacityExceeded,
    assert_membership_capacity,
    evaluate_entitlements,
)
from apps.billing.models import (
    BillingAccount,
    BillingAuditEvent,
    BillingDomainEvent,
    CheckoutAttempt,
    InvoiceSummary,
    Plan,
    PlanEntitlement,
    Price,
    ProviderCustomerReference,
    ReconciliationIssue,
    Subscription,
    WebhookEvent,
)
from apps.billing.providers.base import ProviderSubscription
from apps.identity.models import User
from apps.organizations.models import Membership, Organization

SECRET = b"phase10-test-webhook-secret"


def make_org(slug="billing-org"):
    owner = User.objects.create_user(email=f"{slug}@example.com", password="SecurePass123!")
    org = Organization.objects.create(name=slug, slug=slug, owner_user=owner)
    Membership.objects.create(user=owner, organization=org, role="owner", status="active")
    return org, owner


def make_catalog(*, grace_days=3, trial_days=0, staff_limit=None, client_limit=None):
    plan = Plan.objects.create(
        code=f"plan-{time.time_ns()}",
        name_en="Approved plan",
        name_fa="طرح تاییدشده",
        description_en="Organization plan",
        description_fa="طرح سازمان",
        is_active=True,
    )
    PlanEntitlement.objects.create(
        plan=plan,
        key="program_builder",
        kind="boolean",
        enabled=True,
        label_en="Program builder",
        label_fa="برنامه‌ساز",
    )
    if staff_limit is not None:
        PlanEntitlement.objects.create(
            plan=plan,
            key="staff_seats",
            kind="integer",
            integer_limit=staff_limit,
            label_en="Staff seats",
            label_fa="جایگاه کارکنان",
        )
    if client_limit is not None:
        PlanEntitlement.objects.create(
            plan=plan,
            key="active_clients",
            kind="integer",
            integer_limit=client_limit,
            label_en="Active clients",
            label_fa="ورزشکاران فعال",
        )
    price_ref = f"price_{time.time_ns()}"
    price = Price.objects.create(
        plan=plan,
        code=f"approved-{time.time_ns()}",
        provider="fake",
        provider_price_id=price_ref,
        currency="USD",
        currency_exponent=2,
        unit_amount_minor=12345,
        interval="month",
        trial_days=trial_days,
        grace_period_days=grace_days,
        is_active=True,
    )
    return plan, price


def make_account(org):
    account = BillingAccount.objects.create(
        organization=org, default_provider="fake", status="active"
    )
    customer = ProviderCustomerReference.objects.create(
        billing_account=account,
        provider="fake",
        external_customer_id=f"cus_{org.id.replace('-', '')}",
    )
    return account, customer


def subscription_event(
    customer_id, price_ref, *, event_id, created, status="active", sub_id="sub_one"
):
    return {
        "id": event_id,
        "type": "subscription.updated",
        "created": created,
        "data": {
            "customer_id": customer_id,
            "subscription": {
                "id": sub_id,
                "status": status,
                "price_id": price_ref,
                "quantity": 1,
                "current_period_start": created,
                "current_period_end": created + 30 * 86400,
                "trial_end": created + 7 * 86400 if status == "trialing" else None,
                "cancel_at_period_end": False,
                "canceled_at": created if status == "canceled" else None,
            },
        },
    }


def signed_body(payload, *, signature_timestamp=None):
    body = json.dumps(payload, separators=(",", ":")).encode()
    timestamp = signature_timestamp or int(time.time())
    signature = hmac.new(SECRET, str(timestamp).encode() + b"." + body, hashlib.sha256).hexdigest()
    return body, f"t={timestamp},v1={signature}"


def post_event(api_client, payload, *, signature_timestamp=None):
    body, signature = signed_body(payload, signature_timestamp=signature_timestamp)
    return api_client.generic(
        "POST",
        "/api/v1/billing/webhooks/fake",
        data=body,
        content_type="application/json",
        HTTP_X_BILLING_SIGNATURE=signature,
    )


@pytest.mark.django_db
def test_catalog_has_no_seeded_or_hardcoded_prices_and_athletes_are_included(api_client):
    assert Plan.objects.count() == 0
    org, owner = make_org()
    _, price = make_catalog()
    api_client.force_authenticate(owner)
    response = api_client.get("/api/v1/billing/plans")
    assert response.status_code == 200
    item = response.data["plans"][0]
    assert item["included_athletes"] is True
    assert item["prices"][0]["unit_amount_minor"] == price.unit_amount_minor
    assert "provider_price_id" not in item["prices"][0]
    assert "card" not in json.dumps(response.data).lower()


@pytest.mark.django_db
def test_athlete_cannot_list_plans_or_open_another_org_workspace(api_client):
    org, _ = make_org()
    athlete = User.objects.create_user(email="athlete-billing@example.com")
    Membership.objects.create(user=athlete, organization=org, role="athlete", status="active")
    api_client.force_authenticate(athlete)
    assert api_client.get("/api/v1/billing/plans").status_code == 403
    assert api_client.get(f"/api/v1/billing/organizations/{org.id}/workspace").status_code == 403


@pytest.mark.django_db
def test_checkout_is_server_created_idempotent_and_client_cannot_set_money_or_url(api_client):
    org, owner = make_org()
    _, price = make_catalog()
    api_client.force_authenticate(owner)
    payload = {
        "price_id": price.id,
        "locale": "en-US",
        "amount": 1,
        "return_url": "https://attacker.example/paid",
        "status": "active",
    }
    headers = {"HTTP_IDEMPOTENCY_KEY": "checkout-request-0001"}
    first = api_client.post(
        f"/api/v1/billing/organizations/{org.id}/checkout-sessions",
        payload,
        format="json",
        **headers,
    )
    second = api_client.post(
        f"/api/v1/billing/organizations/{org.id}/checkout-sessions",
        payload,
        format="json",
        **headers,
    )
    assert first.status_code == second.status_code == 201
    assert first.data == second.data
    assert first.data["url"].startswith("https://payments.test.coachos.invalid/checkout/")
    assert CheckoutAttempt.objects.count() == 1
    assert Subscription.objects.count() == 0  # checkout/redirect never grants state
    assert ProviderCustomerReference.objects.filter(billing_account__organization=org).count() == 1


@pytest.mark.django_db
def test_checkout_idempotency_payload_conflict_and_missing_key(api_client):
    org, owner = make_org()
    _, first_price = make_catalog()
    _, second_price = make_catalog()
    api_client.force_authenticate(owner)
    url = f"/api/v1/billing/organizations/{org.id}/checkout-sessions"
    key = {"HTTP_IDEMPOTENCY_KEY": "checkout-conflict-0001"}
    assert (
        api_client.post(
            url, {"price_id": first_price.id, "locale": "en-US"}, format="json", **key
        ).status_code
        == 201
    )
    assert (
        api_client.post(
            url, {"price_id": second_price.id, "locale": "en-US"}, format="json", **key
        ).status_code
        == 409
    )
    assert (
        api_client.post(
            url, {"price_id": first_price.id, "locale": "en-US"}, format="json"
        ).status_code
        == 409
    )


@pytest.mark.django_db
def test_cross_tenant_coach_suspended_owner_and_archived_org_cannot_checkout(api_client):
    org, owner = make_org("checkout-target")
    _, price = make_catalog()
    other_org, coach = make_org("checkout-other")
    Membership.objects.create(user=coach, organization=other_org, role="coach", status="active")
    api_client.force_authenticate(coach)
    path = f"/api/v1/billing/organizations/{org.id}/checkout-sessions"
    data = {"price_id": price.id, "locale": "en-US"}
    assert (
        api_client.post(
            path, data, format="json", HTTP_IDEMPOTENCY_KEY="cross-tenant-key-0001"
        ).status_code
        == 403
    )
    owner_membership = Membership.objects.get(organization=org, user=owner, role="owner")
    owner_membership.status = "suspended"
    owner_membership.save()
    api_client.force_authenticate(owner)
    assert (
        api_client.post(
            path, data, format="json", HTTP_IDEMPOTENCY_KEY="suspended-owner-key-1"
        ).status_code
        == 403
    )
    owner_membership.status = "active"
    owner_membership.save()
    org.archived_at = timezone.now()
    org.save()
    assert (
        api_client.post(
            path, data, format="json", HTTP_IDEMPOTENCY_KEY="archived-org-key-0001"
        ).status_code
        == 403
    )


@pytest.mark.django_db
def test_portal_requires_existing_provider_customer(api_client):
    org, owner = make_org()
    api_client.force_authenticate(owner)
    path = f"/api/v1/billing/organizations/{org.id}/portal-sessions"
    denied = api_client.post(
        path,
        {"locale": "fa-IR"},
        format="json",
        HTTP_IDEMPOTENCY_KEY="portal-without-customer",
    )
    assert denied.status_code == 409
    account = BillingAccount.objects.get(organization=org)
    ProviderCustomerReference.objects.create(
        billing_account=account, provider="fake", external_customer_id="cus_portal"
    )
    allowed = api_client.post(
        path,
        {"locale": "fa-IR"},
        format="json",
        HTTP_IDEMPOTENCY_KEY="portal-with-customer-1",
    )
    assert allowed.status_code == 201
    assert "/portal/" in allowed.data["url"]


@pytest.mark.django_db
def test_owner_can_delegate_active_staff_but_not_athlete(api_client):
    org, owner = make_org()
    coach = User.objects.create_user(email="billing-admin@example.com")
    athlete = User.objects.create_user(email="billing-athlete@example.com")
    support = User.objects.create_user(email="billing-support@example.com")
    coach_membership = Membership.objects.create(
        user=coach, organization=org, role="coach", status="active"
    )
    Membership.objects.create(user=athlete, organization=org, role="athlete", status="active")
    Membership.objects.create(user=support, organization=org, role="support", status="active")
    workspace_path = f"/api/v1/billing/organizations/{org.id}/workspace"
    api_client.force_authenticate(coach)
    assert api_client.get(workspace_path).status_code == 403
    api_client.force_authenticate(support)
    assert api_client.get("/api/v1/billing/plans").status_code == 403
    assert api_client.get(workspace_path).status_code == 403
    api_client.force_authenticate(owner)
    path = f"/api/v1/billing/organizations/{org.id}/admins"
    assert api_client.post(path, {"user_id": athlete.id}, format="json").status_code == 409
    granted = api_client.post(path, {"user_id": coach.id}, format="json")
    assert granted.status_code == 201
    api_client.force_authenticate(coach)
    assert api_client.get(workspace_path).status_code == 200
    assert api_client.post(
        f"/api/v1/billing/organizations/{org.id}/portal-sessions",
        {"locale": "en-US"},
        format="json",
        HTTP_IDEMPOTENCY_KEY="delegated-admin-portal",
    ).status_code in {201, 409}
    coach_membership.status = "suspended"
    coach_membership.save(update_fields=["status"])
    assert api_client.get(workspace_path).status_code == 403


@pytest.mark.django_db
def test_unsigned_malformed_and_replayed_webhooks_are_rejected_without_state(api_client):
    payload = {
        "id": "evt_secure_1",
        "type": "ignored.test",
        "created": int(time.time()),
        "data": {},
    }
    body = json.dumps(payload).encode()
    unsigned = api_client.generic(
        "POST", "/api/v1/billing/webhooks/fake", data=body, content_type="application/json"
    )
    assert unsigned.status_code == 400
    malformed_body = b"not-json"
    timestamp = int(time.time())
    signature = hmac.new(
        SECRET, str(timestamp).encode() + b"." + malformed_body, hashlib.sha256
    ).hexdigest()
    malformed = api_client.generic(
        "POST",
        "/api/v1/billing/webhooks/fake",
        data=malformed_body,
        content_type="application/json",
        HTTP_X_BILLING_SIGNATURE=f"t={timestamp},v1={signature}",
    )
    assert malformed.status_code == 400
    replayed = post_event(api_client, payload, signature_timestamp=int(time.time()) - 1000)
    assert replayed.status_code == 400
    assert WebhookEvent.objects.count() == 0


@pytest.mark.django_db
def test_webhook_processes_subscription_once_and_creates_audit_hook(api_client):
    org, _ = make_org()
    _, price = make_catalog()
    account, customer = make_account(org)
    created = int(time.time())
    payload = subscription_event(
        customer.external_customer_id,
        price.provider_price_id,
        event_id="evt_subscription_active_1",
        created=created,
    )
    first = post_event(api_client, payload)
    second = post_event(api_client, payload)
    assert first.status_code == second.status_code == 200
    assert first.data["duplicate"] is False
    assert second.data["duplicate"] is True
    subscription = Subscription.objects.get(billing_account=account)
    assert subscription.status == "active"
    assert WebhookEvent.objects.get().attempt_count == 2
    assert (
        BillingAuditEvent.objects.filter(action="billing.subscription_state_changed").count() == 1
    )
    assert BillingDomainEvent.objects.count() == 1
    assert evaluate_entitlements(account).features["program_builder"] is True


@pytest.mark.django_db
def test_webhook_does_not_trust_customer_or_subscription_across_tenants(api_client):
    org_a, _ = make_org("event-org-a")
    org_b, _ = make_org("event-org-b")
    _, price = make_catalog()
    account_a, customer_a = make_account(org_a)
    account_b, customer_b = make_account(org_b)
    created = int(time.time())
    assert (
        post_event(
            api_client,
            subscription_event(
                customer_a.external_customer_id,
                price.provider_price_id,
                event_id="evt_cross_first",
                created=created,
                sub_id="sub_cross",
            ),
        ).status_code
        == 200
    )
    collision = post_event(
        api_client,
        subscription_event(
            customer_b.external_customer_id,
            price.provider_price_id,
            event_id="evt_cross_second",
            created=created + 1,
            sub_id="sub_cross",
        ),
    )
    assert collision.status_code == 503
    assert (
        Subscription.objects.get(external_subscription_id="sub_cross").billing_account == account_a
    )
    assert not Subscription.objects.filter(billing_account=account_b).exists()
    assert ReconciliationIssue.objects.filter(
        issue_code="cross_account_subscription_reference"
    ).exists()


@pytest.mark.django_db
def test_stale_event_is_ignored_and_past_due_grace_does_not_extend(api_client):
    org, _ = make_org()
    _, price = make_catalog(grace_days=2)
    account, customer = make_account(org)
    created = int(time.time()) - 20
    active = subscription_event(
        customer.external_customer_id,
        price.provider_price_id,
        event_id="evt_order_active",
        created=created,
    )
    assert post_event(api_client, active).status_code == 200
    stale = subscription_event(
        customer.external_customer_id,
        price.provider_price_id,
        event_id="evt_order_stale",
        created=created - 5,
        status="past_due",
    )
    response = post_event(api_client, stale)
    assert response.status_code == 200
    assert response.data["event_status"] == "ignored"
    subscription = Subscription.objects.get(billing_account=account)
    assert subscription.status == "active"

    past_due = subscription_event(
        customer.external_customer_id,
        price.provider_price_id,
        event_id="evt_order_past_due",
        created=created + 1,
        status="past_due",
    )
    assert post_event(api_client, past_due).status_code == 200
    subscription.refresh_from_db()
    first_grace_end = subscription.grace_period_ends_at
    later = subscription_event(
        customer.external_customer_id,
        price.provider_price_id,
        event_id="evt_order_past_due_later",
        created=created + 2,
        status="past_due",
    )
    assert post_event(api_client, later).status_code == 200
    subscription.refresh_from_db()
    assert subscription.grace_period_ends_at == first_grace_end
    assert evaluate_entitlements(account).access_state == "grace"


@pytest.mark.django_db
def test_canceled_is_terminal_and_client_success_query_cannot_reactivate(api_client):
    org, owner = make_org()
    _, price = make_catalog()
    account, customer = make_account(org)
    created = int(time.time())
    canceled = subscription_event(
        customer.external_customer_id,
        price.provider_price_id,
        event_id="evt_terminal_cancel",
        created=created,
        status="canceled",
    )
    assert post_event(api_client, canceled).status_code == 200
    api_client.force_authenticate(owner)
    workspace = api_client.get(
        f"/api/v1/billing/organizations/{org.id}/workspace?checkout=success&paid=true"
    )
    assert workspace.status_code == 200
    assert workspace.data["subscription"]["status"] == "canceled"
    assert workspace.data["entitlement"]["access_state"] == "restricted"
    assert workspace.data["entitlement"]["athlete_access_included"] is True
    illegal = subscription_event(
        customer.external_customer_id,
        price.provider_price_id,
        event_id="evt_terminal_illegal",
        created=created + 1,
        status="active",
    )
    assert post_event(api_client, illegal).status_code == 503
    assert Subscription.objects.get(billing_account=account).status == "canceled"


@pytest.mark.django_db
def test_event_identity_collision_is_failed_and_visible(api_client):
    org, _ = make_org()
    _, price = make_catalog()
    _, customer = make_account(org)
    created = int(time.time())
    first = subscription_event(
        customer.external_customer_id,
        price.provider_price_id,
        event_id="evt_collision_1",
        created=created,
    )
    second = subscription_event(
        customer.external_customer_id,
        price.provider_price_id,
        event_id="evt_collision_1",
        created=created,
        status="past_due",
    )
    assert post_event(api_client, first).status_code == 200
    assert post_event(api_client, second).status_code == 503
    assert ReconciliationIssue.objects.filter(issue_code="event_identity_collision").exists()


@pytest.mark.django_db
def test_unknown_event_and_customer_are_ignored_without_retry_loop(api_client):
    unknown_type = {
        "id": "evt_unknown_type",
        "type": "future.event",
        "created": int(time.time()),
        "data": {},
    }
    assert post_event(api_client, unknown_type).status_code == 200
    assert WebhookEvent.objects.get(provider_event_id="evt_unknown_type").status == "ignored"
    _, price = make_catalog()
    unknown_customer = subscription_event(
        "cus_does_not_exist",
        price.provider_price_id,
        event_id="evt_unknown_customer",
        created=int(time.time()),
    )
    assert post_event(api_client, unknown_customer).status_code == 200
    assert WebhookEvent.objects.get(provider_event_id="evt_unknown_customer").status == "ignored"
    assert ReconciliationIssue.objects.filter(issue_code="unknown_customer").exists()


@pytest.mark.django_db
def test_invoice_metadata_is_bounded_and_does_not_grant_entitlement(api_client):
    org, owner = make_org()
    account, customer = make_account(org)
    issued = int(time.time())
    payload = {
        "id": "evt_invoice_paid_1",
        "type": "invoice.paid",
        "created": issued,
        "data": {
            "customer_id": customer.external_customer_id,
            "invoice": {
                "id": "inv_fixture_1",
                "number": "INV-TEST-001",
                "status": "paid",
                "currency": "USD",
                "currency_exponent": 2,
                "amount_due_minor": 12345,
                "amount_paid_minor": 12345,
                "hosted_invoice_url": "https://invoices.test.coachos.invalid/i/fixture",
                "receipt_url": "https://invoices.test.coachos.invalid/r/fixture",
                "issued_at": issued,
                "paid_at": issued,
            },
        },
    }
    assert post_event(api_client, payload).status_code == 200
    assert InvoiceSummary.objects.get().status == "paid"
    assert evaluate_entitlements(account).access_state == "none"
    api_client.force_authenticate(owner)
    workspace = api_client.get(f"/api/v1/billing/organizations/{org.id}/workspace")
    assert workspace.status_code == 200
    assert workspace.data["invoices"][0]["number"] == "INV-TEST-001"
    assert workspace.data["entitlement"]["athlete_access_included"] is True


@pytest.mark.django_db
def test_prohibited_payment_instrument_shape_is_rejected_and_raw_payload_not_stored(api_client):
    payload = {
        "id": "evt_card_data",
        "type": "future.event",
        "created": int(time.time()),
        "data": {"card_number": "not-a-real-number", "cvv": "000"},
    }
    response = post_event(api_client, payload)
    assert response.status_code == 400
    assert WebhookEvent.objects.count() == 0
    model_fields = {
        field.name.lower()
        for model in [
            BillingAccount,
            Subscription,
            InvoiceSummary,
            WebhookEvent,
            CheckoutAttempt,
        ]
        for field in model._meta.fields
    }
    assert not model_fields.intersection({"pan", "card_number", "cvv", "cvc", "raw_payload"})


@pytest.mark.django_db
def test_optional_capacity_limit_blocks_new_admission_but_never_existing_athlete_access():
    org, _ = make_org()
    plan, price = make_catalog(client_limit=1)
    account, _ = make_account(org)
    athlete = User.objects.create_user(email="existing-client@example.com")
    Membership.objects.create(user=athlete, organization=org, role="athlete", status="active")
    Subscription.objects.create(
        billing_account=account,
        plan=plan,
        price=price,
        provider="fake",
        external_subscription_id="sub_capacity",
        status="active",
        current_period_start=timezone.now(),
        current_period_end=timezone.now() + timedelta(days=30),
        last_provider_event_created_at=timezone.now(),
    )
    new_athlete = User.objects.create_user(email="new-client@example.com")
    with pytest.raises(CapacityExceeded):
        assert_membership_capacity(organization=org, user=new_athlete, role="athlete")
    decision = evaluate_entitlements(account)
    assert decision.athlete_access_included is True
    assert Membership.objects.filter(user=athlete, status="active").exists()


@pytest.mark.django_db
def test_database_constraints_scope_external_references_and_events():
    org, _ = make_org()
    account, _ = make_account(org)
    other_org, _ = make_org("constraint-org")
    other_account = BillingAccount.objects.create(
        organization=other_org, default_provider="fake", status="active"
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        ProviderCustomerReference.objects.create(
            billing_account=other_account,
            provider="fake",
            external_customer_id=ProviderCustomerReference.objects.get(
                billing_account=account
            ).external_customer_id,
        )
    now = timezone.now()
    WebhookEvent.objects.create(
        provider="fake",
        provider_event_id="evt_constraint_unique",
        event_type="future.event",
        payload_sha256="0" * 64,
        provider_created_at=now,
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        WebhookEvent.objects.create(
            provider="fake",
            provider_event_id="evt_constraint_unique",
            event_type="future.event",
            payload_sha256="1" * 64,
            provider_created_at=now,
        )


@pytest.mark.django_db
def test_billing_audit_is_immutable():
    org, owner = make_org()
    account, _ = make_account(org)
    event = BillingAuditEvent.objects.create(
        billing_account=account,
        actor_user=owner,
        source="actor",
        action="billing.test",
        target_type="BillingAccount",
        target_id=account.id,
    )
    event.next_state = "tampered"
    with pytest.raises(ValueError):
        event.save()
    with pytest.raises(ValueError):
        event.delete()


@pytest.mark.django_db
def test_workspace_queries_are_bounded(django_assert_num_queries, api_client):
    org, owner = make_org()
    account, _ = make_account(org)
    for index in range(25):
        InvoiceSummary.objects.create(
            billing_account=account,
            provider="fake",
            external_invoice_id=f"inv_query_{index}",
            status="open",
            currency="USD",
            currency_exponent=2,
            amount_due_minor=index,
            last_provider_event_created_at=timezone.now(),
        )
    api_client.force_authenticate(owner)
    # The list is capped at 20 and remains one query regardless of result count.
    with django_assert_num_queries(9):
        response = api_client.get(f"/api/v1/billing/organizations/{org.id}/workspace")
    assert response.status_code == 200
    assert len(response.data["invoices"]) == 20


@pytest.mark.django_db
def test_same_timestamp_subscription_conflict_cannot_change_price(api_client):
    org, _ = make_org()
    _, first_price = make_catalog()
    _, second_price = make_catalog()
    account, customer = make_account(org)
    created = int(time.time())
    first = subscription_event(
        customer.external_customer_id,
        first_price.provider_price_id,
        event_id="evt_same_time_first",
        created=created,
    )
    conflict = subscription_event(
        customer.external_customer_id,
        second_price.provider_price_id,
        event_id="evt_same_time_conflict",
        created=created,
    )
    assert post_event(api_client, first).status_code == 200
    assert post_event(api_client, conflict).status_code == 503
    subscription = Subscription.objects.get(billing_account=account)
    assert subscription.price == first_price
    assert ReconciliationIssue.objects.filter(issue_code="conflicting_event_timestamp").exists()


@pytest.mark.django_db
def test_invoice_ordering_and_state_machine_prevent_regression(api_client):
    org, _ = make_org()
    _, customer = make_account(org)
    created = int(time.time()) - 10

    def invoice_event(event_id, event_created, invoice_status):
        return {
            "id": event_id,
            "type": "invoice.updated",
            "created": event_created,
            "data": {
                "customer_id": customer.external_customer_id,
                "invoice": {
                    "id": "inv_ordering",
                    "status": invoice_status,
                    "currency": "USD",
                    "currency_exponent": 2,
                    "amount_due_minor": 100,
                    "amount_paid_minor": 100 if invoice_status == "paid" else 0,
                    "issued_at": created,
                    "paid_at": created if invoice_status == "paid" else None,
                },
            },
        }

    assert (
        post_event(api_client, invoice_event("evt_invoice_paid", created, "paid")).status_code
        == 200
    )
    stale = post_event(api_client, invoice_event("evt_invoice_stale", created - 1, "open"))
    assert stale.status_code == 200
    assert stale.data["event_status"] == "ignored"
    illegal = post_event(api_client, invoice_event("evt_invoice_regress", created + 1, "open"))
    assert illegal.status_code == 503
    assert InvoiceSummary.objects.get(external_invoice_id="inv_ordering").status == "paid"
    assert ReconciliationIssue.objects.filter(issue_code="stale_invoice_event").exists()
    assert ReconciliationIssue.objects.filter(issue_code="illegal_invoice_transition").exists()


@pytest.mark.django_db
def test_future_event_time_and_trial_without_end_fail_closed(api_client):
    future = {
        "id": "evt_future_time",
        "type": "future.event",
        "created": int(time.time()) + 1000,
        "data": {},
    }
    assert post_event(api_client, future).status_code == 400
    assert not WebhookEvent.objects.filter(provider_event_id="evt_future_time").exists()

    org, _ = make_org()
    _, price = make_catalog(trial_days=7)
    _, customer = make_account(org)
    created = int(time.time())
    missing_end = subscription_event(
        customer.external_customer_id,
        price.provider_price_id,
        event_id="evt_trial_missing_end",
        created=created,
        status="trialing",
    )
    missing_end["data"]["subscription"]["trial_end"] = None
    assert post_event(api_client, missing_end).status_code == 503
    assert not Subscription.objects.exists()


@pytest.mark.django_db
def test_webhook_observability_logs_identifiers_but_not_payload_or_signature(api_client, caplog):
    payload = {
        "id": "evt_safe_observability",
        "type": "future.event",
        "created": int(time.time()),
        "data": {"note": "payload-marker-must-not-be-logged"},
    }
    body, signature = signed_body(payload)
    with caplog.at_level("INFO"):
        response = api_client.generic(
            "POST",
            "/api/v1/billing/webhooks/fake",
            data=body,
            content_type="application/json",
            HTTP_X_BILLING_SIGNATURE=signature,
        )
    assert response.status_code == 200
    assert "evt_safe_observability" in caplog.text
    assert "payload-marker-must-not-be-logged" not in caplog.text
    assert signature not in caplog.text


@pytest.mark.django_db
def test_reconciliation_applies_retrieved_state_and_surfaces_reference_conflicts(
    api_client, monkeypatch
):
    org, owner = make_org("reconciliation-org")
    _, price = make_catalog(grace_days=2)
    account, customer = make_account(org)
    created = int(time.time()) - 10
    assert (
        post_event(
            api_client,
            subscription_event(
                customer.external_customer_id,
                price.provider_price_id,
                event_id="evt_reconcile_initial",
                created=created,
                sub_id="sub_reconcile",
            ),
        ).status_code
        == 200
    )
    updated_at = datetime.fromtimestamp(created + 1, tz=UTC)
    remote = ProviderSubscription(
        id="sub_reconcile",
        customer_id=customer.external_customer_id,
        status="past_due",
        price_id=price.provider_price_id,
        quantity=1,
        current_period_start=updated_at,
        current_period_end=updated_at + timedelta(days=30),
        trial_end=None,
        cancel_at_period_end=False,
        canceled_at=None,
        updated_at=updated_at,
    )

    class RetrievedProvider:
        def __init__(self, result):
            self.result = result

        def retrieve_subscription(self, *, subscription_ref):
            assert subscription_ref == "sub_reconcile"
            return self.result

    provider = RetrievedProvider(remote)
    monkeypatch.setattr("apps.billing.views.get_provider", lambda name: provider)
    api_client.force_authenticate(owner)
    path = f"/api/v1/billing/organizations/{org.id}/reconcile"
    response = api_client.post(path, {}, format="json")
    assert response.status_code == 200
    assert response.data["status"] == "processed"
    subscription = Subscription.objects.get(billing_account=account)
    assert subscription.status == "past_due"
    assert evaluate_entitlements(account).access_state == "grace"
    assert BillingAuditEvent.objects.filter(action="billing.subscription_reconciled").exists()

    provider.result = ProviderSubscription(
        **{
            **remote.__dict__,
            "customer_id": "cus_unmapped",
            "updated_at": updated_at + timedelta(seconds=1),
        }
    )
    conflict = api_client.post(path, {}, format="json")
    assert conflict.status_code == 409
    assert ReconciliationIssue.objects.filter(issue_code="customer_reference_mismatch").exists()
    subscription.refresh_from_db()
    assert subscription.status == "past_due"


@pytest.mark.django_db
def test_entitlement_state_matrix_and_period_end_cancellation_are_fail_closed():
    plan, price = make_catalog(grace_days=2, trial_days=7)
    now = timezone.now()
    scenarios = [
        ("trialing", "trial"),
        ("active", "active"),
        ("past_due", "grace"),
        ("incomplete", "restricted"),
        ("unpaid", "restricted"),
        ("canceled", "restricted"),
    ]
    for index, (status_value, expected_access) in enumerate(scenarios):
        org, _ = make_org(f"state-matrix-{index}")
        account, _ = make_account(org)
        requires_period = status_value in {"trialing", "active", "past_due"}
        subscription = Subscription.objects.create(
            billing_account=account,
            plan=plan,
            price=price,
            provider="fake",
            external_subscription_id=f"sub_state_matrix_{status_value}",
            status=status_value,
            current_period_start=now if requires_period else None,
            current_period_end=now + timedelta(days=30) if requires_period else None,
            trial_end=now + timedelta(days=7) if status_value == "trialing" else None,
            grace_period_ends_at=(now + timedelta(days=2) if status_value == "past_due" else None),
            canceled_at=now if status_value == "canceled" else None,
            last_provider_event_created_at=now + timedelta(seconds=index),
        )
        decision = evaluate_entitlements(account)
        assert decision.access_state == expected_access
        assert decision.athlete_access_included is True
        if expected_access == "restricted":
            assert decision.features["program_builder"] is False
        subscription.delete()

    org, _ = make_org("period-ended-cancellation")
    account, _ = make_account(org)
    Subscription.objects.create(
        billing_account=account,
        plan=plan,
        price=price,
        provider="fake",
        external_subscription_id="sub_period_ended_cancellation",
        status="active",
        current_period_start=now - timedelta(days=30),
        current_period_end=now - timedelta(seconds=1),
        cancel_at_period_end=True,
        last_provider_event_created_at=now,
    )
    assert evaluate_entitlements(account).access_state == "restricted"


@pytest.mark.django_db
def test_newer_approved_price_change_reprojects_caps_without_deleting_athletes(api_client):
    org, _ = make_org("deterministic-downgrade")
    _, first_price = make_catalog(client_limit=5)
    second_plan, second_price = make_catalog(client_limit=1)
    account, customer = make_account(org)
    existing = [
        User.objects.create_user(email=f"existing-downgrade-{index}@example.com")
        for index in range(2)
    ]
    for athlete in existing:
        Membership.objects.create(user=athlete, organization=org, role="athlete", status="active")
    created = int(time.time()) - 10
    assert (
        post_event(
            api_client,
            subscription_event(
                customer.external_customer_id,
                first_price.provider_price_id,
                event_id="evt_before_downgrade",
                created=created,
                sub_id="sub_deterministic_downgrade",
            ),
        ).status_code
        == 200
    )
    assert (
        post_event(
            api_client,
            subscription_event(
                customer.external_customer_id,
                second_price.provider_price_id,
                event_id="evt_after_downgrade",
                created=created + 1,
                sub_id="sub_deterministic_downgrade",
            ),
        ).status_code
        == 200
    )
    subscription = Subscription.objects.get(billing_account=account)
    assert subscription.plan == second_plan
    decision = evaluate_entitlements(account)
    assert decision.limits["active_clients"] == 1
    assert decision.athlete_access_included is True
    assert (
        Membership.objects.filter(organization=org, user__in=existing, status="active").count() == 2
    )
    newcomer = User.objects.create_user(email="blocked-after-downgrade@example.com")
    with pytest.raises(CapacityExceeded):
        assert_membership_capacity(organization=org, user=newcomer, role="athlete")
