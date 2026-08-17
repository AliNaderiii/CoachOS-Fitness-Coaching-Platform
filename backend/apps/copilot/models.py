"""Phase 11 — Governed AI Copilot models.

Tier 8 (AI inference records) persistence:

- Raw provider request/response strings are NEVER stored. Only the redacted,
  truncated context snapshot actually used (coach-inspectable) and the
  schema-validated structured draft are persisted.
- Retention: ``AIRun.expires_at`` bounds context/output retention;
  ``apps.copilot.services.purge_expired_runs`` clears sensitive payloads.
- ``AIAuditEvent`` is append-only and immutable at ORM level (mirrors the
  Phase 05 ``AuditEvent`` contract; kept separate so sibling domains stay
  untouched in this branch).
- ``AIProviderAdapterConfig`` stores non-secret provider metadata only. API
  keys/credentials are prohibited here and arrive (if ever) via server-side
  environment injection only.
"""

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.utils.id_generator import generate_uuid7
from apps.identity.models import User
from apps.organizations.models import Organization

from .constants import (
    CAPABILITIES,
    GENERATION_LANGUAGES,
    OUTPUT_STATUS_CHOICES,
    REPORT_TYPES,
    RUN_STATUS_CHOICES,
)


def _uuid7():
    return generate_uuid7()


class AIProviderAdapterConfig(models.Model):
    """Non-secret provider adapter metadata. Secrets are strictly prohibited."""

    id = models.CharField(primary_key=True, max_length=36, default=_uuid7, editable=False)
    slug = models.SlugField(max_length=64, unique=True, db_index=True)
    provider_kind = models.CharField(
        max_length=32,
        choices=[("fake", "Deterministic fake (dev/CI)"), ("http", "HTTP provider (declarative)")],
        default="fake",
    )
    display_name = models.CharField(max_length=120)
    model_identifier = models.CharField(max_length=120, blank=True, default="")
    is_enabled = models.BooleanField(default=True)
    timeout_ms = models.PositiveIntegerField(default=8000)
    max_context_chars = models.PositiveIntegerField(default=12000)
    max_output_tokens = models.PositiveIntegerField(default=1200)
    cost_per_1k_input_micro_usd = models.PositiveIntegerField(default=0)
    cost_per_1k_output_micro_usd = models.PositiveIntegerField(default=0)
    retention_note = models.CharField(
        max_length=240,
        blank=True,
        default="",
        help_text="Declared, unverified provider retention assumption (no zero-retention claim).",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI provider adapter config"
        verbose_name_plural = "AI provider adapter configs"

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.slug} ({'enabled' if self.is_enabled else 'disabled'})"


class PromptTemplateVersion(models.Model):
    """Versioned, vetted prompt template (system directive + schema pointer).

    Template text is platform-authored vetted content (not user data), so it is
    safe to persist; it is never derived from runs.
    """

    id = models.CharField(primary_key=True, max_length=36, default=_uuid7, editable=False)
    capability = models.CharField(max_length=64, choices=[(k, k) for k in sorted(CAPABILITIES)])
    version = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    locale = models.CharField(
        max_length=10,
        choices=[(lng, lng) for lng in GENERATION_LANGUAGES],
    )
    template_sha256 = models.CharField(max_length=64)
    system_directive = models.TextField()
    output_schema = models.CharField(max_length=64)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "prompt template version"
        verbose_name_plural = "prompt template versions"
        constraints = [
            models.UniqueConstraint(
                fields=["capability", "version", "locale"], name="unique_template_version"
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"{self.capability} v{self.version} ({self.locale})"


class AIRun(models.Model):
    """Auditable AI run record. Stores no raw prompts/completions."""

    id = models.CharField(primary_key=True, max_length=36, default=_uuid7, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.PROTECT, related_name="ai_runs", db_index=True
    )
    actor_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="ai_runs", db_index=True
    )
    athlete_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="ai_subject_runs", db_index=True
    )
    capability = models.CharField(max_length=64, choices=[(k, k) for k in sorted(CAPABILITIES)])
    generation_language = models.CharField(
        max_length=10, choices=[(lng, lng) for lng in GENERATION_LANGUAGES]
    )
    status = models.CharField(max_length=20, choices=[(s, s) for s in RUN_STATUS_CHOICES])
    idempotency_key = models.CharField(max_length=64, db_index=True)

    policy_version = models.CharField(max_length=40)
    prompt_template = models.ForeignKey(
        PromptTemplateVersion,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="runs",
    )
    provider_slug = models.CharField(max_length=64, blank=True, default="")
    model_identifier = models.CharField(max_length=120, blank=True, default="")
    provider_request_id = models.CharField(max_length=120, blank=True, default="")

    # Redacted, truncated, coach-inspectable context actually sent to the adapter.
    context_snapshot = models.JSONField(null=True, blank=True)
    input_context_hash = models.CharField(max_length=64, blank=True, default="")
    parameters_hash = models.CharField(max_length=64, blank=True, default="")

    attempt_count = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=2)
    duration_ms = models.PositiveIntegerField(default=0)
    input_tokens_est = models.PositiveIntegerField(default=0)
    output_tokens_est = models.PositiveIntegerField(default=0)
    cost_micro_usd = models.PositiveIntegerField(default=0)

    error_code = models.CharField(max_length=64, blank=True, default="")
    fallback_applied = models.BooleanField(default=False)
    schema_valid = models.BooleanField(default=False)

    regenerated_from = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="regenerations"
    )
    cancelled_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    cancellation_reason = models.CharField(max_length=240, blank=True, default="")

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = "AI run"
        verbose_name_plural = "AI runs"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "actor_user", "idempotency_key"],
                name="unique_ai_run_idempotency",
            )
        ]
        indexes = [
            models.Index(fields=["organization", "actor_user", "created_at"]),
            models.Index(fields=["organization", "athlete_user", "created_at"]),
        ]

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return f"AIRun {self.id} ({self.capability}:{self.status})"


