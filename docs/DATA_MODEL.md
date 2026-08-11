# Conceptual Data Model & Entity Specifications — CoachOS

**Document version:** 2.0.0 (Phase 03 Architecture Finalized)  
**Last updated:** 2026-08-10  
**Phase alignment:** Phase 03 — Architecture, Data, Security, and Privacy — logical/physical model coherent with PRD and UX (34 screens, 27 P0 stories).  
**Architectural Notice:** Phase 01 provisional model has been finalized in Phase 03. Authoritative physical model, indexes, constraints, state machines, ERD, and conceptual DDL are now in `docs/architecture/ERD.md`. This document retains the detailed entity specification for traceability but should be read alongside `docs/architecture/ERD.md`, `docs/architecture/DOMAIN_MODULES.md`, `docs/JSON_SCHEMAS.md`, and `docs/DECISIONS.md` ADR-014..ADR-018.  
**Language constraints:** Bilingual metadata fields supporting `fa-IR` and `en-US` only. **No Arabic tables, columns, or seed catalogs.**  
**Identifier Strategy:** UUIDv7 proposed (ADR-017) — time-ordered, non-sequential, supports offline client-side generation for Phase12 queue, but NOT authz substitute — requires validation against PG/runtime support in Phase04.  
**Offline & Snapshot Integrity:** Program assignments preserve immutable historical snapshots (JSONB) — duplication justified; every tenant-scoped query derives organization scope from authenticated server context; progress photos never use public URLs; multi-professional access requires explicit consent + revocation.

**Authoritative Artifacts Created in Phase03:**
- `docs/architecture/ERD.md` — ER diagram + detailed entity specs with PK/FK/tenant ownership/sensitive fields/indexes/unique constraints/state machines/soft-delete/archive policy/audit/retention/localization
- `docs/architecture/DOMAIN_MODULES.md` — module ownership + test boundaries
- `docs/architecture/AUTHORIZATION_ARCHITECTURE.md` — object-level rules for sensitive entities
- `docs/JSON_SCHEMAS.md` — snapshot, queue entry, export manifest, notification payload, Persian normalization pseudocode (Perso-Arabic script keyboard-variant normalization for Persian search)

**Phase03 Exit Gate Verification:** Logical/physical model coherent, ERD renders, tenant isolation explicit, program snapshot immutability explicit, photo private storage explicit, consent revocation explicit.

---

## 1. Architectural Modeling Principles

1. **Multi-Tenancy Isolation:** Every tenant-scoped entity links explicitly to `organization_id`. Database queries enforce organization boundaries on the server.
2. **Immutable Program Snapshots:** Assigning a program to an athlete creates an immutable `ProgramSnapshot` to guarantee that future edits to master templates never corrupt historical workout logs.
3. **Multi-Professional Extensibility (P1-Ready):** Athlete entities link to coaching professionals via explicit assignment tables (`CoachAthleteAssignment`, `NutritionistAssignment`), allowing athletes to work with multiple professionals under strict, consent-governed boundaries.
4. **Bilingual Normalization:** Canonical exercise entities separate language-neutral biomechanical classification from localized translation tables (`ExerciseTranslation`) and search indexes (`ExerciseAlias`).
5. **Time-Ordered UUIDs:** Primary keys utilize **UUIDv7** (128-bit time-sortable identifiers) to prevent sequential enumeration attacks and support client-side ID generation for offline PWA logging.
6. **Strict Media Provenance:** All image and video assets maintain mandatory copyright license and creator attribution metadata (`MediaRights`).
7. **Append-Only Audit Logging:** Security- and authorization-sensitive events write to an immutable `AuditEvent` table that cannot be updated or deleted by application users.

---

## 2. Domain Entity Relationship Overview

```
[User] ────1:N────< [Membership] >────N:1──── [Organization]
  │                      │                          │
  │                      │                          ├──1:1── [Location (Primary MVP)]
  │                      ▼                          │
  │            [CoachAthleteAssignment]             ├──1:N── [Program (Templates)]
  │                      │                          │
  ├──1:N── [WorkoutSession] ──1:N──< [SetLog]       ├──1:N── [Custom Exercise]
  │              │                                  │
  ├──1:N── [ProgressPhoto] (Signed URL)             └──1:N── [AuditEvent]
  │
[Global Exercise] ──1:N── [ExerciseTranslation (fa/en)]
        │
        ├──1:N── [ExerciseAlias (Search Normalized)]
        └──1:N── [MediaAsset] ──1:1── [MediaRights]
```

