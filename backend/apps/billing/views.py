"""Phase 10 organization billing HTTP boundary.

All management authorization starts from an active organization membership.
No browser-supplied payment result, amount, customer reference, status, URL, or
entitlement is accepted.
"""

import logging
from time import perf_counter

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.identity.models import User
from apps.identity.permissions import IsAuthenticatedAndActive
from apps.organizations.models import Membership, Organization

from .entitlements import evaluate_entitlements
from .models import (
    BillingAccount,
    BillingAuditEvent,
    BillingRoleAssignment,
    InvoiceSummary,
    Plan,
    Price,
    ReconciliationIssue,
    Subscription,
)
from .providers import get_provider
from .providers.base import (
    BillingProviderError,
    InvalidWebhookSignature,
    MalformedProviderEvent,
    ProviderUnavailable,
)
from .serializers import (
    BillingAdminInputSerializer,
    BillingRoleAssignmentSerializer,
    CheckoutInputSerializer,
    PlanSerializer,
    PortalInputSerializer,
)
from .services import (
    BillingConfigurationFailure,
    BillingConflict,
    ReconciliationFailure,
    WebhookProcessingFailure,
    create_hosted_session,
    ensure_account,
    ingest_webhook,
    reconcile_subscription_state,
)

logger = logging.getLogger(__name__)


def _problem(request, status_code, title, message_key, detail=None):
    return Response(
        {
            "type": f"https://errors.coachos.io/{message_key.replace('.', '-')}",
            "title": title,
            "status": status_code,
            "detail": detail or title,
            "instance": request.get_full_path(),
            "message_key": message_key,
            "correlation_id": getattr(request, "correlation_id", "-"),
        },
        status=status_code,
    )


def _org(org_id):
    return Organization.objects.filter(id=org_id).first()


def _active_roles(user, organization):
    return set(
        Membership.objects.filter(
            user=user, organization=organization, status="active"
        ).values_list("role", flat=True)
    )


def _billing_access(user, organization, *, owner_only=False):
    roles = _active_roles(user, organization)
    if not roles:
        return False
    if "owner" in roles:
        return True
    if owner_only:
        return False
    account = BillingAccount.objects.filter(organization=organization, status="active").first()
    return bool(
        account
        and BillingRoleAssignment.objects.filter(
            billing_account=account,
            user=user,
            role="billing_admin",
            is_active=True,
            revoked_at__isnull=True,
        ).exists()
    )


def _rate_limited(user, org_id, action, limit=6, window=60):
    key = f"billing-rate:{action}:{user.id}:{org_id}"
    if cache.add(key, 1, timeout=window):
        return False
    try:
        return cache.incr(key) > limit
    except ValueError:
        cache.set(key, 1, timeout=window)
        return False


def _idempotency(request):
    return request.headers.get("Idempotency-Key", "")


def _safe_session_response(attempt):
    return {
        "session_id": attempt.external_session_id,
        "url": attempt.hosted_url,
        "status": attempt.status,
        "message_key": "billing.redirect.provider_hosted",
    }


class PlanListView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        roles = set(
            Membership.objects.filter(user=request.user, status="active").values_list(
                "role", flat=True
            )
        )
        delegated = BillingRoleAssignment.objects.filter(
            user=request.user,
            is_active=True,
            revoked_at__isnull=True,
            billing_account__organization__memberships__user=request.user,
            billing_account__organization__memberships__status="active",
        ).exists()
        if not (roles.intersection({"owner", "coach"}) or delegated):
            return _problem(request, 403, "Permission Denied", "billing.permission_denied")
        plans = (
            Plan.objects.filter(is_active=True, prices__is_active=True)
            .prefetch_related("entitlements", "prices")
            .distinct()
        )
        return Response({"plans": PlanSerializer(plans, many=True).data})


