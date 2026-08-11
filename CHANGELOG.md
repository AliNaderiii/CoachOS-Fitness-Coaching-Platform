# Changelog

All notable changes to this project are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
This project will follow [Semantic Versioning](https://semver.org/) once the first versioned release is cut.

## [Unreleased] — Phase 03 Architecture, Data, Security, Privacy (in progress towards release)

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

### Changed

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
