"""Server-authoritative billing entitlement evaluation and capacity checks."""

from dataclasses import dataclass
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.organizations.models import Membership

from .models import BillingAccount, EntitlementSnapshot, Subscription


class CapacityExceeded(Exception):
    def __init__(self, key: str):
        self.key = key
        super().__init__(key)


@dataclass(frozen=True)
class EntitlementDecision:
    access_state: str
    athlete_access_included: bool
    features: dict[str, bool]
    limits: dict[str, int | None]
    usage: dict[str, int]
    effective_until: Any
    reason: str
    subscription: Subscription | None

    def as_dict(self):
        return {
            "access_state": self.access_state,
            "athlete_access_included": True,
            "features": self.features,
            "limits": self.limits,
            "usage": self.usage,
            "effective_until": self.effective_until.isoformat() if self.effective_until else None,
            "reason": self.reason,
        }


def _usage(account: BillingAccount) -> dict[str, int]:
    memberships = Membership.objects.filter(organization=account.organization, status="active")
    staff = memberships.filter(role__in=["owner", "coach"]).values("user_id").distinct().count()
    clients = memberships.filter(role="athlete").values("user_id").distinct().count()
    return {"staff_seats": staff, "active_clients": clients}


def evaluate_entitlements(
    account: BillingAccount, *, at=None, persist: bool = False
) -> EntitlementDecision:
    now = at or timezone.now()
    subscription = (
        Subscription.objects.filter(billing_account=account)
        .select_related("plan", "price")
        .prefetch_related("plan__entitlements")
        .order_by("-last_provider_event_created_at", "-created_at")
        .first()
    )
    access_state = "none"
    reason = "billing.entitlement.no_subscription"
    effective_until = None
    entitled = False
    if subscription and account.status == "active":
        if subscription.status == "trialing" and (
            subscription.trial_end is not None and subscription.trial_end > now
        ):
            access_state, entitled = "trial", True
            reason = "billing.entitlement.trial"
            effective_until = subscription.trial_end
        elif subscription.status == "active":
            if (
                subscription.cancel_at_period_end
                and subscription.current_period_end
                and subscription.current_period_end <= now
            ):
                access_state, reason = "restricted", "billing.entitlement.period_ended"
            else:
                access_state, entitled = "active", True
                reason = "billing.entitlement.active"
                effective_until = (
                    subscription.current_period_end if subscription.cancel_at_period_end else None
                )
        elif (
            subscription.status == "past_due"
            and subscription.grace_period_ends_at
            and subscription.grace_period_ends_at > now
        ):
            access_state, entitled = "grace", True
            reason = "billing.entitlement.grace"
            effective_until = subscription.grace_period_ends_at
        else:
            access_state, reason = "restricted", f"billing.entitlement.{subscription.status}"
    elif subscription:
        access_state, reason = "restricted", "billing.entitlement.account_not_active"

    features: dict[str, bool] = {}
    limits: dict[str, int | None] = {"staff_seats": None, "active_clients": None}
    if subscription:
        for item in subscription.plan.entitlements.all():
            if item.kind == "boolean":
                features[item.key] = bool(entitled and item.enabled)
            elif item.key in limits:
                limits[item.key] = item.integer_limit if entitled else 0
    decision = EntitlementDecision(
        access_state=access_state,
        athlete_access_included=True,
        features=features,
        limits=limits,
        usage=_usage(account),
        effective_until=effective_until,
        reason=reason,
        subscription=subscription,
    )
    if persist:
        snapshot, created = EntitlementSnapshot.objects.get_or_create(
            billing_account=account,
            defaults={
                "subscription": subscription,
                "access_state": access_state,
                "payload": decision.as_dict(),
                "effective_until": effective_until,
            },
        )
        if not created:
            snapshot.subscription = subscription
            snapshot.access_state = access_state
            snapshot.payload = decision.as_dict()
            snapshot.effective_until = effective_until
            snapshot.evaluated_at = now
            snapshot.version += 1
            snapshot.save()
    return decision


@transaction.atomic
def assert_membership_capacity(*, organization, user, role: str) -> None:
    """Serialize admission checks; existing membership/data is never revoked."""
    try:
        account = BillingAccount.objects.select_for_update().get(organization=organization)
    except BillingAccount.DoesNotExist:
        return  # no approved cap exists
    key = (
        "active_clients"
        if role == "athlete"
        else "staff_seats"
        if role in {"owner", "coach"}
        else None
    )
    if key is None:
        return
    if Membership.objects.filter(
        organization=organization, user=user, role=role, status="active"
    ).exists():
        return
    decision = evaluate_entitlements(account)
    limit = decision.limits[key]
    if limit is not None and decision.usage[key] >= limit:
        raise CapacityExceeded(key)
