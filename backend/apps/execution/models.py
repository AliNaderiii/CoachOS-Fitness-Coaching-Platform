"""
Phase 07 — Athlete Execution and Progress models.

Implements the athlete workout session lifecycle, set actual logging, exercise
substitution, subjective feedback flags, progress body metrics, consent-gated
progress photos, and privacy consent records.

Security/privacy notes:
- All sensitive media (ProgressPhoto) is private; only a private storage key is
  stored and signed URLs are generated on demand under consent.
- FeedbackFlag values are subjective athlete reports, never clinical diagnosis.
- ConsentRecord gates coach/owner access to progress photos and body metrics.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.core.utils.id_generator import generate_uuid7
from apps.exercises.models import Exercise
from apps.identity.models import User
from apps.organizations.models import Organization
from apps.programs.models import ProgramAssignment


class WorkoutSession(models.Model):
    """
    One scheduled workout execution for an athlete from an authorized assignment.

    Status lifecycle (enforced via :meth:`transition`):
      scheduled -> in_progress (start)
      scheduled -> skipped     (skip, reason required)
      in_progress -> completed (complete)
      in_progress -> modified  (modify, reason required)
    completed is terminal within Phase 07 (documented correction flow only).
    """

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In progress"),
        ("completed", "Completed"),
        ("skipped", "Skipped"),
        ("modified", "Modified"),
    ]

    # Allowed transitions: current -> {next: reason_required}
    TRANSITIONS = {
        "scheduled": {"in_progress": False, "skipped": True},
        "in_progress": {"completed": False, "modified": True},
        "completed": {},
        "skipped": {},
        "modified": {},
    }

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.PROTECT, related_name="workout_sessions"
    )
    program_assignment = models.ForeignKey(
        ProgramAssignment, on_delete=models.PROTECT, related_name="workout_sessions"
    )
    athlete_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="workout_sessions"
    )
    scheduled_date = models.DateField(db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    skip_or_modify_reason = models.TextField(null=True, blank=True)
    session_rpe = models.PositiveIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    fatigue_score = models.PositiveIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    athlete_notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["program_assignment", "scheduled_date"],
                name="unique_assignment_scheduled_date",
            )
        ]
        indexes = [
            models.Index(fields=["athlete_user", "scheduled_date", "status"]),
            models.Index(fields=["organization", "athlete_user", "status"]),
        ]

    def clean(self):
        errors = {}
        if self.program_assignment_id:
            assignment = self.program_assignment
            if assignment.athlete_user_id != self.athlete_user_id:
                errors["program_assignment"] = (
                    "Only the athlete assigned to the program may create a session."
                )
            if assignment.organization_id != self.organization_id:
                errors["organization"] = "Session organization must match the assignment."
            if assignment.status != "active":
                errors["program_assignment"] = "Only an active assignment may be executed."
        if self.status in ("skipped", "modified") and not self.skip_or_modify_reason:
            errors["skip_or_modify_reason"] = "A reason is required when skipping or modifying."
        if self.status not in ("skipped", "modified") and self.skip_or_modify_reason:
            # Not an error by itself, but a skip/modify reason on another status is unusual;
            # keep permissive so completion can carry a reason without a status mismatch.
            pass
        if errors:
            raise ValidationError(errors)

    def can_transition_to(self, new_status):
        return new_status in self.TRANSITIONS.get(self.status, {})

    def transition(self, new_status, *, reason=None, **fields):
        """Validate and perform a status transition atomically at the caller's scope."""
        if new_status not in self.TRANSITIONS.get(self.status, {}):
            raise ValidationError(
                {"status": f"Cannot transition from {self.status} to {new_status}."}
            )
        reason_required = self.TRANSITIONS[self.status][new_status]
        if reason_required and not reason:
            raise ValidationError({"skip_or_modify_reason": "A reason is required."})
        self.status = new_status
        if reason is not None:
            self.skip_or_modify_reason = reason
        for field, value in fields.items():
            setattr(self, field, value)
        if new_status == "in_progress":
            self.started_at = timezone.now()
        elif new_status == "completed":
            self.completed_at = timezone.now()
        self.full_clean()
        return self

    def __str__(self):
        return f"Session {self.id} ({self.status})"


class SetLog(models.Model):
    """Actual performed reps/load/RPE for one set of an exercise in a session."""

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name="set_logs")
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, related_name="set_logs")
    set_index = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    actual_reps = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    # Actual load is stored in kilograms (explicit unit conversion policy). Frontends
    # convert lbs -> kg before sending; responses always report kg.
    actual_load_kg = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal("0"))]
    )
    actual_rpe = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("1")), MaxValueValidator(Decimal("10"))],
    )
    is_completed = models.BooleanField(default=True)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["set_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["session", "exercise", "set_index"], name="unique_session_exercise_set"
            )
        ]
        indexes = [models.Index(fields=["session", "exercise", "set_index"])]

    def __str__(self):
        return f"Set {self.set_index} of {self.exercise_id}"


