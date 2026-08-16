"""Phase 07 execution serializers. Responses never leak raw media or health data."""

from django.utils import timezone
from rest_framework import serializers

from .models import (
    BodyMetric,
    ConsentRecord,
    FeedbackFlag,
    ProgressPhoto,
    SetLog,
    Substitution,
    WorkoutSession,
)
from .storage import storage_adapter


class WorkoutSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutSession
        fields = [
            "id",
            "organization_id",
            "program_assignment_id",
            "athlete_user_id",
            "scheduled_date",
            "status",
            "started_at",
            "completed_at",
            "session_rpe",
            "fatigue_score",
            "athlete_notes",
            "skip_or_modify_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class StartSessionInputSerializer(serializers.Serializer):
    program_assignment_id = serializers.CharField()
    scheduled_date = serializers.DateField()

    def validate_program_assignment_id(self, value):
        return str(value)


class CompleteSessionInputSerializer(serializers.Serializer):
    session_rpe = serializers.IntegerField(min_value=1, max_value=10, required=False)
    fatigue_score = serializers.IntegerField(min_value=1, max_value=5, required=False)
    athlete_notes = serializers.CharField(allow_blank=True, required=False)
    skip_or_modify_reason = serializers.CharField(allow_blank=True, required=False)


class SetLogSerializer(serializers.ModelSerializer):
    exercise_id = serializers.CharField()

    class Meta:
        model = SetLog
        fields = [
            "id",
            "exercise_id",
            "set_index",
            "actual_reps",
            "actual_load_kg",
            "actual_rpe",
            "is_completed",
            "note",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_set_index(self, value):
        if value < 1:
            raise serializers.ValidationError("set_index must be >= 1.")
        return value


class SubstitutionSerializer(serializers.ModelSerializer):
    original_exercise_id = serializers.CharField()
    substituted_exercise_id = serializers.CharField()

    class Meta:
        model = Substitution
        fields = [
            "id",
            "original_exercise_id",
            "substituted_exercise_id",
            "reason",
            "note",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        if attrs.get("original_exercise_id") == attrs.get("substituted_exercise_id"):
            raise serializers.ValidationError(
                {"substituted_exercise_id": "Substituted exercise must differ."}
            )
        return attrs


class FeedbackFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedbackFlag
        fields = [
            "id",
            "flag_type",
            "anatomical_location",
            "severity",
            "details",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]


class BodyMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = BodyMetric
        fields = [
            "id",
            "metric_type",
            "value",
            "unit",
            "recorded_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProgressPhotoSerializer(serializers.ModelSerializer):
    signed_url = serializers.SerializerMethodField()
    thumbnail_signed_url = serializers.SerializerMethodField()

    class Meta:
        model = ProgressPhoto
        fields = [
            "id",
            "athlete_user_id",
            "photo_type",
            "captured_at",
            "signed_url",
            "thumbnail_signed_url",
            "created_at",
        ]
        read_only_fields = ["id", "athlete_user_id", "created_at"]

    def _may_surface_url(self):
        """
        Signed URLs are consent-gated. Only surface a URL when the serializer was
        constructed with `include_signed_url=True` (set by authorized views) so no
        public storage key or URL leaks in normal responses.
        """
        return bool(self.context.get("include_signed_url"))

    def get_signed_url(self, obj):
        if not self._may_surface_url():
            return None
        return storage_adapter.get_signed_url(obj.storage_key)

    def get_thumbnail_signed_url(self, obj):
        # Phase 07 mock adapter has no separate thumbnail; reuse the same mock URL
        # only when authorized. Mirrors list/owner semantics.
        if not self._may_surface_url():
            return None
        return storage_adapter.get_signed_url(obj.storage_key)


class ConsentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentRecord
        fields = [
            "id",
            "athlete_user_id",
            "grantee_user_id",
            "consent_type",
            "is_granted",
            "granted_at",
            "revoked_at",
            "created_at",
        ]
        read_only_fields = ["id", "granted_at", "revoked_at", "created_at"]


class CreateConsentInputSerializer(serializers.Serializer):
    athlete_user_id = serializers.CharField()
    grantee_user_id = serializers.CharField()
    consent_type = serializers.ChoiceField(
        choices=["progress_photo", "nutrition_sharing", "body_metrics"]
    )
    is_granted = serializers.BooleanField(default=True)


class UploadProgressPhotoInputSerializer(serializers.Serializer):
    file = serializers.FileField()
    photo_type = serializers.ChoiceField(choices=["front", "side", "back"])
    captured_at = serializers.DateField(required=False, allow_null=True)


def _today_date():
    return timezone.localdate()
