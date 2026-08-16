"""
Phase 07 athlete execution, progress, and consent APIs.

Authorization model (server-authoritative):
- Athlete self: full access to own data.
- Assigned coach: read-only access to assigned athlete sessions; consent-gated
  access to progress photos and body metrics; may view (not write) feedback flags.
- Owner: read access within org; consent-gated + audited for sensitive media.
- Support and unrelated users: denied (403/404, no leakage).
- Cross-tenant IDs resolve to safe 403/404.
"""

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.models import AuditEvent
from apps.exercises.models import Exercise
from apps.identity.models import User
from apps.identity.permissions import IsAuthenticatedAndActive
from apps.organizations.models import Organization
from apps.programs.models import CoachAthleteAssignment, ProgramAssignment

from . import snapshot_utils
from .models import (
    BodyMetric,
    ConsentRecord,
    ProgressPhoto,
    SetLog,
    WorkoutSession,
)
from .serializers import (
    BodyMetricSerializer,
    CompleteSessionInputSerializer,
    ConsentRecordSerializer,
    CreateConsentInputSerializer,
    FeedbackFlagSerializer,
    ProgressPhotoSerializer,
    SetLogSerializer,
    StartSessionInputSerializer,
    SubstitutionSerializer,
    UploadProgressPhotoInputSerializer,
    WorkoutSessionSerializer,
)
from .storage import storage_adapter


def _active_roles(user, organization):
    if not organization or not user.is_authenticated:
        return set()
    from apps.organizations.models import Membership

    return set(
        Membership.objects.filter(
            user=user, organization=organization, status="active"
        ).values_list("role", flat=True)
    )


def _has_active_membership(user, organization):
    """Explicit shared helper: every execution endpoint must verify active membership."""
    if not organization or not user.is_authenticated:
        return False
    from apps.organizations.models import Membership

    return Membership.objects.filter(user=user, organization=organization, status="active").exists()


def _coach_assigned_to(coach, athlete, organization=None):
    """Organization-aware assignment lookup to prevent cross-tenant authorization."""
    qs = CoachAthleteAssignment.objects.filter(
        coach_user=coach, athlete_user=athlete, is_active=True
    )
    if organization is not None:
        qs = qs.filter(organization=organization)
    return qs.exists()


def _audit(request, organization, action, target_type, target_id, metadata=None):
    AuditEvent.objects.create(
        actor_user=request.user,
        organization=organization,
        action=action,
        target_entity_type=target_type,
        target_entity_id=target_id,
        metadata=metadata or {},
        request_id=getattr(request, "correlation_id", ""),
    )


def _exercise_visible(exercise, org):
    return (
        exercise is not None
        and exercise.status == "published"
        and (exercise.organization_id is None or exercise.organization_id == org.id)
    )


def _translation_name(exercise, locale):
    translations = exercise.translations.all()
    for item in translations:
        if item.locale == locale:
            return item.name
    for item in translations:
        return item.name
    return str(exercise.id)


def _present_workout(workout, locale):
    """Present a snapshot workout item list for the athlete UI (no DB N+1)."""
    items = []
    for item in workout.get("items") or []:
        exercise = item.get("exercise") or {}
        name = None
        for translation in exercise.get("translations") or []:
            if translation.get("locale") == locale:
                name = translation.get("name")
                break
        if name is None:
            for translation in exercise.get("translations") or []:
                name = translation.get("name")
                break
        items.append(
            {
                "exercise_id": item.get("exercise_id"),
                "name": name or str(item.get("exercise_id")),
                "group_key": item.get("group_key"),
                "segment": item.get("segment"),
                "rest_seconds_between_sets": item.get("rest_seconds_between_sets"),
                "coach_notes": item.get("coach_notes"),
                "prescriptions": item.get("prescriptions") or [],
            }
        )
    return {
        "workout_id": workout.get("id"),
        "title": workout.get("title"),
        "estimated_minutes": workout.get("estimated_minutes"),
        "sequence_order": workout.get("sequence_order"),
        "items": items,
    }


def _session_exercise_ids(session):
    """Set of exercise ids scheduled in the session's workout plus substitutions."""
    ids = set()
    for workout in snapshot_utils.workouts_for_date(
        session.program_assignment.snapshot_payload,
        session.program_assignment.start_date,
        session.scheduled_date,
    ):
        for item in workout.get("items") or []:
            if item.get("exercise_id"):
                ids.add(item["exercise_id"])
    for sub in session.substitutions.all():
        ids.add(sub.substituted_exercise_id)
    return ids