---

## 3. Detailed Entity Schemas (Logical Specifications)

### 3.1 Identity & Tenancy Domain

#### `User`
*Global authentication and user identity.*
- `id` (UUIDv7, PK): Unique global user identifier.
- `email` (VARCHAR(255), Unique, Indexed): Verified user email.
- `password_hash` (VARCHAR(255)): Argon2id / bcrypt encrypted password hash.
- `display_name` (VARCHAR(150)): User's public full name.
- `phone_number` (VARCHAR(32), Nullable): Optional contact/SMS number.
- `preferred_locale` (VARCHAR(10), Default: `fa-IR` or `en-US`): Active UI locale.
- `preferred_unit` (VARCHAR(10), Default: `kg`): `kg` (metric) or `lbs` (imperial).
- `timezone` (VARCHAR(50), Default: `Asia/Tehran` or `UTC`): User local timezone.
- `is_platform_admin` (BOOLEAN, Default: `false`): System-wide super-admin flag.
- `is_active` (BOOLEAN, Default: `true`): Account activation state.
- `created_at` (TIMESTAMPTZ, UTC): Registration timestamp.
- `updated_at` (TIMESTAMPTZ, UTC): Last profile modification.

#### `Organization` (Corrected Owner Source of Truth — see ERD.md Task 4.1)
*The top-level customer boundary (Tenant).*
- `id` (UUIDv7, PK): Unique organization tenant ID.
- `name` (VARCHAR(150)): Business or gym name (e.g., "Alborz Performance").
- `slug` (VARCHAR(100), Unique, Indexed): URL-friendly unique identifier.
- `owner_user_id` (UUIDv7, FK -> `User.id`): **Authoritative source of truth for single owner MVP** (legal/billing owner) — invariant: exactly one active Membership role=owner must exist and its user_id must equal owner_user_id; drift prevented via transactional `OrganizationService.transferOwnership()` updating both atomically, audit `org.owner_transferred`.
- `settings` (JSONB): Organization-wide defaults (branding colors, logo URL, default schedule start day).
- `created_at` (TIMESTAMPTZ, UTC): Creation timestamp.
- `archived_at` (TIMESTAMPTZ, Nullable): Archival timestamp.

#### `Location` (Single-Location MVP / Multi-Location P1)
*Physical facility or branch metadata.*
- `id` (UUIDv7, PK): Location identifier.
- `organization_id` (UUIDv7, FK -> `Organization.id`, Indexed): Owning organization.
- `name` (VARCHAR(150)): Facility name (e.g., "Main Gym", "Central Branch").
- `is_primary` (BOOLEAN, Default: `true`): Primary facility flag (single-location MVP enforces 1 primary per org).
- `address_line1` (VARCHAR(255), Nullable): Street address.
- `city` (VARCHAR(100), Nullable): City.
- `phone` (VARCHAR(32), Nullable): Front-desk phone number.
- `created_at` (TIMESTAMPTZ, UTC): Creation timestamp.

#### `Membership` (Corrected Multi-Role Behavior — Task 4.2)
*Scoped relationship binding a User to an Organization with a defined Role.*
- `id` (UUIDv7, PK): Membership record ID.
- `user_id` (UUIDv7, FK -> `User.id`, Indexed): Authenticated user.
- `organization_id` (UUIDv7, FK -> `Organization.id`, Indexed): Organization tenant.
- `role` (VARCHAR(30)): Role within this organization (`owner`, `coach`, `athlete`, `support`).
- `status` (VARCHAR(20), Default: `active`): Membership state (`invited`, `active`, `suspended`, `archived`).
- `created_at` (TIMESTAMPTZ, UTC): Membership grant timestamp.
- `archived_at` (TIMESTAMPTZ, Nullable): For soft-archive when role removed.
- *Constraint:* `UNIQUE(user_id, organization_id, role)` allows multi-role per org; MVP policy single primary role recommended but multi-role allowed (e.g., coach+athlete same org). Effective permissions = union of all active roles for that user+org (most permissive, priority owner>coach>support>athlete for UI display). Role elevation audited (`membership.created`, `status_changed`, `role_changed`). Active org + active role via session `active_organization_id` + optional `active_role`; frontend receives `memberships` array + `effective_permissions` computed server-side (union), UI shows role switcher if multiple roles, default highest privilege. See ERD.md 4.2 for full invariant, no migrations in Phase03.

