"""Program builder, template clone, and immutable assignment APIs."""

from copy import deepcopy

from django.db import transaction
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditEvent
from apps.identity.models import User
from apps.identity.permissions import IsAuthenticatedAndActive
from apps.organizations.models import Membership, Organization

from .models import CoachAthleteAssignment, Program, ProgramAssignment
from .serializers import (
    ProgramAssignmentSerializer,
    ProgramSerializer,
    program_queryset,
    snapshot_program,
)


def _membership(user, organization, roles=None):
    query = Membership.objects.filter(user=user, organization=organization, status="active")
    if roles:
        query = query.filter(role__in=roles)
    return query.first()


def _org(org_id):
    return Organization.objects.filter(id=org_id, archived_at__isnull=True).first()


def _active_roles(user, organization):
    if not organization:
        return set()
    return set(
        Membership.objects.filter(
            user=user, organization=organization, status="active"
        ).values_list("role", flat=True)
    )


def _audit(action, request, organization, target_type, target_id):
    AuditEvent.objects.create(
        actor_user=request.user,
        organization=organization,
        action=action,
        target_entity_type=target_type,
        target_entity_id=target_id,
        metadata={},
        request_id=getattr(request, "correlation_id", ""),
    )


class ProgramListCreateView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        organization = _org(request.query_params.get("org_id"))
        if not organization or not _membership(request.user, organization, ["owner", "coach"]):
            return Response(status=status.HTTP_403_FORBIDDEN)
        programs = Program.objects.filter(organization=organization, is_archived=False)
        template = request.query_params.get("is_template")
        if template in {"true", "false"}:
            programs = programs.filter(is_template=template == "true")
        data = [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "target_goal": item.target_goal,
                "is_template": item.is_template,
                "version": item.version,
                "updated_at": item.updated_at,
            }
            for item in programs.order_by("-updated_at")[:100]
        ]
        return Response({"programs": data, "count": len(data)})

    def post(self, request):
        organization = _org(request.data.get("org_id"))
        if not organization or not _membership(request.user, organization, ["owner", "coach"]):
            return Response(status=status.HTTP_403_FORBIDDEN)
        payload = request.data.copy()
        payload.pop("org_id", None)
        serializer = ProgramSerializer(data=payload, context={"organization": organization})
        serializer.is_valid(raise_exception=True)
        program = serializer.save(organization=organization, created_by_user=request.user)
        _audit("program.created", request, organization, "Program", program.id)
        program = program_queryset().get(id=program.id)
        return Response(ProgramSerializer(program).data, status=status.HTTP_201_CREATED)


class ProgramDetailView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def _get(self, request, program_id):
        program = program_queryset().filter(id=program_id, is_archived=False).first()
        if not program or not _membership(request.user, program.organization, ["owner", "coach"]):
            return None
        return program

    def get(self, request, program_id):
        program = self._get(request, program_id)
        if not program:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(ProgramSerializer(program).data)

    def patch(self, request, program_id):
        program = self._get(request, program_id)
        if not program:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProgramSerializer(
            program,
            data=request.data,
            partial=True,
            context={"organization": program.organization},
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        _audit("program.updated", request, program.organization, "Program", program.id)
        return Response(ProgramSerializer(program_queryset().get(id=updated.id)).data)


class ProgramCloneView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    @transaction.atomic
    def post(self, request, program_id):
        source = (
            program_queryset().select_for_update().filter(id=program_id, is_archived=False).first()
        )
        if not source or not _membership(request.user, source.organization, ["owner", "coach"]):
            return Response(status=status.HTTP_404_NOT_FOUND)
        payload = deepcopy(ProgramSerializer(source).data)
        payload["title"] = request.data.get("title") or f"{source.title} — Copy"
        payload["is_template"] = bool(request.data.get("is_template", False))
        for key in (
            "id",
            "organization_id",
            "created_by_user_id",
            "version",
            "created_at",
            "updated_at",
        ):
            payload.pop(key, None)
        serializer = ProgramSerializer(data=payload, context={"organization": source.organization})
        serializer.is_valid(raise_exception=True)
        clone = serializer.save(organization=source.organization, created_by_user=request.user)
        _audit("template.cloned", request, source.organization, "Program", clone.id)
        return Response(
            ProgramSerializer(program_queryset().get(id=clone.id)).data,
            status=status.HTTP_201_CREATED,
        )


class CoachAthleteAssignmentView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request):
        organization = _org(request.data.get("org_id"))
        if not organization or not _membership(request.user, organization, ["owner"]):
            return Response(status=status.HTTP_403_FORBIDDEN)
        coach = User.objects.filter(id=request.data.get("coach_user_id"), is_active=True).first()
        athlete = User.objects.filter(
            id=request.data.get("athlete_user_id"), is_active=True
        ).first()
        if not coach or not athlete:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if not _membership(coach, organization, ["coach"]) or not _membership(
            athlete, organization, ["athlete"]
        ):
            return Response(
                {"detail": "Active coach and athlete memberships are required."}, status=400
            )
        relation, _ = CoachAthleteAssignment.objects.update_or_create(
            organization=organization,
            coach_user=coach,
            athlete_user=athlete,
            defaults={"is_active": True},
        )
        _audit(
            "coach_athlete.assigned",
            request,
            organization,
            "CoachAthleteAssignment",
            relation.id,
        )
        return Response(
            {
                "id": relation.id,
                "organization_id": organization.id,
                "coach_user_id": coach.id,
                "athlete_user_id": athlete.id,
                "is_active": relation.is_active,
            },
            status=status.HTTP_201_CREATED,
        )


