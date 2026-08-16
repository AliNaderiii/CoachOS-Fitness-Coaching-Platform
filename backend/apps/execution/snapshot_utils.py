"""
Helpers to read authorized ProgramAssignment snapshot payloads for the athlete
execution domain. The snapshot is immutable (enforced by ProgramAssignment) and
is the authoritative source for workout execution in Phase 07.
"""


def flatten_program_days(snapshot):
    """
    Flatten a snapshot's nested phases -> weeks -> days into an ordered list of
    day objects (each with a `workouts` list). Snapshot is server-trusted JSON.
    """
    if not isinstance(snapshot, dict):
        return []
    program = snapshot.get("program") or {}
    days = []
    for phase in program.get("phases") or []:
        for week in phase.get("weeks") or []:
            for day in week.get("days") or []:
                days.append(day)
    return days


def day_for_date(snapshot, start_date, date):
    """
    Return the day object scheduled for `date` given the snapshot and assignment
    start date. Programs schedule one day per calendar day from the assignment
    start; after the linear program ends the schedule cycles. Returns None when
    `date` precedes the assignment start or the snapshot has no days.
    """
    if date < start_date:
        return None
    days = flatten_program_days(snapshot)
    if not days:
        return None
    offset = (date - start_date).days
    return days[offset % len(days)]


def workouts_for_date(snapshot, start_date, date):
    """Return the list of workouts scheduled for a date (may be empty)."""
    day = day_for_date(snapshot, start_date, date)
    if not day:
        return []
    return day.get("workouts") or []
