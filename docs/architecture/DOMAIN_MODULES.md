# Domain Modules & Boundaries — CoachOS

**Version:** 1.0.0 Phase 03  
**Status:** Proposed (modular monolith)  
**Pattern:** Each module owns entities, exposes service layer interface, emits/consumes domain events via in-process event bus (future extraction to message bus if needed).

---

## 1. Module List & Ownership

| # | Module | P0/P1/P2 | Owned Entities (Primary) |
|---|--------|----------|--------------------------|
| M01 | Identity and Authentication | P0 | User, Credential (password hash), Session/RefreshToken, PasswordResetToken |
| M02 | Organizations and Tenancy | P0 | Organization, Location (primary MVP) |
| M03 | Memberships and Invitations | P0 | Membership, Invitation, Role binding |
| M04 | Authorization and Consent | P0 | CoachAthleteAssignment, ConsentRecord, RoleDefinitions |
| M05 | Exercise Catalog | P0 | Exercise, ExerciseTranslation, ExerciseAlias, MuscleGroup*, Equipment*, MovementPattern |
| M06 | Media and Rights Provenance | P0 | MediaAsset, MediaRights, ModerationAction |
| M07 | Training Programs | P0 | Program, ProgramPhase, ProgramWeek, ProgramDay, Workout |
| M08 | Program Templates | P0 | Program (is_template flag), Template clone logic — same table as Program |
| M09 | Program Assignments & Snapshots | P0 | ProgramAssignment, ProgramSnapshot (JSONB), ProgramVersion |
| M10 | Athlete Workout Sessions | P0 | WorkoutSession, SetLog, ExerciseSubstitution, CompletionStatus |
| M11 | Progress and Feedback | P0 | FeedbackFlag, BodyMetric, ProgressPhoto, BodyWeight log |
| M12 | Messaging | P0 | MessageThread, Message (contextual workout_session_id) |
| M13 | Notifications | P0 | Notification, NotificationPreference |
| M14 | Admin and Moderation | P0 | Moderation queue view, Platform Admin actions (uses Audit) |
| M15 | Audit Events | P0 | AuditEvent (immutable) |
| M16 | Privacy Export and Erasure | P0 | ExportRequest, ErasureRequest, Anonymization pipeline |
| M17 | Future Nutrition | P1 | NutritionProfessionalAssignment, MealPlan, Recipe, FoodItem, AllergyRestriction |
| M18 | Future Billing | P1 (Phase10) | Product, Subscription, Payment, Entitlement, Coupon |
| M19 | Future Marketplace | P2 | MarketplaceListing, Review, Rating |
| M20 | Future AI Copilot | P2 (Phase11) | AIRunLog, PromptVersion, HumanReviewDecision |

*Taxonomy tables optional — can be enum + translation.

---

## 2. Module Specifications

### M01 Identity & Authentication
- **Responsibility:** Registration, login, password reset, session management, rate limiting.
- **Owned Entities:** User, Session, PasswordResetToken
- **Public Interfaces:** `AuthService.register()`, `login()`, `issueTokens()`, `resetPassword()`, `verifySession()`
- **Read Dependencies:** Memberships (for post-login org picker)
- **Write Dependencies:** AuditEvents (auth events)
- **Security Boundary:** Argon2id/bcrypt hashing, 5/15min rate limit via Redis, single-use tokens 15min TTL.
- **Events Emitted:** `user.registered`, `user.logged_in`, `user.password_reset`
- **Events Consumed:** none
- **Data Sensitivity:** Tier 1 (email, hash) — no plaintext passwords logged.
- **Test Boundary:** Unit + integration for hashing, negative login, reuse token, rate limit.
- **Future Extraction Risk:** Low — stable, rarely extracted.

### M02 Organizations and Tenancy
- **Responsibility:** Organization creation, slug uniqueness, single primary location MVP.
- **Owned Entities:** Organization, Location
- **Public Interfaces:** `OrgService.createOrg(ownerId, name, slug)`, `updateLocation(orgId, data)`
- **Read Dependencies:** Memberships for owner check
- **Write Dependencies:** Audit, Membership (owner)
- **Security Boundary:** Only authenticated users can create orgs; slug must be unique; org_id derivation from auth context mandatory in all queries.
- **Events Emitted:** `org.created`, `org.location_updated`
- **Events Consumed:** `user.registered` (optional provisioning)
- **Data Sensitivity:** Tier1
- **Test Boundary:** slug collision 409, cross-tenant org read 404/403.
- **Future Extraction Risk:** Low.

