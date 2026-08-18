"""Protected operational visibility for minimized billing metadata."""

from django.contrib import admin

from .models import (
    BillingAccount,
    BillingAuditEvent,
    BillingDomainEvent,
    BillingRoleAssignment,
    CheckoutAttempt,
    EntitlementSnapshot,
    InvoiceSummary,
    Plan,
    PlanEntitlement,
    Price,
    ProviderCustomerReference,
    ReconciliationIssue,
    Subscription,
    WebhookEvent,
)


class ReadOnlyBillingAdmin(admin.ModelAdmin):
    """Provider-owned and audit records are inspectable but never edited in admin."""

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.concrete_fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("code", "is_active", "included_athletes", "display_order", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name_en", "name_fa")


@admin.register(PlanEntitlement)
class PlanEntitlementAdmin(admin.ModelAdmin):
    list_display = ("plan", "key", "kind", "enabled", "integer_limit")
    list_filter = ("kind", "enabled")
    search_fields = ("plan__code", "key")


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "plan",
        "provider",
        "currency",
        "unit_amount_minor",
        "interval",
        "is_active",
    )
    list_filter = ("provider", "currency", "interval", "is_active")
    search_fields = ("code", "provider_price_id", "plan__code")


@admin.register(BillingAccount)
class BillingAccountAdmin(admin.ModelAdmin):
    list_display = ("organization", "status", "default_provider", "updated_at")
    list_filter = ("status", "default_provider")
    search_fields = ("organization__name", "organization__slug", "billing_email")


@admin.register(ProviderCustomerReference)
class ProviderCustomerReferenceAdmin(ReadOnlyBillingAdmin):
    list_display = ("billing_account", "provider", "external_customer_id", "created_at")
    list_filter = ("provider",)
    search_fields = ("billing_account__organization__slug", "external_customer_id")


@admin.register(Subscription)
class SubscriptionAdmin(ReadOnlyBillingAdmin):
    list_display = (
        "billing_account",
        "provider",
        "status",
        "plan",
        "current_period_end",
        "last_provider_event_created_at",
    )
    list_filter = ("provider", "status", "cancel_at_period_end")
    search_fields = ("billing_account__organization__slug", "external_subscription_id")


@admin.register(InvoiceSummary)
class InvoiceSummaryAdmin(ReadOnlyBillingAdmin):
    list_display = (
        "billing_account",
        "provider",
        "invoice_number",
        "status",
        "currency",
        "amount_due_minor",
        "issued_at",
    )
    list_filter = ("provider", "status", "currency")
    search_fields = (
        "billing_account__organization__slug",
        "external_invoice_id",
        "invoice_number",
    )


@admin.register(WebhookEvent)
class WebhookEventAdmin(ReadOnlyBillingAdmin):
    list_display = (
        "provider_event_id",
        "provider",
        "event_type",
        "status",
        "attempt_count",
        "error_code",
        "received_at",
    )
    list_filter = ("provider", "status", "event_type")
    search_fields = ("provider_event_id", "request_id")


@admin.register(ReconciliationIssue)
class ReconciliationIssueAdmin(ReadOnlyBillingAdmin):
    list_display = (
        "issue_code",
        "billing_account",
        "provider",
        "status",
        "last_seen_at",
    )
    list_filter = ("provider", "status", "issue_code")
    search_fields = (
        "billing_account__organization__slug",
        "provider_event_id",
        "issue_code",
    )


@admin.register(CheckoutAttempt)
class CheckoutAttemptAdmin(ReadOnlyBillingAdmin):
    list_display = ("billing_account", "kind", "provider", "status", "error_code", "created_at")
    list_filter = ("provider", "kind", "status")
    search_fields = ("billing_account__organization__slug", "external_session_id")


@admin.register(BillingRoleAssignment)
class BillingRoleAssignmentAdmin(ReadOnlyBillingAdmin):
    list_display = ("billing_account", "user", "role", "is_active", "granted_at", "revoked_at")
    list_filter = ("role", "is_active")
    search_fields = ("billing_account__organization__slug", "user__email")


@admin.register(EntitlementSnapshot)
class EntitlementSnapshotAdmin(ReadOnlyBillingAdmin):
    list_display = ("billing_account", "access_state", "effective_until", "evaluated_at", "version")
    list_filter = ("access_state",)
    search_fields = ("billing_account__organization__slug",)


@admin.register(BillingAuditEvent)
class BillingAuditEventAdmin(ReadOnlyBillingAdmin):
    list_display = ("action", "billing_account", "source", "request_id", "created_at")
    list_filter = ("source", "action")
    search_fields = ("billing_account__organization__slug", "target_id", "request_id")


@admin.register(BillingDomainEvent)
class BillingDomainEventAdmin(ReadOnlyBillingAdmin):
    list_display = ("event_type", "billing_account", "status", "created_at", "published_at")
    list_filter = ("event_type", "status")
    search_fields = ("event_key", "billing_account__organization__slug")