def _sensitive_scope(request, org, athlete, consent_type=None):
    """
    Return (allowed, level, needs_audit).
    level: self | coach | owner. consent_type None => coach/owner may view flags.
    Enforces active membership in the target organization.
    """
    user = request.user
    if not _has_active_membership(user, org):
        return (False, "none", False)
    if user.id == athlete.id:
        return (True, "self", False)
    roles = _active_roles(user, org)
    if not roles:
        return (False, "none", False)
    is_assigned = _coach_assigned_to(user, athlete, organization=org)
    is_owner = "owner" in roles
    if not (is_assigned or is_owner):
        return (False, "none", False)
    if consent_type is not None:
        consent_active = ConsentRecord.objects.filter(
            athlete_user=athlete,
            grantee_user=user,
            consent_type=consent_type,
            is_granted=True,
            revoked_at__isnull=True,
        ).exists()
        if not consent_active:
            return (False, "none", False)
    return (True, "owner" if is_owner and not is_assigned else "coach", is_owner)


class AthleteTodayView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        today = timezone.localdate()
        athlete = request.user
        # Enforce active membership on every execution endpoint
        # Find any active membership to determine org context
        from apps.organizations.models import Membership

        active_membership = Membership.objects.filter(user=athlete, status="active").first()
        if not active_membership:
            return Response(status=status.HTTP_403_FORBIDDEN)
        assignment = (
            ProgramAssignment.objects.filter(
                athlete_user=athlete,
                status="active",
                start_date__lte=today,
                organization=active_membership.organization,
            )
            .filter(models_end_date_none_or_gte(today))
            .order_by("-created_at")
            .first()
        )
        scheduled = []
        if assignment:
            workouts = snapshot_utils.workouts_for_date(
                assignment.snapshot_payload, assignment.start_date, today
            )
            session = WorkoutSession.objects.filter(
                program_assignment=assignment, scheduled_date=today
            ).first()
            for workout in workouts:
                scheduled.append(
                    {
                        "session_id": session.id if session else None,
                        "assignment_id": assignment.id,
                        "title": workout.get("title"),
                        "status": session.status if session else "scheduled",
                        "workout": _present_workout(workout, athlete.preferred_locale),
                    }
                )
        return Response({"date": today.isoformat(), "scheduled_workouts": scheduled})


def models_end_date_none_or_gte(today):
    from django.db.models import Q

    return Q(end_date__isnull=True) | Q(end_date__gte=today)