class AIOutput(models.Model):
    """Schema-validated structured draft. Never auto-sent, never auto-applied."""

    id = models.CharField(primary_key=True, max_length=36, default=_uuid7, editable=False)
    run = models.OneToOneField(AIRun, on_delete=models.CASCADE, related_name="output")
    schema_name = models.CharField(max_length=64)
    schema_version = models.PositiveIntegerField(default=1)
    validation_status = models.CharField(
        max_length=16, choices=[("valid", "Valid"), ("invalid", "Invalid")]
    )
    validation_errors = models.JSONField(default=list, blank=True)
    payload = models.JSONField(null=True, blank=True)
    edited_payload = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=16, choices=[(s, s) for s in OUTPUT_STATUS_CHOICES], default="draft"
    )
    reviewed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.CharField(max_length=500, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI output"
        verbose_name_plural = "AI outputs"

    @property
    def effective_payload(self):
        return self.edited_payload if self.edited_payload is not None else self.payload


class AISourceReference(models.Model):
    """Provenance record linking a run to authorized source entities."""

    SOURCE_TYPES = [
        ("workout_session", "Workout session"),
        ("set_log", "Set log"),
        ("feedback_flag", "Feedback flag (non-clinical)"),
        ("program_assignment", "Program assignment"),
        ("exercise", "Exercise"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=_uuid7, editable=False)
    run = models.ForeignKey(AIRun, on_delete=models.CASCADE, related_name="sources")
    source_type = models.CharField(max_length=32, choices=SOURCE_TYPES)
    source_id = models.CharField(max_length=64)
    descriptor = models.CharField(max_length=240)
    ordinal = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "AI source reference"
        verbose_name_plural = "AI source references"
        indexes = [models.Index(fields=["run", "ordinal"])]


class AIFeedback(models.Model):
    """Human report about a run/output (safety, correctness, privacy...)."""

    id = models.CharField(primary_key=True, max_length=36, default=_uuid7, editable=False)
    run = models.ForeignKey(AIRun, on_delete=models.CASCADE, related_name="feedback_reports")
    reporter_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="ai_feedback_reports"
    )
    report_type = models.CharField(max_length=32, choices=[(t, t) for t in REPORT_TYPES])
    detail = models.CharField(max_length=1000, blank=True, default="")
    status = models.CharField(
        max_length=16,
        choices=[("open", "Open"), ("triaged", "Triaged"), ("resolved", "Resolved")],
        default="open",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "AI feedback report"
        verbose_name_plural = "AI feedback reports"
        indexes = [models.Index(fields=["run", "report_type"])]


class AIPolicyDecision(models.Model):
    """Append-only record of policy gate outcomes (allow/deny + reason)."""

    id = models.CharField(primary_key=True, max_length=36, default=_uuid7, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    actor_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    run = models.ForeignKey(
        AIRun, on_delete=models.SET_NULL, null=True, blank=True, related_name="policy_decisions"
    )
    capability = models.CharField(max_length=64, blank=True, default="")
    stage = models.CharField(max_length=32, default="request")
    decision = models.CharField(max_length=8, choices=[("allow", "Allow"), ("deny", "Deny")])
    reason_code = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "AI policy decision"
        verbose_name_plural = "AI policy decisions"
        indexes = [models.Index(fields=["organization", "created_at"])]


class AIAuditEvent(models.Model):
    """Immutable append-only Copilot audit log (Tier 8 scoping of Tier 5)."""

    ACTION_CHOICES = [
        ("ai.run.requested", "ai.run.requested"),
        ("ai.run.denied", "ai.run.denied"),
        ("ai.run.completed", "ai.run.completed"),
        ("ai.run.failed", "ai.run.failed"),
        ("ai.run.cancelled", "ai.run.cancelled"),
        ("ai.run.regenerated", "ai.run.regenerated"),
        ("ai.output.viewed", "ai.output.viewed"),
        ("ai.output.edited", "ai.output.edited"),
        ("ai.output.approved", "ai.output.approved"),
        ("ai.output.rejected", "ai.output.rejected"),
        ("ai.output.reported", "ai.output.reported"),
        ("ai.source.opened", "ai.source.opened"),
        ("ai.purge.executed", "ai.purge.executed"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=_uuid7, editable=False)
    actor_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="ai_audit_events"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    action = models.CharField(max_length=40, choices=ACTION_CHOICES, db_index=True)
    target_entity_type = models.CharField(max_length=64, blank=True, default="")
    target_entity_id = models.CharField(max_length=64, blank=True, default="", db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    request_id = models.CharField(max_length=36, blank=True, default="", db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "AI audit event"
        verbose_name_plural = "AI audit events"
        indexes = [
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["organization", "created_at"]),
        ]

    def save(self, *args, **kwargs):
        if self.pk and AIAuditEvent.objects.filter(pk=self.pk).exists():
            raise ValueError("AIAuditEvent records are immutable. Updates are forbidden.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("AIAuditEvent records are immutable. Deletion is forbidden.")


class AIUsageMeter(models.Model):
    """Daily usage/cost accounting per actor within an organization."""

    id = models.CharField(primary_key=True, max_length=36, default=_uuid7, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="+")
    actor_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    date = models.DateField(db_index=True)
    run_count = models.PositiveIntegerField(default=0)
    input_tokens_est = models.PositiveIntegerField(default=0)
    output_tokens_est = models.PositiveIntegerField(default=0)
    cost_micro_usd = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "AI usage meter"
        verbose_name_plural = "AI usage meters"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "actor_user", "date"], name="unique_ai_meter_day"
            )
        ]