### M03 Memberships and Invitations
- **Responsibility:** Invitation lifecycle (7-day single-use, hashed token storage), role binding, suspend/revoke.
- **Owned Entities:** Membership, Invitation
- **Public Interfaces:** `InvitationService.create(email, role, orgId, invitedBy)`, `accept(token)`, `revoke()`
- **Read Dependencies:** Organizations, Users
- **Write Dependencies:** AuditEvents, Membership statuses
- **Security Boundary:** Token hashed with SHA-256 stored, plaintext token only in email; single-use enforcement; resend limited; suspended membership blocks all org-scoped reads via middleware.
- **Events Emitted:** `invitation.sent`, `invitation.accepted`, `membership.suspended`
- **Events Consumed:** `org.created` (owner membership creation)
- **Data Sensitivity:** Tier1
- **Test Boundary:** reuse token 410 Gone negative test, suspended membership 403.
- **Extraction Risk:** Medium — could become Identity sub-domain externally.

### M04 Authorization and Consent
- **Responsibility:** Central RBAC + object-level ABAC evaluation; consent records for progress photos and P1 nutrition sharing.
- **Owned Entities:** CoachAthleteAssignment, ConsentRecord
- **Public Interfaces:** `AuthZService.can(user, action, resource)`, `requireOrgScope()`, `requireCoachAssignment()`, `requireConsent()`
- **Read Dependencies:** Memberships, Organizations, ConsentRecords
- **Write Dependencies:** AuditEvent on sensitive reads.
- **Security Boundary:** All tenant-scoped queries must pass through OrgScope filter; coach-athlete must have active assignment; owner cannot view raw progress photo without explicit consent.
- **Events Emitted:** `consent.granted`, `consent.revoked`, `assignment.created`
- **Events Consumed:** `membership.suspended` (auto-archive assignments)
- **Data Sensitivity:** Tier3/4 — audited reads
- **Test Boundary:** Negative matrix: cross-tenant read, unassigned coach access, suspended membership, photo without consent, message without assignment — all must return 403/404.
- **Extraction Risk:** High if moved to policy engine (OPA) later — keep interface abstraction.

### M05 Exercise Catalog
- **Responsibility:** Bilingual canonical + private custom exercises, translations, alias normalization, filtering/search.
- **Owned Entities:** Exercise, ExerciseTranslation, ExerciseAlias, (optional MuscleGroup taxonomy)
- **Public Interfaces:** `ExerciseService.search(q, filters, locale, orgId)`, `createPrivate()`, `publishCanonical()`
- **Read Dependencies:** Media, Organizations (private scope)
- **Write Dependencies:** Audit (publish), Search index (pg_trgm)
- **Security Boundary:** Private exercises visible only to org members; canonical published globally; Persian Unicode character-variant folding performed in search pipeline.
- **Events Emitted:** `exercise.created_private`, `exercise.submitted_for_review`, `exercise.published`
- **Events Consumed:** `media.uploaded`
- **Data Sensitivity:** Tier0 (public canonical) + Tier2 (private custom proprietary)
- **Test Boundary:** Search normalization test: Arabic Yeh → Persian Yeh mapping; ZWNJ folding; cross-org private exercise isolation.
- **Extraction Risk:** Medium — could become search microservice with external index (Elastic) if scale demands; keep interface search-agnostic.

### M06 Media and Rights Provenance
- **Responsibility:** Upload validation, storage keys, rights metadata, moderation state.
- **Owned Entities:** MediaAsset, MediaRights, ModerationAction
- **Public Interfaces:** `MediaService.upload(file, exerciseId, rights)`, `generateSignedUrl(assetId, requesterId)` with TTL ≤15min
- **Read Dependencies:** Exercise, User (reviewer)
- **Write Dependencies:** S3, Audit (media rights review)
- **Security Boundary:** Private buckets only, no public ACL; MIME whitelist (image/jpeg, png, webp, mp4); size limits (10MB image, 100MB video proposed); checksum SHA256; optional ClamAV stub for Phase 13.
- **Events Emitted:** `media.uploaded`, `media.rights_reviewed`
- **Events Consumed:** `exercise.published`
- **Data Sensitivity:** Tier4 for progress photos — never public URL.
- **Test Boundary:** Malicious upload (e.g., .php disguised as jpeg) must fail; oversized file 413; unauthorized signed URL generation 403.
- **Extraction Risk:** High — media processing often extracted to dedicated service (thumbnail, transcoding).

