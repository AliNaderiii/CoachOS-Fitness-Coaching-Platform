"""Phase 11 — Copilot API input serializers and run presentation.

Presentation helpers render only persisted (redacted) data. Nothing here
re-reads source tables; source re-authorization happens in the service layer
on every read.
"""

from rest_framework import serializers

from .constants import CAPABILITIES, GENERATION_LANGUAGES, REPORT_TYPES


class RunParametersSerializer(serializers.Serializer):
    period_days = serializers.IntegerField(required=False, min_value=1, max_value=30)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)
    target_assignment_id = serializers.CharField(required=False, allow_blank=True, max_length=64)
    variation = serializers.IntegerField(required=False, min_value=0, max_value=50)

    def to_internal_value(self, data):
        data = {key: value for key, value in (data or {}).items() if key in self.fields}
        return super().to_internal_value(data)


class RunCreateSerializer(serializers.Serializer):
    capability = serializers.ChoiceField(choices=list(CAPABILITIES.keys()))
    athlete_id = serializers.CharField(max_length=64)
    generation_language = serializers.ChoiceField(choices=GENERATION_LANGUAGES)
    parameters = RunParametersSerializer(required=False, default=dict)
    idempotency_key = serializers.CharField(required=False, allow_blank=True, max_length=64)


class EditOutputSerializer(serializers.Serializer):
    payload = serializers.DictField()


class ReviewNoteSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)


class ReportSerializer(serializers.Serializer):
    report_type = serializers.ChoiceField(choices=REPORT_TYPES)
    detail = serializers.CharField(required=False, allow_blank=True, max_length=1000)


# ---------------------------------------------------------------------------
# Presentation
# ---------------------------------------------------------------------------


def _output_payload(run) -> dict | None:
    output = getattr(run, "output", None)
    if output is None:
        return None
    return {
        "id": output.id,
        "schema_name": output.schema_name,
        "schema_version": output.schema_version,
        "validation_status": output.validation_status,
        "status": output.status,
        "payload": output.effective_payload,
        "was_edited": output.edited_payload is not None,
        "reviewed_by_id": str(output.reviewed_by_id) if output.reviewed_by_id else None,
        "reviewed_at": output.reviewed_at.isoformat() if output.reviewed_at else None,
        "review_note": output.review_note,
    }


def run_list_item(run) -> dict:
    return {
        "id": run.id,
        "capability": run.capability,
        "generation_language": run.generation_language,
        "status": run.status,
        "athlete_id": str(run.athlete_user_id),
        "created_at": run.created_at.isoformat(),
        "policy_version": run.policy_version,
        "error_code": run.error_code,
        "fallback_applied": run.fallback_applied,
        "output_status": getattr(getattr(run, "output", None), "status", None),
        "regenerated_from_id": str(run.regenerated_from_id) if run.regenerated_from_id else None,
    }


def run_detail(run, *, actor, roles: set[str]) -> dict:
    sources = [
        {
            "id": source.id,
            "source_type": source.source_type,
            "source_id": source.source_id,
            "descriptor": source.descriptor,
            "ordinal": source.ordinal,
        }
        for source in run.sources.all().order_by("ordinal")
    ]
    context_snapshot = run.context_snapshot or {}
    output = getattr(run, "output", None)
    can_review = (
        run.status == "succeeded"
        and output is not None
        and output.status in ("draft", "edited")
        and (run.actor_user_id == actor.id or "owner" in roles)
    )
    return {
        **run_list_item(run),
        "model_identifier": run.model_identifier,
        "provider_slug": run.provider_slug,
        "prompt_template_id": str(run.prompt_template_id) if run.prompt_template_id else None,
        "policy_version": run.policy_version,
        "attempt_count": run.attempt_count,
        "duration_ms": run.duration_ms,
        "input_tokens_est": run.input_tokens_est,
        "output_tokens_est": run.output_tokens_est,
        "cost_micro_usd": run.cost_micro_usd,
        "input_context_hash": run.input_context_hash,
        "created_at": run.created_at.isoformat(),
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "expires_at": run.expires_at.isoformat() if run.expires_at else None,
        "context": {
            "payload": context_snapshot.get("payload"),
            "limitations": context_snapshot.get("limitations") or [],
            "omissions": context_snapshot.get("omissions") or [],
        }
        if run.context_snapshot
        else None,
        "output": _output_payload(run),
        "sources": sources,
        "actions": {
            "can_cancel": run.status in ("queued", "running"),
            "can_regenerate": run.status in ("succeeded", "failed"),
            "can_edit": can_review,
            "can_approve": can_review,
            "can_reject": can_review,
            "can_report": run.status == "succeeded",
        },
        "ai_generated": True,
        "requires_human_review": True,
    }
