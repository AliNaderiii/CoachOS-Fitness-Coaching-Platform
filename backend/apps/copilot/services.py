"""Phase 11 — Copilot run lifecycle orchestration.

Guarantees:

- policy gates before retrieval and before provider calls;
- idempotent run creation per (organization, actor, idempotency_key);
- bounded attempts (max 1 retry, transient errors only);
- measured timeout around the provider call;
- strict output validation (schema + anti-hallucination citations);
- database-enforced daily quotas and org cost caps before provider calls;
- every outcome emits :class:`AIPolicyDecision` and :class:`AIAuditEvent`
  records with safe metadata (no user free text);
- fail closed with explicit fallback on provider/validation failure.
"""

import datetime
import hashlib
import json
import time

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.core.utils.id_generator import generate_uuid7

from . import policy
from .bootstrap import seed_defaults
from .constants import (
    CAPABILITIES,
    POLICY_VERSION,
    REASON_BUDGET_EXHAUSTED,
    REASON_CONTEXT_TOO_LARGE,
    REASON_NOT_AUTHORIZED,
    REASON_OUTPUT_INVALID,
    REASON_PROVIDER_UNAVAILABLE,
    REASON_QUOTA_EXHAUSTED,
    REASON_RATE_LIMITED,
)
from .context import SubjectNotAuthorized, actor_roles, build_context
from .exceptions import (
    CopilotBadRequest,
    CopilotConflict,
    CopilotFeatureDisabled,
    CopilotGone,
    CopilotNotAuthorized,
    CopilotProhibitedUse,
    CopilotThrottled,
)
from .models import (
    AIAuditEvent,
    AIOutput,
    AIPolicyDecision,
    AIRun,
    AISourceReference,
    AIUsageMeter,
    PromptTemplateVersion,
)
from .providers.base import (
    ProviderError,
    ProviderRequest,
    ProviderTimeout,
    ProviderUnavailable,
)
from .providers.registry import resolve_provider
from .schemas import validate_output

# ---------------------------------------------------------------------------
# Recording helpers
# ---------------------------------------------------------------------------


def _record_decision(*, organization, actor, capability, stage, decision, reason_code="", run=None):
    AIPolicyDecision.objects.create(
        organization=organization,
        actor_user=actor,
        run=run,
        capability=capability or "",
        stage=stage,
        decision=decision,
        reason_code=reason_code,
    )


def _audit(
    request=None,
    *,
    organization=None,
    actor=None,
    action,
    run=None,
    metadata=None,
    target_type="",
    target_id="",
):
    AIAuditEvent.objects.create(
        actor_user=actor or (request.user if request is not None else None),
        organization=organization,
        action=action,
        target_entity_type=target_type or ("AIRun" if run is not None else ""),
        target_entity_id=target_id or (run.id if run is not None else ""),
        metadata=metadata or {},
        request_id=getattr(request, "correlation_id", "") if request is not None else "",
    )


# ---------------------------------------------------------------------------
# Gate checks (raise safe DRF exceptions; record decisions/audits)
# ---------------------------------------------------------------------------


def _gate_feature_and_capability(*, organization, actor, capability):
    enabled, reason = policy.feature_state(organization)
    if not enabled:
        _record_decision(
            organization=organization,
            actor=actor,
            capability=capability,
            stage="request",
            decision="deny",
            reason_code=reason,
        )
        _audit(
            organization=organization,
            actor=actor,
            action="ai.run.denied",
            metadata={"reason_code": reason, "capability": capability},
        )
        raise CopilotFeatureDisabled()
    ok, reason = policy.capability_state(capability)
    if not ok:
        _record_decision(
            organization=organization,
            actor=actor,
            capability=capability,
            stage="request",
            decision="deny",
            reason_code=reason,
        )
        _audit(
            organization=organization,
            actor=actor,
            action="ai.run.denied",
            metadata={"reason_code": reason, "capability": capability},
        )
        raise CopilotBadRequest(message_key="error.ai_capability_unknown")


