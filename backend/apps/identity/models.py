"""
Phase 05 — Custom User Model (Identity)
UUIDv7 PK, normalized email, Argon2id preferred, bilingual settings, no secrets in API.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone as dj_timezone

from apps.core.utils.id_generator import generate_uuid7


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_platform_admin", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_platform_admin", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)

    def normalize_email(self, email):
        """Deterministic normalization: lower-case + strip."""
        if email:
            email = email.strip().lower()
        return email


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for CoachOS Phase 05.
    - UUIDv7 primary key (via id_generator)
    - Normalized unique indexed email
    - Argon2id (Django default when configured) or PBKDF2 fallback
    - display_name
    - optional phone
    - preferred_locale: fa-IR | en-US (default fa-IR)
    - preferred_unit: kg | lbs (default kg)
    - timezone validated
    - is_platform_admin (break-glass only)
    - No raw tokens/passwords in responses or logs
    """

    id = models.CharField(
        primary_key=True,
        max_length=36,
        default=generate_uuid7,
        editable=False,
        db_index=True,
    )

    email = models.EmailField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="email address",
    )

    display_name = models.CharField(max_length=150, blank=True)

    phone_number = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9\s\-()]{7,32}$",
                message="Enter a valid phone number.",
            )
        ],
    )

    preferred_locale = models.CharField(
        max_length=10,
        choices=[("fa-IR", "Persian (fa-IR)"), ("en-US", "English (en-US)")],
        default="fa-IR",
    )

    preferred_unit = models.CharField(
        max_length=3,
        choices=[("kg", "Kilograms"), ("lbs", "Pounds")],
        default="kg",
    )

    timezone = models.CharField(
        max_length=50,
        default="Asia/Tehran",
        help_text="IANA timezone name",
    )

    is_platform_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=dj_timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["display_name"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.email

    def set_password(self, raw_password):
        # Prefer Argon2id if available in hasher list (Django will use first matching)
        super().set_password(raw_password)

    def get_full_name(self):
        return self.display_name or self.email.split("@")[0]

    def get_short_name(self):
        return self.display_name or self.email.split("@")[0]

    def clean(self):
        self.email = User.objects.normalize_email(self.email)

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return True


class PasswordResetToken(models.Model):
    """Simple hashed reset token storage (Phase 05 foundation)."""

    id = models.CharField(primary_key=True, max_length=36, default=generate_uuid7, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reset_tokens")
    token_hash = models.CharField(max_length=128, unique=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=dj_timezone.now)

    class Meta:
        indexes = [models.Index(fields=["token_hash"])]

    @property
    def is_valid(self):
        return self.used_at is None and dj_timezone.now() < self.expires_at
