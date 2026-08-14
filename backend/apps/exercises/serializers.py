from django.db import transaction
from rest_framework import serializers

from .models import Exercise, ExerciseAlias, ExerciseTranslation, MediaAsset, MediaRights


class ExerciseTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseTranslation
        fields = [
            "id",
            "locale",
            "name",
            "instructions",
            "coaching_cues",
            "common_mistakes",
            "safety_notes",
        ]
        read_only_fields = ["id"]


class ExerciseAliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseAlias
        fields = ["id", "locale", "alias"]
        read_only_fields = ["id"]


class MediaRightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaRights
        fields = [
            "license_type",
            "source_url",
            "creator_attribution",
            "permitted_commercial_use",
            "reviewed_by_user_id",
            "reviewed_at",
        ]
        read_only_fields = ["reviewed_by_user_id", "reviewed_at"]


class MediaAssetSerializer(serializers.ModelSerializer):
    rights = MediaRightsSerializer()

    class Meta:
        model = MediaAsset
        fields = [
            "id",
            "media_type",
            "storage_key",
            "thumbnail_storage_key",
            "duration_seconds",
            "bytes_size",
            "checksum_sha256",
            "rights",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {
            "storage_key": {"write_only": True},
            "thumbnail_storage_key": {"write_only": True},
        }

    def validate_storage_key(self, value):
        if value.startswith("/") or ".." in value.split("/") or "://" in value:
            raise serializers.ValidationError("Use a relative private object key.")
        return value

    def validate_checksum_sha256(self, value):
        if len(value) != 64 or any(char not in "0123456789abcdefABCDEF" for char in value):
            raise serializers.ValidationError(
                "Must be a 64-character hexadecimal SHA-256 checksum."
            )
        return value.lower()


class ExerciseSerializer(serializers.ModelSerializer):
    translations = ExerciseTranslationSerializer(many=True)
    aliases = ExerciseAliasSerializer(many=True, required=False)
    media_assets = MediaAssetSerializer(many=True, required=False)

    class Meta:
        model = Exercise
        fields = [
            "id",
            "organization_id",
            "movement_pattern",
            "difficulty",
            "primary_muscles",
            "secondary_muscles",
            "equipment_required",
            "status",
            "translations",
            "aliases",
            "media_assets",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organization_id", "status", "created_at", "updated_at"]

    def validate_translations(self, value):
        locales = [item["locale"] for item in value]
        if len(locales) != len(set(locales)):
            raise serializers.ValidationError("Translation locales must be unique.")
        if set(locales) != {"fa-IR", "en-US"}:
            raise serializers.ValidationError("Exactly fa-IR and en-US translations are required.")
        return value

    def validate_media_assets(self, value):
        for asset in value:
            if not asset["rights"].get("permitted_commercial_use", False):
                raise serializers.ValidationError(
                    "Attached media must permit commercial use before publication."
                )
        return value

    def validate_aliases(self, value):
        seen = set()
        for item in value:
            key = (item["locale"], item["alias"])
            if key in seen:
                raise serializers.ValidationError("Aliases must be unique per locale.")
            seen.add(key)
        return value

    @transaction.atomic
    def create(self, validated_data):
        translations = validated_data.pop("translations")
        aliases = validated_data.pop("aliases", [])
        media = validated_data.pop("media_assets", [])
        exercise = Exercise.objects.create(**validated_data)
        for item in translations:
            ExerciseTranslation.objects.create(exercise=exercise, **item)
        for item in aliases:
            ExerciseAlias.objects.create(exercise=exercise, **item)
        for item in media:
            rights_data = item.pop("rights")
            asset = MediaAsset.objects.create(exercise=exercise, **item)
            rights = MediaRights(media_asset=asset, **rights_data)
            rights.full_clean()
            rights.save()
        return exercise