def _gate_parameters(*, organization, actor, capability, parameters):
    for key in ("notes", "target_assignment_id"):
        allowed, reason = policy.screen_free_text(parameters.get(key))
        if not allowed:
            _record_decision(
                organization=organization,
                actor=actor,
                capability=capability,
                stage="request",
                decision="deny",
                reason_code=reason,
            )
            _audit(
                organization=organization,
                actor=actor,
                action="ai.run.denied",
                metadata={"reason_code": reason, "capability": capability},
            )
            raise CopilotProhibitedUse()


def _gate_rate_limit(*, organization, actor, capability):
    if policy.rate_limit_hit(str(actor.id)):
        _record_decision(
            organization=organization,
            actor=actor,
            capability=capability,
            stage="request",
            decision="deny",
            reason_code=REASON_RATE_LIMITED,
        )
        _audit(
            organization=organization,
            actor=actor,
            action="ai.run.denied",
            metadata={"reason_code": REASON_RATE_LIMITED, "capability": capability},
        )
        raise CopilotThrottled(message_key="error.rate_limit_exceeded")


def _meter_row(organization, actor, today):
    row, _ = AIUsageMeter.objects.select_for_update().get_or_create(
        organization=organization, actor_user=actor, date=today
    )
    return row


def _gate_quota_and_budget(*, organization, actor, capability, today):
    row = _meter_row(organization, actor, today)
    if row.run_count >= policy.daily_quota_per_actor():
        _deny_quota(organization, actor, capability, REASON_QUOTA_EXHAUSTED)
    org_count = AIUsageMeter.objects.filter(organization=organization, date=today).values_list(
        "run_count", flat=True
    )
    if sum(org_count) >= policy.daily_quota_per_org():
        _deny_quota(organization, actor, capability, REASON_QUOTA_EXHAUSTED)
    org_cost = AIUsageMeter.objects.filter(organization=organization, date=today).values_list(
        "cost_micro_usd", flat=True
    )
    if sum(org_cost) >= policy.daily_cost_cap_micro_usd():
        _deny_quota(organization, actor, capability, REASON_BUDGET_EXHAUSTED)


def _deny_quota(organization, actor, capability, reason):
    _record_decision(
        organization=organization,
        actor=actor,
        capability=capability,
        stage="request",
        decision="deny",
        reason_code=reason,
    )
    _audit(
        organization=organization,
        actor=actor,
        action="ai.run.denied",
        metadata={"reason_code": reason, "capability": capability},
    )
    raise CopilotThrottled(message_key="error.ai_quota_exceeded")


# ---------------------------------------------------------------------------
# Run creation + execution
# ---------------------------------------------------------------------------


def record_feature_denial(request, *, organization, capability: str, reason_code: str) -> None:
    """Durable record for feature-flag/kill-switch denials raised by views."""
    _record_decision(
        organization=organization,
        actor=request.user,
        capability=capability,
        stage="request",
        decision="deny",
        reason_code=reason_code,
    )
    _audit(
        request,
        organization=organization,
        action="ai.run.denied",
        metadata={"reason_code": reason_code, "capability": capability},
    )