class BillingWorkspaceView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, org_id):
        organization = _org(org_id)
        if organization is None:
            return _problem(request, 404, "Resource Not Found", "billing.organization_not_found")
        if not _billing_access(request.user, organization):
            return _problem(request, 403, "Permission Denied", "billing.permission_denied")
        try:
            account = BillingAccount.objects.get(organization=organization)
        except BillingAccount.DoesNotExist:
            return Response(
                {
                    "organization_id": organization.id,
                    "billing_account": None,
                    "subscription": None,
                    "entitlement": {
                        "access_state": "none",
                        "athlete_access_included": True,
                        "features": {},
                        "limits": {"staff_seats": None, "active_clients": None},
                        "usage": {
                            "staff_seats": Membership.objects.filter(
                                organization=organization,
                                status="active",
                                role__in=["owner", "coach"],
                            )
                            .values("user_id")
                            .distinct()
                            .count(),
                            "active_clients": Membership.objects.filter(
                                organization=organization, status="active", role="athlete"
                            )
                            .values("user_id")
                            .distinct()
                            .count(),
                        },
                        "effective_until": None,
                        "reason": "billing.entitlement.no_subscription",
                    },
                    "invoices": [],
                    "reconciliation_issues": [],
                }
            )
        decision = evaluate_entitlements(account)
        subscription = decision.subscription
        subscription_data = None
        if subscription:
            subscription_data = {
                "id": subscription.id,
                "plan_code": subscription.plan.code,
                "price_id": subscription.price_id,
                "status": subscription.status,
                "quantity": subscription.quantity,
                "current_period_end": subscription.current_period_end,
                "trial_end": subscription.trial_end,
                "grace_period_ends_at": subscription.grace_period_ends_at,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "canceled_at": subscription.canceled_at,
            }
        invoices = InvoiceSummary.objects.filter(billing_account=account)[:20]
        issues = ReconciliationIssue.objects.filter(billing_account=account, status="open")[:10]
        return Response(
            {
                "organization_id": organization.id,
                "billing_account": {"id": account.id, "status": account.status},
                "subscription": subscription_data,
                "entitlement": decision.as_dict(),
                "invoices": [
                    {
                        "id": item.id,
                        "number": item.invoice_number,
                        "status": item.status,
                        "currency": item.currency,
                        "currency_exponent": item.currency_exponent,
                        "amount_due_minor": item.amount_due_minor,
                        "amount_paid_minor": item.amount_paid_minor,
                        "hosted_invoice_url": item.hosted_invoice_url,
                        "receipt_url": item.receipt_url,
                        "issued_at": item.issued_at,
                        "due_at": item.due_at,
                        "paid_at": item.paid_at,
                    }
                    for item in invoices
                ],
                "reconciliation_issues": [
                    {
                        "id": item.id,
                        "issue_code": item.issue_code,
                        "message_key": item.safe_detail_key,
                        "first_seen_at": item.first_seen_at,
                        "last_seen_at": item.last_seen_at,
                    }
                    for item in issues
                ],
            }
        )


class CheckoutSessionView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, org_id):
        organization = _org(org_id)
        if organization is None:
            return _problem(request, 404, "Resource Not Found", "billing.organization_not_found")
        if organization.archived_at or not _billing_access(request.user, organization):
            return _problem(request, 403, "Permission Denied", "billing.permission_denied")
        if _rate_limited(request.user, org_id, "checkout"):
            return _problem(request, 429, "Rate Limit Exceeded", "billing.rate_limited")
        serializer = CheckoutInputSerializer(data=request.data)
        if not serializer.is_valid():
            return _problem(request, 400, "Validation Error", "billing.invalid_checkout_request")
        price = (
            Price.objects.select_related("plan")
            .filter(id=serializer.validated_data["price_id"])
            .first()
        )
        if price is None:
            return _problem(request, 404, "Resource Not Found", "billing.price_not_found")
        try:
            attempt = create_hosted_session(
                organization=organization,
                actor=request.user,
                kind="checkout",
                idempotency_key=_idempotency(request),
                locale=serializer.validated_data["locale"],
                price=price,
            )
        except BillingConflict as exc:
            return _problem(request, 409, "Conflict", f"billing.{exc.args[0]}")
        except (BillingConfigurationFailure, BillingProviderError):
            return _problem(
                request, 503, "Billing Provider Unavailable", "billing.provider_unavailable"
            )
        return Response(_safe_session_response(attempt), status=status.HTTP_201_CREATED)