#### `Invitation`
*Cryptographically secure single-use organization onboarding token.*
- `id` (UUIDv7, PK): Invitation record ID.
- `organization_id` (UUIDv7, FK -> `Organization.id`, Indexed): Inviting organization.
- `invited_by_user_id` (UUIDv7, FK -> `User.id`): Inviting owner or coach.
- `email` (VARCHAR(255), Indexed): Target recipient email.
- `role` (VARCHAR(30)): Designated membership role upon acceptance.
- `token_hash` (VARCHAR(255), Unique, Indexed): SHA-256 hash of single-use URL token.
- `expires_at` (TIMESTAMPTZ, UTC): Token expiration (7 days from dispatch).
- `accepted_at` (TIMESTAMPTZ, Nullable): Acceptance timestamp.
- `created_at` (TIMESTAMPTZ, UTC): Invitation dispatch timestamp.

#### `CoachAthleteAssignment` (Corrected Reactivation Invariant — Task 4.3)
*Explicit authorization binding an Athlete to a specific Coach within an Organization.*
- `id` (UUIDv7, PK): Assignment ID.
- `organization_id` (UUIDv7, FK -> `Organization.id`, Indexed): Tenant context.
- `coach_user_id` (UUIDv7, FK -> `User.id`, Indexed): Assigned coach.
- `athlete_user_id` (UUIDv7, FK -> `User.id`, Indexed): Assigned athlete.
- `status` (VARCHAR(20), Default: `active`): `active` | `archived`.
- `created_at` (TIMESTAMPTZ, UTC): Assignment start timestamp.
- `archived_at` (TIMESTAMPTZ, Nullable): Soft-archive timestamp, `ended_at` alternative.
- *Constraint (Corrected):* Use partial unique for active only: `UNIQUE(organization_id, coach_user_id, athlete_user_id) WHERE status='active'` (or WHERE archived_at IS NULL) — allows historical archived rows + recreation after archival, only one active per triple at a time. Previous permanent unique prevented recreation.
- *Workflow:* Archival sets status archived + archived_at/ended_at + audit `assignment.archived`; reactivation via `AssignmentService.reactivate` creates new row (preserving history) or reactivates if no active exists, audit `assignment.reactivated`; reassignment archives old + creates new, audit both. Partial unique ensures idempotent assign returns existing if active. No migrations in Phase03 — conceptual invariant only, proposed for Phase04/05.

---

### 3.2 Bilingual Exercise Library Domain

#### `Exercise`
*Language-neutral biomechanical exercise definition.*
- `id` (UUIDv7, PK): Unique exercise identifier.
- `organization_id` (UUIDv7, FK -> `Organization.id`, Nullable, Indexed): NULL = Platform Canonical Global Exercise; Non-NULL = Private Custom Gym Exercise.
- `created_by_user_id` (UUIDv7, FK -> `User.id`, Nullable): Creator user ID.
- `movement_pattern` (VARCHAR(50)): `squat` | `hinge` | `horizontal_push` | `horizontal_pull` | `vertical_push` | `vertical_pull` | `lunge` | `carry` | `isolation` | `cardio` | `other`.
- `difficulty` (VARCHAR(20)): `beginner` | `intermediate` | `advanced`.
- `primary_muscles` (TEXT[]): Array of primary muscle tags (e.g., `["quadriceps", "glutes"]`).
- `secondary_muscles` (TEXT[]): Array of secondary muscle tags (e.g., `["hamstrings", "calves"]`).
- `equipment_required` (TEXT[]): Array of equipment requirements (e.g., `["barbell", "squat_rack"]`).
- `status` (VARCHAR(20), Default: `published`): `draft` | `pending_review` | `published` | `archived`.
- `created_at` (TIMESTAMPTZ, UTC): Creation timestamp.
- `updated_at` (TIMESTAMPTZ, UTC): Last modification timestamp.

#### `ExerciseTranslation`
*Localized names, coaching cues, instructions, and safety notes.*
- `id` (UUIDv7, PK): Translation ID.
- `exercise_id` (UUIDv7, FK -> `Exercise.id`, Indexed): Parent exercise.
- `locale` (VARCHAR(10), Indexed): `fa-IR` or `en-US` only.
- `name` (VARCHAR(200)): Localized exercise name (e.g., "اسکوات از پشت با هالتر" or "Barbell Back Squat").
- `instructions` (TEXT): Step-by-step setup and movement instructions.
- `coaching_cues` (TEXT[]): Key verbal cues (e.g., `["Chest up", "Drive through midfoot"]`).
- `common_mistakes` (TEXT[]): Pitfalls and form errors to avoid.
- `safety_notes` (TEXT, Nullable): Contraindications and safety cautions.
- *Constraint:* `UNIQUE(exercise_id, locale)`