def request_run(
    request,
    *,
    organization,
    actor,
    capability: str,
    athlete_id: str,
    generation_language: str,
    parameters: dict,
    idempotency_key: str,
) -> tuple[AIRun, bool]:
    """Validate gates, then create (or replay) and execute a run.

    Returns ``(run, replayed)``. Raises safe DRF exceptions for denials.
    """
    seed_defaults()  # idempotent defaults (provider config + v1 templates)

    _gate_feature_and_capability(organization=organization, actor=actor, capability=capability)
    _gate_parameters(
        organization=organization, actor=actor, capability=capability, parameters=parameters
    )
    _gate_rate_limit(organization=organization, actor=actor, capability=capability)

    # Idempotent replay: an existing run with the same key returns unchanged.
    existing = AIRun.objects.filter(
        organization=organization, actor_user=actor, idempotency_key=idempotency_key
    ).first()
    if existing is not None:
        return existing, True

    roles = actor_roles(actor, organization)

    # Subject authorization pre-check (server-side, before any retrieval and
    # before a run row exists). Mid-run revocation is caught again defensively
    # by the context builder inside execution.
    subject_ok = _subject_still_authorized(
        organization=organization, actor=actor, athlete_id=athlete_id, roles=roles
    )
    if not subject_ok:
        _record_decision(
            organization=organization,
            actor=actor,
            capability=capability,
            stage="pre_context",
            decision="deny",
            reason_code=REASON_NOT_AUTHORIZED,
        )
        _audit(
            request,
            organization=organization,
            action="ai.run.denied",
            metadata={"reason_code": REASON_NOT_AUTHORIZED, "capability": capability},
        )
        from apps.identity.models import User

        subject_exists = (
            User.objects.filter(id=athlete_id, is_active=True)
            .filter(
                memberships__organization=organization,
                memberships__role="athlete",
                memberships__status="active",
            )
            .exists()
        )
        if not subject_exists:
            from rest_framework.exceptions import NotFound

            raise NotFound()
        raise CopilotNotAuthorized()

    today = timezone.now().date()
    # Quota/budget gate runs outside the creation transaction so durable denial
    # records survive; the known race window (concurrent requests passing the
    # gate simultaneously) is documented as residual risk — hard consistency
    # arrives with the async queue budget lock (see report §Deferred work).
    _gate_quota_and_budget(
        organization=organization, actor=actor, capability=capability, today=today
    )
    with transaction.atomic():
        run = AIRun(
            organization=organization,
            actor_user=actor,
            athlete_user_id=athlete_id,
            capability=capability,
            generation_language=generation_language,
            status="queued",
            idempotency_key=idempotency_key,
            policy_version=POLICY_VERSION,
            max_attempts=policy.max_attempts(),
            parameters_hash=hashlib.sha256(
                json.dumps(parameters, sort_keys=True, default=str).encode("utf-8")
            ).hexdigest(),
            expires_at=timezone.now() + datetime.timedelta(days=policy.retention_days()),
        )
        try:
            run.save()
        except IntegrityError:
            run = AIRun.objects.get(
                organization=organization,
                actor_user=actor,
                idempotency_key=idempotency_key,
            )
            return run, True
        # Pre-provider authorization decision is recorded before any retrieval.
        try:
            context = build_context(
                capability=capability,
                organization=organization,
                actor=actor,
                athlete_user_id=athlete_id,
                actor_roles_set=roles,
                parameters=parameters,
                generation_language=generation_language,
            )
        except SubjectNotAuthorized:
            _record_decision(
                organization=organization,
                actor=actor,
                capability=capability,
                stage="pre_context",
                decision="deny",
                reason_code=REASON_NOT_AUTHORIZED,
                run=run,
            )
            run.status = "failed"
            run.error_code = REASON_NOT_AUTHORIZED
            run.fallback_applied = True
            run.completed_at = timezone.now()
            run.save(update_fields=["status", "error_code", "fallback_applied", "completed_at"])
            _audit(
                request,
                organization=organization,
                action="ai.run.denied",
                run=run,
                metadata={"reason_code": REASON_NOT_AUTHORIZED},
            )
            raise CopilotNotAuthorized() from None

        _record_decision(
            organization=organization,
            actor=actor,
            capability=capability,
            stage="pre_context",
            decision="allow",
            run=run,
        )
        _audit(
            request,
            organization=organization,
            action="ai.run.requested",
            run=run,
            metadata={"capability": capability, "language": generation_language},
        )
        _execute_run(request, run=run, context=context, organization=organization, actor=actor)
        return run, False