class Substitution(models.Model):
    """Exercise substitution with a mandatory reason."""

    REASON_CHOICES = [
        ("equipment_unavailable", "Equipment unavailable"),
        ("discomfort", "Discomfort"),
        ("preference", "Preference"),
        ("other", "Other"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    session = models.ForeignKey(
        WorkoutSession, on_delete=models.CASCADE, related_name="substitutions"
    )
    original_exercise = models.ForeignKey(
        Exercise, on_delete=models.PROTECT, related_name="substituted_from"
    )
    substituted_exercise = models.ForeignKey(
        Exercise, on_delete=models.PROTECT, related_name="substituted_to"
    )
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    note = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.original_exercise_id and self.substituted_exercise_id:
            if self.original_exercise_id == self.substituted_exercise_id:
                raise ValidationError(
                    {"substituted_exercise_id": "Substituted exercise must differ."}
                )
        if not self.reason:
            raise ValidationError({"reason": "A substitution reason is mandatory."})


class FeedbackFlag(models.Model):
    """
    Subjective athlete pain/fatigue report.

    Explicitly NOT a clinical diagnosis, injury prediction, or medical advice.
    Values are athlete-entered subjective feedback used for coach awareness only.
    """

    FLAG_TYPE_CHOICES = [
        ("joint_pain", "Joint pain"),
        ("muscle_strain", "Muscle strain"),
        ("dizziness", "Dizziness"),
        ("severe_fatigue", "Severe fatigue"),
    ]
    SEVERITY_CHOICES = [
        ("mild", "Mild"),
        ("moderate", "Moderate"),
        ("severe", "Severe"),
    ]
    STATUS_CHOICES = [("unresolved", "Unresolved"), ("resolved", "Resolved")]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    session = models.ForeignKey(
        WorkoutSession, on_delete=models.CASCADE, related_name="feedback_flags"
    )
    athlete_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="feedback_flags")
    flag_type = models.CharField(max_length=30, choices=FLAG_TYPE_CHOICES)
    anatomical_location = models.CharField(max_length=200)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    details = models.TextField(help_text="Subjective athlete feedback, not a clinical diagnosis.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unresolved")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["session", "status"])]

    def clean(self):
        if self.session_id and self.athlete_user_id:
            if self.session.athlete_user_id != self.athlete_user_id:
                raise ValidationError(
                    {"athlete_user": "Feedback flag must belong to the session athlete."}
                )


class BodyMetric(models.Model):
    """A single recorded body metric. Sensitive (Tier 3) — consent-gated for coach/owner."""

    METRIC_TYPE_CHOICES = [
        ("body_weight", "Body weight"),
        ("body_fat_percentage", "Body fat percentage"),
        ("waist_circumference", "Waist circumference"),
        ("other", "Other"),
    ]
    UNIT_CHOICES = [("kg", "Kilograms"), ("lbs", "Pounds")]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.PROTECT, related_name="body_metrics", null=True, blank=True
    )
    athlete_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="body_metrics")
    metric_type = models.CharField(max_length=40, choices=METRIC_TYPE_CHOICES)
    value = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=5, choices=UNIT_CHOICES, default="kg")
    recorded_at = models.DateField(db_index=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [models.Index(fields=["athlete_user", "recorded_at"])]

    def clean(self):
        if self.value is not None and self.value < 0:
            raise ValidationError({"value": "Metric value cannot be negative."})


class ProgressPhoto(models.Model):
    """
    Athlete progress photo.

    Privacy boundary:
    - Only a private storage key is stored. No public URL is ever stored.
    - Signed URLs are generated on demand (mock adapter in Phase 07) and are
      strictly consent-gated (ConsentRecord) for coach/owner viewers.
    - Raw media is not stored in Git.
    """

    PHOTO_TYPE_CHOICES = [("front", "Front"), ("side", "Side"), ("back", "Back")]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    athlete_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progress_photos")
    organization = models.ForeignKey(
        Organization, on_delete=models.PROTECT, related_name="progress_photos"
    )
    storage_key = models.CharField(max_length=500, unique=True)
    photo_type = models.CharField(max_length=20, choices=PHOTO_TYPE_CHOICES)
    consent_status = models.BooleanField(
        default=False,
        help_text="Snapshot of whether athlete has granted sharing consent for this photo.",
    )
    captured_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["athlete_user", "created_at"])]

    def __str__(self):
        return f"Photo {self.id} ({self.photo_type})"


class ConsentRecord(models.Model):
    """Athlete-granted consent for a grantee (assigned coach, or owner escalation)."""

    CONSENT_TYPE_CHOICES = [
        ("progress_photo", "Progress photo"),
        ("nutrition_sharing", "Nutrition sharing"),
        ("body_metrics", "Body metrics"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    athlete_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="consents_given")
    grantee_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="consents_received"
    )
    consent_type = models.CharField(max_length=30, choices=CONSENT_TYPE_CHOICES)
    is_granted = models.BooleanField(default=False)
    granted_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["athlete_user", "grantee_user", "consent_type"],
                name="unique_consent_athlete_grantee_type",
            )
        ]

    def clean(self):
        if self.athlete_user_id and self.grantee_user_id:
            if self.athlete_user_id == self.grantee_user_id:
                raise ValidationError({"grantee_user": "Consent grantee must be a different user."})

    @property
    def is_active(self):
        return self.is_granted and self.revoked_at is None

    def grant(self):
        self.is_granted = True
        self.granted_at = timezone.now()
        self.revoked_at = None

    def revoke(self):
        self.is_granted = False
        self.revoked_at = timezone.now()

    def __str__(self):
        return f"Consent {self.consent_type} {self.athlete_user_id}->{self.grantee_user_id}"