#### `ExerciseAlias`
*Synonyms, colloquial fitness names, and search-normalized tokens.*
- `id` (UUIDv7, PK): Alias record ID.
- `exercise_id` (UUIDv7, FK -> `Exercise.id`, Indexed): Parent exercise.
- `locale` (VARCHAR(10)): `fa-IR` or `en-US`.
- `alias` (VARCHAR(200)): Raw alternate search term (e.g., "زیربغل سیمکش").
- `normalized_alias` (VARCHAR(200), Indexed): Character-folded search index token (`pg_trgm` indexed).

#### `MediaAsset`
*Instructional video demonstrations, animations, and anatomical diagrams.*
- `id` (UUIDv7, PK): Media identifier.
- `exercise_id` (UUIDv7, FK -> `Exercise.id`, Indexed): Parent exercise.
- `media_type` (VARCHAR(20)): `video_mp4` | `image_webp` | `animation_gif`.
- `storage_key` (VARCHAR(500)): S3-compatible private storage object key.
- `thumbnail_storage_key` (VARCHAR(500), Nullable): Thumbnail image key.
- `duration_seconds` (INT, Nullable): Video length.
- `bytes_size` (BIGINT): File size.
- `checksum_sha256` (VARCHAR(64)): File integrity checksum.

#### `MediaRights`
*Mandatory intellectual property and copyright provenance tracking.*
- `id` (UUIDv7, PK): Provenance record ID.
- `media_asset_id` (UUIDv7, FK -> `MediaAsset.id`, Unique, Indexed): Associated media asset.
- `license_type` (VARCHAR(50)): `original_production` | `licensed_cc_by` | `commercial_license` | `coach_upload`.
- `source_url` (VARCHAR(500), Nullable): Original provenance link.
- `creator_attribution` (VARCHAR(255)): Creator/owner credit.
- `permitted_commercial_use` (BOOLEAN, Default: `true`): Legal verification flag.
- `reviewed_by_user_id` (UUIDv7, FK -> `User.id`, Nullable): Platform admin reviewer.
- `reviewed_at` (TIMESTAMPTZ, Nullable): Admin verification timestamp.

---

### 3.3 Training Programming Domain

#### `Program`
*Master training program container / template.*
- `id` (UUIDv7, PK): Program identifier.
- `organization_id` (UUIDv7, FK -> `Organization.id`, Indexed): Owning organization tenant.
- `created_by_user_id` (UUIDv7, FK -> `User.id`): Authoring coach.
- `title` (VARCHAR(200)): Program title (e.g., "12-Week Hypertrophy Periodization").
- `description` (TEXT, Nullable): Overview and athlete instructions.
- `target_goal` (VARCHAR(50)): `hypertrophy` | `strength` | `fat_loss` | `endurance` | `general_fitness`.
- `is_template` (BOOLEAN, Default: `false`): If true, available to clone as an organization template.
- `is_archived` (BOOLEAN, Default: `false`): Archival state.
- `created_at` (TIMESTAMPTZ, UTC): Creation timestamp.
- `updated_at` (TIMESTAMPTZ, UTC): Last modification timestamp.

#### `ProgramPhase`
*Mesocycle or macrocycle block within a program.*
- `id` (UUIDv7, PK): Phase ID.
- `program_id` (UUIDv7, FK -> `Program.id`, Indexed): Parent program.
- `name` (VARCHAR(150)): Phase name (e.g., "Phase 1: Accumulation").
- `sequence_order` (INT): Order within the program (1, 2, 3...).
- `duration_weeks` (INT, Default: 4): Number of weeks in this block.

#### `ProgramWeek`
*Microcycle container.*
- `id` (UUIDv7, PK): Week ID.
- `phase_id` (UUIDv7, FK -> `ProgramPhase.id`, Indexed): Parent phase.
- `week_number` (INT): Week number (e.g., 1, 2, 3...).
- `focus_note` (TEXT, Nullable): Coach instructions for the week.

#### `ProgramDay`
*Scheduled training day within a week.*
- `id` (UUIDv7, PK): Day ID.
- `week_id` (UUIDv7, FK -> `ProgramWeek.id`, Indexed): Parent week.
- `day_number` (INT): Day sequence (e.g., 1 = Day 1, 2 = Day 2...).
- `title` (VARCHAR(150)): Day title (e.g., "Upper Body Power").