class ProgramAssignmentView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        organization = _org(request.query_params.get("org_id"))
        roles = _active_roles(request.user, organization)
        if not organization or not roles:
            return Response(status=status.HTTP_403_FORBIDDEN)
        query = ProgramAssignment.objects.filter(organization=organization)
        athlete_id = request.query_params.get("athlete_id")
        # Effective permissions are the union of active roles, with owner scope
        # taking precedence over coach and athlete restrictions.
        if "owner" in roles:
            pass
        elif "coach" in roles:
            allowed = CoachAthleteAssignment.objects.filter(
                organization=organization, coach_user=request.user, is_active=True
            ).values_list("athlete_user_id", flat=True)
            query = query.filter(athlete_user_id__in=allowed)
        elif "athlete" in roles:
            query = query.filter(athlete_user=request.user)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if athlete_id:
            query = query.filter(athlete_user_id=athlete_id)
        data = ProgramAssignmentSerializer(query.order_by("-created_at")[:100], many=True).data
        return Response({"assignments": data, "count": len(data)})

    @transaction.atomic
    def post(self, request):
        organization = _org(request.data.get("org_id"))
        roles = _active_roles(request.user, organization)
        if not organization or not roles.intersection({"owner", "coach"}):
            return Response(status=status.HTTP_403_FORBIDDEN)
        athlete = User.objects.filter(
            id=request.data.get("athlete_user_id"), is_active=True
        ).first()
        if not athlete or not _membership(athlete, organization, ["athlete"]):
            return Response(
                {"athlete_user_id": ["Active organization athlete required."]}, status=400
            )
        if (
            "owner" not in roles
            and "coach" in roles
            and not CoachAthleteAssignment.objects.filter(
                organization=organization,
                coach_user=request.user,
                athlete_user=athlete,
                is_active=True,
            ).exists()
        ):
            return Response(status=status.HTTP_403_FORBIDDEN)
        program = (
            program_queryset()
            .select_for_update()
            .filter(
                id=request.data.get("source_program_id"),
                organization=organization,
                is_archived=False,
            )
            .first()
        )
        if not program:
            return Response({"source_program_id": ["Program not found."]}, status=400)
        date_serializer = _AssignmentInputSerializer(data=request.data)
        date_serializer.is_valid(raise_exception=True)
        assignment = ProgramAssignment(
            organization=organization,
            athlete_user=athlete,
            assigned_by_user=request.user,
            source_program=program,
            source_program_version=program.version,
            start_date=date_serializer.validated_data["start_date"],
            end_date=date_serializer.validated_data.get("end_date"),
            snapshot_payload=snapshot_program(program),
        )
        assignment.full_clean()
        assignment.save()
        _audit("program.assigned", request, organization, "ProgramAssignment", assignment.id)
        return Response(
            ProgramAssignmentSerializer(assignment).data, status=status.HTTP_201_CREATED
        )


class _AssignmentInputSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        if attrs.get("end_date") and attrs["end_date"] < attrs["start_date"]:
            raise serializers.ValidationError("End date cannot precede start date.")
        return attrs
