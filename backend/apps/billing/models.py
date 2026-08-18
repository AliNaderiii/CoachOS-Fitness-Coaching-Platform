"""Provider-neutral organization billing records for Phase 10.

No model in this module stores payment instruments, provider secrets, or raw
webhook payloads. Money is represented as integer minor units plus ISO currency.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.core.utils.id_generator import generate_uuid7
from apps.identity.models import User
from apps.organizations.models import Organization


class Plan(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    code = models.SlugField(max_length=64, unique=True)
    name_en = models.CharField(max_length=120)
    name_fa = models.CharField(max_length=120)
    description_en = models.CharField(max_length=500, blank=True)
    description_fa = models.CharField(max_length=500, blank=True)
    included_athletes = models.BooleanField(default=True, editable=False)
    is_active = models.BooleanField(default=False, db_index=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "code"]
        constraints = [
            models.CheckConstraint(
                condition=Q(included_athletes=True), name="billing_athletes_always_included"
            )
        ]

    def __str__(self):
        return self.code

    def clean(self):
        if not self.included_athletes:
            raise ValidationError("Phase 10 requires athletes to remain included.")


class PlanEntitlement(models.Model):
    KIND_CHOICES = [("boolean", "Boolean"), ("integer", "Integer limit")]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name="entitlements")
    key = models.SlugField(max_length=80)
    kind = models.CharField(max_length=16, choices=KIND_CHOICES)
    enabled = models.BooleanField(default=False)
    integer_limit = models.PositiveIntegerField(null=True, blank=True)
    label_en = models.CharField(max_length=160)
    label_fa = models.CharField(max_length=160)

    class Meta:
        ordering = ["key"]
        constraints = [
            models.UniqueConstraint(
                fields=["plan", "key"], name="billing_plan_entitlement_key_uniq"
            ),
            models.CheckConstraint(
                condition=(Q(kind="boolean", integer_limit__isnull=True) | Q(kind="integer")),
                name="billing_entitlement_value_shape",
            ),
        ]

    def clean(self):
        if self.kind == "boolean" and self.integer_limit is not None:
            raise ValidationError("Boolean entitlements cannot have an integer limit.")


class Price(models.Model):
    INTERVAL_CHOICES = [("month", "Month"), ("year", "Year")]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="prices")
    code = models.SlugField(max_length=80, unique=True)
    provider = models.SlugField(max_length=32)
    provider_price_id = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=3)
    currency_exponent = models.PositiveSmallIntegerField()
    unit_amount_minor = models.PositiveBigIntegerField()
    interval = models.CharField(max_length=12, choices=INTERVAL_CHOICES)
    trial_days = models.PositiveSmallIntegerField(default=0)
    grace_period_days = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["plan__display_order", "unit_amount_minor"]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_price_id"],
                condition=Q(provider_price_id__isnull=False),
                name="billing_provider_price_ref_uniq",
            ),
            models.CheckConstraint(
                condition=Q(currency__regex=r"^[A-Z]{3}$"), name="billing_currency_upper_iso"
            ),
            models.CheckConstraint(
                condition=Q(currency_exponent__lte=4), name="billing_currency_exponent_range"
            ),
            models.CheckConstraint(
                condition=(
                    Q(is_active=False)
                    | (Q(provider_price_id__isnull=False) & ~Q(provider_price_id=""))
                ),
                name="billing_active_price_has_provider_ref",
            ),
        ]

    def clean(self):
        self.currency = self.currency.upper()
        if self.is_active and not self.provider_price_id:
            raise ValidationError("An active price requires a provider mapping.")


class BillingAccount(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("suspended", "Suspended"), ("closed", "Closed")]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    organization = models.OneToOneField(
        Organization, on_delete=models.PROTECT, related_name="billing_account"
    )
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="active")
    default_provider = models.SlugField(max_length=32)
    billing_email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"billing:{self.organization_id}"


class ProviderCustomerReference(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    billing_account = models.ForeignKey(
        BillingAccount, on_delete=models.PROTECT, related_name="provider_customers"
    )
    provider = models.SlugField(max_length=32)
    external_customer_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "external_customer_id"],
                name="billing_provider_customer_ref_uniq",
            ),
            models.UniqueConstraint(
                fields=["billing_account", "provider"], name="billing_account_provider_uniq"
            ),
        ]


class Subscription(models.Model):
    STATUS_CHOICES = [
        ("trialing", "Trialing"),
        ("active", "Active"),
        ("past_due", "Past due"),
        ("incomplete", "Incomplete"),
        ("unpaid", "Unpaid"),
        ("canceled", "Canceled"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    billing_account = models.ForeignKey(
        BillingAccount, on_delete=models.PROTECT, related_name="subscriptions"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    price = models.ForeignKey(Price, on_delete=models.PROTECT, related_name="subscriptions")
    provider = models.SlugField(max_length=32)
    external_subscription_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    grace_period_ends_at = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    last_provider_event_created_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["billing_account", "status"]),
            models.Index(fields=["provider", "external_subscription_id"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "external_subscription_id"],
                name="billing_provider_subscription_ref_uniq",
            ),
            models.CheckConstraint(condition=Q(quantity__gte=1), name="billing_quantity_positive"),
            models.CheckConstraint(
                condition=(
                    ~Q(status__in=["trialing", "active", "past_due"])
                    | (
                        Q(current_period_start__isnull=False)
                        & Q(current_period_end__isnull=False)
                        & Q(current_period_end__gt=models.F("current_period_start"))
                    )
                ),
                name="billing_entitled_states_have_period",
            ),
            models.CheckConstraint(
                condition=(~Q(status="trialing") | Q(trial_end__isnull=False)),
                name="billing_trial_has_end",
            ),
            models.CheckConstraint(
                condition=(~Q(status="canceled") | Q(canceled_at__isnull=False)),
                name="billing_canceled_has_timestamp",
            ),
        ]


class InvoiceSummary(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("open", "Open"),
        ("paid", "Paid"),
        ("uncollectible", "Uncollectible"),
        ("void", "Void"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    billing_account = models.ForeignKey(
        BillingAccount, on_delete=models.PROTECT, related_name="invoices"
    )
    subscription = models.ForeignKey(
        Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name="invoices"
    )
    provider = models.SlugField(max_length=32)
    external_invoice_id = models.CharField(max_length=255)
    invoice_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    currency = models.CharField(max_length=3)
    currency_exponent = models.PositiveSmallIntegerField()
    amount_due_minor = models.PositiveBigIntegerField(default=0)
    amount_paid_minor = models.PositiveBigIntegerField(default=0)
    hosted_invoice_url = models.URLField(max_length=500, null=True, blank=True)
    receipt_url = models.URLField(max_length=500, null=True, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    due_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    last_provider_event_created_at = models.DateTimeField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issued_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "external_invoice_id"],
                name="billing_provider_invoice_ref_uniq",
            ),
            models.CheckConstraint(
                condition=Q(currency__regex=r"^[A-Z]{3}$"),
                name="billing_invoice_currency_iso",
            ),
            models.CheckConstraint(
                condition=Q(currency_exponent__lte=4),
                name="billing_invoice_exponent_range",
            ),
        ]


class WebhookEvent(models.Model):
    STATUS_CHOICES = [
        ("received", "Received"),
        ("verified", "Verified"),
        ("processed", "Processed"),
        ("failed", "Failed"),
        ("ignored", "Ignored"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    provider = models.SlugField(max_length=32)
    provider_event_id = models.CharField(max_length=255)
    event_type = models.CharField(max_length=100)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="received")
    payload_sha256 = models.CharField(max_length=64)
    provider_created_at = models.DateTimeField()
    billing_account = models.ForeignKey(
        BillingAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="webhook_events",
    )
    attempt_count = models.PositiveSmallIntegerField(default=1)
    error_code = models.CharField(max_length=80, blank=True)
    request_id = models.CharField(max_length=36, blank=True)
    received_at = models.DateTimeField(default=timezone.now, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["status", "received_at"])]
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "provider_event_id"], name="billing_webhook_event_uniq"
            )
        ]


class BillingRoleAssignment(models.Model):
    ROLE_CHOICES = [("billing_admin", "Billing administrator")]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    billing_account = models.ForeignKey(
        BillingAccount, on_delete=models.CASCADE, related_name="role_assignments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="billing_roles")
    role = models.CharField(max_length=24, choices=ROLE_CHOICES, default="billing_admin")
    is_active = models.BooleanField(default=True)
    granted_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="billing_roles_granted"
    )
    granted_at = models.DateTimeField(default=timezone.now)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["billing_account", "user", "role"],
                name="billing_role_assignment_uniq",
            )
        ]


class CheckoutAttempt(models.Model):
    KIND_CHOICES = [("checkout", "Checkout"), ("portal", "Portal")]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("created", "Created"),
        ("failed", "Failed"),
        ("expired", "Expired"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    billing_account = models.ForeignKey(
        BillingAccount, on_delete=models.PROTECT, related_name="checkout_attempts"
    )
    price = models.ForeignKey(Price, on_delete=models.PROTECT, null=True, blank=True)
    provider = models.SlugField(max_length=32)
    kind = models.CharField(max_length=16, choices=KIND_CHOICES)
    idempotency_key = models.CharField(max_length=128)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    external_session_id = models.CharField(max_length=255, blank=True)
    hosted_url = models.URLField(max_length=500, blank=True)
    error_code = models.CharField(max_length=80, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["billing_account", "idempotency_key"],
                name="billing_checkout_idempotency_uniq",
            )
        ]


class EntitlementSnapshot(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    billing_account = models.OneToOneField(
        BillingAccount, on_delete=models.CASCADE, related_name="entitlement_snapshot"
    )
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    access_state = models.CharField(max_length=20)
    payload = models.JSONField(default=dict)
    effective_until = models.DateTimeField(null=True, blank=True)
    evaluated_at = models.DateTimeField(default=timezone.now)
    version = models.PositiveIntegerField(default=1)


class BillingAuditEvent(models.Model):
    """Immutable, minimized financial-domain audit trail."""

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    billing_account = models.ForeignKey(
        BillingAccount, on_delete=models.PROTECT, related_name="billing_audit_events"
    )
    actor_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.CharField(max_length=20)  # actor | provider | system
    action = models.CharField(max_length=100, db_index=True)
    target_type = models.CharField(max_length=64)
    target_id = models.CharField(max_length=255)
    previous_state = models.CharField(max_length=32, blank=True)
    next_state = models.CharField(max_length=32, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    request_id = models.CharField(max_length=36, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        indexes = [models.Index(fields=["billing_account", "created_at"])]

    def save(self, *args, **kwargs):
        if self.pk and BillingAuditEvent.objects.filter(pk=self.pk).exists():
            raise ValueError("BillingAuditEvent records are immutable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("BillingAuditEvent records are immutable.")


class BillingDomainEvent(models.Model):
    """Durable hook for future notifications; this is not a notification engine."""

    STATUS_CHOICES = [("pending", "Pending"), ("published", "Published"), ("failed", "Failed")]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    billing_account = models.ForeignKey(
        BillingAccount, on_delete=models.PROTECT, related_name="domain_events"
    )
    event_key = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)


class ReconciliationIssue(models.Model):
    STATUS_CHOICES = [("open", "Open"), ("resolved", "Resolved")]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    billing_account = models.ForeignKey(
        BillingAccount,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reconciliation_issues",
    )
    provider = models.SlugField(max_length=32)
    provider_event_id = models.CharField(max_length=255, blank=True)
    issue_code = models.CharField(max_length=80)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="open")
    safe_detail_key = models.CharField(max_length=120)
    first_seen_at = models.DateTimeField(default=timezone.now)
    last_seen_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-last_seen_at"]
        indexes = [models.Index(fields=["status", "last_seen_at"])]
