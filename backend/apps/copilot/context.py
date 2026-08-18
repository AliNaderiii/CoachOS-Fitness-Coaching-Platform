"""Phase 11 — authorized, minimum-necessary context builder.

Responsibilities:

1. Re-verify server-side authorization BEFORE any retrieval (org scope, role,
   assignment). Raises :class:`SubjectNotAuthorized` on any mismatch — callers
   translate that into safe 403/404 envelopes without leaking existence.
2. Assemble only the data the selected capability needs, truncated and
   sanitized (see :mod:`apps.copilot.redaction`).
3. Emit provenance: a list of ``{source_type, source_id, descriptor}`` entries
   persisted as :class:`AISourceReference` rows and re-authorized on every
   later read.
4. Never include Tier 3 free-text details (feedback flag details / anatomical
   locations), Tier 4 media, contact data, credentials, or other athletes.
"""

import datetime
from dataclasses import dataclass, field

from django.utils import timezone

from apps.execution.models import FeedbackFlag, SetLog, WorkoutSession
from apps.exercises.models import Exercise
from apps.organizations.models import Membership
from apps.programs.models import CoachAthleteAssignment, ProgramAssignment

from .constants import (
    CAPABILITY_DRAFT_CHECK_IN,
    CAPABILITY_SUGGEST_PROGRAM_ADJUSTMENT,
    CAPABILITY_SUMMARIZE_PROGRESS,
    CONTEXT_OMISSIONS,
)
from .redaction import sanitize_untrusted_text

DEFAULT_PERIOD_DAYS = 14
MAX_PERIOD_DAYS = 30
MAX_SESSIONS = 20
MAX_SET_LOGS = 24
MAX_EXERCISE_ALLOWLIST = 150


class SubjectNotAuthorized(Exception):
    """Raised when the actor may not build context for the requested athlete.

    ``not_found=True`` means the subject does not map to an active athlete in
    the actor's organization (safe 404); otherwise the subject exists but the
    actor lacks the assignment (safe 403).
    """

    def __init__(self, *, not_found: bool = False):
        super().__init__("subject not authorized")
        self.not_found = not_found


@dataclass
class BuiltContext:
    capability: str
    period_days: int
    payload: dict
    sources: list[dict] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    omissions: list[str] = field(default_factory=list)
    exercise_allowlist_ids: list[str] = field(default_factory=list)

    @property
    def source_ids(self) -> set[str]:
        return {s["source_id"] for s in self.sources}


def _active_athlete_subject(organization, athlete_user_id):
    from apps.identity.models import User

    athlete = (
        User.objects.filter(id=athlete_user_id, is_active=True)
        .filter(
            memberships__organization=organization,
            memberships__role="athlete",
            memberships__status="active",
        )
        .distinct()
        .first()
    )
    if athlete is None:
        raise SubjectNotAuthorized(not_found=True)
    return athlete


def _assert_actor_scope(*, organization, actor, athlete, actor_roles):
    """Owner: org-scoped read (audited downstream). Coach: active assignment."""
    if "owner" in actor_roles:
        return
    assigned = CoachAthleteAssignment.objects.filter(
        organization=organization,
        coach_user=actor,
        athlete_user=athlete,
        is_active=True,
    ).exists()
    if not assigned:
        raise SubjectNotAuthorized(not_found=False)


def actor_roles(user, organization) -> set[str]:
    return set(
        Membership.objects.filter(
            user=user, organization=organization, status="active"
        ).values_list("role", flat=True)
    )


def _session_descriptor(session) -> str:
    return f"{session.scheduled_date.isoformat()} · {session.status}"


def _collect_sessions(*, organization, athlete, since_date):
    sessions = list(
        WorkoutSession.objects.filter(
            organization=organization,
            athlete_user=athlete,
            scheduled_date__gte=since_date,
        ).order_by("-scheduled_date")[:MAX_SESSIONS]
    )
    return sessions