### M07 Training Programs (Hierarchy)
- **Responsibility:** Hierarchical builder: Program → Phase → Week → Day → Workout → WorkoutItem → SetPrescription
- **Owned Entities:** Program, ProgramPhase, ProgramWeek, ProgramDay, Workout, WorkoutItem, SetPrescription
- **Public Interfaces:** `ProgramBuilder.create()`, `addPhase()`, `addWorkoutItem()`, `groupSuperset(groupKey)`, `save()`
- **Read Dependencies:** Exercise (existence), Organization (owner)
- **Write Dependencies:** Audit, ProgramVersion/Snapshot via M09
- **Security Boundary:** Only Owner/Coach of org can mutate; program templates org-private; atomic transactions for multi-entity saves.
- **Events Emitted:** `program.created`, `program.updated`, `workoutitem.added`
- **Data Sensitivity:** Tier2 proprietary
- **Test Boundary:** Empty phase validation, cross-tenant program edit 403.
- **Extraction Risk:** Low-medium.

### M08 Program Templates
- **Responsibility:** Template flag, clone/fork logic ensuring deep copy does not mutate master.
- **Owned Entities:** Reuses Program table with is_template boolean.
- **Public Interfaces:** `TemplateService.saveAsTemplate(programId)`, `cloneTemplate(templateId, athleteId?)`
- **Read Dependencies:** Programs
- **Write Dependencies:** Programs (clone), Audit
- **Security Boundary:** Same as M07; clone isolated.
- **Events Emitted:** `template.created`, `template.cloned`
- **Events Consumed:** `program.created`
- **Test Boundary:** Clone independence test — mutating clone does not affect master snapshot.

### M09 Assignments & Snapshots
- **Responsibility:** Binding program to athlete with immutable snapshot JSONB preserving point-in-time prescriptions.
- **Owned Entities:** ProgramAssignment, ProgramSnapshot (embedded JSONB), ProgramVersion
- **Public Interfaces:** `AssignmentService.assign(programId, athleteId, startDate) → Snapshot`, `pushUpdate()` (explicit re-assign with confirmation)
- **Read Dependencies:** CoachAthleteAssignment, Program hierarchy
- **Write Dependencies:** Audit, Notification (assignment notification)
- **Security Boundary:** Only assigned coach or owner can assign; athlete must belong to same org; snapshot immutable after creation.
- **Events Emitted:** `program.assigned`, `snapshot.created`
- **Events Consumed:** `coachAssignment.created` (validates)
- **Data Sensitivity:** Tier2
- **Test Boundary:** Assignment creates snapshot that does NOT change when master template edited; cross-tenant assignment fails 403.
- **Extraction Risk:** Low.

### M10 Workout Sessions
- **Responsibility:** Athlete execution lifecycle: scheduled → in_progress → completed/skipped/modified; set actuals logging; rest timer is client-side.
- **Owned Entities:** WorkoutSession, SetLog, ExerciseSubstitution
- **Public Interfaces:** `SessionService.start(scheduledId)`, `logSet()`, `substituteExercise(reason)`, `complete()`
- **Read Dependencies:** Assignment snapshot, Exercise, Consent (for photo context)
- **Write Dependencies:** Audit (completion), FeedbackFlag (via M11), Notification (coach notified)
- **Security Boundary:** Athlete self-only logging; coach proxy logging allowed? Proposed: coach can log on behalf (flagged) but primary is athlete; all set logs timestamped.
- **Events Emitted:** `session.started`, `session.completed`, `set.logged`, `exercise.substituted`
- **Events Consumed:** `program.assigned` (schedules sessions)
- **Data Sensitivity:** Tier2 operational + Tier3 if discomfort flag
- **Test Boundary:** Unassigned coach cannot read session 403; suspended athlete cannot log 403; temp offline preservation is in-memory only, not durable until Phase12.

