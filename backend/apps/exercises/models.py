"""Phase 06 bilingual exercise catalog and media provenance models."""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.utils.id_generator import generate_uuid7
from apps.core.utils.persian_normalizer import PersianNormalizer
from apps.identity.models import User
from apps.organizations.models import Organization

LOCALE_CHOICES = [("fa-IR", "Persian"), ("en-US", "English")]


class Exercise(models.Model):
    MOVEMENT_CHOICES = [
        (value, value.replace("_", " ").title())
        for value in (
            "squat",
            "hinge",
            "horizontal_push",
            "horizontal_pull",
            "vertical_push",
            "vertical_pull",
            "lunge",
            "carry",
            "isolation",
            "cardio",
            "other",
        )
    ]
    DIFFICULTY_CHOICES = [
        (value, value.title()) for value in ("beginner", "intermediate", "advanced")
    ]
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending_review", "Pending review"),
        ("published", "Published"),
        ("archived", "Archived"),
        ("rejected", "Rejected"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True, related_name="exercises"
    )
    created_by_user = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name="created_exercises"
    )
    movement_pattern = models.CharField(max_length=50, choices=MOVEMENT_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    primary_muscles = models.JSONField(default=list)
    secondary_muscles = models.JSONField(default=list, blank=True)
    equipment_required = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["movement_pattern", "difficulty"]),
        ]

    def clean(self):
        for field in ("primary_muscles", "secondary_muscles", "equipment_required"):
            value = getattr(self, field)
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise ValidationError({field: "Must be a list of strings."})
        if (
            self.organization_id is None
            and self.created_by_user_id
            and not self.created_by_user.is_platform_admin
        ):
            raise ValidationError("Only a platform administrator may author a canonical exercise.")


class ExerciseTranslation(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="translations")
    locale = models.CharField(max_length=10, choices=LOCALE_CHOICES)
    name = models.CharField(max_length=200)
    normalized_name = models.CharField(max_length=200, db_index=True, editable=False)
    instructions = models.TextField()
    coaching_cues = models.JSONField(default=list, blank=True)
    common_mistakes = models.JSONField(default=list, blank=True)
    safety_notes = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["exercise", "locale"], name="unique_exercise_locale")
        ]
        indexes = [models.Index(fields=["locale", "normalized_name"])]

    def save(self, *args, **kwargs):
        self.normalized_name = PersianNormalizer.normalize(self.name)
        super().save(*args, **kwargs)


class ExerciseAlias(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="aliases")
    locale = models.CharField(max_length=10, choices=LOCALE_CHOICES)
    alias = models.CharField(max_length=200)
    normalized_alias = models.CharField(max_length=200, db_index=True, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["exercise", "locale", "normalized_alias"], name="unique_normalized_alias"
            )
        ]
        indexes = [models.Index(fields=["locale", "normalized_alias"])]

    def save(self, *args, **kwargs):
        self.normalized_alias = PersianNormalizer.normalize(self.alias)
        super().save(*args, **kwargs)


class MediaAsset(models.Model):
    MEDIA_CHOICES = [
        ("video_mp4", "MP4 video"),
        ("image_webp", "WebP image"),
        ("animation_gif", "GIF animation"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="media_assets")
    media_type = models.CharField(max_length=20, choices=MEDIA_CHOICES)
    storage_key = models.CharField(max_length=500, unique=True)
    thumbnail_storage_key = models.CharField(max_length=500, null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    bytes_size = models.PositiveBigIntegerField()
    checksum_sha256 = models.CharField(max_length=64)


class MediaRights(models.Model):
    LICENSE_CHOICES = [
        ("original_production", "Original production"),
        ("licensed_cc_by", "CC BY licensed"),
        ("commercial_license", "Commercial license"),
        ("coach_upload", "Coach upload"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    media_asset = models.OneToOneField(MediaAsset, on_delete=models.CASCADE, related_name="rights")
    license_type = models.CharField(max_length=50, choices=LICENSE_CHOICES)
    source_url = models.URLField(max_length=500, null=True, blank=True)
    creator_attribution = models.CharField(max_length=255)
    permitted_commercial_use = models.BooleanField(default=False)
    reviewed_by_user = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True, related_name="reviewed_media_rights"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.license_type != "original_production" and not self.source_url:
            raise ValidationError({"source_url": "Source URL is required for non-original media."})
        if bool(self.reviewed_by_user_id) != bool(self.reviewed_at):
            raise ValidationError("Reviewer and review timestamp must be set together.")
        if self.reviewed_by_user_id and not self.reviewed_by_user.is_platform_admin:
            raise ValidationError(
                {"reviewed_by_user": "Reviewer must be a platform administrator."}
            )
