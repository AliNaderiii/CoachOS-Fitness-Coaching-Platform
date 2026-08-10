# Data Model — CoachOS

**Status:** Conceptual outline (Phase 00). **Authoritative normalized schema in Phase 03.**  
**Last updated:** 2026-08-10  

---

## 1. Design goals

- Multi-tenant organizations with optional locations  
- Athlete may eventually relate to **multiple professionals** (model early)  
- Bilingual content fields (`fa`, `en`) without Arabic tables/resources  
- Auditability and soft-delete/archive where appropriate  
- Media rights/provenance on all binary references  
- Extensible for nutrition, billing, AI logs later without rewrite  

## 2. Core domain clusters

```
Identity & Tenancy     Exercise Library     Programming
─────────────────      ────────────────     ───────────
User                   Exercise             Program
Credential             ExerciseI18n         ProgramPhase / Week / Day
Organization           ExerciseAlias        Workout
Membership/Role        Muscle/Equipment     ExercisePrescription
Invitation             MediaAsset           ProgramTemplate
Assignment (coach↔ath) MediaRights          ProgramAssignment
LocalePreferences      Tag / Favorite       ProgramVersion

Logging & Progress     Communication        Admin & Audit
──────────────────     ──────────────       ─────────────
WorkoutSession         MessageThread        AuditEvent
SetLog                 Message              ModerationAction
AdherenceSnapshot      Notification         FeatureFlag (optional)
BodyMetric             NotificationPref
ProgressPhoto (+consent)
FeedbackFlag
```

## 3. Entity sketches (not SQL)

### User

- id, email (unique), password hash, is_active, is_platform_admin  
- display_name, phone (optional), created_at  
- preferred_locale: `fa-IR` | `en-US`  
- timezone  

### Organization

- id, name, slug, owner_user_id  
- settings JSON (branding later)  
- created_at, archived_at  

### Location (optional depth in MVP)

- id, organization_id, name, address fields optional  

### Membership

- user_id, organization_id, role: `owner` | `coach` | `athlete` | `manager` | `support`  
- status: invited | active | suspended  
- unique(user, org) or allow multi-role via role table — **decide Phase 03**  

### CoachAthleteAssignment

- coach_membership_id or coach_user_id + organization_id  
- athlete_user_id  
- starts_at, ends_at, active  

Supports future multi-coach and multi-pro.

### Invitation

- token hash, email, org_id, role, invited_by, expires_at, accepted_at  

### Exercise

- id, status: draft | published | archived  
- difficulty, movement_pattern, equipment M2M, muscles M2M  
- owner_org_id nullable (null = platform canonical)  
- created_by, moderation fields  

### ExerciseTranslation

- exercise_id, locale (`fa-IR` | `en-US`), name, instructions, cues, safety_notes, mistakes  
- unique(exercise_id, locale)  

### ExerciseAlias

- exercise_id, locale, alias, normalized_form (for search)  

### MediaAsset

- id, storage_key, content_type, bytes, checksum  
- **rights:** license, source_url, attribution, permitted_use, reviewed_by, reviewed_at  
- provenance notes  

### Program hierarchy

`Program` → `ProgramPhase` → `ProgramWeek` → `ProgramDay` → `Workout` → `WorkoutItem` → `SetPrescription`

Prescription fields: sets, reps, time, distance, load, percent, RPE, RIR, tempo, rest_seconds, notes, group_key (superset/circuit), segment (warmup|main|cooldown).

### ProgramAssignment

- program_id / version_id, athlete_id, assigned_by, start_date, end_date, state  

### WorkoutSession (athlete execution)

- assignment or scheduled workout ref, athlete_id  
- started_at, completed_at, status: not_started | in_progress | completed | skipped | modified  
- modify_reason, athlete_notes, pain_flag, fatigue_score  

### SetLog

- session_item_id, set_index, reps, load, rpe, completed, notes  

### MessageThread / Message

- participants constrained by assignment/org  
- optional reference_type/id (workout, checkin)  

### Notification

- user_id, type, payload, read_at, channel preferences separate  

### AuditEvent

- actor_id, action, object_type, object_id, org_id, ip hash?, metadata JSON, created_at  
- no raw sensitive bodies  

## 4. Future entities (do not implement now)

- NutritionProfessional profile, MealPlan, FoodItem, Recipe, Allergy  
- Product, Subscription, Payment, Entitlement  
- AIRunLog (prompt version, reviewer)  
- Marketplace Listing, Review  

Schema should avoid hard-coding single-coach-only athlete ownership that blocks multi-pro.

## 5. i18n data rules

- User-generated content: store as entered; UI direction from viewer locale  
- Catalog content: explicit translation rows for `fa-IR` and `en-US` only  
- Search: normalize yeh/kaf variants etc. for Persian; do not add Arabic locale catalogs  

## 6. Open modeling questions (Phase 03)

1. Single Membership row vs UserOrgRole table  
2. Program versioning strategy (copy-on-publish vs event sourced)  
3. Soft delete vs archive flags  
4. ID type: UUID everywhere vs bigint  
5. Full-text: Postgres FTS vs external search later  

## 7. Related

- Phase 03 will produce ERD diagrams under `docs/architecture/`  
- API shapes in `docs/API_CONTRACT.md`  
