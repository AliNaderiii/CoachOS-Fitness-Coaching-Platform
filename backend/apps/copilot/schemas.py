"""Phase 11 — strict structured-output validation for Copilot drafts.

A draft is only persisted as usable when it validates here. Validation is
allowlist-based (required keys, exact key sets, types, enums, length caps) and
includes an anti-hallucination check: every ``source_id`` cited by the model
must exist in the authorized context sources. Invalid output produces a
``validation_failed`` run (visible as a safe failure, never as a draft).
"""

from .constants import CAPABILITIES

SCHEMA_VERSION = 1

_CHANGE_TYPES = ("substitute", "reduce_load", "adjust_sets", "coach_note")

# Field length caps. Keep drafts focused and bounded.
CAPS = {
    "title": 160,
    "subject": 140,
    "body": 1600,
    "item": 240,
    "rationale": 280,
    "limitation": 240,
    "disclaimer": 400,
    "list_items": 12,
    "sources": 40,
    "suggestions": 8,
}


def _err(errors: list[str], field: str, message: str) -> None:
    errors.append(f"{field}: {message}")


def _check_str(errors, payload, key, max_len, *, required=True, allow_empty=False):
    if key not in payload:
        if required:
            _err(errors, key, "missing")
        return
    value = payload[key]
    if not isinstance(value, str):
        _err(errors, key, "must be a string")
        return
    if not value.strip() and not allow_empty:
        _err(errors, key, "must not be empty")
    if len(value) > max_len:
        _err(errors, key, f"exceeds {max_len} characters")


def _check_bool(errors, payload, key):
    if not isinstance(payload.get(key), bool):
        _err(errors, key, "must be a boolean")


def _check_int(errors, payload, key, minimum, maximum):
    value = payload.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        _err(errors, key, "must be an integer")
        return
    if value < minimum or value > maximum:
        _err(errors, key, f"must be between {minimum} and {maximum}")


def _check_str_list(errors, payload, key, *, max_len, max_items, min_items=0):
    if key not in payload:
        _err(errors, key, "missing")
        return
    value = payload[key]
    if not isinstance(value, list):
        _err(errors, key, "must be a list")
        return
    if len(value) < min_items:
        _err(errors, key, f"must contain at least {min_items} item(s)")
    if len(value) > max_items:
        _err(errors, key, f"must contain at most {max_items} items")
    for index, item in enumerate(value):
        if not isinstance(item, str):
            _err(errors, f"{key}[{index}]", "must be a string")
        elif not item.strip() or len(item) > max_len:
            _err(errors, f"{key}[{index}]", f"must be 1..{max_len} characters")


def _check_sources(errors, payload, allowed_source_ids: set[str]):
    source_ids = payload.get("source_ids")
    if not isinstance(source_ids, list):
        _err(errors, "source_ids", "must be a list")
        return
    if len(source_ids) > CAPS["sources"]:
        _err(errors, "source_ids", "too many citations")
    seen = set()
    for index, sid in enumerate(source_ids):
        if not isinstance(sid, str) or not sid:
            _err(errors, f"source_ids[{index}]", "must be a non-empty string")
            continue
        if sid in seen:
            continue
        seen.add(sid)
        if sid not in allowed_source_ids:
            _err(errors, f"source_ids[{index}]", "citation not present in authorized context")


def _base_check(errors, payload, *, schema_name, allowed_source_ids, extra_keys=()):
    if not isinstance(payload, dict):
        errors.append("payload: must be an object")
        return set()
    expected = {
        "schema_name",
        "schema_version",
        "ai_generated",
        "requires_human_review",
        "limitations",
        "source_ids",
        *extra_keys,
    }
    missing = expected - set(payload)
    extra = set(payload) - expected
    for key in sorted(missing):
        _err(errors, str(key), "missing")
    for key in sorted(extra):
        _err(errors, str(key), "unexpected field")
    if payload.get("schema_name") != schema_name:
        _err(errors, "schema_name", f"must equal {schema_name!r}")
    if payload.get("schema_version") != SCHEMA_VERSION:
        _err(errors, "schema_version", f"must equal {SCHEMA_VERSION}")
    if payload.get("ai_generated") is not True:
        _err(errors, "ai_generated", "must be true (draft label)")
    if payload.get("requires_human_review") is not True:
        _err(errors, "requires_human_review", "must be true")
    _check_str_list(
        errors, payload, "limitations", max_len=CAPS["limitation"], max_items=10, min_items=1
    )
    _check_sources(errors, payload, allowed_source_ids)
    return expected


