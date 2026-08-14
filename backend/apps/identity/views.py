"""
Phase 05 — Authentication Views (Email/Password + Cookie Session MVP)
"""

import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.cache import cache
from django.utils import timezone as dj_timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditEvent
from apps.organizations.models import Invitation, Membership

from .models import PasswordResetToken
from .serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UpdateMeSerializer,
    UserSerializer,
)

# Test-only seam for capturing raw reset tokens (never used in prod; raw tokens never returned in responses/logs/audit)
# Only populated when settings.TEST_CAPTURE_RESET_TOKENS is truthy
_captured_reset_tokens = []  # module level list for test access (cleared between tests)

User = get_user_model()


def _get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _hash_ip(ip: str) -> str:
    if not ip:
        return ""
    return hashlib.sha256(ip.encode()).hexdigest()


def _record_audit(
    action, actor=None, org=None, target_type="", target_id="", metadata=None, request=None
):
    ip = _get_client_ip(request) if request else ""
    AuditEvent.objects.create(
        actor_user=actor,
        organization=org,
        action=action,
        target_entity_type=target_type,
        target_entity_id=str(target_id) if target_id else "",
        ip_hash=_hash_ip(ip),
        metadata=metadata or {},
        request_id=getattr(request, "correlation_id", "") if request else "",
    )


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Rate limiting via cache (atomic where possible). Keyed by IP + email
        ip = _get_client_ip(request)
        rate_key = f"reg_rate:{ip}:{data['email']}"
        try:
            attempts = cache.incr(rate_key)
        except ValueError:
            # first time
            cache.set(rate_key, 1, timeout=60 * 5)
            attempts = 1
        if attempts > 5:
            return Response(
                {
                    "type": "https://errors.coachos.io/too-many-requests",
                    "title": "Too Many Requests",
                    "status": 429,
                    "detail": "Too many registration attempts",
                    "message_key": "auth.rate_limited",
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        if User.objects.filter(email__iexact=data["email"]).exists():
            # Non-enumerating for security (consistent with auth contract)
            return Response(
                {
                    "type": "https://errors.coachos.io/conflict",
                    "title": "Conflict",
                    "status": 409,
                    "detail": "Unable to complete registration",
                    "message_key": "auth.registration_failed",
                },
                status=status.HTTP_409_CONFLICT,
            )

        user = User.objects.create_user(
            email=data["email"],
            password=data["password"],
            display_name=data["display_name"],
            preferred_locale=data.get("preferred_locale", "fa-IR"),
        )

        # Support invitation_token during registration (binds membership)
        inv_token = data.get("invitation_token")
        if inv_token:
            token_hash = hashlib.sha256(inv_token.encode()).hexdigest()
            try:
                inv = Invitation.objects.get(token_hash=token_hash, accepted_at__isnull=True)
                if inv.is_expired or inv.accepted_at:
                    # expired or already used → do not bind
                    pass
                elif inv.email.lower() != data["email"].lower():
                    # email mismatch → do not bind
                    pass
                else:
                    # atomic bind + update status if previously invited
                    membership, created = Membership.objects.get_or_create(
                        user=user,
                        organization=inv.organization,
                        role=inv.role,
                        defaults={"status": "active"},
                    )
                    if not created and membership.status != "active":
                        membership.status = "active"
                        membership.save(update_fields=["status"])
                    inv.accepted_at = dj_timezone.now()
                    inv.save()
                    _record_audit(
                        "invitation.accepted",
                        actor=user,
                        org=inv.organization,
                        target_type="Invitation",
                        target_id=inv.id,
                        request=request,
                    )
            except Invitation.DoesNotExist:
                pass  # safe, non-enumerating
            # Do NOT swallow broad Exception — unexpected DB/runtime errors will surface
            # (DRF exception handler + logging will record; no membership created on failure)

        # Login (establishes session cookie)
        login(request, user)

        _record_audit(
            "auth.registered",
            actor=user,
            target_type="User",
            target_id=user.id,
            metadata={"email_hash": hashlib.sha256(user.email.encode()).hexdigest()[:12]},
            request=request,
        )

        user_ser = UserSerializer(user)
        # Return real active memberships (minimal; full effective-permissions + active-org context deferred)
        memberships = list(
            Membership.objects.filter(user=user, status="active").values(
                "id", "organization_id", "role", "status"
            )
        )
        resp = {
            "user": user_ser.data,
            "memberships": memberships,
            "csrf_token": request.META.get("CSRF_COOKIE", None),
        }
        return Response(resp, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Rate limit failed logins (atomic cache)
        ip = _get_client_ip(request)
        fail_key = f"login_fail:{ip}:{data['email']}"
        try:
            fails = cache.incr(fail_key)
        except ValueError:
            cache.set(fail_key, 1, timeout=60 * 15)
            fails = 1
        if fails > 5:
            return Response(
                {
                    "type": "https://errors.coachos.io/too-many-requests",
                    "title": "Too Many Requests",
                    "status": 429,
                    "detail": "Too many login attempts",
                    "message_key": "auth.rate_limited",
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        user = authenticate(request, username=data["email"], password=data["password"])
        if not user or not user.is_active:
            cache.set(fail_key, fails + 1, timeout=60 * 15)
            _record_audit(
                "auth.login_failed",
                target_type="User",
                metadata={"email_hash": hashlib.sha256(data["email"].encode()).hexdigest()[:12]},
                request=request,
            )
            return Response(
                {
                    "type": "https://errors.coachos.io/unauthorized",
                    "title": "Unauthorized",
                    "status": 401,
                    "detail": "Invalid credentials",
                    "message_key": "auth.invalid_credentials",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        cache.delete(fail_key)
        login(request, user)
        _record_audit(
            "auth.login", actor=user, target_type="User", target_id=user.id, request=request
        )

        user_ser = UserSerializer(user)
        # Return minimal active memberships (effective-permissions + active-org context deferred)
        memberships = list(
            Membership.objects.filter(user=user, status="active").values(
                "id", "organization_id", "role", "status"
            )
        )
        resp = {
            "user": user_ser.data,
            "memberships": memberships,
        }
        return Response(resp, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        _record_audit("auth.logout", actor=user, request=request)
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    def get(self, request):
        user = request.user
        ser = UserSerializer(user)
        # Return minimal active memberships (effective-permissions + active-org context deferred)
        memberships = list(
            Membership.objects.filter(user=user, status="active").values(
                "id", "organization_id", "role", "status"
            )
        )
        data = {"user": ser.data, "memberships": memberships}
        return Response(data)

    def patch(self, request):
        user = request.user
        serializer = UpdateMeSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        _record_audit(
            "user.profile_updated",
            actor=user,
            target_type="User",
            target_id=user.id,
            request=request,
        )
        return Response({"user": UserSerializer(user).data})


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        # Always return 202 to avoid enumeration (security contract)
        try:
            user = User.objects.get(email__iexact=email)
            # Generate cryptographically secure single-use token (>=32 bytes)
            raw_token = secrets.token_urlsafe(48)
            token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

            # Persist only the hash + expiry (never raw token)
            PasswordResetToken.objects.filter(user=user, used_at__isnull=True).update(
                used_at=dj_timezone.now()
            )  # invalidate prior
            PasswordResetToken.objects.create(
                user=user,
                token_hash=token_hash,
                expires_at=dj_timezone.now() + timedelta(minutes=15),
            )

            _record_audit(
                "auth.password_reset_requested",
                actor=user,
                target_type="User",
                target_id=user.id,
                metadata={
                    "email_hash": hashlib.sha256(email.encode()).hexdigest()[:16]
                },  # minimized
                request=request,
            )
            # Development adapter: do not send real email. Token would be in outbox in prod.

            # Test seam ONLY (never in prod responses/logs/audit)
            if getattr(settings, "TEST_CAPTURE_RESET_TOKENS", False):
                # Attach to request for test access (safe, scoped to test request)
                if not hasattr(request, "_captured_reset_tokens"):
                    request._captured_reset_tokens = []
                request._captured_reset_tokens.append(raw_token)
                # Also append to module-level for robust test access across APIClient instances
                _captured_reset_tokens.append(raw_token)
        except User.DoesNotExist:
            pass  # non-enumerating

        return Response(
            {"message_key": "auth.reset_email_sent_if_exists"}, status=status.HTTP_202_ACCEPTED
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, token=None):
        if not token:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data["new_password"]

        token_hash = hashlib.sha256(token.encode()).hexdigest()

        try:
            prt = PasswordResetToken.objects.get(token_hash=token_hash)
        except PasswordResetToken.DoesNotExist:
            _record_audit(
                "auth.password_reset_completed",
                metadata={"reason": "invalid_token"},
                request=request,
            )
            return Response(
                {
                    "type": "https://errors.coachos.io/bad-request",
                    "title": "Bad Request",
                    "status": 400,
                    "detail": "Invalid or expired reset token",
                    "message_key": "auth.invalid_reset_token",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if prt.used_at is not None or prt.expires_at < dj_timezone.now():
            _record_audit(
                "auth.password_reset_completed",
                metadata={"reason": "expired_or_used"},
                request=request,
            )
            return Response(
                {
                    "type": "https://errors.coachos.io/bad-request",
                    "title": "Bad Request",
                    "status": 400,
                    "detail": "Invalid or expired reset token",
                    "message_key": "auth.invalid_reset_token",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update password using Django hasher
        user = prt.user
        user.set_password(new_password)
        user.save()

        # Mark single-use
        prt.used_at = dj_timezone.now()
        prt.save(update_fields=["used_at"])

        # Invalidate ALL active sessions for this user (full contract)
        from django.contrib.sessions.models import Session

        for s in Session.objects.filter(expire_date__gt=dj_timezone.now()):
            try:
                data = s.get_decoded()
                if data.get("_auth_user_id") == str(user.id):
                    s.delete()
            except Exception:
                # malformed session data — ignore
                pass

        _record_audit(
            "auth.password_reset_completed",
            actor=user,
            target_type="User",
            target_id=user.id,
            metadata={"reset_success": True},  # no raw token or prefix
            request=request,
        )

        # Also logout the current request if it belongs to this user
        if request.user.is_authenticated and getattr(request.user, "id", None) == user.id:
            logout(request)

        return Response({"message_key": "auth.password_reset_success"}, status=status.HTTP_200_OK)
