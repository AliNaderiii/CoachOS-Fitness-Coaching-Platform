"""
Phase 05 — Immutable AuditEvent Foundation.
"""

from django.db import models
from django.utils import timezone

from apps.core.utils.id_generator import generate_uuid7
from apps.identity.models import User
from apps.organizations.models import Organization


class AuditEvent(models.Model):
    """
    Immutable append-only audit log for security-sensitive events.
    Never updated/deleted by application code (DB constraints + tests enforce).
    """

    ACTION_CHOICES = [
        # Auth
        ("auth.registered", "auth.registered"),
        ("auth.login", "auth.login"),
        ("auth.login_failed", "auth.login_failed"),
        ("auth.logout", "auth.logout"),
        ("auth.password_reset_requested", "auth.password_reset_requested"),
        ("auth.password_reset_completed", "auth.password_reset_completed"),
        # Org
        ("org.created", "org.created"),
        ("org.settings_updated", "org.settings_updated"),
        ("org.owner_transferred", "org.owner_transferred"),
        # Membership
        ("membership.created", "membership.created"),
        ("membership.status_changed", "membership.status_changed"),
        ("membership.role_changed", "membership.role_changed"),
        # Invitation
        ("invitation.created", "invitation.created"),
        ("invitation.sent", "invitation.sent"),
        ("invitation.accepted", "invitation.accepted"),
        ("invitation.revoked", "invitation.revoked"),
    ]

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    actor_user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_events"
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_events"
    )
    action = models.CharField(max_length=100, choices=ACTION_CHOICES, db_index=True)
    target_entity_type = models.CharField(max_length=64, blank=True)
    target_entity_id = models.CharField(max_length=64, blank=True, db_index=True)
    ip_hash = models.CharField(max_length=64, blank=True)  # SHA256 hash only
    metadata = models.JSONField(default=dict, blank=True)
    request_id = models.CharField(max_length=36, blank=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "audit event"
        verbose_name_plural = "audit events"
        indexes = [
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["organization", "created_at"]),
            models.Index(fields=["actor_user", "created_at"]),
        ]
        # Prevent accidental mutation at ORM level (further DB rules recommended)
        permissions = [("can_view_audit", "Can view audit events")]

    def __str__(self):
        return f"{self.action} @ {self.created_at.isoformat()}"

    def save(self, *args, **kwargs):
        # Enforce immutability: cannot update existing
        if self.pk and AuditEvent.objects.filter(pk=self.pk).exists():
            # Allow only creation
            raise ValueError("AuditEvent records are immutable. Updates are forbidden.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("AuditEvent records are immutable. Deletion is forbidden.")