def _execute_run(request, *, run: AIRun, context, organization, actor) -> None:
    """Attempt the provider call (bounded retry), validate, persist output."""
    run.status = "running"
    run.started_at = timezone.now()
    run.save(update_fields=["status", "started_at"])

    capability = run.capability
    language = run.generation_language

    try:
        resolved = resolve_provider()
    except ProviderUnavailable:
        _finalize_failure(
            request,
            run=run,
            organization=organization,
            error_code=REASON_PROVIDER_UNAVAILABLE,
        )
        return
    config = resolved.config
    run.provider_slug = config.slug

    template = (
        PromptTemplateVersion.objects.filter(capability=capability, locale=language, is_active=True)
        .order_by("-version")
        .first()
    ) or (
        PromptTemplateVersion.objects.filter(capability=capability, locale="en-US", is_active=True)
        .order_by("-version")
        .first()
    )
    run.prompt_template = template

    # Context size cap (fail closed; snapshot stays redacted either way).
    context_json = json.dumps(context.payload, ensure_ascii=False, sort_keys=True)
    if len(context_json) > config.max_context_chars:
        run.prompt_template = template
        run.provider_slug = config.slug
        _finalize_failure(
            request, run=run, organization=organization, error_code=REASON_CONTEXT_TOO_LARGE
        )
        return

    run.context_snapshot = {
        "capability": capability,
        "period_days": context.period_days,
        "payload": context.payload,
        "limitations": context.limitations,
        "omissions": context.omissions,
    }
    run.input_context_hash = hashlib.sha256(context_json.encode("utf-8")).hexdigest()

    system_directive = template.system_directive if template else ""
    schema_name = CAPABILITIES[capability]["output_schema"]

    response = None
    failure_code = ""
    attempts = max(1, run.max_attempts)
    start_monotonic = time.monotonic()
    for attempt in range(1, attempts + 1):
        run.attempt_count = attempt
        try:
            response = resolved.provider.generate(
                ProviderRequest(
                    capability=capability,
                    generation_language=language,
                    system_directive=system_directive,
                    context_payload=context.payload,
                    output_schema=schema_name,
                    max_output_tokens=config.max_output_tokens,
                )
            )
            elapsed_ms = int((time.monotonic() - start_monotonic) * 1000)
            if elapsed_ms > config.timeout_ms:
                raise ProviderTimeout("measured timeout exceeded")
            failure_code = ""
            break
        except (ProviderUnavailable, ProviderTimeout) as exc:
            failure_code = exc.code
            response = None
            continue
        except ProviderError as exc:
            failure_code = exc.code
            response = None
            break  # non-transient: no retry
        except Exception:  # noqa: BLE001 - adapter blew up unexpectedly; fail closed
            failure_code = REASON_PROVIDER_UNAVAILABLE
            response = None
            break

    run.duration_ms = int((time.monotonic() - start_monotonic) * 1000)

    if response is None:
        run.save(
            update_fields=[
                "prompt_template",
                "provider_slug",
                "context_snapshot",
                "input_context_hash",
                "attempt_count",
                "duration_ms",
            ]
        )
        _finalize_failure(
            request,
            run=run,
            organization=organization,
            error_code=failure_code or REASON_PROVIDER_UNAVAILABLE,
        )
        return

    run.model_identifier = response.model_identifier
    run.provider_request_id = response.provider_request_id[:120]
    run.input_tokens_est = response.input_tokens_est
    run.output_tokens_est = response.output_tokens_est
    run.cost_micro_usd = response.cost_micro_usd

    validation_errors = validate_output(
        capability,
        response.payload,
        allowed_source_ids=context.source_ids,
        allowed_exercise_ids=set(context.exercise_allowlist_ids),
    )

    output = AIOutput(
        run=run,
        schema_name=schema_name,
        validation_status="valid" if not validation_errors else "invalid",
        validation_errors=validation_errors,
    )
    if validation_errors:
        # Quarantined: invalid output is never persisted as usable content.
        output.payload = None
        output.status = "quarantined"
        output.save()
        run.schema_valid = False
        run.save(
            update_fields=[
                "prompt_template",
                "provider_slug",
                "model_identifier",
                "provider_request_id",
                "context_snapshot",
                "input_context_hash",
                "attempt_count",
                "duration_ms",
                "input_tokens_est",
                "output_tokens_est",
                "cost_micro_usd",
                "schema_valid",
            ]
        )
        _meter_usage(run)
        _finalize_failure(
            request, run=run, organization=organization, error_code=REASON_OUTPUT_INVALID
        )
        return

    output.payload = response.payload
    output.status = "draft"
    output.save()

    for source in context.sources:
        AISourceReference.objects.create(
            run=run,
            source_type=source["source_type"],
            source_id=source["source_id"],
            descriptor=source["descriptor"][:240],
            ordinal=source.get("source_ordinal", 1),
        )

    run.status = "succeeded"
    run.schema_valid = True
    run.completed_at = timezone.now()
    run.save(
        update_fields=[
            "prompt_template",
            "provider_slug",
            "model_identifier",
            "provider_request_id",
            "context_snapshot",
            "input_context_hash",
            "attempt_count",
            "duration_ms",
            "input_tokens_est",
            "output_tokens_est",
            "cost_micro_usd",
            "schema_valid",
            "status",
            "completed_at",
        ]
    )
    _meter_usage(run)
    _record_decision(
        organization=organization,
        actor=actor,
        capability=capability,
        stage="post_output",
        decision="allow",
        run=run,
    )
    _audit(
        request,
        organization=organization,
        action="ai.run.completed",
        run=run,
        metadata={
            "capability": capability,
            "duration_ms": run.duration_ms,
            "attempts": run.attempt_count,
            "output_tokens_est": run.output_tokens_est,
            "cost_micro_usd": run.cost_micro_usd,
        },
    )