### M11 Progress and Feedback
- **Responsibility:** Pain/fatigue flags, body metrics, progress photos with consent gating.
- **Owned Entities:** FeedbackFlag, BodyMetric, ProgressPhoto, ConsentRecord (reuses M04)
- **Public Interfaces:** `ProgressService.uploadPhoto()`, `recordBodyMetric()`, `flagPain()`
- **Read Dependencies:** Consent, Assignment, Organization
- **Write Dependencies:** Media (S3 private), Audit (sensitive health read), Notification (pain flag to coach)
- **Security Boundary:** Photo upload blocked until consent modal logged; photo view requires consent + CoachAssignment; Owner aggregate reporting allowed, raw individual photo requires explicit consent + audited escalation; support DENIED.
- **Events Emitted:** `photo.uploaded`, `pain.flagged`, `body_metric.recorded`
- **Events Consumed:** `consent.granted`
- **Data Sensitivity:** Tier3 health-adjacent + Tier4 media — most sensitive.
- **Test Boundary:** Negative tests: David (unassigned coach) cannot view Neda's photo 403; Owner without consent cannot view; signed URL never generated for unauthorized.
- **Extraction Risk:** Medium — privacy module may need hardening later.

### M12 Messaging
- **Responsibility:** Contextual 1:1 threads linked to workout sessions.
- **Owned Entities:** MessageThread, Message
- **Public Interfaces:** `MessageService.send(sender, recipient, threadId, workoutSessionId?)`, `listThreads(user)`
- **Read Dependencies:** CoachAthleteAssignment, WorkoutSession (context)
- **Write Dependencies:** Notification, Audit (admin escalation reads)
- **Security Boundary:** Only assigned coach and owner(?) + athlete can message; messages org-private; thread listing scoped to participant; no cross-tenant message read.
- **Events Emitted:** `message.sent`
- **Events Consumed:** none
- **Data Sensitivity:** Tier2 + private — Tier4-like confidentiality expectations; Owner escalation audited.
- **Test Boundary:** Unauthorized coach cannot read private thread 403; suspended user cannot send.
- **Extraction Risk:** Medium — messaging often extracted to separate service, but P0 stays monolithic.

### M13 Notifications
- **Responsibility:** In-app notification engine, preferences, email fan-out via abstraction.
- **Owned Entities:** Notification, NotificationPreference
- **Public Interfaces:** `NotificationService.dispatch(eventType, userId, payload)`, `markRead()`, `updatePreferences()`
- **Read Dependencies:** Membership, Message, Session, Pain flags
- **Write Dependencies:** Redis queue, Email provider (via M14? actually direct), Audit
- **Security Boundary:** User can only read own notifications; preferences cannot silence mandatory security or assignment alerts.
- **Events Emitted:** `notification.dispatched`
- **Events Consumed:** `session.completed`, `message.sent`, `pain.flagged`, `program.assigned`, `invitation.sent`
- **Data Sensitivity:** Tier1
- **Test Boundary:** Notification preference disabling must still deliver critical assignment alerts.
- **Extraction Risk:** Medium — push likely extracted later.

