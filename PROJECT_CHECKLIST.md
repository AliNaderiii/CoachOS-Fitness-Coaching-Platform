# Project Checklist — CoachOS

**Legend**

| Mark | Meaning |
|------|---------|
| `[ ]` | Not started |
| `[~]` | In progress |
| `[x]` | Completed and evidenced |
| `[!]` | Blocked |
| `[-]` | Deferred by decision |

**Last updated:** 2026-08-14 (UTC)

Evidence links point to repository paths, commits, or GitHub artifacts. Update after every meaningful task and at phase end.

---

## Phase 00 — Discovery and Repository Audit

- [x] Repository audit completed — evidence: `docs/reports/PHASE-00-DISCOVERY-REPORT.md`
- [x] Existing code, docs, tests, and deployment inspected — **none present** beyond MIT `LICENSE` + stub README
- [x] Product vision recorded — `docs/MASTER_PRODUCT_BRIEF.md`
- [x] Persian/English-only constraint recorded — README, brief, decisions, security doc
- [x] Arabic explicitly marked out of scope — same
- [x] User roles and initial scope recorded — brief + PRD outline
- [x] Risks and unknowns recorded — `PROJECT_STATUS.md`, Phase 00 report
- [x] Initial technical options evaluated — `docs/DECISIONS.md` (ADR-001 draft)
- [x] Initial GitHub issues/milestones created **or** in-repo backlog equivalent — milestones [1–9](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/milestones); issues [#1](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/issues/1), [#2](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/issues/2); canonical backlog `docs/RELEASE_PLAN.md`
- [x] Phase 00 report committed — `docs/reports/PHASE-00-DISCOVERY-REPORT.md`
- [x] Phase 00 merged to main via PR #3 (commit `f52c4134087b18c4bd1a8aef9e0100fd63f71b8e`)

**Phase 00 status:** `[x]` Complete (2026-08-10)

---

## Phase 01 — Product Requirements and Scope

- [x] Personas written — evidence: `docs/PERSONAS.md`
- [x] User journeys written — evidence: `docs/USER_JOURNEYS.md`
- [x] Domain glossary written — evidence: `docs/DOMAIN_GLOSSARY.md`
- [x] Competitive landscape & market benchmarking written — evidence: `docs/COMPETITIVE_LANDSCAPE.md`
- [x] P0 MVP defined (detailed stories) — evidence: `docs/PRD.md` §5
- [x] P1 and P2 backlog defined — evidence: `docs/PRD.md` §7, `docs/RELEASE_PLAN.md`
- [x] User stories written with stable IDs — evidence: `docs/PRD.md` §5
- [x] Acceptance criteria written in Gherkin with positive/negative authZ — evidence: `docs/PRD.md` §5
- [x] Non-functional requirements written with measurable targets — evidence: `docs/PRD.md` §8
- [x] Permissions matrix written — evidence: `docs/PRD.md` §6, `docs/SECURITY_AND_PRIVACY.md`
- [x] Decisions updated with PWA, License, Location, Calendar ADRs — evidence: `docs/DECISIONS.md`
- [x] Traceability matrix expanded with all P0 mappings — evidence: `docs/TRACEABILITY_MATRIX.md`
- [x] Phase 01 report committed — evidence: `docs/reports/PHASE-01-REQUIREMENTS-REPORT.md`

**Phase 01 status:** `[x]` Complete (2026-08-10)

---

## Phase 02 — UX, Information Architecture, and Design System

- [x] Navigation model defined — evidence: `docs/ux/NAVIGATION_MODEL.md`, `docs/ux/INFORMATION_ARCHITECTURE.md`
- [x] Coach flows designed — evidence: `docs/ux/USER_FLOWS.md`, `docs/ux/WIREFRAMES.md`
- [x] Athlete flows designed — evidence: `docs/ux/USER_FLOWS.md`, `docs/ux/WIREFRAMES.md`
- [x] Organization/admin flows designed — evidence: `docs/ux/USER_FLOWS.md`, `docs/ux/SCREEN_INVENTORY.md`
- [x] Persian RTL reviewed (typography & layout) — evidence: `docs/ux/RTL_LTR_SPECIFICATION.md`
- [x] English LTR reviewed — evidence: `docs/ux/RTL_LTR_SPECIFICATION.md`, `docs/ux/DESIGN_TOKENS.md`
- [x] Accessibility baseline defined (WCAG 2.2 AA) — evidence: `docs/ux/ACCESSIBILITY_SPEC.md`
- [x] Responsive breakpoints defined — evidence: `docs/ux/RESPONSIVE_BEHAVIOR.md`
- [x] Empty/loading/error/offline states designed — evidence: `docs/ux/STATE_AND_ERROR_MATRIX.md`
- [x] Phase 02 report committed — evidence: `docs/reports/PHASE-02-UX-DESIGN-REPORT.md`

**Phase 02 status:** `[x]` Complete (2026-08-10)

---

## Phase 03 — Architecture, Data, Security, and Privacy

- [x] Architecture diagram created (C4 System Context & Container) — evidence: `docs/architecture/SYSTEM_CONTEXT.md`, `docs/architecture/CONTAINER_ARCHITECTURE.md` with Mermaid C4Context/C4Container + fallback generic flow
- [x] ADRs created/finalized — evidence: `docs/DECISIONS.md` ADR-002 conditionally accepted stack, ADR-005 auth/session, ADR-009 calendar accepted conditional, ADR-010 monorepo proposed, ADR-014 membership multi-role accepted, ADR-015 snapshot accepted, ADR-016 soft-delete vs anonymized hard delete accepted, ADR-017 UUIDv7 proposed not authz substitute, ADR-018 Persian normalization accepted conditional, ADR-029 frontend Next.js boundaries, ADR-030 backend 20 modules, ADR-031 PG16 extensions, ADR-032 auth/session, ADR-033 RFC7807 error, ADR-034 media storage private signed TTL≤15min, ADR-035 PWA three-level, ADR-036 offline boundary, ADR-037 backup RTO/RPO proposed, ADR-038 env separation, ADR-039 CI/CD GitHub Actions, ADR-040 observability, ADR-041 OpenAPI 3.1 structure, ADR-042 threat model + control matrix, ADR-043 privacy lifecycle — license ADR-012 remains pending founder approval
- [x] Domain boundaries defined — evidence: `docs/architecture/DOMAIN_MODULES.md` M01-M20 with responsibility, owned entities, public interfaces, read/write deps, security boundary, events emitted/consumed, sensitivity, test boundary, extraction risk; `docs/architecture/COMPONENT_BOUNDARIES.md` frontend/backend component layout, middleware stack, dependency rules, sequence diagram assignment
- [x] Normalized PostgreSQL data model & ERD created — evidence: `docs/architecture/ERD.md` erDiagram + detailed entity specs for identity/tenancy (User, Organization, Location, Membership, Invitation, CoachAthleteAssignment), exercise catalog (Exercise, ExerciseTranslation, ExerciseAlias, MediaAsset, MediaRights, ModerationAction), programming (Program, Phase, Week, Day, Workout, WorkoutItem, SetPrescription, Assignment, Snapshot), athlete execution (WorkoutSession, SetLog, Substitution, FeedbackFlag, BodyMetric, ProgressPhoto, ConsentRecord), comms/ops (MessageThread, Message, Notification, Preference, AuditEvent, ExportRequest, ErasureRequest), future extensibility P1/P2 reserved, indexes GIN trigram, tenant ownership org_id, sensitive fields, unique constraints, state machines, soft-delete/archive policy, audit, retention, localization; conceptual DDL illustrative
- [x] Authorization model (RBAC + ABAC) defined — evidence: `docs/architecture/AUTHORIZATION_ARCHITECTURE.md` RBAC roles P0 platform_admin/owner/coach/athlete/support + future nutritionist P1 consent-gated, org boundaries active context request.org_id, object-level assignment rules, owner visibility aggregate vs raw (no automatic raw photo/message), break-glass admin MFA+reason+audit, consent lifecycle progress_photo and nutrition_sharing, export/erasure auth self-only, audit visibility owner own org only coach/athlete forbidden, suspension immediate 403, invitation permissions owner any coach athlete-only, detailed matrix per sensitive resource create/read/update/archive/export/share/revoke/consent/audited, negative controls list
- [x] Threat model completed — evidence: `docs/THREAT_MODEL.md` STRIDE 21 threats T01-T21 (account takeover, credential stuffing, session theft, invitation abuse, cross-tenant IDOR, unassigned coach, owner overreach, photo exposure, malicious uploads, stored XSS, CSRF, SSRF, webhook forgery future Phase10, notification abuse, export abuse, erasure abuse, insider/admin misuse, prompt injection future Phase11, supply-chain, backup leakage, enumeration) with asset, actor, attack path, impact, likelihood, risk level, preventive/detective/corrective controls, test strategy, owner, residual risk, OWASP mapping; `docs/SECURITY_CONTROL_MATRIX.md` mapping
- [x] Privacy/data lifecycle documented — evidence: `docs/PRIVACY_DATA_LIFECYCLE.md` 11 lifecycle stages collection/consent/storage/use/sharing/export/retention/revocation/deletion/anonymization/backup destruction, Tier0-8 classification per class purpose/legal assumption/owner/controller assumption/access/encryption/logging retention/export/deletion/consent, pre-DPIA checklist large-scale sensitive systematic monitoring profiling multi-prof sharing progress-photo wearable AI, privacy-aligned engineering design requires jurisdiction-specific legal review, consent UX ADR-027 explicit affirmative modal, multi-prof P1 consent, export/erasure pipelines sequence diagrams in `DATA_FLOW.md`
- [x] API strategy & OpenAPI catalog documented — evidence: `docs/OPENAPI.yaml` OpenAPI 3.1 provisional version /api/v1 covering 25+ endpoint groups auth/current user/profile/orgs/locations/memberships/invitations/exercises/moderation/programs/templates/assignments/today/sessions/set logs/feedback flags/progress photos/metrics/consents/messages/notifications/audit/privacy export/deletion/media signed URLs with method/path/purpose/auth/required role/object permission/request/response schema/error responses/localization/idempotency/audit/rate-limit/sensitivity + RFC7807 error model + message_key, `docs/JSON_SCHEMAS.md` snapshot JSON schema immutable, queue entry, export manifest, notification payload, consent, Persian normalizer pseudocode (Perso-Arabic script keyboard-variant normalization for Persian search), `docs/API_CONTRACT.md` v2.0 pointing to OPENAPI.yaml provisional
- [x] Backup/restore strategy documented — evidence: `docs/architecture/BACKUP_AND_DISASTER_RECOVERY.md` PG daily snapshot 30d retention proposed + WAL PITR 15min RPO 1h RTO proposed + manual pre-migration snapshot, S3 versioning noncurrent expire 30d, exports-tmp 7d lifecycle, Redis not source of truth loss acceptable, code git, restore runbooks DB/S3, weekly automated restore testing smoke tests, RPO/RTO proposed table, disaster scenarios, incident response detect triage contain investigate recover post-mortem communicate, breach response containment audit notification 72h if GDPR legal required, rollback app previous image + migration reverse 2-step pattern; `docs/architecture/OBSERVABILITY.md` structured logging JSON structlog redaction request_id correlation, audit vs debug separation, metrics Prometheus counters/histograms, Sentry error tracking, healthz/readyz, alerting categories auth anomaly cross-tenant 403 spike photo 403 spike 5xx>1% latency p95 DB connections Redis S3 Celery export fail backup fail disk cert expiry
- [x] Phase 03 report committed — evidence: `docs/reports/PHASE-03-ARCHITECTURE-REPORT.md` with 31 sections including preflight review, corrections, objectives, system context, container, domain modules, tech decisions, data model/ERD, authorization, API/OpenAPI, threat model, security control matrix, privacy lifecycle, media storage, PWA, observability, backup/DR, ADRs, validation checklist, files changed, GitHub branch/commit/PR, tests/validation, security/privacy risks, assumptions, open questions, founder approval items, deferred items, checklist changes, next prompt Phase04
- [x] Phase 03 architecture review corrections (PR #6 review — correction-only) — evidence: correction commit `b6ea570` on `arena/019fed02-coachos-fitness-coaching-platf` addressing critical review items: secret-manager boundary corrected FE --> SecretMgr forbidden removed, public NEXT_PUBLIC_* only private secrets only backend/worker, CSP corrected nonce/hash preferred no unsafe-inline as accepted production temporary exception marked with risk TODO-CSP-001, auth transport consistency corrected recommended MVP cookie HttpOnly Secure SameSite Lax CSRF double-submit + optional JWT short-lived memory rotating refresh HttpOnly reuse detection prohibition localStorage, data-model integrity corrections owner source of truth Organization.owner_user_id authoritative exactly one active owner Membership must match transactional transfer, membership multi-role union effective permissions role elevation audited active org/role selection frontend receives effective_permissions, CoachAthleteAssignment partial unique active WHERE status='active' allows archival recreation, backup wording corrected versioning ≠ independent backup nor cross-region DR versioning ≠ erasure compliance RPO/RTO proposed targets not guarantees cross-region replication multi-AZ retention residency requires cost/legal approval Redis not source of truth but important jobs must have durable DB state outbox/retry, API spec validated YAML parses OpenAPI 3.1 $ref resolve 135 local missing [] security schemes consistent RFC7807 message_key P0 groups align no payment/AI/wearable P0 provisional until Phase04 — evidence: `docs/architecture/DEPLOYMENT_ARCHITECTURE.md`, `CONTAINER_ARCHITECTURE.md`, `SYSTEM_CONTEXT.md`, `COMPONENT_BOUNDARIES.md`, `THREAT_MODEL.md`, `SECURITY_CONTROL_MATRIX.md`, `OPENAPI.yaml`, `ERD.md`, `DATA_MODEL.md`, `DECISIONS.md` ADR-005 ADR-014 ADR-032, `BACKUP_AND_DISASTER_RECOVERY.md`, `docs/reports/PHASE-03-ARCHITECTURE-REPORT.md` §32-34, `PROJECT_STATUS.md` §1.2

- [x] Phase 03 final review fixes (PR #6 final review — correction-only) — evidence: final review correction commit on `arena/019fed02-coachos-fitness-coaching-platf` after `b6ea570` addressing final review items: remove misleading public-config frontend-to-backend arrow FE -->|Public runtime config only| BE (public config is not secret request from frontend to backend) and replace with correct notation PublicConfigProvider --> FE (public config only NEXT_PUBLIC_* no secrets), BE --> SecretMgr (private secrets), Worker --> SecretMgr (private secrets), FE --> BE : HTTPS /api/v1 requests only (normal API, no secret-management flow); make OpenAPI AuthResponse consistent with recommended cookie-session MVP — cookie-session registration/login responses do not imply tokens returned, access_token/refresh_token optional/nullable present only when optional bearer strategy selected, recommended MVP uses HttpOnly session cookie + CSRF mechanism (csrf_token optional), optional JWT response short-lived in-memory access + rotating HttpOnly refresh cookie, no long-lived token in localStorage/sessionStorage, security/schemes/AuthResponse/registration/login/ADR-032 consistent, remains provisional until Phase04 implementation validation; validate after correction (YAML parses OpenAPI 3.1 $ref 137 local 137 missing [] 61 schemas, no FE --> SecretMgr actual diagram arrow, correct notation present, no app code) — evidence: `docs/architecture/DEPLOYMENT_ARCHITECTURE.md` (Config subgraph PublicConfigProvider, correct arrows), `CONTAINER_ARCHITECTURE.md` (fallback generic flow PublicConfigProvider --> WebApp, WebApp --> API HTTPS /api/v1 only, API --> SecretMgr), `SYSTEM_CONTEXT.md` (fallback generic flow Config subgraph PublicConfig --> Web, Web --> API HTTPS /api/v1 only, API --> SecretMgr), `docs/OPENAPI.yaml` (AuthResponse optional nullable tokens + csrf_token + CookieAuthResponse/BearerAuthResponse schemas + endpoint descriptions clarified MVP cookie no tokens in body), `docs/reports/PHASE-03-ARCHITECTURE-REPORT.md` §36, `PROJECT_STATUS.md` §1.3, `CHANGELOG.md`, `docs/PROMPT_LOG.md` Prompt 006, `docs/DECISIONS.md` ADR-005/032/014 final review notes

**Phase 03 status:** `[x]` Complete (2026-08-10) + corrections applied (review task b6ea570 + final review fixes current) — awaiting founder review of PR #6 before Phase04

---

## Phase 04 — Project Foundation & PWA Baseline

- [x] Local development setup works — evidence: `docker-compose.yml`, `compose.yaml`, `infra/docker/`, `docs/architecture/LOCAL_DEVELOPMENT.md`
- [x] Environment configuration documented — evidence: `.env.example`, `docs/architecture/LOCAL_DEVELOPMENT.md`, `backend/config/settings/`
- [x] Frontend scaffold works (Next.js + TypeScript + Tailwind) — evidence: `frontend/` Next.js 14 App Router, `tailwind.config.js`, 49 Vitest tests passing, 18-page static build verified from clean tracked implementation commit `8c268db973530157fb1468bc1838f8bca59f7310`
- [x] Backend scaffold works (Django + DRF) — evidence: `backend/` Django 5.2 + DRF 3.18, 37 Pytest tests passing, middleware pipeline, RFC 7807 problem details
- [x] PWA foundation (Manifest, installable shell, Service Worker) works — evidence: `frontend/public/manifest.json`, `frontend/public/sw.js`, `frontend/public/icons/`, `frontend/app/[locale]/offline/page.tsx`, `frontend/components/pwa/`
- [x] Database and migrations work — evidence: PostgreSQL 16 connection config, initial foundation syncdb/migrations tested in test/dev
- [x] GitHub Actions activation — evidence: PR #10 (`chore/activate-github-actions-manual`) **merged** into `main` at `0855867cc85f56bb4b77c5f708db8e122ded6b81` (2026-08-14T06:36:42Z); `.github/workflows/ci.yml` and `.github/workflows/security-scan.yml` verified present on remote `main` (`git ls-tree origin/main`); GitHub Actions workflows active; post-merge runs on the merge commit succeeded — CoachOS CI Quality Gates run ID `31776895893` (conclusion `success`) and Security & Vulnerability Scan run ID `31776896050` (conclusion `success`); no deployment job or real secret exists
- [x] Local lint/type/test commands work — evidence: Ruff lint + format (clean), ESLint (clean), TypeScript `tsc --noEmit` (clean), Pytest (37 passed), Vitest (49 passed)
- [x] Health checks work — evidence: `GET /healthz` (200 OK liveness), `GET /readyz` (DB + Redis readiness), `GET /api/v1/meta` (public system metadata)
- [x] Phase 04 report committed — evidence: `docs/reports/PHASE-04-FOUNDATION-REPORT.md`
- [x] Post-merge source audit completed — authoritative original source for the nine missing `frontend/lib/` files was unrecoverable; no restoration claim is made
- [x] Founder-authorized specification-based frontend reimplementation completed — evidence: exactly nine tracked files under `frontend/lib/` at implementation commit `8c268db973530157fb1468bc1838f8bca59f7310`
- [x] Narrow `.gitignore` correction applied — general `lib/` rule retained; only `/frontend/lib/` and `/frontend/lib/**` explicitly unignored
- [x] Focused remediation tests added without weakening existing tests — API client, service-worker registration, public configuration, date boundaries, Persian normalization, exact locale metadata, and 54-key bilingual governance
- [x] Clean tracked-only validation completed — `npm ci`, frontend lint/type-check/49 tests/build, backend Ruff/37 tests, compliance/language/PWA scans, `git diff --check`, `git check-ignore`, and `git ls-files frontend/lib`
- [x] Separate correction report committed — evidence: `docs/reports/POST-MERGE-PHASE-04-FRONTEND-REIMPLEMENTATION-REPORT.md`; original report retained unchanged
- [x] Post-merge remediation PR merged — evidence: PR [#8](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/8) merged into `main` on 2026-08-11T15:20:23Z at merge commit `dd7dea56945d96a6a2d595afb5154b6828c4e3b6`; all nine `frontend/lib/` files verified present and tracked on remote `main` via GitHub Contents API and `git ls-tree origin/main`; broad `lib/` ignore rule retained with only `/frontend/lib/` exceptions
- [x] Post-merge status synchronization PR #9 merged (`0eae53b...`, 2026-08-12); CI activation PR #10 (`chore/activate-github-actions-manual`) **merged** at `0855867cc85f56bb4b77c5f708db8e122ded6b81` (2026-08-14T06:36:42Z); `.github/workflows/ci.yml` and `.github/workflows/security-scan.yml` present on remote `main`; GitHub Actions active with successful post-merge runs (`31776895893`, `31776896050`); Phase 05 was subsequently authorized, delivered, and merged via PR #13 (`d7f72b3f...`)

**Phase 04 status:** `[x]` Complete — original foundation merged via PR #7; post-merge frontend remediation merged via PR #8 (`dd7dea56945d96a6a2d595afb5154b6828c4e3b6`) on 2026-08-11; docs synchronization PR #9 (`0eae53b89343ec0a4eb1200086b769011012c406`) merged 2026-08-12; CI activation PR #10 (`chore/activate-github-actions-manual`) merged at `0855867cc85f56bb4b77c5f708db8e122ded6b81` on 2026-08-14 with both workflows on remote `main` and successful post-merge runs (CoachOS CI Quality Gates `31776895893` success, Security & Vulnerability Scan `31776896050` success); Phase 05 was subsequently authorized, delivered, and merged via PR #13 (`d7f72b3f...`)

---

## Phase 05 — Identity, Tenancy, and Roles

- [x] Authentication works (Email + Password) — cookie session MVP + CSRF
- [x] Single-location organization creation works — transactional + owner membership
- [x] Invitations work (single-use tokens) — hashed, 7d expiry, role-limited
- [x] Role permissions work server-side — RBAC + tenant isolation
- [x] Object-level access tests exist (negative authZ tests) — cross-tenant, suspended, replay
- [x] Audit events exist (immutable logging) — redacted, append-only
- [x] Persian/English settings work — locale/unit/timezone on User
- [x] Phase 05 report committed — `docs/reports/PHASE-05-IDENTITY-TENANCY-ROLES-REPORT.md`
- [x] Phase 05 implementation PR merged — evidence: PR [#13](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/13) (`feat(phase-05): Identity, Tenancy, and Roles foundation`, head `arena/019fff0b-coachos-fitness-coaching-platf`) **merged** into `main` at merge commit `d7f72b3fcfd6667df524af5adf71328c5de6edba` on 2026-08-14T08:40:58Z; all four post-merge GitHub Actions checks on the merge commit successful — Backend Lint, Type & Tests (Django/DRF); Frontend Lint, Type & Tests (Next.js/PWA); Security Scan & Language Compliance; Secret & Pattern Scanning (runs `31784911766`, `31784911764`, both `success`)
- [-] Deferred Phase 05 items (deferred by decision, pending later authorized phases): frontend onboarding UI, ownership transfer, full effective-permissions/active-org context, production email delivery, MFA, compliance certification. Phase 06 adds only the minimal tenant-scoped `CoachAthleteAssignment` relation needed for program-assignment authorization; broader lifecycle/UI remains deferred.

**Phase 05 status:** `[x]` **Merged & Complete** — merged into `main` via PR #13 at `d7f72b3fcfd6667df524af5adf71328c5de6edba` (2026-08-14T08:40:58Z) with all post-merge GitHub Actions checks passing; complete for its documented scope with deferred items recorded above. Phase 06 was subsequently authorized and is now an unmerged candidate on its dedicated Arena branch.

---

## Phase 06 — Exercise Library and Training Programs

- [x] Exercise schema works
- [x] Bilingual exercise search & Persian character variant folding works
- [x] Media rights metadata exists
- [x] Program builder works (hierarchical phases/weeks/days/items/prescriptions)
- [x] Reusable templates work
- [x] Program assignments work (immutable snapshot creation)
- [x] Admin moderation queue API works
- [x] Coach tests exist
- [x] Phase 06 report prepared on the Phase 06 branch

**Phase 06 status:** `[~]` Gates 0–9 have local, isolated-checkout, publication, and successful published-head GitHub Actions evidence. PR [#15](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/15) is open targeting `main` (runs `31790374656`, `31790374657`, `31790363694` succeeded). Phase 06 is not merged and is not declared complete. Founder review is required; do not start Phase 07.

---

## Phase 07 — Athlete App and Progress

- [ ] Today workout view works
- [ ] Mobile set actuals logging works
- [ ] Rest timer works
- [ ] Exercise substitution/modification works with reasons
- [ ] Completion/adherence tracking works
- [ ] Feedback and pain/fatigue flags work
- [ ] Progress photos are permissioned and consent-governed
- [ ] Mobile responsiveness & installed-PWA mobile experience tested
- [ ] Phase 07 report committed

**Phase 07 status:** `[ ]` Not started

---

## Phase 08 — Communication and Notifications

- [ ] Contextual 1:1 message threads work
- [ ] Workout session contextual references work
- [ ] In-app notifications work
- [ ] Notification preferences work
- [ ] Email/push adapter interface documented
- [ ] Abuse/rate limits considered
- [ ] Phase 08 report committed

**Phase 08 status:** `[ ]` Not started

---

## Phase 09 — Nutrition and Multi-Professional Collaboration

- [ ] Nutritionist role implemented
- [ ] Consent-based collaboration implemented
- [ ] Meal plans work
- [ ] Persian & international food/recipe data model works
- [ ] Macro calculations are tested
- [ ] Health-data privacy review completed
- [ ] Phase 09 report committed

**Phase 09 status:** `[ ]` Not started — **P1, deferred until activated**

---

## Phase 10 — Billing and Coach Monetization

- [ ] Payment provider abstraction (Shetab domestic / Stripe international) exists
- [ ] Products and packages exist
- [ ] Subscriptions exist
- [ ] Webhooks are idempotent
- [ ] Entitlements are tested
- [ ] Multi-location gym support implemented
- [ ] Coach storefront exists
- [ ] Phase 10 report committed

**Phase 10 status:** `[ ]` Not started — **P1, deferred until activated**

---

## Phase 11 — AI Copilot

- [ ] AI use cases prioritized
- [ ] Safety boundaries & human-in-the-loop review workflow documented
- [ ] Approved retrieval data sources defined
- [ ] Prompt/version logging exists
- [ ] Cost/rate limits exist
- [ ] Evaluation cases exist
- [ ] Fallback behavior exists
- [ ] Phase 11 report committed

**Phase 11 status:** `[ ]` Not started — **P2, deferred until activated**

---

## Phase 12 — Advanced Offline PWA & Integrations

- [ ] Advanced IndexedDB offline workout caching works
- [ ] Sync queues & conflict resolution work
- [ ] Background sync where supported works
- [ ] Push notification limitations documented
- [ ] Wearable integrations (HealthKit / Health Connect) evaluated
- [ ] Native application strategy decision recorded
- [ ] Phase 12 report committed

**Phase 12 status:** `[ ]` Not started — **P2, deferred until activated**

---

## Phase 13 — QA, Security, Performance, and Release

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] RTL/LTR visual regression tests pass
- [ ] Accessibility review pass (WCAG 2.2 AA)
- [ ] Security review & penetration testing pass
- [ ] Dependency scan pass
- [ ] Performance baseline recorded (< 1.5s Today view on 3G)
- [ ] Backup/restore tested
- [ ] Staging deployment works
- [ ] Release checklist completed
- [ ] Phase 13 report committed

**Phase 13 status:** `[ ]` Not started

---

## Phase 14 — Pilot and Iteration

- [ ] Pilot cohort defined (gyms, coaches, athletes)
- [ ] Feedback mechanism exists
- [ ] Empirical usage and business metrics collected
- [ ] Critical bugs resolved
- [ ] Onboarding documented
- [ ] Pricing hypothesis tested
- [ ] Pilot report committed

**Phase 14 status:** `[ ]` Not started

---

## Cross-Cutting Standing Rules (Always On)

- [x] No Arabic content, locale files, or requirements
- [x] No secrets committed to Git repository
- [x] Synthetic test data only (no real PII/health data)
- [x] Current tracked user-facing strings supplied through matching `fa-IR` and `en-US` resources (54 governed keys)
- [ ] Server-side authorization for every sensitive action
- [ ] Immutable audit log for sensitive access/mutations
- [ ] Phase report + checklist + changelog + prompt log updated per phase
