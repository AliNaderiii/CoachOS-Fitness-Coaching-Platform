# Changelog

All notable changes to this project are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
This project will follow [Semantic Versioning](https://semver.org/) once the first versioned release is cut.

## [Unreleased]

### Changed — Post-Merge Phase 07 Status Synchronization (docs-only, no code/test/dependency/workflow changes)

- Recorded that PR [#15](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/15) and docs-only PR [#16](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/16) are merged, and that Phase 07 PR [#17](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/17) (`feat(phase-07): athlete app and progress logging`) merged into `main` at `0949abeead5ba74a3deb0d2439a464ab6bbd99dd` on 2026-08-16T09:57:48Z.
- Marked Phase 07 — Athlete App and Progress Logging **merged and complete for its documented scope**, replacing stale pre-merge wording (Phase 07 in progress; PR #17 open / staged for founder review; next step to complete Phase 07 and open a PR).
- Recorded successful post-merge GitHub Actions on the PR #17 merge SHA: **CoachOS CI Quality Gates** run [`31940418392`](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31940418392) and **Security & Vulnerability Scan** run [`31940418535`](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31940418535), both completed with conclusion `success` on `0949abeead5ba74a3deb0d2439a464ab6bbd99dd`.
- Kept deferred items deferred: durable offline sync and conflict resolution (Phase 12), messaging/notifications (Phase 08), nutrition (Phase 09), billing/payments (Phase 10), AI (Phase 11), wearables, native apps, marketplace, production media storage/signing/transcoding, formal accessibility certification, device-matrix validation, and penetration testing.
- Recorded Phase 08 as the next product phase; it has **not started** and requires explicit founder authorization in a new dedicated branch. No Phase 08 code, workflow files, application source, tests, or dependencies were modified; historical records below are unchanged.

### Added — Phase 07 Athlete App and Progress Logging

- Added the athlete execution domain (`apps.execution`) with `WorkoutSession`, `SetLog`, `Substitution`, `FeedbackFlag`, `BodyMetric`, `ProgressPhoto`, and `ConsentRecord` models plus migration `0001_initial.py` and audit action migration `0003_alter_auditevent_action.py`. Session status lifecycle, mandatory skip/substitute reason, set-index uniqueness/idempotency, load/reps/RPE/fatigue bounds, ownership, and tenant constraints enforced at the model and API layers.
- Added authorized **Today** dashboard reads (`GET /api/v1/athlete/today`) from immutable program-assignment snapshots, idempotent/race-safe session start (`POST /workout-sessions`) gated on the athlete's own active assignment and active membership, session detail/complete (`GET/POST /workout-sessions/{id}`), set actual logging with a kg unit-conversion policy (`POST .../set-logs`), mandatory-reason exercise substitution (`POST .../substitutions`), and subjective non-clinical pain/fatigue feedback flags (`POST .../feedback-flags`).
- Added consent-gated progress photos (`GET/POST /athletes/{id}/progress/photos`) and body metrics (`GET/POST /athletes/{id}/body-metrics`) with a mock storage adapter (no production bucket/credentials), no public storage key in normal responses, signed URLs only under active consent, revocation blocking reads and URL generation, and sensitive-view/consent-change audit events. Added athlete-controlled consent grant/revoke (`GET/POST/DELETE /consents`).
- Enforced server-authoritative authorization and tenant isolation: athlete self, assigned coach (read + consent-gated sensitive media), owner (consent-gated + audited escalation), support and unassigned/cross-tenant users denied with safe 403/404; suspended memberships denied; completed sessions immutable; substitution reason mandatory; no health/media raw details in logs/errors.
- Added the athlete mobile-first PWA frontend: rewritten Today dashboard (loading/empty/error/forbidden/offline states), workout execution view (one-handed `SetLogger` with keyboard alternative and localized units/kg conversion, `RestTimer`, `SubstitutionModal`, `FeedbackFlagForm`, completion with session RPE/fatigue/notes), and `ProgressManager` (consent-gated metrics + photo upload/consent). Added a typed athlete API client and a temporary in-memory offline boundary (`useNetworkStatus` + `OfflineBanner`) with no durable queue.
- Bilingual `fa-IR` RTL / `en-US` LTR parity (202 dictionary keys each), no Arabic locale/resources, 44px+ touch targets, focus/keyboard/screen-reader/live-region semantics.
- Tests: 34 backend execution tests (authorization matrix, consent/media boundary, adversarial cases, bounded-query performance) and 14 new frontend component/integration tests (75 total); backend lint/format, frontend lint/type-check/build, OpenAPI 3.1 validation (88 local refs), and security/language compliance all pass.
- Marked the 9 Phase 07 OpenAPI operations `implemented-phase-07` and reconciled schemas; Django routes match the OpenAPI paths. Updated `PROJECT_STATUS.md`, `PROJECT_CHECKLIST.md`, `CHANGELOG.md`, `docs/PROMPT_LOG.md`, and created `docs/reports/PHASE-07-ATHLETE-APP-PROGRESS-REPORT.md`.
- Deferred (not implemented): durable offline sync and conflict resolution (Phase 12), messaging/notifications (Phase 08), nutrition (Phase 09), billing/payments (Phase 10), AI (Phase 11), wearables, native apps, marketplace, and production media storage/signing/transcoding. No Phase 08+ implementation or Arabic resources were added.

### Changed — Post-Merge Phase 06 Status Synchronization (docs-only, no code/test/dependency/workflow changes)

- Recorded that PR [#13](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/13) and docs-only PR [#14](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/14) are merged, and that Phase 06 PR [#15](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/15) merged into `main` at `9e09c4785283ffd688e355cb9c1cf7af39c83d3c` on 2026-08-15T13:47:52Z.
- Marked Phase 06 — Exercise Library and Training Programs merged and complete for its documented scope. Recorded final validation evidence: OpenAPI 3.1 with all 191 local references resolved, 72 backend tests, 59 frontend tests plus lint/type-check/production build, and successful clean-checkout/candidate Actions evidence.
- Recorded successful post-merge GitHub Actions on the PR #15 merge SHA: **CoachOS CI Quality Gates** run [`31888177718`](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31888177718) and **Security & Vulnerability Scan** run [`31888175915`](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31888175915), both completed with conclusion `success` on `9e09c4785283ffd688e355cb9c1cf7af39c83d3c`.
- Kept formal accessibility certification, device-matrix validation, penetration testing, production media storage/upload/signing/transcoding, production `pg_trgm` load tuning, broader assignment lifecycle/UI, and all Phase 07+ domains deferred.
- Recorded Phase 07 as the next product phase while keeping it not started and gated on explicit founder authorization in a new dedicated branch.

### Added — Phase 06 Exercise Library and Training Programs

- Added bilingual canonical/organization-private exercise definitions, translations, aliases, Persian keyboard-variant-normalized search, catalog filters, media metadata, mandatory rights provenance, and platform-admin moderation API.
- Added organization-scoped hierarchical programs and set prescriptions, atomic nested persistence, version increments, deep template clone, minimal coach-athlete assignment authorization, and immutable point-in-time assignment snapshots.
- Added active-role and tenant-isolation enforcement with cross-tenant, athlete, suspended, unassigned-coach, media-rights, moderation, snapshot-integrity, and bounded-query tests.
- Replaced the Phase 04 coach program placeholder with a bilingual responsive coach/owner catalog and program-builder workspace, typed API adapter, dictionary parity, normalized search, keyboard reorder alternatives, and component tests.
- Added Phase 06 Stage 0 plan and implementation report. Domain validation recorded separately from frontend baseline validation.
- **Review correction:** removed the unapproved Next.js/ESLint/Vitest/Vite/TypeScript/jsdom migration and lockfile rewrite. Restored the Phase 05 frontend package manifest, lockfile, `.eslintrc.json`, `next lint`, TypeScript config, generated `next-env.d.ts`, and locale layout typing exactly; removed the ESLint 9 flat config and all rule overrides. Phase 06 frontend code passes the unchanged baseline lint/type/test/build commands, including a fresh isolated clone. Corrected-head Actions runs `31879015578`, `31879015703`, and `31879013603` pass. Any toolchain migration requires a separate proposal and PR.
- **Final review correction:** reconciled `docs/OPENAPI.yaml` to 13 implemented Phase 06 operations with current cookie-session/CSRF, tenant, media-rights, hierarchy, and snapshot schemas; OpenAPI 3.1 validates and 191 local refs resolve. Phase 07+ paths are explicitly marked planned.
- Replaced the three-item hardcoded frontend catalog/local-only save with actual session organization loading, `listExercises`, and `createProgram`; added loading, empty, error, unauthorized, retry, save-success, and save-failure tests.
- Hardened program-assignment effective multi-role handling and added cross-tenant private exercise/detail/org_id and owner-role precedence tests. Fresh isolated validation passes: backend 72, frontend 59/build, OpenAPI 3.1 with 191 refs, compliance, and clean status. Final Actions runs `31880019393`, `31880019224`, and `31880015763` pass.
- Published PR [#15](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/15) targeting `main`; pull-request runs `31790374656` and `31790374657` and push run `31790363694` succeeded on published head `a2d8b0a4…`. After final review corrections, PR #15 subsequently merged at `9e09c4785283ffd688e355cb9c1cf7af39c83d3c`; see the post-merge status entry above.
- Phase 06 is merged and complete for its documented scope. No Arabic localization or Phase 07+ code was added; Phase 07 remains not started pending explicit founder authorization.

### Changed — Post-Merge Phase 05 Status Synchronization (docs-only, no code/test/dependency/workflow changes)

- Recorded that Phase 05 PR #13 (`feat(phase-05): Identity, Tenancy, and Roles foundation`, head `arena/019fff0b-coachos-fitness-coaching-platf`) **merged** into `main` at merge commit `d7f72b3fcfd6667df524af5adf71328c5de6edba` on 2026-08-14T08:40:58Z.
- Recorded that all four post-merge GitHub Actions checks on the merge commit are successful: **Backend Lint, Type & Tests (Django/DRF)**, **Frontend Lint, Type & Tests (Next.js/PWA)**, **Security Scan & Language Compliance**, and **Secret & Pattern Scanning** (workflow runs CoachOS CI Quality Gates `31784911766` `success`, Security & Vulnerability Scan `31784911764` `success`). GitHub Actions remain active and passing on `main`.
- Marked Phase 05 — Identity, Tenancy, and Roles **merged and complete for its documented scope** in `PROJECT_STATUS.md` and `PROJECT_CHECKLIST.md`, replacing stale pre-merge wording (PR #13 open / awaiting review; implementation awaiting review).
- Recorded that deferred Phase 05 items remain deferred: frontend onboarding UI, `CoachAthleteAssignment`, ownership transfer, full effective-permissions/active-org context, production email delivery, MFA, and compliance certification.
- Recorded that Phase 06 (Exercise Library and Training Programs) is the next product phase; it has **not started** and requires explicit founder authorization in a new dedicated branch. No Phase 06 code, workflow files, application source, tests, or dependencies were modified; historical records below are unchanged.

### Added — Phase 05 Identity, Tenancy & Roles Foundation

- Custom Django `User` model (UUIDv7 PK via existing generator, normalized unique indexed email, Argon2id-capable hashing, `display_name`, optional phone, `preferred_locale` (fa-IR/en-US), `preferred_unit` (kg/lbs), timezone, `is_platform_admin`, `is_active`).
- Email/password registration, login, logout, current-user (`/me`) with PATCH profile.
- Password reset foundation: request (non-enumerating 202), cryptographically secure 48-byte single-use token (SHA-256 hashed storage only), 15-minute expiry, confirm endpoint, post-reset session invalidation.
- Organization + single primary Location creation in one atomic transaction with exactly one matching owner `Membership`.
- Membership model supporting multi-role (`owner`/`coach`/`athlete`/`support`), status lifecycle (`invited`/`active`/`suspended`/`archived`).
- Secure invitation system (owner any role; coach → athlete only), hashed tokens, 7-day expiry, single-use, role-limited acceptance.
- Immutable `AuditEvent` foundation covering all required P0 events with redaction and immutability enforcement.
- Server-side RBAC + tenant isolation (`IsAuthenticatedAndActive`, membership checks); no client-side trust.
- Comprehensive negative authorization tests (cross-tenant 403/404, suspended access denial, coach/athlete invitation limits, replay/expiry/wrong-email, owner invariant).
- Bilingual foundation (fa-IR RTL / en-US LTR) via existing i18n; new auth/onboarding route scaffolds.
- API surfaces exactly matching documented `/api/v1/auth/*` and `/api/v1/organizations/*` contracts (cookie-session MVP, no tokens in body).
- All Phase 05 artifacts: `PROJECT_STATUS.md`, `PROJECT_CHECKLIST.md`, `CHANGELOG.md`, `docs/PROMPT_LOG.md`, full `PHASE-05-IDENTITY-TENANCY-ROLES-REPORT.md`.
- Preflight gate fully satisfied (PR #10 + #12 merged, workflows on remote main, successful post-merge GitHub Actions runs).

**Branch:** `arena/019fff0b-coachos-fitness-coaching-platf` (session) + proposed `phase/05-identity-tenancy-roles`. PR #13 opened targeting `main` (not auto-merged at delivery time; subsequently merged at `d7f72b3fcfd6667df524af5adf71328c5de6edba` on 2026-08-14T08:40:58Z — see post-merge status synchronization entry above). No Phase 06+ code or Arabic resources added.

### Changed — Post-Merge CI Activation Status Synchronization (docs-only, no code/test/dependency/workflow changes)

- Recorded that CI activation PR #10 (`chore/activate-github-actions-manual`) **merged** into `main` at merge commit `0855867cc85f56bb4b77c5f708db8e122ded6b81` on 2026-08-14T06:36:42Z.
- Recorded that both canonical workflow files — `.github/workflows/ci.yml` and `.github/workflows/security-scan.yml` — are present on remote `main` and GitHub Actions workflows are active.
- Recorded both successful post-merge workflow runs on the merge commit: **CoachOS CI Quality Gates** run ID `31776895893` (conclusion `success`) and **Security & Vulnerability Scan** run ID `31776896050` (conclusion `success`).
- Marked Phase 04 foundation and CI activation complete in `PROJECT_STATUS.md` and `PROJECT_CHECKLIST.md`; PR #8 and PR #9 remain merged as previously recorded.
- Phase 05 remains unstarted and awaits explicit founder authorization; no Phase 05 implementation has been added. No workflow files, application source, tests, or dependencies were modified.

### Fixed — Phase 04 Post-Merge Frontend Reimplementation

- Recorded that the nine `frontend/lib/` files documented by Phase 04 were absent from merged `main`, authoritative original source was unrecoverable, and the founder authorized a specification-based reimplementation. This is not described as restoration or original-source recovery.
- Reimplemented exactly the missing public-environment, locale metadata/dictionaries, formatter, Persian normalizer, BiDi, API client, and service-worker registration files from tracked Phase 00–04 specifications, tests, UX copy, and call sites.
- Retained the root Python-oriented `lib/` ignore rule while adding only `/frontend/lib/` and `/frontend/lib/**` exceptions.
- Added focused API client and service-worker tests and expanded public-config, UTC/date-boundary, normalization, locale-metadata, and exhaustive 54-key bilingual dictionary-governance coverage.
- Clean-validated implementation commit `8c268db973530157fb1468bc1838f8bca59f7310`: frontend lint/type-check/49 tests/build (18 pages), backend Ruff/37 tests, compliance and scope scans, whitespace/ignore checks, and exact nine-file tracked-source audit all passed.
- Added `docs/reports/POST-MERGE-PHASE-04-FRONTEND-REIMPLEMENTATION-REPORT.md` without rewriting the original Phase 04 report.
- Kept GitHub Actions activation and Phase 05 out of scope; both require later separate authorization/review.

### Changed — Phase 04 Post-Merge Status Synchronization (docs-only, no code/test/dependency/workflow changes)

- Recorded that PR #9 (docs synchronization, `arena/019ff171-coachos-fitness-coaching-platf`) merged into `main` on 2026-08-12T15:31:09Z at merge commit `0eae53b89343ec0a4eb1200086b769011012c406`, correcting tracking-document wording.
- Recorded that PR #10 (`chore/activate-github-actions-manual`, open, unmerged, head `871c4f21c7f8e78dfef555916ffb5b939625af9e`) contains exactly `.github/workflows/ci.yml` and `.github/workflows/security-scan.yml`, matching validated `infra/ci/` definitions; no deployment job or real secret exists; CI remains pending merge and remote GitHub check results.
- Updated `PROJECT_STATUS.md`, `PROJECT_CHECKLIST.md`, `CHANGELOG.md`, and `docs/PROMPT_LOG.md` to reflect PR #9 merged, PR #10 open/unmerged, `.github/workflows/` files present on PR branch but absent from `main`, CI inactive, and Phase 05 unstarted and unauthorized.

## [0.4.0] — 2026-08-11 — Phase 04 Project Foundation and PWA Baseline

### Added

- **Monorepo Architecture & Scaffolding:**
  - `frontend/`: Next.js 14.2 App Router, TypeScript strict mode, Tailwind CSS with logical properties, Vitest test suite.
  - `backend/`: Django 5.2 + Django REST Framework 3.18, Python 3.12 target, modular environment settings (`base`, `dev`, `staging`, `prod`, `test`), Pytest suite.
  - `infra/`: Multi-container Docker Compose definitions (`compose.yaml`, `docker-compose.yml`), container definitions (`infra/docker/frontend.Dockerfile`, `backend.Dockerfile`, `redis.conf`), development automation scripts (`infra/scripts/dev.sh`, `check-secrets.sh`, `wait-for-services.sh`).
  - Local CI quality-gate definitions under `infra/ci/` (`ci.yml`, `security-scan.yml`) cover linting, type-checking, backend Pytest, frontend Vitest, Next.js build, PWA manifest, secret scanning, and strict Arabic exclusion; GitHub Actions activation remains pending a separate PR and Workflows permission.
- **PWA Baseline (Level 1 Foundation — ADR-011, ADR-046):**
  - Web App Manifest (`manifest.json` and `manifest.webmanifest`) with standalone display, dark obsidian background `#0B0F17`, and original 192px/512px standard and maskable PNG icons.
  - Service Worker (`sw.js`) implementing Cache-First caching for static assets, Network-First navigation with fallback, and offline shell caching.
  - Dedicated bilingual Offline Fallback Page (`/offline`) with auto-reconnection listeners and retry CTA.
  - `NetworkStatusBanner` component detecting connectivity and warning users that offline data is retained temporarily in memory.
  - `InstallPromptBanner` component providing Android `beforeinstallprompt` handling and iOS Safari "Add to Home Screen" instructions.
- **Bilingual RTL/LTR Foundation (ADR-003, ADR-047):**
  - Dynamic `lang` and `dir` injection on HTML document root (`fa-IR` -> `rtl`, `en-US` -> `ltr`).
  - Strict CSS logical properties for layout directionality.
  - Reusable `PersianNormalizer` utility in both frontend (`lib/i18n/normalizer.ts`) and backend (`apps/core/utils/persian_normalizer.py`) folding Perso-Arabic keyboard variants (`ي`/`ى` -> `ی`, `ك` -> `ک`, Arabic-Indic digits, and ZWNJ handling).
  - BiDi text isolation utility (`<bdi>` / unicode isolates) preventing punctuation flipping in mixed Persian/Latin text.
  - Complete translation dictionaries (`fa-IR.json` and `en-US.json`) with 100% key parity and zero Arabic resources.
  - Solar Hijri (Jalali) date conversion algorithm separate from UTC/Gregorian timestamp storage (ADR-009).
- **Backend Foundation & Security Baseline (ADR-048):**
  - Safe health endpoints: `GET /healthz` (200 OK liveness), `GET /readyz` (PostgreSQL + Redis readiness check), `GET /api/v1/meta` (public system metadata).
  - RFC 7807 Problem Details custom exception handler with localized `message_key` and field error breakdown.
  - Middleware stack: `CorrelationIDMiddleware` (generating/propagating `X-Request-ID` UUIDv7), `SecurityHeadersMiddleware` (HSTS, CSP, X-Frame-Options DENY, X-Content-Type-Options nosniff), `LoggingRedactionMiddleware` (scrubbing sensitive passwords, tokens, auth headers), and `TenantContextMiddleware` interface.
  - Time-ordered UUIDv7 identifier generator (`id_generator.py`) with validation and tests.
  - HttpOnly session cookie authentication configuration with CSRF double-submit token headers.
  - Strict frontend secret boundary (`NEXT_PUBLIC_*` public config only; runtime error on private key detection).
- **Architecture Specifications:**
  - `docs/architecture/HOSTING_AND_DATA_RESIDENCY_DECISION.md`: Comprehensive 10-dimension evaluation of PaaS, EU Cloud, Bare VPS, Dual-Region Active-Passive (Iran Edge Proxy + EU Core), and Dual-Region Active-Active.
  - `docs/architecture/PHASE04_FOUNDATION_DECISIONS.md`: Monorepo architecture, boundaries, and ADR summaries.
  - `docs/architecture/LOCAL_DEVELOPMENT.md`: Step-by-step local developer guide for Docker and native runtimes.
  - `docs/architecture/CI_CD_FOUNDATION.md`: GitHub Actions workflow specification and CI quality gates.
  - `docs/architecture/PWA_FOUNDATION.md`: PWA Level 1 specification, manifest, service worker, and browser limitations.
  - `docs/architecture/SECURITY_FOUNDATION.md`: Security headers, session transport, log scrubbing, and error sanitization.
  - `docs/reports/PHASE-04-FOUNDATION-REPORT.md`: Comprehensive 25-section completion report.
- **Architecture Decision Records (`docs/DECISIONS.md`):**
  - ADR-010: Monorepo Folder Layout & Package Boundaries (Accepted).
  - ADR-012: Repository License & Intellectual Property Strategy (Accepted — Proprietary / All Rights Reserved).
  - ADR-044: Monorepo Structure & Local Workspace Scaffolding (Accepted).
  - ADR-045: Frontend Foundation Architecture & Public Runtime Configuration Boundary (Accepted).
  - ADR-046: PWA Baseline Architecture, App-Shell Caching, and Offline Fallback Strategy (Accepted).
  - ADR-047: Bilingual RTL/LTR Execution & Persian Search Normalization Architecture (Accepted).
  - ADR-048: Backend Foundation, Error Sanitization Envelope, Middleware Pipeline, and Health Endpoints (Accepted).
  - ADR-049: Hosting and Dual-Region Deployment Strategy (Accepted — Decision Gate Defined).

### Changed

- Transitioned repository `LICENSE` from MIT to **Proprietary / All Rights Reserved** (Copyright (c) 2026 CoachOS Technologies / Ali Naderi) pursuant to founder intellectual property mandate (ADR-012).
- Applied security & configuration review corrections:
  - Fail-closed secret configuration for production/staging (mandatory `DJANGO_SECRET_KEY` and `DATABASE_URL`, strict `ALLOWED_HOSTS`).
  - Secure default DRF permissions (`IsAuthenticated` global default; `/healthz`, `/readyz`, `/api/v1/meta` explicit `AllowAny`).
  - Validated `CorrelationIDMiddleware` preventing malformed or log-injection request IDs.
  - Tenant context safety enforcing session-only active organization derivation (`ALLOW_TENANT_HEADER_OVERRIDE=False`).
  - Frontend security headers and CSP delivery on HTML responses via `next.config.mjs`.
  - Normalized static-page build count to 18 pages.
- Updated `README.md` with runnable local development commands, architecture structure, and updated project status.
- Updated `PROJECT_STATUS.md` and `PROJECT_CHECKLIST.md` marking Phase 04 complete.

---

## [0.3.0] — 2026-08-11 — Phase 03 Architecture, Data, Security, Privacy

### Added

- **Phase 03 Architecture, Data, Security, Privacy Package (13 architecture docs + 6 top-level architecture specs + 1 report):**
  - `docs/architecture/SYSTEM_CONTEXT.md`: C4 Level1 system context P0/P1/P2, external services email/push/payment/AI/wearable future dashed, trust boundaries, sensitive-data boundaries Tier0-6, Mermaid C4Context + fallback flowchart.
  - `docs/architecture/CONTAINER_ARCHITECTURE.md`: C4 Level2 containers Next.js frontend + Django modular monolith backend + PostgreSQL 16 proposed + Redis7 Celery + private S3 + email abstraction + future dashed, deployment topology logical PaaS vs K8s, failure modes, NFR targets proposed.
  - `docs/architecture/COMPONENT_BOUNDARIES.md`: Frontend Next.js app structure mapping 34 screens + backend Django 20 modules + middleware stack RequestID/SecurityHeaders/OrgScope/AuthZ/Audit + import-linter dependency rules + sequence diagram assignment.
  - `docs/architecture/DATA_FLOW.md`: Data flows auth/invite, exercise search Persian normalization pg_trgm, assignment snapshot JSONB immutable, workout logging offline boundary Phase04/07/12, progress photo consent + signed URL gated, messaging, privacy export/erasure.
  - `docs/architecture/DEPLOYMENT_ARCHITECTURE.md`: PaaS vs K8s options, env local/staging/prod distinct VPC/DB/buckets/secrets, Docker + GitHub Actions CI/CD lint/type/unit/integration/security scan Playwright E2E staging auto prod manual gate, TLS HSTS CSP, secrets manager, backup hooks, RPO/RTO proposed.
  - `docs/architecture/ERD.md`: erDiagram 30+ entities + detailed entity specs PK/FK tenant ownership sensitive fields indexes unique constraints state machines soft-delete archive audit retention localization, identifier UUIDv7 proposed not authz substitute, conceptual DDL illustrative.
  - `docs/architecture/DOMAIN_MODULES.md`: 20 modules M01-M20 (Identity, Org, Membership, AuthZ/Consent, Exercise Catalog, Media/Rights, Programs, Templates, Assignments/Snapshots, Sessions, Progress/Feedback, Messaging, Notifications, Admin/Moderation, Audit, Privacy Export/Erasure, Future Nutrition P1, Future Billing Phase10, Future Marketplace P2, Future AI Phase11) with responsibility owned entities public interfaces read/write deps security boundary events emitted/consumed sensitivity test boundary extraction risk.
  - `docs/architecture/AUTHORIZATION_ARCHITECTURE.md`: RBAC P0 roles platform_admin/owner/coach/athlete/support + future nutritionist P1 consent-gated + progress-photo consent explicit affirmative modal + break-glass admin MFA+reason+audit + owner aggregate vs raw distinction + invitation permissions + detailed matrix per sensitive resource create/read/update/archive/export/share/revoke/consent/audited + negative controls cross-tenant unassigned suspended photo message audit export.
  - `docs/architecture/PWA_ARCHITECTURE.md`: Three-level PWA Phase04 manifest/icons/standalone/SW app-shell caching/offline fallback/install guidance, Phase07 touch-optimized 44/48px form-state temp memory network indicator retry no durable queue, Phase12 IndexedDB durable queue sync status retry/backoff conflict background sync push limitations HealthKit eval native bridge decision + browser limitations table.
  - `docs/architecture/MEDIA_STORAGE.md`: Tier0/2/4 classification buckets private no listing BlockPublicAcls true versioning SSE-S3 signed URL TTL≤15min no caching Tier4 SW MIME whitelist size limits thumbnail strategy Pillow ffmpeg malware scan ClamAV proposed quarantine rights metadata mandatory takedown workflow photo access control + future transcoding CDN rules.
  - `docs/architecture/OBSERVABILITY.md`: Structured logging JSON structlog redaction request_id correlation audit vs debug separation ELK 30d vs audit PG 1y+, metrics Prometheus counters/histograms, Sentry error tracking, healthz/readyz checks, alerting categories auth anomaly cross-tenant 403 spike 5xx>1% latency etc.
  - `docs/architecture/BACKUP_AND_DISASTER_RECOVERY.md`: PG daily snapshot 30d + WAL PITR 15min RPO proposed 1h RTO, S3 versioning noncurrent expire 30d exports-tmp 7d lifecycle, Redis loss acceptable, restore runbooks DB/S3 weekly automated restore testing smoke tests, RTO full platform 2-4h, incident response, breach response 72h if GDPR legal required, rollback app previous image + migration reverse 2-step.
  - `docs/architecture/README.md`: Architecture docs index + tech decisions summary + verification no code + rendering notes.
  - `docs/OPENAPI.yaml`: OpenAPI 3.1 provisional /api/v1 covering auth, current user, orgs, locations, memberships, invitations, exercise catalog, moderation, programs, templates, assignments, today, sessions, set logs, substitutions, feedback flags, progress photos/metrics, consents, messages, notifications, audit, privacy export/deletion, media signed URLs — each with method/path/purpose/auth/required role/object permission/request/response schema/error responses/localization/idempotency/audit/rate-limit/sensitivity + RFC7807 error + message_key.
  - `docs/JSON_SCHEMAS.md`: JSON Schema draft 2020-12 snapshot immutable, queue entry offline Phase12, export manifest profile.json workouts.json, notification payload, consent, Persian normalizer pseudocode Perso-Arabic script keyboard-variant normalization.
  - `docs/THREAT_MODEL.md`: STRIDE 21 threats T01-T21 account takeover credential stuffing session theft invitation abuse cross-tenant IDOR unassigned coach owner overreach photo exposure malicious uploads stored XSS CSRF SSRF webhook forgery future Phase10 notification abuse export abuse erasure abuse insider/admin misuse prompt injection future Phase11 supply-chain backup leakage enumeration + OWASP Top10 mapping + controls.
  - `docs/PRIVACY_DATA_LIFECYCLE.md`: 11 lifecycle stages collection/consent/storage/use/sharing/export/retention/revocation/deletion/anonymization/backup destruction, Tier0-8 classification per class purpose/legal assumption/owner/controller/access/encryption/logging retention/export/deletion/consent, consent lifecycle photo + nutrition P1, export ZIP via Celery tmp S3 24h link, erasure pipeline anonymization + S3 delete, retention questions, pre-DPIA checklist large-scale sensitive systematic monitoring profiling multi-prof sharing progress-photo wearable AI.
  - `docs/SECURITY_CONTROL_MATRIX.md`: Threat→Requirement→Architecture Control→Phase→Test Type→Evidence→Status including negative controls cross-tenant reads/writes unassigned coach suspended membership unauthorized photo/message/audit/export.
  - `docs/ARCHITECTURE_VALIDATION_CHECKLIST.md` + `docs/architecture/ARCHITECTURE_VALIDATION_CHECKLIST.md`: V01-V22 validation checklist P0 domains owning modules, sensitive entities access rules, API groups boundaries, stories→domains/APIs, UX routes→frontend boundaries, cross-tenant auth strategy, media types rights, export/deletion paths, PWA sequencing consistency, no Arabic, no AI/payment/wearable P0, open legal/license visible, no secrets/health data, screen 34 UX doc 14 story 27 offline boundary touch 44/48 Jalali/Gregorian modal focus dark-theme Persian terminology.
  - `docs/reports/PHASE-03-ARCHITECTURE-REPORT.md`: 31-section Phase 03 comprehensive report (this phase) with executive summary EN/FA, preflight review, corrections, objectives, system context, container, domain modules, tech decisions, data model/ERD, authorization, API/OpenAPI, threat model, security control matrix, privacy lifecycle, media storage, PWA, observability, backup/DR, ADRs, validation checklist, files changed, GitHub branch/commit/PR, tests/validation, security/privacy risks, assumptions, open questions, founder approval items, deferred items, checklist changes, next prompt Phase04.
- **Phase 02 UX, Information Architecture, and Design System Package (merged PR #5 771afa6):**
  - `docs/ux/INFORMATION_ARCHITECTURE.md`: Role-based information architecture, routing hierarchy, and site map covering athlete, coach, owner, and admin workspaces.
  - `docs/ux/NAVIGATION_MODEL.md`: Multi-device navigation paradigms (mobile bottom navigation, active workout canvas, desktop collapsible sidebar, breadcrumbs, dual-pane builder).
  - `docs/ux/SCREEN_INVENTORY.md`: Comprehensive inventory and technical specifications for 34 P0 screens.
  - `docs/ux/USER_FLOWS.md`: Step-by-step user flows with Mermaid sequence and flowchart diagrams for owner onboarding, coach programming, athlete workout execution, and admin moderation.
  - `docs/ux/WIREFRAMES.md`: Detailed bidirectional ASCII wireframes for core athlete and coach screens in both English LTR and Persian RTL (mirrored).
  - `docs/ux/DESIGN_SYSTEM.md`: Core design principles, component library specifications (buttons, inputs, datepickers, program tree nodes, consent dialogs, rest timers).
  - `docs/ux/DESIGN_TOKENS.md`: Visual tokens (colors, dark obsidian canvas, typography, 4px spacing scale, elevation, z-index, motion) with WCAG 2.2 AA contrast validation tables.
  - `docs/ux/RTL_LTR_SPECIFICATION.md`: CSS logical properties, bidirectional mirroring rules, mixed-direction BiDi isolation (`<bdi>`), and Persian character normalization.
  - `docs/ux/RESPONSIVE_BEHAVIOR.md`: 6-tier breakpoint taxonomy, one-handed mobile gym floor ergonomics, natural thumb zone analysis, and component reflows.
  - `docs/ux/ACCESSIBILITY_SPEC.md`: WCAG 2.2 Level AA compliance specifications, modal focus trapping, ARIA live announcements, and 10-point test checklist.
  - `docs/ux/STATE_AND_ERROR_MATRIX.md`: 8-state handling matrix and progressive offline PWA matrix across Phase 04/07/12.
  - `docs/ux/UX_COPY.md`: Non-clinical bilingual microcopy dictionary and content guidelines in English and Persian.
  - `docs/ux/UX_TRACEABILITY_MATRIX.md`: 1:1 mapping from all 27 P0 user stories (25 core + 2 I18N variants) to UX specifications.
  - `docs/ux/UX_RESEARCH_AND_ASSUMPTIONS.md`: Hypothesis categorization, research questions by persona, and pilot usability protocol.
  - `docs/reports/PHASE-02-UX-DESIGN-REPORT.md`: Comprehensive 31-section Phase 02 completion report with English and Persian executive summaries.
- **UX Architecture Decision Records (`docs/DECISIONS.md`):**
  - ADR-023: Athlete mobile navigation & full-screen active workout canvas pattern.
  - ADR-024: Coach program builder desktop dual-pane master-detail pattern.
  - ADR-025: Persian typography strategy using Vazirmatn variable web font.
  - ADR-026: Non-clinical UX language standard for subjective feedback.
  - ADR-027: Explicit affirmative consent interaction model for sensitive photos.
  - ADR-028: Dark-neutral visual theme for mobile gym-floor glare reduction.

### Changed — Phase 03 Architecture Review Corrections (PR #6 Review — Correction-Only) — First Correction Batch (b6ea570)

- **Critical secret-manager boundary correction (Task 1):** Removed forbidden `FE --> SecretMgr` relationship from `DEPLOYMENT_ARCHITECTURE.md` topology, updated diagrams to show only `BE --> SecretMgr` and `Worker --> SecretMgr` plus `FE -->|Public runtime config only NEXT_PUBLIC_* vars NO private secrets| BE` (intermediate misleading arrow). Updated `CONTAINER_ARCHITECTURE.md` 3.1 Frontend and 3.2 Backend to explicitly forbid frontend accessing Secrets Manager, private secrets only backend/worker via server-side injection, frontend only public `NEXT_PUBLIC_*` runtime config, no private secrets in bundle/render/proxy, bundle secret scan CI. Updated `SYSTEM_CONTEXT.md` Trust Boundaries and `COMPONENT_BOUNDARIES.md` Security Boundaries with corrected secrets boundary. Updated `THREAT_MODEL.md` T02 and `SECURITY_CONTROL_MATRIX.md` T02 for secret boundary + bundle secret scan.

- **CSP correction (Task 2):** Replaced placeholder `script-src 'self' 'unsafe-inline' ?` with clear proposed strategy production preferred nonce- or hash-based `script-src 'self' 'nonce-{random}' 'strict-dynamic' https:` — no `unsafe-inline` as accepted production control. Documented temporary exception if Next.js requires `unsafe-inline` during Phase04 foundation: explicitly marked temporary, documented risk XSS inline injection bypasses CSP, defined hardening task TODO-CSP-001 migrate to nonce before pilot, not presented as accepted production control, do not claim CSP finalized before implementation validation. Updated `DEPLOYMENT_ARCHITECTURE.md` §7, `CONTAINER_ARCHITECTURE.md`, `THREAT_MODEL.md` T02/T09, `SECURITY_CONTROL_MATRIX.md` T02/T09.

- **Authentication transport consistency (Task 3):** Reconciled cookie vs Bearer token docs: defined recommended MVP HttpOnly/Secure/SameSite cookie sessions (HttpOnly true Secure true SameSite Lax, no long-lived tokens in localStorage explicit prohibition, CSRF double-submit/Django middleware X-CSRFToken header) and optional alternative Bearer/JWT short-lived ≤15min in memory + rotating refresh HttpOnly cookie reuse detection explicit prohibition localStorage, frontend/backend trust boundary browser untrusted backend authoritative. Final choice recommended first implementation cookie sessions (simpler), JWT alternative optional proposed/conditional requiring Phase04 validation. Updated `CONTAINER_ARCHITECTURE.md`, `COMPONENT_BOUNDARIES.md`, `SYSTEM_CONTEXT.md`, `DECISIONS.md` ADR-005 and ADR-032, `OPENAPI.yaml` info description + x-auth-strategy + securitySchemes descriptions + top-level security order cookieAuth first, version bumped 1.0.0-provisional → 1.0.1-provisional-corrected, remains provisional until Phase04.

- **Data-model integrity corrections (Task 4):**
  - 4.1 Organization owner source of truth: Chosen invariant `Organization.owner_user_id` authoritative for single owner MVP, exactly one active Membership role=owner per org must exist and user_id must equal owner_user_id, Membership owner row derived automatically managed not independently mutable, creation transaction creates both, transfer via `OrganizationService.transferOwnership()` atomic audit, drift prevention via service + periodic check. Updated `ERD.md` Organization, `DATA_MODEL.md` Organization, `DECISIONS.md` ADR-014.
  - 4.2 Membership multi-role: Schema allows multi-role via UNIQUE(user_id, organization_id, role), MVP policy single primary role recommended but multi-role allowed explicitly enabled, effective permissions = union of all active roles (most permissive, priority owner>coach>support>athlete), role elevation audited, active org + active role via session, frontend receives memberships array + effective_permissions computed server-side. Updated `ERD.md` Membership, `DATA_MODEL.md` Membership, `DECISIONS.md` ADR-014.
  - 4.3 Assignment reactivation: Previous permanent UNIQUE prevented recreation after archival, corrected to partial unique for active only `UNIQUE(org, coach, athlete) WHERE status='active'` (or WHERE archived_at IS NULL), allows historical archived rows + recreation, only one active per triple. Added fields archived_at ended_at, workflow archival sets status archived + timestamps audit, reactivation creates new row preserving history (preferred) or reactivates if no active exists, reassignment archives old + creates new, idempotent assign. Updated `ERD.md` CoachAthleteAssignment, `DATA_MODEL.md` CoachAthleteAssignment, `DECISIONS.md` ADR-014.

- **Backup and disaster-recovery wording (Task 5):** Corrected `BACKUP_AND_DISASTER_RECOVERY.md` and `DEPLOYMENT_ARCHITECTURE.md` to not overclaim: S3 versioning ≠ independent backup nor cross-region DR, versioning does not automatically satisfy deletion/erasure requirements (erasure must permanently delete all versions), RPO/RTO proposed targets not guarantees require validation, cross-region replication multi-AZ retention residency require cost/legal approval, Redis not source of truth but important async jobs must have durable DB state or outbox/retry pattern (create DB record first then enqueue, reconciliation job). Updated §1.2, §1.3, §3, §4.

- **API specification validation (Task 6):** Validated `OPENAPI.yaml` via regex checks (yaml module not available per no-install rule): openapi 3.1.0 OK, total $ref 135 local 135 missing schema refs [] (59 defined schemas), security schemes consistent with corrected auth strategy (bearerAuth optional alternative + cookieAuth recommended MVP), error responses RFC7807-compatible with message_key true, P0 endpoint groups align with API_CONTRACT PRD story IDs auth rules (tags Authentication Organizations Locations Memberships etc), no Payment/AI/Wearable as P0 implemented (forbidden tags absent, /webhooks/payments not present), paths count 37. Corrected spec info description + version bumped provisional-corrected, remains provisional until Phase04 implementation validation.

### Changed — Final Phase 03 Review Fixes (PR #6 Final Review — Correction-Only) — Second Correction Batch (Current)

- **Remove misleading public-config frontend-to-backend arrow (Task 1 Final):** Previous correction removed forbidden `FE --> SecretMgr` correctly but introduced misleading `FE -->|Public runtime config only NEXT_PUBLIC_* NO private secrets| BE` — public frontend runtime config is not a secret request from frontend to backend. Corrected diagrams and text so that frontend receives public runtime config from its deployment/build configuration (PublicConfigProvider), backend and worker receive private secrets through server-side secret injection, browser/frontend does not access Secrets Manager, frontend does not send public runtime config to backend as secret-management flow, normal frontend-to-backend relationship remains API request relationship only. Used clear notation: `PublicConfigProvider --> FE`, `BE --> SecretMgr`, `Worker --> SecretMgr`, `FE --> BE : HTTPS /api/v1 requests only`. Applied to `DEPLOYMENT_ARCHITECTURE.md` (topology diagram updated to include Config subgraph with PublicConfigProvider and SecretMgr, correct arrows, removed misleading arrow), `CONTAINER_ARCHITECTURE.md` (fallback generic flow updated with PublicConfigProvider and SecretMgr nodes, correct arrows, Boundaries text corrected to remove misleading arrow and use correct notation), `SYSTEM_CONTEXT.md` (fallback generic flow updated with Config subgraph, PublicConfig --> Web public runtime config only, Web --> API HTTPS /api/v1 only, API --> SecretMgr private secrets only).

- **Make OpenAPI authentication response consistent with recommended cookie-session MVP (Task 2 Final):** `OPENAPI.yaml` correctly recommends `cookieAuth` for MVP and keeps bearer/JWT as optional alternative, but `AuthResponse` previously presented `access_token` and `refresh_token` as ordinary response properties without conditional nature. Corrected so that cookie-session registration/login responses do not imply tokens returned to frontend — MVP uses HttpOnly session cookie and CSRF mechanism, tokens optional/nullable present only when optional bearer strategy selected. Added `csrf_token` optional/nullable present only when cookieAuth MVP, added separate schemas `CookieAuthResponse` (recommended MVP — no tokens in body, HttpOnly cookie via Set-Cookie, CSRF token) and `BearerAuthResponse` (optional alternative — short-lived access ≤15min memory + rotating HttpOnly refresh cookie), explicit prohibition no long-lived token in localStorage/sessionStorage. Updated `AuthResponse` description with corrected auth transport consistency, made access_token/refresh_token optional nullable with descriptions conditional presence only when bearer selected, added csrf_token optional, updated `/auth/register` and `/auth/login` endpoint descriptions to clarify MVP cookie session no tokens in body, optional bearer tokens optional, explicit prohibitions, FE --> SecretMgr forbidden, public config PublicConfigProvider --> FE, private secrets BE/Worker --> SecretMgr, FE --> BE HTTPS /api/v1 only, provisional until Phase04. Kept security, securitySchemes, ADR-032 consistent, remains provisional.

- **Validate after correction (Task 3):** Parse `OPENAPI.yaml` as YAML if parser available (yaml module not available per no-install rule, used manual regex validation), confirmed OpenAPI 3.1 (3.1.0 OK), confirmed all local $ref resolve (total 137 local 137 missing schema refs [] after adding CookieAuthResponse and BearerAuthResponse, 61 defined schemas), confirmed no frontend-to-Secrets-Manager relationship remains in architecture diagrams (grep -Rn FE --> SecretMgr in docs/architecture/ shows only explanatory text about forbidden/removed, not actual diagram arrow; correct notation present PublicConfigProvider --> FE, BE --> SecretMgr, Worker --> SecretMgr, FE --> BE HTTPS /api/v1 requests only), confirmed no application source code, dependencies, migrations, secrets, real health data added via find checks.

- **Update project artifacts (Task 4):** Updated `docs/reports/PHASE-03-ARCHITECTURE-REPORT.md` with Section 36 final review fixes, `PROJECT_STATUS.md` Section 1.3, `PROJECT_CHECKLIST.md` note final review fixes, `CHANGELOG.md` with this entry, `docs/PROMPT_LOG.md` with Prompt 006 final review fixes, `docs/DECISIONS.md` ADR-005/032/014 and auth/API decision clarified.

### Changed — Previous

- Updated `PROJECT_STATUS.md` reflecting Phase 02 completion and post-merge base commit `3921083` (Phase 01) — now superseded by `771afa6` (PR #5 Phase 02 merge) as recorded in Phase 03 preflight.
- Updated `PROJECT_CHECKLIST.md` marking all Phase 02 deliverables complete with evidence links.
- Updated `docs/RELEASE_PLAN.md` marking Milestone M2 complete.
- Phase 03 preflight corrections: normalized screen count to exact 34 screens, normalized UX spec count to 14 documents (+README), corrected story count from 29 to 27 P0 stories, clarified Perso-Arabic script keyboard-variant normalization wording for Persian search (no Arabic product scope), and verified offline durability boundaries (Phase 04 shell-only, Phase 07 temporary in-memory, Phase 12 durable queue).

### Notes

- Documentation and design specifications only; **zero application source code, dependencies, or database migrations added** (by design).
- Strict language constraint: Persian (`fa-IR`) and English (`en-US`) only; Arabic remains strictly out of scope.

## [0.0.2] — 2026-08-10

### Added

- Phase 01 Product Requirements and Scope Package (merged via PR #4, commit `392108372450dc8a40fe79c6201144733955b7c0`).
- 22 Architecture Decision Records (ADR-001 through ADR-022).
- Personas (`docs/PERSONAS.md`), user journeys (`docs/USER_JOURNEYS.md`), domain glossary (`docs/DOMAIN_GLOSSARY.md`), and competitive landscape (`docs/COMPETITIVE_LANDSCAPE.md`).

## [0.0.1] — 2026-08-10

### Added

- Phase 00 discovery documentation suite for greenfield CoachOS repository (merged via PR #3, commit `f52c4134087b18c4bd1a8aef9e0100fd63f71b8e`).
- Explicit product constraint: **Persian (`fa-IR`) and English (`en-US`) only**; **Arabic out of scope**.
- Proposed modular-monolith stack direction (Next.js, Django/DRF, PostgreSQL).

## [0.0.0] — 2026-08-10

### Added

- Initial GitHub repository commit by owner: MIT `LICENSE`, stub `README.md`.
