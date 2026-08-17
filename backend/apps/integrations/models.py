from django.db import models
from django.conf import settings


class IntegrationConnection(models.Model):
    STATE_CHOICES = [
        ("connected", "Connected"),
        ("disconnected", "Disconnected"),
        ("reauthorizing", "Reauthorizing"),
        ("limited_permission", "Limited Permission"),
        ("expired", "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=settings.DEFAULT_UUID_GENERATOR, editable=False)
    organization_id = models.UUIDField(db_index=True)
    athlete_user_id = models.UUIDField(db_index=True)
    provider_type = models.CharField(max_length=50, default="mock_fitness")
    provider_account_reference = models.CharField(max_length=255, blank=True)
    connection_state = models.CharField(max_length=30, choices=STATE_CHOICES, default="disconnected")
    scopes_granted = models.JSONField(default=list, blank=True)
    token_vault_reference = models.CharField(max_length=255, blank=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    revocation_status = models.CharField(max_length=20, default="none")
    retained_imported_data_policy = models.CharField(
        max_length=30, default="retain_for_history",
        choices=[
            ("retain_for_history", "Retain for history"),
            ("delete_all", "Delete all"),
        ]
    )

    class Meta:
        indexes = [
            models.Index(fields=["organization_id", "athlete_user_id"]),
            models.Index(fields=["provider_account_reference"]),
        ]
        unique_together = ["organization_id", "athlete_user_id", "provider_type"]