def build_context(
    *,
    capability: str,
    organization,
    actor,
    athlete_user_id: str,
    actor_roles_set: set[str],
    parameters: dict | None,
    generation_language: str,
) -> BuiltContext:
    """Build a provenance-tracked, redacted context payload for one capability.

    Authorization failures raise :class:`SubjectNotAuthorized` before any
    source query is executed.
    """
    parameters = parameters or {}
    athlete = _active_athlete_subject(organization, athlete_user_id)
    _assert_actor_scope(
        organization=organization, actor=actor, athlete=athlete, actor_roles=actor_roles_set
    )

    period_days = parameters.get("period_days") or DEFAULT_PERIOD_DAYS
    period_days = max(1, min(int(period_days), MAX_PERIOD_DAYS))
    since_date = (timezone.now() - datetime.timedelta(days=period_days)).date()

    display_name = sanitize_untrusted_text(athlete.display_name or "athlete", max_chars=80)
    limitations: list[str] = []
    sources: list[dict] = []

    if generation_language == "fa-IR":
        limitations.append(
            "این پیش‌نویس توسط هوش مصنوعی تولید شده و قبل از هر استفاده نیازمند بازبینی مربی است."
        )
    else:
        limitations.append("AI-generated draft — coach review is required before any use.")

    sessions = _collect_sessions(organization=organization, athlete=athlete, since_date=since_date)
    if not sessions:
        if generation_language == "fa-IR":
            limitations.append("هیچ جلسه تمرینی در بازه انتخاب‌شده ثبت نشده است.")
        else:
            limitations.append("No workout sessions were recorded in the selected period.")

    session_rows = []
    completed = 0
    missed = 0
    for position, session in enumerate(sessions):
        ordinal = position + 1
        coach_note = sanitize_untrusted_text(session.athlete_notes, max_chars=160)
        session_rows.append(
            {
                "source_id": session.id,
                "date": session.scheduled_date.isoformat(),
                "status": session.status,
                "session_rpe": session.session_rpe,
                "fatigue_score": session.fatigue_score,
                "athlete_note": coach_note,
            }
        )
        sources.append(
            {
                "source_type": "workout_session",
                "source_ordinal": ordinal,
                "source_id": session.id,
                "descriptor": _session_descriptor(session),
            }
        )
        if session.status == "completed":
            completed += 1
        elif (
            session.status in ("skipped", "scheduled")
            and session.scheduled_date < timezone.now().date()
        ):
            missed += 1

    set_rows = _collect_set_logs(
        organization=organization,
        athlete=athlete,
        since_date=since_date,
        sources=sources,
        generation_language=generation_language,
    )

    flag_summary = _collect_flag_summary(
        organization=organization,
        athlete=athlete,
        since_date=since_date,
        sources=sources,
        generation_language=generation_language,
    )

    assignment_row = _active_assignment(
        organization=organization,
        athlete=athlete,
        sources=sources,
        generation_language=generation_language,
    )

    payload_base = {
        "subject_display_name": display_name,
        "period_days": period_days,
        "sessions": session_rows,
        "set_log_aggregates": set_rows,
        "feedback_flag_summary": flag_summary,
        "active_assignment": assignment_row,
        "generation_language": generation_language,
        "coach_directive": sanitize_untrusted_text(parameters.get("notes"), max_chars=240),
        "variation": int(parameters.get("variation") or 0),
        "limitations": limitations,
    }

    limitations.extend(flag_summary["disclaimers"])
    if assignment_row is None:
        if generation_language == "fa-IR":
            limitations.append("برنامه فعالی برای این ورزشکار یافت نشد.")
        else:
            limitations.append("No active program assignment found for this athlete.")

    context = BuiltContext(
        capability=capability,
        period_days=period_days,
        payload=payload_base,
        sources=sources,
        limitations=limitations,
        omissions=list(CONTEXT_OMISSIONS),
    )

    if capability in (CAPABILITY_SUMMARIZE_PROGRESS, CAPABILITY_DRAFT_CHECK_IN):
        return context

    if capability == CAPABILITY_SUGGEST_PROGRAM_ADJUSTMENT:
        _attach_adjustment_context(
            context=context,
            organization=organization,
            assignment_row=assignment_row,
            limitations=limitations,
            sources=sources,
            generation_language=generation_language,
        )
        return context

    raise ValueError(f"unknown capability {capability!r}")