class PortalSessionView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, org_id):
        organization = _org(org_id)
        if organization is None:
            return _problem(request, 404, "Resource Not Found", "billing.organization_not_found")
        if organization.archived_at or not _billing_access(request.user, organization):
            return _problem(request, 403, "Permission Denied", "billing.permission_denied")
        if _rate_limited(request.user, org_id, "portal"):
            return _problem(request, 429, "Rate Limit Exceeded", "billing.rate_limited")
        serializer = PortalInputSerializer(data=request.data)
        if not serializer.is_valid():
            return _problem(request, 400, "Validation Error", "billing.invalid_portal_request")
        try:
            attempt = create_hosted_session(
                organization=organization,
                actor=request.user,
                kind="portal",
                idempotency_key=_idempotency(request),
                locale=serializer.validated_data["locale"],
            )
        except BillingConflict as exc:
            return _problem(request, 409, "Conflict", f"billing.{exc.args[0]}")
        except (BillingConfigurationFailure, BillingProviderError):
            return _problem(
                request, 503, "Billing Provider Unavailable", "billing.provider_unavailable"
            )
        return Response(_safe_session_response(attempt), status=status.HTTP_201_CREATED)


class BillingAdminListCreateView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, org_id):
        organization = _org(org_id)
        if organization is None:
            return _problem(request, 404, "Resource Not Found", "billing.organization_not_found")
        if not _billing_access(request.user, organization):
            return _problem(request, 403, "Permission Denied", "billing.permission_denied")
        account = BillingAccount.objects.filter(organization=organization).first()
        assignments = (
            BillingRoleAssignment.objects.filter(
                billing_account=account, is_active=True, revoked_at__isnull=True
            ).select_related("user")
            if account
            else BillingRoleAssignment.objects.none()
        )
        return Response(
            {"billing_admins": BillingRoleAssignmentSerializer(assignments, many=True).data}
        )

    @transaction.atomic
    def post(self, request, org_id):
        organization = _org(org_id)
        if organization is None:
            return _problem(request, 404, "Resource Not Found", "billing.organization_not_found")
        if not _billing_access(request.user, organization, owner_only=True):
            return _problem(request, 403, "Permission Denied", "billing.owner_required")
        serializer = BillingAdminInputSerializer(data=request.data)
        if not serializer.is_valid():
            return _problem(request, 400, "Validation Error", "billing.invalid_admin_request")
        user = User.objects.filter(id=serializer.validated_data["user_id"]).first()
        if user is None:
            return _problem(request, 404, "Resource Not Found", "billing.member_not_found")
        roles = _active_roles(user, organization)
        if not roles or roles == {"athlete"}:
            return _problem(request, 409, "Conflict", "billing.admin_requires_staff_membership")
        try:
            account = ensure_account(organization)
        except BillingConfigurationFailure:
            return _problem(
                request, 503, "Billing Provider Unavailable", "billing.provider_unavailable"
            )
        assignment, created = BillingRoleAssignment.objects.get_or_create(
            billing_account=account,
            user=user,
            role="billing_admin",
            defaults={"granted_by": request.user},
        )
        if not created:
            assignment.is_active = True
            assignment.revoked_at = None
            assignment.granted_by = request.user
            assignment.granted_at = timezone.now()
            assignment.save()
        BillingAuditEvent.objects.create(
            billing_account=account,
            actor_user=request.user,
            source="actor",
            action="billing.admin_granted",
            target_type="User",
            target_id=user.id,
        )
        return Response(
            BillingRoleAssignmentSerializer(assignment).data,
            status=status.HTTP_201_CREATED,
        )


