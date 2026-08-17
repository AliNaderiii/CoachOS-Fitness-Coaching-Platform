from django.db import migrations, models
import django.db.models.deletion
import django.db.models.functions
import apps.core.utils.id_generator
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="IntegrationConnection",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("provider_type", models.CharField(default="mock_fitness", max_length=50)),
                ("provider_account_reference", models.CharField(blank=True, max_length=255)),
                ("connection_state", models.CharField(choices=[("connected", "Connected"), ("disconnected", "Disconnected"), ("reauthorizing", "Reauthorizing"), ("limited_permission", "Limited Permission"), ("expired", "Expired")], default="disconnected", max_length=30)),
                ("scopes_granted", models.JSONField(blank=True, default=list)),
                ("token_vault_reference", models.CharField(blank=True, max_length=255)),
                ("connected_at", models.DateTimeField(auto_now_add=True)),
                ("disconnected_at", models.DateTimeField(blank=True, null=True)),
                ("last_sync_at", models.DateTimeField(blank=True, null=True)),
                ("revocation_status", models.CharField(default="none", max_length=20)),
                ("retained_imported_data_policy", models.CharField(choices=[("retain_for_history", "Retain for history"), ("delete_all", "Delete all")], default="retain_for_history", max_length=30)),
                ("organization_id", models.UUIDField(db_index=True)),
                ("athlete_user_id", models.UUIDField(db_index=True)),
            ],
            options={
                "indexes": [models.Index(fields=["organization_id", "athlete_user_id"], name="integratio_organi_4f7e6d_idx"), models.Index(fields=["provider_account_reference"], name="integratio_provide_8c5b1f_idx")],
            },
        ),
    ]
