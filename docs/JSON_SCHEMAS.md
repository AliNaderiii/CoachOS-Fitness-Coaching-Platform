# JSON Schemas & Serialization Contracts — CoachOS

**Version:** 1.0.0 Phase 03  
**Status:** Provisional — JSON Schema draft 2020-12 compatible, used to validate OPENAPI.yaml examples + storage JSONB snapshots.

---

## 1. Purpose

Defines canonical JSON shapes for:
- Program Snapshot (immutable historical copy stored in `ProgramAssignment.snapshot_payload` JSONB)
- SetLog batch payload
- Export archive `profile.json`, `workouts.json`
- Notification payload
- Consent record serialization
- Exercise search normalized token

These schemas are specification artifacts only — not implemented.

---

## 2. Program Snapshot Schema (Immutable)

Program snapshot preserved at assignment time — complete frozen copy of hierarchy.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://coachos.example.com/schemas/program-snapshot.json",
  "title": "ProgramSnapshot",
  "description": "Immutable point-in-time snapshot of program hierarchy at assignment — preserves historical integrity.",
  "type": "object",
  "required": ["program_id", "title", "frozen_at", "phases"],
  "properties": {
    "program_id": {"type": "string", "format": "uuid", "description": "Source program"},
    "title": {"type": "string"},
    "description": {"type": ["string", "null"]},
    "target_goal": {"type": "string", "enum": ["hypertrophy","strength","fat_loss","endurance","general_fitness"]},
    "frozen_at": {"type": "string", "format": "date-time"},
    "phases": {
      "type": "array",
      "items": {"$ref": "#/$defs/Phase"}
    },
    "version": {"type": "integer", "minimum": 1, "description": "Snapshot version, increment on re-assign"}
  },
  "$defs": {
    "Phase": {
      "type": "object",
      "required": ["id","name","sequence_order","duration_weeks","weeks"],
      "properties": {
        "id": {"type": "string", "format":"uuid"},
        "name": {"type":"string"},
        "sequence_order": {"type":"integer"},
        "duration_weeks": {"type":"integer"},
        "weeks": {"type":"array","items":{"$ref":"#/$defs/Week"}}
      }
    },
    "Week": {
      "type":"object",
      "required":["id","week_number","days"],
      "properties":{
        "id":{"type":"string","format":"uuid"},
        "week_number":{"type":"integer"},
        "focus_note":{"type":["string","null"]},
        "days":{"type":"array","items":{"$ref":"#/$defs/Day"}}
      }
    },
    "Day": {
      "type":"object",
      "required":["id","day_number","title","workouts"],
      "properties":{
        "id":{"type":"string","format":"uuid"},
        "day_number":{"type":"integer"},
        "title":{"type":"string"},
        "workouts":{"type":"array","items":{"$ref":"#/$defs/Workout"}}
      }
    },
    "Workout": {
      "type":"object",
      "required":["id","title","items"],
      "properties":{
        "id":{"type":"string","format":"uuid"},
        "title":{"type":"string"},
        "estimated_minutes":{"type":["integer","null"]},
        "items":{"type":"array","items":{"$ref":"#/$defs/WorkoutItem"}}
      }
    },
    "WorkoutItem": {
      "type":"object",
      "required":["id","exercise_id","sequence_order","prescriptions"],
      "properties":{
        "id":{"type":"string","format":"uuid"},
        "exercise_id":{"type":"string","format":"uuid"},
        "sequence_order":{"type":"integer"},
        "group_key":{"type":["string","null"],"description":"A1/A2 for superset"},
        "segment":{"type":"string","enum":["warmup","main","cooldown"]},
        "rest_seconds_between_sets":{"type":"integer"},
        "coach_notes":{"type":["string","null"]},
        "prescriptions":{"type":"array","items":{"$ref":"#/$defs/SetPrescription"}}
      }
    },
    "SetPrescription": {
      "type":"object",
      "required":["set_index","target_reps"],
      "properties":{
        "set_index":{"type":"integer"},
        "target_reps":{"type":"string"},
        "target_load":{"type":["string","null"]},
        "target_rpe":{"type":["number","null"]},
        "target_rir":{"type":["integer","null"]},
        "tempo":{"type":["string","null"]}
      }
    }
  }
}
```

**Invariants:**
- Snapshot `frozen_at` set at assignment commit time, never mutated thereafter.
- Snapshot preserves `exercise_id` references at time — if exercise later archived, snapshot remains valid historical record.

---

## 3. SetLog Batch & Offline Queue Entry (Phase12)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://coachos.example.com/schemas/set-log-queue.json",
  "title": "SetLogQueueEntry",
  "type":"object",
  "required":["id","session_id","exercise_id","set_index","actual_reps","actual_load_kg","client_created_at","status"],
  "properties":{
    "id":{"type":"string","format":"uuid","description":"Client-generated UUIDv7 for offline creation"},
    "session_id":{"type":"string","format":"uuid"},
    "exercise_id":{"type":"string","format":"uuid"},
    "set_index":{"type":"integer"},
    "actual_reps":{"type":"integer"},
    "actual_load_kg":{"type":"number"},
    "actual_rpe":{"type":["number","null"]},
    "notes":{"type":["string","null"]},
    "client_created_at":{"type":"string","format":"date-time","description":"Local device time"},
    "status":{"type":"string","enum":["pending","syncing","synced","failed","conflict"]},
    "retry_count":{"type":"integer","minimum":0}
  }
}
```

