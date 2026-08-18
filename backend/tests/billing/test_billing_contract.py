from pathlib import Path

import pytest
import yaml
from django.db import IntegrityError, transaction
from django.test import override_settings
from django.urls import resolve
from openapi_spec_validator import validate_spec

from apps.billing.models import Plan, Price
from apps.billing.providers import get_provider
from apps.billing.providers.base import ProviderConfigurationError

IMPLEMENTED_PATHS = {
    "/billing/plans",
    "/billing/organizations/{org_id}/workspace",
    "/billing/organizations/{org_id}/checkout-sessions",
    "/billing/organizations/{org_id}/portal-sessions",
    "/billing/organizations/{org_id}/admins",
    "/billing/organizations/{org_id}/admins/{assignment_id}",
    "/billing/organizations/{org_id}/reconcile",
    "/billing/webhooks/{provider}",
}


def test_openapi_31_billing_contract_validates_and_routes_resolve():
    document = yaml.safe_load((Path(__file__).parents[3] / "docs" / "OPENAPI.yaml").read_text())
    validate_spec(document)
    assert document["openapi"] == "3.1.0"
    assert IMPLEMENTED_PATHS.issubset(document["paths"])
    assert document["paths"]["/billing/webhooks/{provider}"]["post"]["security"] == []
    assert (
        document["components"]["schemas"]["BillingEntitlement"]["properties"][
            "athlete_access_included"
        ]["const"]
        is True
    )
    concrete = {
        "/api/v1/billing/plans",
        "/api/v1/billing/organizations/org-id/workspace",
        "/api/v1/billing/organizations/org-id/checkout-sessions",
        "/api/v1/billing/organizations/org-id/portal-sessions",
        "/api/v1/billing/organizations/org-id/admins",
        "/api/v1/billing/organizations/org-id/admins/assignment-id",
        "/api/v1/billing/organizations/org-id/reconcile",
        "/api/v1/billing/webhooks/fake",
    }
    for path in concrete:
        assert resolve(path).func is not None


@override_settings(
    BILLING_DEFAULT_PROVIDER="fake",
    BILLING_ALLOW_FAKE_PROVIDER=False,
    BILLING_FAKE_WEBHOOK_SECRET="must-not-enable-production-fake",
)
def test_fake_provider_is_explicitly_disabled_outside_test_mode():
    with pytest.raises(ProviderConfigurationError):
        get_provider("fake")


@pytest.mark.django_db
def test_database_forces_included_athletes_and_approved_provider_mapping():
    with pytest.raises(IntegrityError), transaction.atomic():
        Plan.objects.create(
            code="invalid-athlete-policy",
            name_en="Invalid",
            name_fa="نامعتبر",
            included_athletes=False,
        )
    plan = Plan.objects.create(
        code="valid-athlete-policy",
        name_en="Valid",
        name_fa="معتبر",
        included_athletes=True,
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        Price.objects.create(
            plan=plan,
            code="missing-provider-map",
            provider="fake",
            provider_price_id=None,
            currency="USD",
            currency_exponent=2,
            unit_amount_minor=1,
            interval="month",
            is_active=True,
        )
