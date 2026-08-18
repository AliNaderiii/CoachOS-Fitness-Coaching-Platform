"""Phase 11 — Copilot REST API.

Thin HTTP layer over :mod:`apps.copilot.services`. Every endpoint:

- requires an authenticated, active user with an active ``owner`` or ``coach``
  membership in the tenant-context organization (never trust the UI);
- checks the feature flag state server-side;
- returns the Phase 04 RFC 7807 envelope via the shared exception handler.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.id_generator import generate_uuid7
from apps.identity.permissions import IsAuthenticatedAndActive
from apps.organizations.models import Organization

from . import policy, serializers, services
from .constants import CAPABILITIES, POLICY_VERSION
from .context import actor_roles
from .exceptions import CopilotFeatureDisabled, CopilotNotAuthorized
from .providers.registry import provider_capabilities


def _professional_actor(request):
    """Resolve tenant org + verify active owner/coach membership.

    Consistent with Phase 06 coach-facing APIs, the organization may be
    addressed explicitly via the ``org_id`` parameter; otherwise the tenant
    middleware context is used. Either way, authorization is decided by
    server-side membership checks, never by the client.
    """
    org_id = request.query_params.get("org_id")
    if not org_id and request.method != "GET":
        try:
            org_id = (request.data or {}).get("org_id")
        except Exception:  # noqa: BLE001 - unparsed body falls back to context
            org_id = None
    if not org_id:
        org_id = getattr(request, "org_id", None)
    organization = None
    if org_id:
        organization = Organization.objects.filter(id=org_id, archived_at__isnull=True).first()
    if organization is None:
        raise CopilotNotAuthorized()
    roles = actor_roles(request.user, organization)
    if not roles.intersection({"owner", "coach"}):
        raise CopilotNotAuthorized()
    return organization, roles


def _require_enabled(request, organization, capability=""):
    enabled, reason = policy.feature_state(organization)
    if not enabled:
        # Denials are durable evidence; record before raising.
        services.record_feature_denial(
            request, organization=organization, capability=capability, reason_code=reason
        )
        raise CopilotFeatureDisabled()


class CopilotCapabilitiesView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        organization, _roles = _professional_actor(request)
        enabled, reason = policy.feature_state(organization)
        capabilities = []
        for slug, meta in CAPABILITIES.items():
            allowed, cap_reason = policy.capability_state(slug)
            capabilities.append(
                {
                    "id": slug,
                    "output_schema": meta["output_schema"],
                    "requires_human_review": meta["requires_human_review"],
                    "enabled": bool(enabled and allowed),
                    "disabled_reason": reason or cap_reason,
                    "label": {"en-US": meta["label_en"], "fa-IR": meta["label_fa"]},
                }
            )
        return Response(
            {
                "feature": {"enabled": enabled, "disabled_reason": reason},
                "policy_version": POLICY_VERSION,
                "provider": provider_capabilities(),
                "capabilities": capabilities,
                "limits": {
                    "rate_limit_per_minute": policy.rate_limit_per_minute(),
                    "daily_run_quota_per_actor": policy.daily_quota_per_actor(),
                    "daily_run_quota_per_org": policy.daily_quota_per_org(),
                    "retention_days": policy.retention_days(),
                },
                "prohibited_notice_key": "copilot.prohibited_notice",
            }
        )


class CopilotRunsView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        organization, roles = _professional_actor(request)
        capability = request.query_params.get("capability") or None
        status_filter = request.query_params.get("status") or None
        runs = services.list_runs(
            organization=organization,
            actor=request.user,
            capability=capability,
            status_filter=status_filter,
        )
        return Response(
            {
                "runs": [serializers.run_list_item(run) for run in runs],
                "count": len(runs),
                "retention_days": policy.retention_days(),
            }
        )

    def post(self, request):
        organization, _roles = _professional_actor(request)
        _require_enabled(
            request, organization, capability=(request.data or {}).get("capability", "")
        )
        serializer = serializers.RunCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        idempotency_key = (
            request.headers.get("Idempotency-Key") or data.get("idempotency_key") or ""
        ).strip()
        if not idempotency_key:
            idempotency_key = generate_uuid7()
        run, replayed = services.request_run(
            request,
            organization=organization,
            actor=request.user,
            capability=data["capability"],
            athlete_id=data["athlete_id"],
            generation_language=data["generation_language"],
            parameters=data.get("parameters") or {},
            idempotency_key=idempotency_key[:64],
        )
        payload = serializers.run_detail(run, actor=request.user, roles=_roles)
        payload["replayed"] = replayed
        response_status = status.HTTP_200_OK if replayed else status.HTTP_201_CREATED
        return Response(payload, status=response_status)


class CopilotRunDetailView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, run_id):
        organization, roles = _professional_actor(request)
        run = services.get_authorized_run(
            organization=organization, actor=request.user, run_id=run_id, request=request
        )
        return Response(serializers.run_detail(run, actor=request.user, roles=roles))


class CopilotRunCancelView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, run_id):
        organization, roles = _professional_actor(request)
        _require_enabled(request, organization)
        run = services.cancel_run(
            request, organization=organization, actor=request.user, run_id=run_id
        )
        return Response(serializers.run_detail(run, actor=request.user, roles=roles))


class CopilotRunRegenerateView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, run_id):
        organization, roles = _professional_actor(request)
        _require_enabled(request, organization)
        run = services.regenerate_run(
            request, organization=organization, actor=request.user, run_id=run_id
        )
        return Response(
            serializers.run_detail(run, actor=request.user, roles=roles),
            status=status.HTTP_201_CREATED,
        )


class CopilotRunReportView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, run_id):
        organization, _roles = _professional_actor(request)
        _require_enabled(request, organization)
        serializer = serializers.ReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run, report = services.report_run(
            request,
            organization=organization,
            actor=request.user,
            run_id=run_id,
            report_type=serializer.validated_data["report_type"],
            detail=serializer.validated_data.get("detail", ""),
        )
        return Response(
            {
                "id": report.id,
                "run_id": run.id,
                "report_type": report.report_type,
                "status": report.status,
                "created_at": report.created_at.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )


class CopilotOutputEditView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def patch(self, request, run_id):
        organization, roles = _professional_actor(request)
        _require_enabled(request, organization)
        serializer = serializers.EditOutputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = services.edit_output(
            request,
            organization=organization,
            actor=request.user,
            run_id=run_id,
            edited_payload=serializer.validated_data["payload"],
        )
        return Response(serializers.run_detail(run, actor=request.user, roles=roles))


class CopilotOutputReviewView(APIView):
    """Approve/reject are honest, separate, audited human actions."""

    permission_classes = [IsAuthenticatedAndActive]
    action = ""

    def post(self, request, run_id):
        organization, roles = _professional_actor(request)
        _require_enabled(request, organization)
        serializer = serializers.ReviewNoteSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        run = services.review_output(
            request,
            organization=organization,
            actor=request.user,
            run_id=run_id,
            action=self.action,
            note=serializer.validated_data.get("note", ""),
        )
        return Response(serializers.run_detail(run, actor=request.user, roles=roles))


class CopilotOutputApproveView(CopilotOutputReviewView):
    action = "approve"


class CopilotOutputRejectView(CopilotOutputReviewView):
    action = "reject"


class CopilotSourceDetailView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, run_id, source_ref_id):
        organization, _roles = _professional_actor(request)
        return Response(
            services.get_source(
                request,
                organization=organization,
                actor=request.user,
                run_id=run_id,
                source_ref_id=source_ref_id,
            )
        )
