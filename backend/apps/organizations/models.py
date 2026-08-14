"""
Phase 05 — Organization Tenancy, Memberships, Invitations, Single-Location MVP.
"""

from django.db import models
from django.utils import timezone

from apps.core.utils.id_generator import generate_uuid7
from apps.identity.models import User


class Organization(models.Model):
    """
    Top-level tenant.
    - owner_user_id is authoritative source of truth.
    - Exactly one active owner membership must match owner_user_id (enforced in service/transaction).
    - Single primary location enforced in MVP.
    """

    id = models.CharField(
        primary_key=True, max_length=36, default=generate_uuid7, editable=False, db_index=True
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    owner_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="owned_organizations", db_index=True
    )
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "organization"
        verbose_name_plural = "organizations"
        indexes = [models.Index(fields=["slug"]), models.Index(fields=["owner_user"])]

    def __str__(self):
        return self.name

    @property
    def is_archived(self):
        return self.archived_at is not None


class Location(models.Model):
    """Single primary location for MVP organization."""

    id = models.CharField(
        primary_key=True, max_length=36, default=generate_uuid7, editable=False, db_index=True
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="locations"
    )
    name = models.CharField(max_length=150)
    is_primary = models.BooleanField(default=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "location"
        verbose_name_plural = "locations"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "is_primary"],
                condition=models.Q(is_primary=True),
                name="unique_primary_location_per_org",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Membership(models.Model):
    """
    User <-> Organization membership with role.
    - Multi-role allowed via (user, org, role) unique.
    - Status: invited, active, suspended, archived
    - Effective permissions = union of active roles (server computed).
    """

    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("coach", "Coach"),
        ("athlete", "Athlete"),
        ("support", "Support"),
    ]
    STATUS_CHOICES = [
        ("invited", "Invited"),
        ("active", "Active"),
        ("suspended", "Suspended"),
        ("archived", "Archived"),
    ]

    id = models.CharField(
        primary_key=True, max_length=36, default=generate_uuid7, editable=False, db_index=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="invited")
    created_at = models.DateTimeField(default=timezone.now)
    archived_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "membership"
        verbose_name_plural = "memberships"
        unique_together = [("user", "organization", "role")]
        indexes = [
            models.Index(fields=["user", "organization"]),
            models.Index(fields=["organization", "role", "status"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.organization.slug} ({self.role}/{self.status})"


class Invitation(models.Model):
    """
    Secure invitation with hashed token.
    - Token never stored raw; only SHA-256 hash.
    - 7 day expiry.
    - Single use (accepted_at set on accept).
    """

    id = models.CharField(
        primary_key=True, max_length=36, default=generate_uuid7, editable=False, db_index=True
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="invitations"
    )
    invited_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="sent_invitations")
    email = models.EmailField(max_length=255, db_index=True)
    role = models.CharField(max_length=20, choices=Membership.ROLE_CHOICES)
    token_hash = models.CharField(max_length=128, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "invitation"
        verbose_name_plural = "invitations"
        indexes = [models.Index(fields=["email", "organization"])]

    def __str__(self):
        return f"Invite {self.email} -> {self.organization.slug} ({self.role})"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_used(self):
        return self.accepted_at is not None