def _finalize_failure(request, *, run: AIRun, organization, error_code: str) -> None:
    run.status = "failed"
    run.error_code = error_code
    run.fallback_applied = True
    run.completed_at = timezone.now()
    run.save(update_fields=["status", "error_code", "fallback_applied", "completed_at"])
    _record_decision(
        organization=organization,
        actor=run.actor_user,
        capability=run.capability,
        stage="post_output",
        decision="deny",
        reason_code=error_code,
        run=run,
    )
    _audit(
        request,
        organization=organization,
        action="ai.run.failed",
        run=run,
        metadata={"error_code": error_code, "attempts": run.attempt_count},
    )


def _meter_usage(run: AIRun) -> None:
    from django.db.models import F

    today = timezone.now().date()
    row = _meter_row(run.organization, run.actor_user, today)
    AIUsageMeter.objects.filter(pk=row.pk).update(
        run_count=F("run_count") + 1,
        input_tokens_est=F("input_tokens_est") + run.input_tokens_est,
        output_tokens_est=F("output_tokens_est") + run.output_tokens_est,
        cost_micro_usd=F("cost_micro_usd") + run.cost_micro_usd,
    )


# ---------------------------------------------------------------------------
# State-changing review actions
# ---------------------------------------------------------------------------


def get_authorized_run(*, organization, actor, run_id, request=None) -> AIRun:
    """Fetch a run and re-authorize the actor at read time.

    Stale-after-revocation: a run whose actor lost the assignment (or whose
    membership was suspended) is no longer readable. Owners may read any run
    in their org; coaches only their own.
    """
    run = AIRun.objects.filter(id=run_id, organization=organization).first()
    if run is None:
        from rest_framework.exceptions import NotFound

        raise NotFound()
    roles = actor_roles(actor, organization)
    if "owner" not in roles and run.actor_user_id != actor.id:
        raise CopilotNotAuthorized()
    # Re-check the actor's current scope over the subject athlete
    # (stale-after-revocation reads fail closed).
    athlete_ok = _subject_still_authorized(
        organization=organization, actor=actor, athlete_id=run.athlete_user_id, roles=roles
    )
    if not athlete_ok:
        raise CopilotNotAuthorized()
    if run.status == "expired":
        raise CopilotGone()
    if request is not None:
        _audit(request, organization=organization, action="ai.output.viewed", run=run)
    return run