class WorkoutSessionListCreateView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    @transaction.atomic
    def post(self, request):
        today = timezone.localdate()
        input_serializer = StartSessionInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data
        if data["scheduled_date"] != today:
            return Response(
                {
                    "detail": "A session may only be started for today.",
                    "message_key": "errors.session.not_today",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        assignment = (
            ProgramAssignment.objects.select_for_update()
            .filter(
                id=data["program_assignment_id"],
                athlete_user=request.user,
                status="active",
                start_date__lte=today,
            )
            .filter(models_end_date_none_or_gte(today))
            .first()
        )
        if not assignment:
            return Response(
                {
                    "detail": "No active assignment.",
                    "message_key": "errors.authz.unassigned_athlete",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        # Suspended memberships must be denied even if an assignment still exists.
        if not _has_active_membership(request.user, assignment.organization):
            return Response(status=status.HTTP_403_FORBIDDEN)
        session, created = WorkoutSession.objects.get_or_create(
            program_assignment=assignment,
            scheduled_date=today,
            defaults={
                "organization_id": assignment.organization_id,
                "athlete_user_id": request.user.id,
                "status": "in_progress",
                "started_at": timezone.now(),
            },
        )
        if not created and session.status == "scheduled":
            session.transition("in_progress")
            session.save()
        _audit(request, assignment.organization, "session.started", "WorkoutSession", session.id)
        return Response(WorkoutSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class WorkoutSessionDetailView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def _session_for(self, request, session_id):
        session = (
            WorkoutSession.objects.select_related(
                "program_assignment", "athlete_user", "organization"
            )
            .filter(id=session_id)
            .first()
        )
        if not session:
            return None, None
        org = session.organization
        if not _has_active_membership(request.user, org):
            return None, None
        roles = _active_roles(request.user, org)
        is_self = session.athlete_user_id == request.user.id
        is_assigned = _coach_assigned_to(request.user, session.athlete_user, organization=org)
        is_owner = "owner" in roles
        if not (is_self or is_assigned or is_owner):
            return None, None
        return session, org

    def get(self, request, session_id):
        session, org = self._session_for(request, session_id)
        if not session:
            return Response(status=status.HTTP_404_NOT_FOUND)
        workouts = [
            _present_workout(w, request.user.preferred_locale)
            for w in snapshot_utils.workouts_for_date(
                session.program_assignment.snapshot_payload,
                session.program_assignment.start_date,
                session.scheduled_date,
            )
        ]
        data = WorkoutSessionSerializer(session).data
        data["workouts"] = workouts
        data["set_logs"] = [
            {
                "id": log.id,
                "exercise_id": log.exercise_id,
                "set_index": log.set_index,
                "actual_reps": log.actual_reps,
                "actual_load_kg": str(log.actual_load_kg),
                "actual_rpe": str(log.actual_rpe) if log.actual_rpe is not None else None,
                "is_completed": log.is_completed,
                "created_at": log.created_at.isoformat(),
            }
            for log in session.set_logs.all()
        ]
        return Response(data)

    @transaction.atomic
    def post(self, request, session_id):
        session, org = self._session_for(request, session_id)
        if not session:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if session.athlete_user_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        input_serializer = CompleteSessionInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data
        if session.status != "in_progress":
            return Response(
                {
                    "detail": "Only an in-progress session may be completed.",
                    "message_key": "errors.session.not_in_progress",
                },
                status=status.HTTP_409_CONFLICT,
            )
        session.transition(
            "completed",
            session_rpe=data.get("session_rpe"),
            fatigue_score=data.get("fatigue_score"),
            athlete_notes=data.get("athlete_notes"),
            skip_or_modify_reason=data.get("skip_or_modify_reason"),
        )
        session.save()
        _audit(request, org, "session.completed", "WorkoutSession", session.id)
        return Response(WorkoutSessionSerializer(session).data)


class SetLogView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def _session_for(self, request, session_id):
        session = (
            WorkoutSession.objects.select_related(
                "program_assignment", "athlete_user", "organization"
            )
            .filter(id=session_id)
            .first()
        )
        if not session:
            return None, None
        org = session.organization
        if not _has_active_membership(request.user, org):
            return None, None
        if session.athlete_user_id != request.user.id and not _coach_assigned_to(
            request.user, session.athlete_user, organization=org
        ):
            return None, None
        return session, org

    @transaction.atomic
    def post(self, request, session_id):
        session, org = self._session_for(request, session_id)
        if not session:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if session.status != "in_progress":
            return Response(
                {
                    "detail": "Only an in-progress session may accept set logs.",
                    "message_key": "errors.session.not_in_progress",
                },
                status=status.HTTP_409_CONFLICT,
            )
        serializer = SetLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        exercise_id = serializer.validated_data["exercise_id"]
        allowed_ids = _session_exercise_ids(session)
        if exercise_id not in allowed_ids:
            return Response(
                {
                    "detail": "Exercise is not scheduled in this session.",
                    "message_key": "errors.setlog.unknown_exercise",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        exercise = Exercise.objects.filter(id=exercise_id).first()
        if not _exercise_visible(exercise, org):
            return Response(
                {
                    "detail": "Exercise is unavailable.",
                    "message_key": "errors.exercise.unavailable",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        log, created = SetLog.objects.update_or_create(
            session=session,
            exercise_id=exercise_id,
            set_index=serializer.validated_data["set_index"],
            defaults={
                "actual_reps": serializer.validated_data["actual_reps"],
                "actual_load_kg": serializer.validated_data["actual_load_kg"],
                "actual_rpe": serializer.validated_data.get("actual_rpe"),
                "is_completed": serializer.validated_data.get("is_completed", True),
                "note": serializer.validated_data.get("note", ""),
            },
        )
        return Response(SetLogSerializer(log).data, status=status.HTTP_201_CREATED)


class SubstitutionView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    @transaction.atomic
    def post(self, request, session_id):
        session = (
            WorkoutSession.objects.select_related(
                "program_assignment", "athlete_user", "organization"
            )
            .filter(id=session_id)
            .first()
        )
        if not session:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if session.athlete_user_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if session.status != "in_progress":
            return Response(
                {
                    "detail": "Only an in-progress session may accept substitutions.",
                    "message_key": "errors.session.not_in_progress",
                },
                status=status.HTTP_409_CONFLICT,
            )
        serializer = SubstitutionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org = session.organization
        allowed_originals = _session_exercise_ids(session)
        if serializer.validated_data["original_exercise_id"] not in allowed_originals:
            return Response(
                {
                    "detail": "Original exercise is not scheduled in this session.",
                    "message_key": "errors.substitution.unknown_original",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        replacement = Exercise.objects.filter(
            id=serializer.validated_data["substituted_exercise_id"]
        ).first()
        if not _exercise_visible(replacement, org):
            return Response(
                {
                    "detail": "Replacement exercise is unavailable.",
                    "message_key": "errors.exercise.unavailable",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        substitution = serializer.save(session=session)
        _audit(request, org, "exercise.substituted", "Substitution", substitution.id)
        return Response(SubstitutionSerializer(substitution).data, status=status.HTTP_201_CREATED)


class FeedbackFlagView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    @transaction.atomic
    def post(self, request, session_id):
        session = (
            WorkoutSession.objects.select_related(
                "program_assignment", "athlete_user", "organization"
            )
            .filter(id=session_id)
            .first()
        )
        if not session:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if session.athlete_user_id != request.user.id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = FeedbackFlagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        flag = serializer.save(session=session, athlete_user=request.user)
        _audit(request, session.organization, "pain.flagged", "FeedbackFlag", flag.id)
        return Response(FeedbackFlagSerializer(flag).data, status=status.HTTP_201_CREATED)


class ProgressPhotoView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def _target(self, request, athlete_id):
        return User.objects.filter(id=athlete_id, is_active=True).first()

    def get(self, request, athlete_id):
        athlete = self._target(request, athlete_id)
        if not athlete:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # Resolve target org from the athlete's active membership in the context of the resource
        org = Organization.objects.filter(
            memberships__user=athlete,
            memberships__status="active",
            memberships__role="athlete",
        ).first()
        if not org or not _has_active_membership(request.user, org):
            return Response(status=status.HTTP_403_FORBIDDEN)
        allowed, level, needs_audit = _sensitive_scope(
            request, org, athlete, consent_type="progress_photo"
        )
        if not allowed:
            return Response(
                {"detail": "Forbidden.", "message_key": "errors.authz.forbidden"},
                status=status.HTTP_403_FORBIDDEN,
            )
        photos = ProgressPhoto.objects.filter(athlete_user=athlete)
        if level == "self":
            serializer = ProgressPhotoSerializer(
                photos, many=True, context={"include_signed_url": True}
            )
        else:
            serializer = ProgressPhotoSerializer(
                photos, many=True, context={"include_signed_url": True}
            )
            _audit(request, org, "photo.viewed", "ProgressPhoto", athlete.id)
        return Response({"photos": serializer.data})

    @transaction.atomic
    def post(self, request, athlete_id):
        if request.user.id != athlete_id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        athlete = request.user
        org = Organization.objects.filter(
            memberships__user=athlete, memberships__status="active", memberships__role="athlete"
        ).first()
        if not org or not _has_active_membership(athlete, org):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = UploadProgressPhotoInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        key = f"progress-photos/{athlete.id}/{_new_key()}"
        storage_adapter.put(
            key, data["file"], content_type=getattr(data["file"], "content_type", None)
        )
        photo = ProgressPhoto.objects.create(
            athlete_user=athlete,
            organization=org,
            storage_key=key,
            photo_type=data["photo_type"],
            consent_status=ConsentRecord.objects.filter(
                athlete_user=athlete, consent_type="progress_photo", is_granted=True
            ).exists(),
            captured_at=data.get("captured_at"),
        )
        _audit(request, org, "photo.uploaded", "ProgressPhoto", photo.id)
        return Response(
            ProgressPhotoSerializer(photo, context={"include_signed_url": True}).data,
            status=status.HTTP_201_CREATED,
        )


def _new_key():
    from apps.core.utils.id_generator import generate_uuid7

    return generate_uuid7()


class BodyMetricView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def _target(self, request, athlete_id):
        return User.objects.filter(id=athlete_id, is_active=True).first()

    def get(self, request, athlete_id):
        athlete = self._target(request, athlete_id)
        if not athlete:
            return Response(status=status.HTTP_404_NOT_FOUND)
        # Resolve target org from the athlete's active membership
        org = Organization.objects.filter(
            memberships__user=athlete,
            memberships__status="active",
            memberships__role="athlete",
        ).first()
        if not org or not _has_active_membership(request.user, org):
            return Response(status=status.HTTP_403_FORBIDDEN)
        allowed, level, needs_audit = _sensitive_scope(
            request, org, athlete, consent_type="body_metrics"
        )
        if not allowed:
            return Response(
                {"detail": "Forbidden.", "message_key": "errors.authz.forbidden"},
                status=status.HTTP_403_FORBIDDEN,
            )
        metrics = BodyMetric.objects.filter(athlete_user=athlete)
        serializer = BodyMetricSerializer(metrics, many=True)
        if level != "self":
            _audit(request, org, "metric.viewed", "BodyMetric", athlete.id)
        return Response({"metrics": serializer.data})

    @transaction.atomic
    def post(self, request, athlete_id):
        if request.user.id != athlete_id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        athlete = request.user
        org = Organization.objects.filter(
            memberships__user=athlete, memberships__status="active", memberships__role="athlete"
        ).first()
        if not org or not _has_active_membership(athlete, org):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = BodyMetricSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        metric = serializer.save(athlete_user=request.user, organization=org)
        _audit(request, org, "metric.recorded", "BodyMetric", metric.id)
        return Response(BodyMetricSerializer(metric).data, status=status.HTTP_201_CREATED)


class ConsentView(APIView):
    permission_classes = [IsAuthenticatedAndActive]

    def _grantee_allowed(self, org, athlete, grantee):
        if grantee.id == athlete.id:
            return False
        if _coach_assigned_to(grantee, athlete, organization=org):
            return True
        roles = _active_roles(grantee, org)
        return "owner" in roles

    def get(self, request):
        athlete_id = request.query_params.get("athlete_id")
        if not athlete_id:
            return Response(
                {"detail": "athlete_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        athlete = User.objects.filter(id=athlete_id, is_active=True).first()
        if not athlete:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.id == athlete.id:
            consents = ConsentRecord.objects.filter(athlete_user=athlete)
        else:
            # Resolve org from athlete's active membership (no arbitrary .first())
            org = Organization.objects.filter(
                memberships__user=athlete,
                memberships__status="active",
                memberships__role="athlete",
            ).first()
            if not org or not _has_active_membership(request.user, org):
                return Response(status=status.HTTP_403_FORBIDDEN)
            # Assigned coach may read only their own consent status for the athlete.
            if not _coach_assigned_to(request.user, athlete, organization=org):
                return Response(status=status.HTTP_403_FORBIDDEN)
            consents = ConsentRecord.objects.filter(athlete_user=athlete, grantee_user=request.user)
        return Response({"consents": ConsentRecordSerializer(consents, many=True).data})

    @transaction.atomic
    def post(self, request):
        serializer = CreateConsentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if request.user.id != data["athlete_user_id"]:
            return Response(status=status.HTTP_403_FORBIDDEN)
        athlete = request.user
        grantee = User.objects.filter(id=data["grantee_user_id"], is_active=True).first()
        org = Organization.objects.filter(
            memberships__user=athlete, memberships__status="active", memberships__role="athlete"
        ).first()
        if (
            not grantee
            or not org
            or not _has_active_membership(athlete, org)
            or not self._grantee_allowed(org, athlete, grantee)
        ):
            return Response(
                {
                    "detail": "Grantee must be an assigned coach or organization owner.",
                    "message_key": "errors.consent.grantee_invalid",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        record, _ = ConsentRecord.objects.update_or_create(
            athlete_user=athlete,
            grantee_user=grantee,
            consent_type=data["consent_type"],
            defaults={},
        )
        if data.get("is_granted", True):
            record.grant()
        else:
            record.revoke()
        record.save()
        _audit(
            request,
            org,
            "consent.granted" if record.is_granted else "consent.revoked",
            "ConsentRecord",
            record.id,
        )
        return Response(ConsentRecordSerializer(record).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def delete(self, request):
        athlete_id = request.query_params.get("athlete_id")
        grantee_id = request.query_params.get("grantee_id")
        consent_type = request.query_params.get("consent_type")
        if not (athlete_id and grantee_id and consent_type):
            return Response(
                {"detail": "athlete_id, grantee_id, and consent_type are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.id != athlete_id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        org = Organization.objects.filter(
            memberships__user=request.user,
            memberships__status="active",
            memberships__role="athlete",
        ).first()
        record = ConsentRecord.objects.filter(
            athlete_user_id=athlete_id,
            grantee_user_id=grantee_id,
            consent_type=consent_type,
        ).first()
        if not record:
            return Response(status=status.HTTP_404_NOT_FOUND)
        record.revoke()
        record.save()
        _audit(request, org, "consent.revoked", "ConsentRecord", record.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
