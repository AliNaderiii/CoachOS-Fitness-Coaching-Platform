"""
Phase 05 Organization, Location, Membership, Invitation endpoints.
"""

import hashlib
import secrets
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditEvent
from apps.identity.permissions import IsAuthenticatedAndActive
from .models import Organization, Location, Membership, Invitation
from .serializers import (
    CreateOrganizationSerializer,
    OrganizationSerializer,
    LocationSerializer,
    CreateInvitationSerializer,
    InvitationSerializer,
    MembershipSerializer,
)


def _record_audit(action, actor=None, org=None, target_type="", target_id="", metadata=None, request=None):
    ip = request.META.get("REMOTE_ADDR", "") if request else ""
    ip_hash = hashlib.sha256(ip.encode()).hexdigest() if ip else ""
    AuditEvent.objects.create(
        actor_user=actor,
        organization=org,
        action=action,
        target_entity_type=target_type,
        target_entity_id=str(target_id) if target_id else "",
        ip_hash=ip_hash,
        metadata=metadata or {},
        request_id=getattr(request, "correlation_id", "") if request else "",
    )


class OrganizationListCreateView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        user = request.user
        orgs = Organization.objects.filter(memberships__user=user, memberships__status="active").distinct()
        data = OrganizationSerializer(orgs, many=True).data
        return Response({"organizations": data})

    def post(self, request):
        serializer = CreateOrganizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user

        # Create org + primary location + owner membership in one transaction
        from django.db import transaction

        with transaction.atomic():
            org = Organization.objects.create(
                name=data["name"],
                slug=data["slug"],
                owner_user=user,
                settings={"default_locale": user.preferred_locale, "default_unit": user.preferred_unit},
            )

            # Primary location
            loc_data = data.get("primary_location", {"name": "Main Facility"})
            Location.objects.create(
                organization=org,
                name=loc_data.get("name", "Main Facility"),
                address_line1=loc_data.get("address_line1"),
                city=loc_data.get("city"),
                phone=loc_data.get("phone"),
                is_primary=True,
            )

            # Owner membership
            Membership.objects.create(
                user=user,
                organization=org,
                role="owner",
                status="active",
            )

        _record_audit("org.created", actor=user, org=org, target_type="Organization", target_id=org.id, request=request)

        return Response(OrganizationSerializer(org).data, status=status.HTTP_201_CREATED)


class OrganizationDetailView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, org_id):
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Server-side membership check
        if not Membership.objects.filter(user=request.user, organization=org, status="active").exists():
            return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(OrganizationSerializer(org).data)

    def patch(self, request, org_id):
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        mem = Membership.objects.filter(user=request.user, organization=org, role="owner", status="active").first()
        if not mem:
            return Response(status=status.HTTP_403_FORBIDDEN)

        org.name = request.data.get("name", org.name)
        if "settings" in request.data:
            org.settings.update(request.data["settings"])
        org.save()

        _record_audit("org.settings_updated", actor=request.user, org=org, target_type="Organization", target_id=org.id, request=request)
        return Response(OrganizationSerializer(org).data)


class LocationView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, org_id):
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not Membership.objects.filter(user=request.user, organization=org, status="active").exists():
            return Response(status=status.HTTP_403_FORBIDDEN)

        loc = org.locations.filter(is_primary=True).first()
        if not loc:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(LocationSerializer(loc).data)

    def patch(self, request, org_id):
        # Owner only
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        mem = Membership.objects.filter(user=request.user, organization=org, role="owner", status="active").first()
        if not mem:
            return Response(status=status.HTTP_403_FORBIDDEN)

        loc = org.locations.filter(is_primary=True).first()
        if not loc:
            return Response(status=status.HTTP_404_NOT_FOUND)

        for field in ["name", "address_line1", "city", "phone"]:
            if field in request.data:
                setattr(loc, field, request.data[field])
        loc.save()
        return Response(LocationSerializer(loc).data)


class InvitationListCreateView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, org_id):
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        mem = Membership.objects.filter(user=request.user, organization=org, status="active").first()
        if not mem:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Permission: owner any role, coach athlete only
        if mem.role not in ["owner", "coach"]:
            return Response(status=status.HTTP_403_FORBIDDEN)

        ser = CreateInvitationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        if mem.role == "coach" and d["role"] != "athlete":
            return Response({"detail": "Coach may only invite athletes"}, status=status.HTTP_403_FORBIDDEN)

        raw_token = secrets.token_urlsafe(48)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

        inv = Invitation.objects.create(
            organization=org,
            invited_by=request.user,
            email=d["email"],
            role=d["role"],
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(days=7),
        )

        _record_audit("invitation.created", actor=request.user, org=org, target_type="Invitation", target_id=inv.id, request=request)
        # In production: send via outbox (raw_token only in email)

        return Response(InvitationSerializer(inv).data, status=status.HTTP_201_CREATED)

    def get(self, request, org_id):
        # Owner only for listing
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        mem = Membership.objects.filter(user=request.user, organization=org, role="owner", status="active").first()
        if not mem:
            return Response(status=status.HTTP_403_FORBIDDEN)

        invites = Invitation.objects.filter(organization=org, accepted_at__isnull=True)
        return Response({"invitations": InvitationSerializer(invites, many=True).data})


class AcceptInvitationView(APIView):
    permission_classes = [AllowAny]  # public for token use
    authentication_classes = []

    def post(self, request, token):
        # Find by hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        try:
            inv = Invitation.objects.get(token_hash=token_hash)
        except Invitation.DoesNotExist:
            return Response(status=status.HTTP_410_GONE)

        if inv.is_used or inv.is_expired:
            return Response(status=status.HTTP_410_GONE)

        # Create / activate membership (transactional)
        from django.db import transaction

        with transaction.atomic():
            user = request.user if request.user.is_authenticated else None
            # For simplicity in scaffold assume user already registered or create placeholder
            # In full flow user registers first or accepts during registration
            if not user:
                return Response({"detail": "Must be authenticated or register first"}, status=status.HTTP_401_UNAUTHORIZED)

            Membership.objects.get_or_create(
                user=user,
                organization=inv.organization,
                role=inv.role,
                defaults={"status": "active"},
            )
            inv.accepted_at = timezone.now()
            inv.save()

        _record_audit("invitation.accepted", actor=user, org=inv.organization, target_type="Invitation", target_id=inv.id, request=request)
        return Response({"message_key": "invitation.accepted"}, status=status.HTTP_200_OK)


class MemberListView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, org_id):
        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not Membership.objects.filter(user=request.user, organization=org, status="active").exists():
            return Response(status=status.HTTP_403_FORBIDDEN)

        members = Membership.objects.filter(organization=org)
        return Response({"members": MembershipSerializer(members, many=True).data})


class MembershipUpdateView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def patch(self, request, org_id, membership_id):
        try:
            org = Organization.objects.get(id=org_id)
            mem = Membership.objects.get(id=membership_id, organization=org)
        except (Organization.DoesNotExist, Membership.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Only owner
        owner_mem = Membership.objects.filter(user=request.user, organization=org, role="owner", status="active").first()
        if not owner_mem:
            return Response(status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get("status")
        if new_status in dict(Membership.STATUS_CHOICES):
            old = mem.status
            mem.status = new_status
            mem.save()
            _record_audit(
                "membership.status_changed",
                actor=request.user,
                org=org,
                target_type="Membership",
                target_id=mem.id,
                metadata={"old": old, "new": new_status},
                request=request,
            )
            return Response(MembershipSerializer(mem).data)

        return Response(status=status.HTTP_400_BAD_REQUEST)