#### `Workout`
*Workout container attached to a training day.*
- `id` (UUIDv7, PK): Workout ID.
- `day_id` (UUIDv7, FK -> `ProgramDay.id`, Indexed): Parent day.
- `title` (VARCHAR(150)): Workout title.
- `estimated_minutes` (INT, Nullable): Estimated duration.

#### `WorkoutItem`
*Prescribed exercise block within a workout.*
- `id` (UUIDv7, PK): Workout item ID.
- `workout_id` (UUIDv7, FK -> `Workout.id`, Indexed): Parent workout.
- `exercise_id` (UUIDv7, FK -> `Exercise.id`, Indexed): Prescribed exercise.
- `sequence_order` (INT): Order within workout (1, 2, 3...).
- `group_key` (VARCHAR(10), Nullable): Grouping letter for supersets/circuits (e.g., "A1", "A2", "B1").
- `segment` (VARCHAR(20), Default: `main`): `warmup` | `main` | `cooldown`.
- `rest_seconds_between_sets` (INT, Default: 90): Prescribed rest interval.
- `coach_notes` (TEXT, Nullable): Specific coaching cue or instruction for this athlete.

#### `SetPrescription`
*Prescribed target parameters for individual sets.*
- `id` (UUIDv7, PK): Prescription ID.
- `workout_item_id` (UUIDv7, FK -> `WorkoutItem.id`, Indexed): Parent workout item.
- `set_index` (INT): Set number (1, 2, 3, 4...).
- `target_reps` (VARCHAR(50)): Prescribed reps (e.g., "8", "8-10", "AMRAP").
- `target_load` (VARCHAR(50), Nullable): Prescribed weight or intensity (e.g., "100 kg", "75% 1RM", "RPE 8").
- `target_rpe` (NUMERIC(3,1), Nullable): Target RPE rating (e.g., 8.5).
- `target_rir` (INT, Nullable): Reps in Reserve target (e.g., 2).
- `tempo` (VARCHAR(20), Nullable): Prescribed tempo (e.g., "3-0-1-0").

#### `ProgramAssignment` & `ProgramSnapshot`
*Binding of a program version to an athlete with an immutable point-in-time snapshot.*
- `id` (UUIDv7, PK): Assignment identifier.
- `organization_id` (UUIDv7, FK -> `Organization.id`, Indexed): Tenant context.
- `athlete_user_id` (UUIDv7, FK -> `User.id`, Indexed): Recipient athlete.
- `assigned_by_user_id` (UUIDv7, FK -> `User.id`): Assigning coach.
- `source_program_id` (UUIDv7, FK -> `Program.id`): Original template ID.
- `start_date` (DATE, Indexed): Training cycle start date.
- `end_date` (DATE, Nullable): Training cycle end date.
- `status` (VARCHAR(20), Default: `active`): `active` | `completed` | `archived`.
- `snapshot_payload` (JSONB): Complete frozen copy of all phases, weeks, workouts, items, and prescriptions at the instant of assignment.
- `created_at` (TIMESTAMPTZ, UTC): Assignment timestamp.

---

### 3.4 Athlete Workout Execution & Progress Domain

#### `WorkoutSession`
*Athlete's active or completed execution of a scheduled workout.*
- `id` (UUIDv7, PK): Session identifier.
- `program_assignment_id` (UUIDv7, FK -> `ProgramAssignment.id`, Indexed): Parent assignment.
- `athlete_user_id` (UUIDv7, FK -> `User.id`, Indexed): Executing athlete.
- `scheduled_date` (DATE, Indexed): Scheduled calendar date.
- `started_at` (TIMESTAMPTZ, Nullable): Execution start timestamp.
- `completed_at` (TIMESTAMPTZ, Nullable): Execution finish timestamp.
- `status` (VARCHAR(20), Default: `scheduled`): `scheduled` | `in_progress` | `completed` | `skipped` | `modified`.
- `skip_or_modify_reason` (VARCHAR(100), Nullable): Mandatory reason if skipped/modified.
- `session_rpe` (NUMERIC(3,1), Nullable): Overall session subjective exertion (1–10).
- `fatigue_score` (INT, Nullable): Subjective readiness/energy rating (1–5).
- `athlete_notes` (TEXT, Nullable): Athlete's post-workout comments.
- `created_at` (TIMESTAMPTZ, UTC): Session record creation.

