"""Phase 06 organization-scoped program hierarchy and immutable assignments."""

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from apps.core.utils.id_generator import generate_uuid7
from apps.exercises.models import Exercise
from apps.identity.models import User
from apps.organizations.models import Organization


class Program(models.Model):
    GOAL_CHOICES = [
        (value, value.replace("_", " ").title())
        for value in ("hypertrophy", "strength", "fat_loss", "endurance", "general_fitness")
    ]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="programs"
    )
    created_by_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="programs")
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    target_goal = models.CharField(max_length=50, choices=GOAL_CHOICES)
    is_template = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["organization", "is_template", "is_archived"])]


class ProgramPhase(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="phases")
    name = models.CharField(max_length=150)
    sequence_order = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    duration_weeks = models.PositiveIntegerField(default=4, validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["sequence_order"]
        constraints = [
            models.UniqueConstraint(fields=["program", "sequence_order"], name="unique_phase_order")
        ]


class ProgramWeek(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    phase = models.ForeignKey(ProgramPhase, on_delete=models.CASCADE, related_name="weeks")
    week_number = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    focus_note = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["week_number"]
        constraints = [
            models.UniqueConstraint(fields=["phase", "week_number"], name="unique_phase_week")
        ]


class ProgramDay(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    week = models.ForeignKey(ProgramWeek, on_delete=models.CASCADE, related_name="days")
    day_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    title = models.CharField(max_length=150)

    class Meta:
        ordering = ["day_number"]
        constraints = [
            models.UniqueConstraint(fields=["week", "day_number"], name="unique_week_day")
        ]


class Workout(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    day = models.ForeignKey(ProgramDay, on_delete=models.CASCADE, related_name="workouts")
    title = models.CharField(max_length=150)
    estimated_minutes = models.PositiveIntegerField(null=True, blank=True)
    sequence_order = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["sequence_order"]
        constraints = [
            models.UniqueConstraint(fields=["day", "sequence_order"], name="unique_day_workout")
        ]


class WorkoutItem(models.Model):
    SEGMENT_CHOICES = [(value, value.title()) for value in ("warmup", "main", "cooldown")]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE, related_name="items")
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT, related_name="workout_items")
    sequence_order = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    group_key = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        validators=[RegexValidator(r"^[A-Z][0-9]{0,2}$", "Use a group such as A, A1, or B2.")],
    )
    segment = models.CharField(max_length=20, choices=SEGMENT_CHOICES, default="main")
    rest_seconds_between_sets = models.PositiveIntegerField(default=90)
    coach_notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["sequence_order"]
        constraints = [
            models.UniqueConstraint(fields=["workout", "sequence_order"], name="unique_item_order")
        ]


class SetPrescription(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    workout_item = models.ForeignKey(
        WorkoutItem, on_delete=models.CASCADE, related_name="prescriptions"
    )
    set_index = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    target_reps = models.CharField(max_length=50)
    target_load = models.CharField(max_length=50, null=True, blank=True)
    target_rpe = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    target_rir = models.PositiveIntegerField(
        null=True, blank=True, validators=[MaxValueValidator(10)]
    )
    tempo = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[RegexValidator(r"^[0-9Xx]-[0-9Xx]-[0-9Xx]-[0-9Xx]$", "Use tempo 3-1-1-0.")],
    )

    class Meta:
        ordering = ["set_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["workout_item", "set_index"], name="unique_item_set_index"
            )
        ]


class CoachAthleteAssignment(models.Model):
    """Minimal Phase 06 authorization relationship; no workout execution behavior."""

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    coach_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="coached_assignments"
    )
    athlete_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="coach_assignments"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "coach_user", "athlete_user"],
                name="unique_coach_athlete_assignment",
            )
        ]
        indexes = [models.Index(fields=["organization", "coach_user", "athlete_user"])]

    def clean(self):
        if self.coach_user_id == self.athlete_user_id:
            raise ValidationError("Coach and athlete must be different users.")


class ProgramAssignment(models.Model):
    STATUS_CHOICES = [(value, value.title()) for value in ("active", "completed", "archived")]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="program_assignments"
    )
    athlete_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="received_program_assignments"
    )
    assigned_by_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_program_assignments"
    )
    source_program = models.ForeignKey(
        Program, on_delete=models.PROTECT, related_name="assignments"
    )
    source_program_version = models.PositiveIntegerField()
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    snapshot_payload = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [models.Index(fields=["organization", "athlete_user", "status"])]

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date cannot precede start date."})
        if self.source_program_id and self.organization_id != self.source_program.organization_id:
            raise ValidationError("Source program must belong to the assignment organization.")

    def save(self, *args, **kwargs):
        if self.pk:
            old = (
                type(self)
                .objects.filter(pk=self.pk)
                .values_list("snapshot_payload", flat=True)
                .first()
            )
            if old is not None and old != self.snapshot_payload:
                raise ValidationError("Assignment snapshots are immutable.")
        super().save(*args, **kwargs)