def _collect_set_logs(*, organization, athlete, since_date, sources, generation_language):
    """Bounded per-exercise aggregates (top recent working sets, kg)."""
    qs = (
        SetLog.objects.filter(
            session__organization=organization,
            session__athlete_user=athlete,
            session__scheduled_date__gte=since_date,
            is_completed=True,
        )
        .select_related("exercise")
        .order_by("-session__scheduled_date", "-actual_load_kg")[:MAX_SET_LOGS]
    )
    rows = []
    for log in qs:
        exercise = log.exercise
        source_id = f"setlog:{log.id}"
        rows.append(
            {
                "source_id": source_id,
                "exercise_id": str(exercise.id),
                "exercise_name": _exercise_name(exercise, generation_language),
                "load_kg": float(log.actual_load_kg),
                "reps": log.actual_reps,
                "rpe": float(log.actual_rpe) if log.actual_rpe is not None else None,
            }
        )
        sources.append(
            {
                "source_type": "set_log",
                "source_ordinal": len(sources) + 1,
                "source_id": source_id,
                "descriptor": f"{_exercise_name(exercise, generation_language)} · {log.actual_load_kg} kg × {log.actual_reps}",
            }
        )
    return rows


def _exercise_name(exercise, locale) -> str:
    translations = exercise.translations.all()
    name = None
    for item in translations:
        if item.locale == locale:
            name = item.name
            break
    if name is None:
        for item in translations:
            name = item.name
            break
    return sanitize_untrusted_text(name or str(exercise.id), max_chars=80)


def _collect_flag_summary(*, organization, athlete, since_date, sources, generation_language):
    """Non-clinical counts only. Free-text details never leave the database."""
    flags = FeedbackFlag.objects.filter(
        session__organization=organization,
        athlete_user=athlete,
        created_at__date__gte=since_date,
    ).order_by("-created_at")[:10]
    by_type: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    for flag in flags:
        by_type[flag.flag_type] = by_type.get(flag.flag_type, 0) + 1
        by_severity[flag.severity] = by_severity.get(flag.severity, 0) + 1
        sources.append(
            {
                "source_type": "feedback_flag",
                "source_ordinal": len(sources) + 1,
                "source_id": flag.id,
                "descriptor": f"{flag.flag_type} · {flag.severity} · {flag.created_at.date().isoformat()}",
            }
        )
    disclaimer = (
        "پرچم‌های بازخورد گزارش ذهنی ورزشکار است و تشخیص بالینی نیست؛ پیگیری حضوری لازم است."
        if generation_language == "fa-IR"
        else "Feedback flags are subjective athlete reports, not clinical findings; follow up in person."
    )
    summary = {
        "total": len(flags),
        "by_type": by_type,
        "by_severity": by_severity,
        # details + anatomical_location purposely absent (CONTEXT_OMISSIONS)
        "disclaimers": [disclaimer] if flags else [],
    }
    return summary


def _active_assignment(*, organization, athlete, sources, generation_language):
    assignment = (
        ProgramAssignment.objects.filter(
            organization=organization, athlete_user=athlete, status="active"
        )
        .order_by("-created_at")
        .first()
    )
    if assignment is None:
        return None
    title = sanitize_untrusted_text(
        (assignment.snapshot_payload.get("program") or {}).get("title", ""), max_chars=120
    )
    sources.append(
        {
            "source_type": "program_assignment",
            "source_ordinal": len(sources) + 1,
            "source_id": assignment.id,
            "descriptor": f"{title or 'program'} · v{assignment.source_program_version} · {assignment.start_date.isoformat()}",
        }
    )
    return {
        "source_id": assignment.id,
        "program_title": title,
        "program_version": assignment.source_program_version,
        "start_date": assignment.start_date.isoformat(),
    }