def validate_progress_summary(payload, *, allowed_source_ids: set[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload: must be an object"]
    _base_check(
        errors,
        payload,
        schema_name="ai_progress_summary.v1",
        allowed_source_ids=allowed_source_ids,
        extra_keys=(
            "athlete_display_name",
            "period_days",
            "sessions_completed",
            "sessions_missed",
            "summary",
            "highlights",
            "concerns",
        ),
    )
    if errors:
        return errors
    _check_str(errors, payload, "athlete_display_name", CAPS["title"])
    _check_int(errors, payload, "period_days", 1, 31)
    _check_int(errors, payload, "sessions_completed", 0, 200)
    _check_int(errors, payload, "sessions_missed", 0, 200)
    _check_str(errors, payload, "summary", CAPS["body"])
    _check_str_list(
        errors, payload, "highlights", max_len=CAPS["item"], max_items=CAPS["list_items"]
    )
    _check_str_list(errors, payload, "concerns", max_len=CAPS["item"], max_items=CAPS["list_items"])
    return errors


def validate_check_in_message(payload, *, allowed_source_ids: set[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload: must be an object"]
    _base_check(
        errors,
        payload,
        schema_name="ai_check_in_message.v1",
        allowed_source_ids=allowed_source_ids,
        extra_keys=("subject", "body", "tone"),
    )
    if errors:
        return errors
    _check_str(errors, payload, "subject", CAPS["subject"])
    _check_str(errors, payload, "body", CAPS["body"])
    _check_str(errors, payload, "tone", 40)
    return errors


def validate_program_adjustment(
    payload, *, allowed_source_ids: set[str], allowed_exercise_ids: set[str]
) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["payload: must be an object"]
    _base_check(
        errors,
        payload,
        schema_name="ai_program_adjustment.v1",
        allowed_source_ids=allowed_source_ids,
        extra_keys=("target_day_title", "suggestions", "safety_disclaimer"),
    )
    if errors:
        return errors
    _check_str(errors, payload, "target_day_title", CAPS["title"])
    _check_str(errors, payload, "safety_disclaimer", CAPS["disclaimer"])
    suggestions = payload.get("suggestions")
    if not isinstance(suggestions, list) or not suggestions:
        _err(errors, "suggestions", "must be a non-empty list")
        return errors
    if len(suggestions) > CAPS["suggestions"]:
        _err(errors, "suggestions", f"must contain at most {CAPS['suggestions']} items")
    for index, suggestion in enumerate(suggestions):
        prefix = f"suggestions[{index}]"
        if not isinstance(suggestion, dict):
            _err(errors, prefix, "must be an object")
            continue
        if set(suggestion) - {"exercise_id", "change_type", "rationale"}:
            _err(errors, prefix, "unexpected field")
        exercise_id = suggestion.get("exercise_id")
        if not isinstance(exercise_id, str) or exercise_id not in allowed_exercise_ids:
            _err(errors, f"{prefix}.exercise_id", "not in authorized exercise allowlist")
        if suggestion.get("change_type") not in _CHANGE_TYPES:
            _err(errors, f"{prefix}.change_type", "unsupported change type")
        rationale = suggestion.get("rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            _err(errors, f"{prefix}.rationale", "must not be empty")
        elif len(rationale) > CAPS["rationale"]:
            _err(errors, f"{prefix}.rationale", f"exceeds {CAPS['rationale']} characters")
    return errors


_VALIDATORS = {
    "summarize_progress": lambda payload, sources, exercises: validate_progress_summary(
        payload, allowed_source_ids=sources
    ),
    "draft_check_in": lambda payload, sources, exercises: validate_check_in_message(
        payload, allowed_source_ids=sources
    ),
    "suggest_program_adjustment": lambda payload, sources, exercises: validate_program_adjustment(
        payload, allowed_source_ids=sources, allowed_exercise_ids=exercises
    ),
}


def validate_output(
    capability: str, payload, *, allowed_source_ids: set[str], allowed_exercise_ids: set[str]
) -> list[str]:
    """Validate a provider draft. Returns a list of safe error strings."""
    if capability not in CAPABILITIES:
        return ["capability: unknown"]
    return _VALIDATORS[capability](payload, allowed_source_ids, allowed_exercise_ids)