class BillingAdminDetailView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    @transaction.atomic
    def delete(self, request, org_id, assignment_id):
        organization = _org(org_id)
        if organization is None:
            return _problem(request, 404, "Resource Not Found", "billing.organization_not_found")
        if not _billing_access(request.user, organization, owner_only=True):
            return _problem(request, 403, "Permission Denied", "billing.owner_required")
        assignment = (
            BillingRoleAssignment.objects.select_related("billing_account")
            .filter(
                id=assignment_id,
                billing_account__organization=organization,
                is_active=True,
                revoked_at__isnull=True,
            )
            .first()
        )
        if assignment is None:
            return _problem(request, 404, "Resource Not Found", "billing.admin_not_found")
        assignment.is_active = False
        assignment.revoked_at = timezone.now()
        assignment.save(update_fields=["is_active", "revoked_at"])
        BillingAuditEvent.objects.create(
            billing_account=assignment.billing_account,
            actor_user=request.user,
            source="actor",
            action="billing.admin_revoked",
            target_type="User",
            target_id=assignment.user_id,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(csrf_exempt, name="dispatch")
class BillingWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, provider):
        started_at = perf_counter()
        signature = request.headers.get("X-Billing-Signature", "")
        request_id = getattr(request, "correlation_id", "")
        try:
            event, duplicate = ingest_webhook(
                provider_name=provider,
                raw_body=request.body,
                signature_header=signature,
                request_id=request_id,
            )
        except (InvalidWebhookSignature, MalformedProviderEvent):
            logger.warning(
                "billing_webhook_rejected provider=%r request_id=%s duration_ms=%.2f",
                provider,
                request_id,
                (perf_counter() - started_at) * 1000,
            )
            return _problem(request, 400, "Invalid Webhook", "billing.webhook_invalid")
        except WebhookProcessingFailure as exc:
            logger.warning(
                "billing_webhook_failed provider=%r error_code=%s request_id=%s duration_ms=%.2f",
                provider,
                exc.code,
                request_id,
                (perf_counter() - started_at) * 1000,
            )
            return _problem(request, 503, "Webhook Processing Failed", "billing.webhook_retry")
        except BillingProviderError as exc:
            logger.warning(
                "billing_provider_unavailable provider=%r error_code=%s request_id=%s duration_ms=%.2f",
                provider,
                exc.code,
                request_id,
                (perf_counter() - started_at) * 1000,
            )
            return _problem(
                request, 503, "Billing Provider Unavailable", "billing.provider_unavailable"
            )
        logger.info(
            "billing_webhook_processed provider=%r event_id=%s status=%s duplicate=%s request_id=%s duration_ms=%.2f",
            provider,
            event.provider_event_id,
            event.status,
            duplicate,
            request_id,
            (perf_counter() - started_at) * 1000,
        )
        return Response(
            {
                "received": True,
                "duplicate": duplicate,
                "event_status": event.status,
            }
        )


class ReconcileView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, org_id):
        organization = _org(org_id)
        if organization is None:
            return _problem(request, 404, "Resource Not Found", "billing.organization_not_found")
        if not _billing_access(request.user, organization):
            return _problem(request, 403, "Permission Denied", "billing.permission_denied")
        if _rate_limited(request.user, org_id, "reconcile", limit=3):
            return _problem(request, 429, "Rate Limit Exceeded", "billing.rate_limited")
        account = BillingAccount.objects.filter(organization=organization).first()
        subscription = (
            Subscription.objects.filter(billing_account=account)
            .order_by("-last_provider_event_created_at")
            .first()
            if account
            else None
        )
        if not account or not subscription:
            return _problem(request, 409, "Conflict", "billing.no_subscription_to_reconcile")
        try:
            provider = get_provider(subscription.provider)
            retrieved = provider.retrieve_subscription(
                subscription_ref=subscription.external_subscription_id
            )
            outcome = reconcile_subscription_state(
                account=account,
                subscription=subscription,
                retrieved=retrieved,
                actor=request.user,
                request_id=getattr(request, "correlation_id", ""),
            )
        except ProviderUnavailable:
            ReconciliationIssue.objects.create(
                billing_account=account,
                provider=subscription.provider,
                issue_code="provider_unavailable",
                safe_detail_key="billing.reconciliation.provider_unavailable",
            )
            return _problem(
                request, 503, "Billing Provider Unavailable", "billing.provider_unavailable"
            )
        except BillingProviderError:
            ReconciliationIssue.objects.create(
                billing_account=account,
                provider=subscription.provider,
                issue_code="provider_error",
                safe_detail_key="billing.reconciliation.provider_error",
            )
            return _problem(
                request, 503, "Billing Provider Unavailable", "billing.provider_unavailable"
            )
        except ReconciliationFailure as exc:
            logger.warning(
                "billing_reconciliation_failed provider=%r error_code=%s request_id=%s",
                subscription.provider,
                exc.code,
                getattr(request, "correlation_id", ""),
            )
            return _problem(
                request, 409, "Reconciliation Conflict", "billing.reconciliation_conflict"
            )
        logger.info(
            "billing_reconciliation_completed provider=%r subscription_id=%s outcome=%s request_id=%s",
            subscription.provider,
            subscription.id,
            outcome,
            getattr(request, "correlation_id", ""),
        )
        return Response({"status": outcome, "message_key": "billing.reconciliation.completed"})