def _attach_adjustment_context(
    *, context, organization, assignment_row, limitations, sources, generation_language
):
    """Attach the snapshot day view + the org published-exercise allowlist."""
    context.payload["assignment_snapshot"] = None
    context.payload["exercise_allowlist"] = []
    context.exercise_allowlist_ids = []

    if assignment_row is not None:
        assignment = ProgramAssignment.objects.filter(id=assignment_row["source_id"]).first()
        if assignment is not None:
            context.payload["assignment_snapshot"] = _snapshot_view(
                assignment.snapshot_payload, generation_language
            )

    allowlist = []
    exercises = (
        Exercise.objects.filter(
            status="published",
        )
        .filter(models_q_organization(organization))
        .order_by("created_at")[:MAX_EXERCISE_ALLOWLIST]
    )
    for exercise in exercises:
        name = _exercise_name(exercise, generation_language)
        allowlist.append(
            {
                "exercise_id": str(exercise.id),
                "name": name,
                "equipment": exercise.equipment_required,
            }
        )
        sources.append(
            {
                "source_type": "exercise",
                "source_ordinal": len(sources) + 1,
                "source_id": f"exercise:{exercise.id}",
                "descriptor": name,
            }
        )
    context.payload["exercise_allowlist"] = allowlist
    context.exercise_allowlist_ids = [e["exercise_id"] for e in allowlist]
    if not allowlist:
        if generation_language == "fa-IR":
            limitations.append("هیچ حرکت منتشرشده‌ای در کتابخانه سازمان برای جایگزینی موجود نیست.")
        else:
            limitations.append("No published exercises are available in the organization library.")
    if context.payload["assignment_snapshot"] is None:
        context.limitations.append(
            "Adjustment drafting requires an active assignment; output will be limited."
            if generation_language != "fa-IR"
            else "پیش‌نویس تعدیل نیازمند یک تکلیف فعال است؛ خروجی محدود خواهد بود."
        )


def models_q_organization(organization):
    from django.db.models import Q

    return Q(organization__isnull=True) | Q(organization=organization)


def _snapshot_view(snapshot_payload, generation_language) -> dict:
    """Minimal view of the immutable assignment snapshot: day/workout titles and
    item exercise names only (no coach notes, no per-set targets beyond reps)."""
    program = snapshot_payload.get("program") or {}
    days_out = []
    for phase in (program.get("phases") or [])[:2]:
        for week in (phase.get("weeks") or [])[:2]:
            for day in (week.get("days") or [])[:7]:
                workouts = []
                for workout in (day.get("workouts") or [])[:3]:
                    items = []
                    for item in (workout.get("items") or [])[:10]:
                        name = None
                        for translation in (item.get("exercise") or {}).get("translations") or []:
                            if translation.get("locale") == generation_language:
                                name = translation.get("name")
                                break
                        if name is None:
                            for translation in (item.get("exercise") or {}).get(
                                "translations"
                            ) or []:
                                name = translation.get("name")
                                break
                        items.append(
                            {
                                "exercise_id": item.get("exercise_id"),
                                "name": sanitize_untrusted_text(name, max_chars=80)
                                if name
                                else None,
                                "segment": item.get("segment"),
                            }
                        )
                    workouts.append(
                        {
                            "title": sanitize_untrusted_text(workout.get("title"), max_chars=120),
                            "items": items,
                        }
                    )
                days_out.append(
                    {
                        "week_number": week.get("week_number"),
                        "day_number": day.get("day_number"),
                        "title": sanitize_untrusted_text(day.get("title"), max_chars=120),
                        "workouts": workouts,
                    }
                )
    return {
        "program_title": sanitize_untrusted_text(program.get("title"), max_chars=120),
        "days": days_out[:14],
    }