def _subject_still_authorized(*, organization, actor, athlete_id, roles) -> bool:
    from apps.identity.models import User

    athlete = User.objects.filter(id=athlete_id, is_active=True).first()
    if athlete is None:
        return False
    from apps.organizations.models import Membership

    active_athlete = Membership.objects.filter(
        user=athlete, organization=organization, role="athlete", status="active"
    ).exists()
    if not active_athlete:
        return False
    if "owner" in roles:
        return True
    if "coach" not in roles:
        return False
    from apps.programs.models import CoachAthleteAssignment

    return CoachAthleteAssignment.objects.filter(
        organization=organization,
        coach_user=actor,
        athlete_user=athlete,
        is_active=True,
    ).exists()


def cancel_run(request, *, organization, actor, run_id) -> AIRun:
    run = get_authorized_run(organization=organization, actor=actor, run_id=run_id)
    if run.status not in ("queued", "running"):
        raise CopilotConflict()
    run.status = "cancelled"
    run.cancelled_by = actor
    run.save(update_fields=["status", "cancelled_by"])
    _audit(request, organization=organization, action="ai.run.cancelled", run=run)
    return run


def regenerate_run(request, *, organization, actor, run_id) -> AIRun:
    source_run = get_authorized_run(organization=organization, actor=actor, run_id=run_id)
    if source_run.status not in ("succeeded", "failed"):
        raise CopilotConflict()
    output = getattr(source_run, "output", None)
    if output is not None and output.status in ("approved",):
        raise CopilotConflict()
    prior = AIRun.objects.filter(regenerated_from=source_run).count()
    new_key = f"regen:{source_run.id}:{prior + 1}:{generate_uuid7()[:8]}"
    parameters = {"variation": prior + 1}
    run, _ = request_run(
        request,
        organization=organization,
        actor=actor,
        capability=source_run.capability,
        athlete_id=source_run.athlete_user_id,
        generation_language=source_run.generation_language,
        parameters=parameters,
        idempotency_key=new_key,
    )
    run.regenerated_from = source_run
    run.save(update_fields=["regenerated_from"])
    _audit(
        request,
        organization=organization,
        action="ai.run.regenerated",
        run=run,
        metadata={"source_run_id": source_run.id},
    )
    return run


def edit_output(request, *, organization, actor, run_id, edited_payload) -> AIRun:
    run = get_authorized_run(organization=organization, actor=actor, run_id=run_id)
    output = getattr(run, "output", None)
    if run.status != "succeeded" or output is None or output.status not in ("draft", "edited"):
        raise CopilotConflict()
    allowed_sources = set(run.sources.values_list("source_id", flat=True))
    allowed_exercises = _current_exercise_allowlist(organization)
    errors = validate_output(
        run.capability,
        edited_payload,
        allowed_source_ids=allowed_sources,
        allowed_exercise_ids=allowed_exercises,
    )
    if errors:
        raise CopilotBadRequest(message_key="error.ai_output_invalid")
    output.edited_payload = edited_payload
    output.status = "edited"
    output.save(update_fields=["edited_payload", "status", "updated_at"])
    _audit(request, organization=organization, action="ai.output.edited", run=run)
    return run


def review_output(request, *, organization, actor, run_id, action: str, note: str = "") -> AIRun:
    run = get_authorized_run(organization=organization, actor=actor, run_id=run_id)
    output = getattr(run, "output", None)
    if run.status != "succeeded" or output is None:
        raise CopilotConflict()
    if output.status not in ("draft", "edited"):
        raise CopilotConflict()
    if action == "approve":
        output.status = "approved"
        audit_action = "ai.output.approved"
    elif action == "reject":
        output.status = "rejected"
        audit_action = "ai.output.rejected"
    else:  # pragma: no cover - guarded by view validation
        raise CopilotBadRequest()
    output.reviewed_by = actor
    output.reviewed_at = timezone.now()
    output.review_note = (note or "")[:500]
    output.save(update_fields=["status", "reviewed_by", "reviewed_at", "review_note", "updated_at"])
    _audit(request, organization=organization, action=audit_action, run=run)
    return run