### M14 Admin and Moderation
- **Responsibility:** Global catalog moderation, organization directory, user management, security audit viewer.
- **Owned Entities:** (views over Exercise, Organization, User, AuditEvent)
- **Public Interfaces:** `AdminService.moderateExercise()`, `listOrgs()`, `suspendUser()`
- **Read Dependencies:** All tenant data (with break-glass)
- **Write Dependencies:** Exercise status, MediaRights, Audit (mandatory for every admin write), Membership suspension.
- **Security Boundary:** `is_platform_admin=true` + MFA required + session short-lived (15min?) + every read of sensitive Tier3/4 logs audited escalation record; no DELETE of audit logs ever.
- **Events Emitted:** `admin.exercise_published`, `admin.user_suspended`, `admin.break_glass_access`
- **Events Consumed:** `exercise.submitted_for_review`
- **Data Sensitivity:** Highest privilege — global read but audited.
- **Test Boundary:** Non-admin cannot access /admin/* 403; admin sensitive health read generates audit.
- **Extraction Risk:** Low.

### M15 Audit Events
- **Responsibility:** Immutable append-only log for security/compliance traceability.
- **Owned Entities:** AuditEvent
- **Public Interfaces:** `AuditService.log(actor, action, target, orgId, metadata)`, `query(orgId?, actorId?)`
- **Read Dependencies:** None (global but query scoped)
- **Write Dependencies:** None (only writes)
- **Security Boundary:** Table has no UPDATE/DELETE permissions for app roles; DB-level RLS or trigger prevents mutation; metadata must not contain raw passwords, health raw, or PII beyond needed; IP stored as SHA256 hash.
- **Events Emitted:** (none — audit is terminal)
- **Events Consumed:** All security events.
- **Data Sensitivity:** Tier5 — sensitive but not PII; careful retention.
- **Test Boundary:** Attempted UPDATE of audit row fails at DB level; audit cannot be deleted by Owner.
- **Extraction Risk:** Low — could move to immutable log store (e.g., append-only S3) later.

### M16 Privacy Export and Erasure
- **Responsibility:** GDPR-adjacent export ZIP (profile.json, workouts.json, set_logs.csv, media) + anonymization pipeline.
- **Owned Entities:** ExportRequest, ErasureRequest
- **Public Interfaces:** `PrivacyService.requestExport(userId)`, `requestErasure(userId, passwordConfirm)`
- **Read Dependencies:** All user-scoped data across modules.
- **Write Dependencies:** S3 (temporary export archive), Audit (export/erasure), Celery jobs, Membership (archive)
- **Security Boundary:** Export requires authenticated user; time-limited download link via verified email; erasure requires password re-entry + confirmation; erasure purges PII but retains anonymized aggregates disassociated.
- **Events Emitted:** `privacy.export_requested`, `privacy.export_completed`, `privacy.erasure_requested`, `privacy.erasure_completed`
- **Events Consumed:** none
- **Data Sensitivity:** Tier1-Tier4.
- **Test Boundary:** Unauthorized user cannot request export for another user 403; erasure wipes email and photos; backup destruction deferred — question.
- **Extraction Risk:** Low.

### M17-M20 Future (P1/P2) — Boundaries Reserved

- **M17 Nutrition:** Requires explicit athlete consent; reads allowed only if `ConsentRecord(nutrition_sharing)` active; own tables MealPlan, FoodItem, etc tenant-scoped + athlete-linked; sensitive Tier3.
- **M18 Billing:** Product, Subscription, Payment tokenization; webhook idempotency; no raw PAN; PCI-adjacent via gateway abstraction.
- **M19 Marketplace:** Listing, Review — public discovery but only published workouts; moderate for IP abuse.
- **M20 AI Copilot:** AIRunLog, PromptVersion, with human-in-loop review, no autonomous medical claims, prompt + completion logged, cost/rate limit.

No P1/P2 implementation in P0; architecture reserves foreign keys and consent hooks.

---

## 3. Cross-Module Dependency Rules

- **Allowed dependencies:** Lower layers (Identity) do not depend on upper (Messaging). Higher may depend on lower.
- **Dependency hierarchy (lowest to highest):** Identity → Organizations → Memberships → Authorization/Consent → Exercise/Media → Programs → Assignments → Sessions/Progress → Messaging/Notifications → Admin/Audit/Privacy → Future modules.
- **Forbidden:** No circular imports; no direct cross-write bypassing public interface; every cross-module read that is tenant-scoped must pass org scope via AuthZ.
- **Enforcement:** `import-linter` or `django-deps` lint in CI to fail if forbidden import detected.

---

## 4. Event Bus (In-Process, P0)

- Simple in-process pub/sub (`django.dispatch` or custom `EventBus`) with type-safe events listed per module.
- No persistent MQ for P0 (Redis/Celery for async tasks is separate, not event bus). If extraction needed, migrate to outbox pattern (Phase 10+).

---

## 5. Security & Privacy Cross-Cutting

- Every module must call `AuthZService` for tenant and assignment checks.
- No module may generate S3 signed URL without going through MediaService + AuthZ.
- All security-relevant mutations must emit AuditEvent.

---

## 6. References

- `SYSTEM_CONTEXT.md`, `CONTAINER_ARCHITECTURE.md`, `AUTHORIZATION_ARCHITECTURE.md`, `ERD.md`
