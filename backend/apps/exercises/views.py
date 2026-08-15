"""Exercise catalog APIs with fail-closed organization and moderation authorization."""

from django.db import transaction
from django.db.models import Case, IntegerField, Q, Value, When
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditEvent
from apps.core.utils.persian_normalizer import PersianNormalizer
from apps.identity.permissions import IsAuthenticatedAndActive
from apps.organizations.models import Membership, Organization

from .models import Exercise
from .serializers import ExerciseSerializer


def _active_membership(user, org, roles=None):
    query = Membership.objects.filter(user=user, organization=org, status="active")
    if roles:
        query = query.filter(role__in=roles)
    return query.exists()


def _audit(action, request, exercise):
    AuditEvent.objects.create(
        actor_user=request.user,
        organization=exercise.organization,
        action=action,
        target_entity_type="Exercise",
        target_entity_id=exercise.id,
        metadata={},
        request_id=getattr(request, "correlation_id", ""),
    )


def _catalog_queryset(org):
    return (
        Exercise.objects.filter(Q(organization__isnull=True) | Q(organization=org))
        .exclude(status__in=["archived", "rejected"])
        .prefetch_related("translations", "aliases", "media_assets__rights")
        .distinct()
    )


class ExerciseListCreateView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def _org(self, request):
        org_id = request.query_params.get("org_id") or request.data.get("org_id")
        try:
            return Organization.objects.get(id=org_id)
        except (Organization.DoesNotExist, TypeError, ValueError):
            return None

    def get(self, request):
        org = self._org(request)
        if not org or not _active_membership(request.user, org):
            return Response(status=status.HTTP_403_FORBIDDEN)

        queryset = _catalog_queryset(org).filter(status="published")
        locale = request.query_params.get("locale")
        if locale:
            if locale not in {"fa-IR", "en-US"}:
                return Response({"locale": ["Use fa-IR or en-US."]}, status=400)
            queryset = queryset.filter(translations__locale=locale)
        movement = request.query_params.get("movement_pattern")
        if movement:
            queryset = queryset.filter(movement_pattern=movement)
        difficulty = request.query_params.get("difficulty")
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        query = PersianNormalizer.normalize(request.query_params.get("q", ""))
        if query:
            queryset = (
                queryset.filter(
                    Q(translations__normalized_name__icontains=query)
                    | Q(aliases__normalized_alias__icontains=query)
                )
                .annotate(
                    search_rank=Case(
                        When(translations__normalized_name=query, then=Value(0)),
                        When(aliases__normalized_alias=query, then=Value(1)),
                        default=Value(2),
                        output_field=IntegerField(),
                    )
                )
                .order_by("search_rank", "created_at")
            )
        else:
            queryset = queryset.order_by("created_at")

        muscle = request.query_params.get("muscle")
        equipment = request.query_params.get("equipment")
        # Joins across translations and aliases can yield duplicate rows with different
        # relevance annotations; preserve ranked order while de-duplicating by entity.
        results = list(queryset[:201])
        results = list({item.id: item for item in results}.values())
        if muscle:
            results = [item for item in results if muscle in item.primary_muscles]
        if equipment:
            results = [item for item in results if equipment in item.equipment_required]
        results = results[:100]
        return Response(
            {"exercises": ExerciseSerializer(results, many=True).data, "count": len(results)}
        )

    def post(self, request):
        org = self._org(request)
        if not org or not _active_membership(request.user, org, ["owner", "coach"]):
            return Response(status=status.HTTP_403_FORBIDDEN)
        payload = request.data.copy()
        payload.pop("org_id", None)
        serializer = ExerciseSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        exercise = serializer.save(
            organization=org, created_by_user=request.user, status="published"
        )
        _audit("exercise.created_private", request, exercise)
        return Response(ExerciseSerializer(exercise).data, status=status.HTTP_201_CREATED)


class ExerciseDetailView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, exercise_id):
        org_id = request.query_params.get("org_id")
        try:
            org = Organization.objects.get(id=org_id)
        except (Organization.DoesNotExist, TypeError, ValueError):
            return Response(status=status.HTTP_403_FORBIDDEN)
        if not _active_membership(request.user, org):
            return Response(status=status.HTTP_403_FORBIDDEN)
        exercise = _catalog_queryset(org).filter(id=exercise_id, status="published").first()
        if not exercise:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(ExerciseSerializer(exercise).data)


class ExerciseModerationView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def _authorized(self, request):
        return bool(request.user.is_platform_admin)

    def get(self, request):
        if not self._authorized(request):
            return Response(status=status.HTTP_403_FORBIDDEN)
        queue = (
            Exercise.objects.filter(status="pending_review")
            .prefetch_related("translations", "aliases", "media_assets__rights")
            .order_by("created_at")[:100]
        )
        return Response({"exercises": ExerciseSerializer(queue, many=True).data})

    @transaction.atomic
    def post(self, request):
        if not self._authorized(request):
            return Response(status=status.HTTP_403_FORBIDDEN)
        exercise = (
            Exercise.objects.select_for_update()
            .filter(id=request.data.get("exercise_id"), status="pending_review")
            .first()
        )
        if not exercise:
            return Response(status=status.HTTP_404_NOT_FOUND)
        decision = request.data.get("decision")
        if decision not in {"approve", "reject"}:
            return Response({"decision": ["Use approve or reject."]}, status=400)
        if decision == "approve":
            if set(exercise.translations.values_list("locale", flat=True)) != {"fa-IR", "en-US"}:
                return Response({"detail": "Both translations are required."}, status=409)
            assets = list(exercise.media_assets.select_related("rights"))
            if not assets:
                return Response(
                    {"detail": "At least one reviewed media asset is required."}, status=409
                )
            for asset in assets:
                rights = getattr(asset, "rights", None)
                if not rights or not rights.permitted_commercial_use:
                    return Response({"detail": "Commercial media rights are required."}, status=409)
                rights.reviewed_by_user = request.user
                rights.reviewed_at = timezone.now()
                rights.full_clean()
                rights.save(update_fields=["reviewed_by_user", "reviewed_at"])
            exercise.status = "published"
            action = "exercise.published"
        else:
            exercise.status = "rejected"
            action = "exercise.rejected"
        exercise.save(update_fields=["status", "updated_at"])
        _audit(action, request, exercise)
        return Response({"status": exercise.status, "message_key": action})