def report_run(request, *, organization, actor, run_id, report_type: str, detail: str = ""):
    from .models import AIFeedback

    run = get_authorized_run(organization=organization, actor=actor, run_id=run_id)
    report = AIFeedback.objects.create(
        run=run, reporter_user=actor, report_type=report_type, detail=(detail or "")[:1000]
    )
    _audit(
        request,
        organization=organization,
        action="ai.output.reported",
        run=run,
        metadata={"report_type": report_type},
    )
    return run, report


def get_source(request, *, organization, actor, run_id, source_ref_id) -> dict:
    """Re-authorized read of one provenance record (source references are
    re-authorized when opened)."""
    run = get_authorized_run(organization=organization, actor=actor, run_id=run_id)
    source = AISourceReference.objects.filter(id=source_ref_id, run=run).first()
    if source is None:
        from rest_framework.exceptions import NotFound

        raise NotFound()
    _audit(
        request,
        organization=organization,
        action="ai.source.opened",
        run=run,
        metadata={"source_type": source.source_type},
    )
    return {
        "id": source.id,
        "run_id": run.id,
        "source_type": source.source_type,
        "source_id": source.source_id,
        "descriptor": source.descriptor,
        "ordinal": source.ordinal,
        "record_url": _record_url_for(source),
    }


def _record_url_for(source) -> str:
    """Safe in-app deep link shape for the UI (no data payload)."""
    base = source.source_id.split(":", 1)[-1]
    if source.source_type == "workout_session":
        return f"/api/v1/workout-sessions/{base}"
    if source.source_type == "program_assignment":
        return f"/api/v1/program-assignments?assignment_id={base}"
    if source.source_type == "exercise":
        return f"/api/v1/exercises/{base}"
    return ""


def _current_exercise_allowlist(organization) -> set[str]:
    from apps.exercises.models import Exercise

    from .context import models_q_organization

    return {
        str(pk)
        for pk in Exercise.objects.filter(status="published")
        .filter(models_q_organization(organization))
        .values_list("id", flat=True)[:200]
    }


def list_runs(*, organization, actor, capability=None, status_filter=None):
    """Coach: own runs only. Owner: all org runs. Bounded to 50 newest."""
    roles = actor_roles(actor, organization)
    qs = AIRun.objects.filter(organization=organization)
    if "owner" not in roles:
        qs = qs.filter(actor_user=actor)
    if capability:
        qs = qs.filter(capability=capability)
    if status_filter:
        qs = qs.filter(status=status_filter)
    return qs.order_by("-created_at")[:50]


def purge_expired_runs(now=None) -> int:
    """Retention policy: clear redacted context + unapproved payloads of
    expired runs; mark runs expired. Approved/rejected drafts keep their final
    structured payload (decision record) but lose the context snapshot.
    """
    now = now or timezone.now()
    runs = AIRun.objects.filter(
        expires_at__lte=now, status__in=("succeeded", "failed", "cancelled")
    ).exclude(context_snapshot__isnull=True, status="expired")
    count = 0
    for run in runs:
        run.context_snapshot = None
        run.status = "expired"
        run.save(update_fields=["context_snapshot", "status"])
        output = getattr(run, "output", None)
        if output is not None and output.status not in ("approved", "rejected"):
            output.payload = None
            output.edited_payload = None
            output.status = "expired"
            output.save(update_fields=["payload", "edited_payload", "status", "updated_at"])
        AIAuditEvent.objects.create(
            actor_user=None,
            organization=run.organization,
            action="ai.purge.executed",
            target_entity_type="AIRun",
            target_entity_id=run.id,
            metadata={"policy": "context_retention"},
        )
        count += 1
    return count