---

## 4. Export Archive Manifest

`export.zip` contains:
- `profile.json`
- `workouts.json`
- `set_logs.csv`
- `progress_photos/` (optional, binary)
- `manifest.json` metadata

### profile.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title":"ExportProfile",
  "type":"object",
  "required":["user_id","email","display_name","preferred_locale","memberships","exported_at"],
  "properties":{
    "user_id":{"type":"string","format":"uuid"},
    "email":{"type":"string","format":"email"},
    "display_name":{"type":"string"},
    "preferred_locale":{"type":"string","enum":["fa-IR","en-US"]},
    "memberships":{"type":"array","items":{"type":"object"}},
    "exported_at":{"type":"string","format":"date-time"}
  }
}
```

### workouts.json

Array of WorkoutSessions with nested SetLogs.

```json
{
  "type":"array",
  "items":{
    "type":"object",
    "required":["session_id","scheduled_date","status","set_logs"],
    "properties":{
      "session_id":{"type":"string","format":"uuid"},
      "scheduled_date":{"type":"string","format":"date"},
      "status":{"type":"string"},
      "set_logs":{"type":"array","items":{"type":"object"}}
    }
  }
}
```

---

## 5. Notification Payload

```json
{
  "$schema":"https://json-schema.org/draft/2020-12/schema",
  "title":"NotificationPayload",
  "type":"object",
  "required":["event_type","recipient_user_id","actor_user_id","navigation_url","localized_params"],
  "properties":{
    "event_type":{"type":"string","enum":["program_assigned","workout_completed","pain_flag_raised","message_received"]},
    "recipient_user_id":{"type":"string","format":"uuid"},
    "actor_user_id":{"type":"string","format":"uuid"},
    "navigation_url":{"type":"string","description":"Deep link e.g., /coach/athletes/:id/logs/:sid"},
    "localized_params":{
      "type":"object",
      "description":"Params for frontend i18n — athlete name, workout title"
    },
    "created_at":{"type":"string","format":"date-time"}
  }
}
```

---

## 6. Consent Serialization

```json
{
  "type":"object",
  "required":["athlete_user_id","grantee_user_id","consent_type","is_granted"],
  "properties":{
    "athlete_user_id":{"type":"string","format":"uuid"},
    "grantee_user_id":{"type":"string","format":"uuid"},
    "consent_type":{"type":"string","enum":["progress_photo","nutrition_sharing","body_metrics"]},
    "is_granted":{"type":"boolean"},
    "granted_at":{"type":["string","null"],"format":"date-time"},
    "revoked_at":{"type":["string","null"],"format":"date-time"}
  }
}
```

---

## 7. Persian Search Normalization — Pseudocode (proposed)

Not JSON but important for search implementation — Perso-Arabic script keyboard-variant normalization for Persian search:

```python
def persian_normalize(text: str) -> str:
    # Fold Perso-Arabic variants
    text = text.replace('\u064A', '\u06CC') # Arabic Yeh ي -> Persian Yeh ی
    text = text.replace('\u0649', '\u06CC') # Arabic Yeh with dots? variant
    text = text.replace('\u0643', '\u06A9') # Arabic Kaf ك -> Persian Kaf ک
    # Fold Arabic-Indic digits ٠-٩ -> Persian ۰-۹ or Latin 0-9 ? Choose Latin for search index
    # Remove ZWNJ \u200C for tokenization but preserve for display? Fold to space for search
    text = text.replace('\u200C', ' ')
    # Strip diacritics/harakat optionally
    # Lowercase latin part
    text = text.lower()
    # Trim whitespace
    text = ' '.join(text.split())
    return text
```

- No Arabic product support implied — normalization handles keyboard-variant input only.
- Index via `pg_trgm` GIN.

---

## 8. References

- `OPENAPI.yaml` — request/response schemas are primary.
- `ERD.md` — entity shapes.
- `DATA_FLOW.md` — normalization flow.
