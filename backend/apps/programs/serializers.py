from django.db import transaction
from rest_framework import serializers

from apps.exercises.models import Exercise

from .models import (
    Program,
    ProgramAssignment,
    ProgramDay,
    ProgramPhase,
    ProgramWeek,
    SetPrescription,
    Workout,
    WorkoutItem,
)


class SetPrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SetPrescription
        exclude = ["workout_item"]
        read_only_fields = ["id"]


class WorkoutItemSerializer(serializers.ModelSerializer):
    exercise_id = serializers.CharField()
    prescriptions = SetPrescriptionSerializer(many=True, min_length=1)

    class Meta:
        model = WorkoutItem
        fields = [
            "id",
            "exercise_id",
            "sequence_order",
            "group_key",
            "segment",
            "rest_seconds_between_sets",
            "coach_notes",
            "prescriptions",
        ]
        read_only_fields = ["id"]


class WorkoutSerializer(serializers.ModelSerializer):
    items = WorkoutItemSerializer(many=True, min_length=1)

    class Meta:
        model = Workout
        fields = ["id", "title", "estimated_minutes", "sequence_order", "items"]
        read_only_fields = ["id"]


class ProgramDaySerializer(serializers.ModelSerializer):
    workouts = WorkoutSerializer(many=True, min_length=1)

    class Meta:
        model = ProgramDay
        fields = ["id", "day_number", "title", "workouts"]
        read_only_fields = ["id"]


class ProgramWeekSerializer(serializers.ModelSerializer):
    days = ProgramDaySerializer(many=True, min_length=1)

    class Meta:
        model = ProgramWeek
        fields = ["id", "week_number", "focus_note", "days"]
        read_only_fields = ["id"]


class ProgramPhaseSerializer(serializers.ModelSerializer):
    weeks = ProgramWeekSerializer(many=True, min_length=1)

    class Meta:
        model = ProgramPhase
        fields = ["id", "name", "sequence_order", "duration_weeks", "weeks"]
        read_only_fields = ["id"]


def _validate_unique_order(items, key, label):
    values = [item[key] for item in items]
    if len(values) != len(set(values)):
        raise serializers.ValidationError(f"{label} values must be unique among siblings.")


def _validate_tree(phases, organization):
    _validate_unique_order(phases, "sequence_order", "Phase sequence_order")
    for phase in phases:
        _validate_unique_order(phase["weeks"], "week_number", "Week number")
        for week in phase["weeks"]:
            _validate_unique_order(week["days"], "day_number", "Day number")
            for day in week["days"]:
                _validate_unique_order(day["workouts"], "sequence_order", "Workout sequence_order")
                for workout in day["workouts"]:
                    _validate_unique_order(
                        workout["items"], "sequence_order", "Item sequence_order"
                    )
                    for item in workout["items"]:
                        _validate_unique_order(
                            item["prescriptions"], "set_index", "Prescription set_index"
                        )
                        exercise = Exercise.objects.filter(
                            id=item["exercise_id"], status="published"
                        ).first()
                        if not exercise or (
                            exercise.organization_id is not None
                            and exercise.organization_id != organization.id
                        ):
                            raise serializers.ValidationError(
                                {"exercise_id": "Exercise is unavailable in this organization."}
                            )


def _create_tree(program, phases):
    for phase_data in phases:
        weeks = phase_data.pop("weeks")
        phase = ProgramPhase.objects.create(program=program, **phase_data)
        for week_data in weeks:
            days = week_data.pop("days")
            week = ProgramWeek.objects.create(phase=phase, **week_data)
            for day_data in days:
                workouts = day_data.pop("workouts")
                day = ProgramDay.objects.create(week=week, **day_data)
                for workout_data in workouts:
                    items = workout_data.pop("items")
                    workout = Workout.objects.create(day=day, **workout_data)
                    for item_data in items:
                        prescriptions = item_data.pop("prescriptions")
                        exercise_id = item_data.pop("exercise_id")
                        item = WorkoutItem.objects.create(
                            workout=workout, exercise_id=exercise_id, **item_data
                        )
                        SetPrescription.objects.bulk_create(
                            [
                                SetPrescription(workout_item=item, **prescription)
                                for prescription in prescriptions
                            ]
                        )


class ProgramSerializer(serializers.ModelSerializer):
    phases = ProgramPhaseSerializer(many=True, min_length=1)

    class Meta:
        model = Program
        fields = [
            "id",
            "organization_id",
            "created_by_user_id",
            "title",
            "description",
            "target_goal",
            "is_template",
            "is_archived",
            "version",
            "phases",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "organization_id",
            "created_by_user_id",
            "version",
            "created_at",
            "updated_at",
        ]

    def validate_phases(self, value):
        organization = self.context["organization"]
        _validate_tree(value, organization)
        return value

    @transaction.atomic
    def create(self, validated_data):
        phases = validated_data.pop("phases")
        program = Program.objects.create(**validated_data)
        _create_tree(program, phases)
        return program

    @transaction.atomic
    def update(self, instance, validated_data):
        phases = validated_data.pop("phases", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.version += 1
        instance.save()
        if phases is not None:
            instance.phases.all().delete()
            _create_tree(instance, phases)
        return instance


def program_queryset():
    return Program.objects.prefetch_related(
        "phases__weeks__days__workouts__items__exercise__translations",
        "phases__weeks__days__workouts__items__prescriptions",
    )


def snapshot_program(program):
    """Generate a detached, JSON-safe ordered point-in-time representation."""
    data = ProgramSerializer(program).data
    return {
        "schema_version": 1,
        "source_program_id": program.id,
        "source_program_version": program.version,
        "program": data,
    }


class ProgramAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramAssignment
        fields = [
            "id",
            "organization_id",
            "athlete_user_id",
            "assigned_by_user_id",
            "source_program_id",
            "source_program_version",
            "start_date",
            "end_date",
            "status",
            "snapshot_payload",
            "created_at",
        ]
        read_only_fields = fields
