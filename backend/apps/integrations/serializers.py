from rest_framework import serializers

from .models import IntegrationConnection


class IntegrationConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationConnection
        fields = [
            "id",
            "organization_id",
            "athlete_user_id",
            "provider_type",
            "connection_state",
            "scopes_granted",
            "connected_at",
            "last_sync_at",
            "revocation_status",
            "retained_imported_data_policy",
        ]
        read_only_fields = ["id", "connected_at", "last_sync_at"]