#### `SetLog`
*Athlete's recorded actuals per set.*
- `id` (UUIDv7, PK): Set log identifier.
- `workout_session_id` (UUIDv7, FK -> `WorkoutSession.id`, Indexed): Parent workout session.
- `exercise_id` (UUIDv7, FK -> `Exercise.id`, Indexed): Completed exercise.
- `set_index` (INT): Set number.
- `actual_reps` (INT): Actual completed repetitions.
- `actual_load_kg` (NUMERIC(6,2)): Actual weight lifted in kilograms.
- `actual_rpe` (NUMERIC(3,1), Nullable): Actual perceived exertion.
- `is_completed` (BOOLEAN, Default: `true`): Set completion status.
- `notes` (VARCHAR(255), Nullable): Athlete set-level note.
- `created_at` (TIMESTAMPTZ, UTC): Timestamp of set completion.

#### `FeedbackFlag`
*High-visibility alert for pain, injury, or severe fatigue.*
- `id` (UUIDv7, PK): Feedback record ID.
- `workout_session_id` (UUIDv7, FK -> `WorkoutSession.id`, Indexed): Associated session.
- `athlete_user_id` (UUIDv7, FK -> `User.id`, Indexed): Athlete.
- `flag_type` (VARCHAR(50)): `joint_pain` | `muscle_strain` | `dizziness` | `severe_fatigue`.
- `anatomical_location` (VARCHAR(100)): e.g., "Left Shoulder", "Lower Back".
- `severity` (VARCHAR(20)): `mild` | `moderate` | `severe`.
- `details` (TEXT): Description of symptoms.
- `is_resolved` (BOOLEAN, Default: `false`): Coach review status.
- `created_at` (TIMESTAMPTZ, UTC): Report timestamp.

#### `ProgressPhoto`
*Private, consent-governed visual conditioning record.*
- `id` (UUIDv7, PK): Photo record ID.
- `athlete_user_id` (UUIDv7, FK -> `User.id`, Indexed): Owning athlete.
- `storage_key` (VARCHAR(500)): Encrypted S3 object key.
- `photo_type` (VARCHAR(20)): `front` | `side` | `back`.
- `athlete_consent_granted` (BOOLEAN, Default: `true`): Consent flag.
- `captured_at` (DATE): Photo date.
- `created_at` (TIMESTAMPTZ, UTC): Upload timestamp.

---

### 3.5 Communication, Notifications & Audit Domain

#### `MessageThread` & `Message`
*Contextual 1:1 coach-athlete communication.*
- `id` (UUIDv7, PK): Message ID.
- `thread_id` (UUIDv7, Indexed): Conversation thread ID.
- `sender_user_id` (UUIDv7, FK -> `User.id`, Indexed): Sending user.
- `recipient_user_id` (UUIDv7, FK -> `User.id`, Indexed): Target user.
- `workout_session_id` (UUIDv7, FK -> `WorkoutSession.id`, Nullable, Indexed): Contextual workout link.
- `content` (TEXT): Localized message body.
- `read_at` (TIMESTAMPTZ, Nullable): Read receipt timestamp.
- `created_at` (TIMESTAMPTZ, UTC): Dispatch timestamp.

#### `Notification` & `NotificationPreference`
*In-app alerts and delivery controls.*
- `id` (UUIDv7, PK): Notification ID.
- `user_id` (UUIDv7, FK -> `User.id`, Indexed): Target user.
- `event_type` (VARCHAR(50)): `program_assigned` | `workout_completed` | `pain_flag_raised` | `message_received`.
- `payload` (JSONB): Navigation links and localized parameters.
- `read_at` (TIMESTAMPTZ, Nullable): In-app read status.
- `created_at` (TIMESTAMPTZ, UTC): Dispatch timestamp.

#### `AuditEvent`
*Immutable security and compliance log.*
- `id` (UUIDv7, PK): Audit event ID.
- `actor_user_id` (UUIDv7, FK -> `User.id`, Nullable, Indexed): User performing action (NULL for system).
- `organization_id` (UUIDv7, FK -> `Organization.id`, Nullable, Indexed): Tenant context.
- `action` (VARCHAR(100), Indexed): Structured event type (e.g., `auth.login`, `membership.revoked`, `photo.viewed`).
- `target_entity_type` (VARCHAR(50)): Target table/model (e.g., `ProgramAssignment`).
- `target_entity_id` (VARCHAR(100)): Target ID.
- `ip_hash` (VARCHAR(64)): Anonymized SHA-256 hash of client IP.
- `metadata` (JSONB): Sanitized event details (excluding raw health payloads or passwords).
- `created_at` (TIMESTAMPTZ, UTC): Immutable event timestamp.
