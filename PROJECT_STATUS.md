# Project Status — CoachOS

**Last updated:** 2026-08-10 (UTC)  
**Current phase:** Phase 03 — Architecture, Data, Security, and Privacy (**complete**)  
**Next phase:** Phase 04 — Project Foundation and PWA Baseline (awaiting explicit instruction)  
**Working branch:** `arena/019fed02-coachos-fitness-coaching-platf`  
**Base commit (main):** `771afa668e71b0b181218be2e4d768e60f4f36f9` (PR #5 merged)  
**Repository:** https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform  
**License:** MIT (Review Pending Founder Decision — see ADR-012)

---

## 1. One-Line Status

Phase 03 architecture complete: C4 system context + container diagrams, 20 domain modules (M01-M20) with boundaries, ERD with 30+ entities + tenant isolation + snapshot immutability + consent revocation, RBAC+ABAC+consent authorization matrix, P0 provisional OpenAPI 3.1 `/api/v1` catalog (25+ groups) with RFC7807 error + message_key, STRIDE threat model 21 threats + OWASP mapping + security control matrix with negative authorization tests, privacy lifecycle Tier0-8 11 stages + pre-DPIA checklist, media storage private buckets no listing signed URLs TTL≤15min MIME whitelist thumbnail rights metadata takedown, PWA three-level strategy Phase04/07/12 with offline durability boundary wording normalized, observability structured JSON logs + redaction + request_id + metrics + Sentry + healthz/readyz + alerting, backup/DR PITR 15min RPO proposed 1h RTO versioned S3 Redis loss acceptable + restore runbooks + incident/breach response + rollback, 43 ADRs (ADR-012 license pending founder approval, ADR-017 UUIDv7 proposed requires validation). **Zero application code, dependencies, migrations created — specification only.** Phase 02 verified 34 screens exact, 14 UX spec docs (+README), 27 P0 stories, no invalid story IDs, Persian terminology precise Perso-Arabic script keyboard-variant normalization for Persian search, no Arabic product scope.

## 1.1 Phase 02 Verification (Post PR #5 Merge) — Preflight Review Details in Phase03 Report §3

- PR #5 merged: `771afa668e71b0b181218be2e4d768e60f4f36f9` — Phase 02 package now in `main`.
- Screen count verified: 34 unique P0 screen IDs in SCREEN_INVENTORY.md — exact count, no 28+.
- UX document count verified: 14 specification documents under `docs/ux/` (+ README = 15 files).
- Story traceability verified: 27 P0 stories (US-AUTH-001..US-PWA-001 including US-I18N-001/002) — no invalid IDs (US-ATH-006 etc corrected in Phase02 report).
- Offline wording verified: Phase04 cached shell only offline fallback; Phase07 temporary in-memory preservation unsaved input retained temporarily retry required after reconnection no durable queue; Phase12 durable IndexedDB queue. Wording normalized per preflight.
- Persian terminology verified: "Perso-Arabic script keyboard-variant normalization for Persian search" / "Persian Unicode character-variant folding" used; no "Arabic Yeh/Kaf variant folding" as product scope — variant examples only to explain keyboard-variant input, no Arabic localization.
- Design-system consistency verified: 44px minimum per WCAG 2.5.5, 48px preferred design target for primary CTAs — requires implementation testing — consistent across DESIGN_SYSTEM, NAVIGATION_MODEL, RESPONSIVE_BEHAVIOR, ACCESSIBILITY_SPEC.
- Color tokens, Persian font Vazirmatn + Inter, breakpoints 6-tier xs-2xl, mobile 5-tab bottom nav Today/Calendar/Progress/Messages/Profile, Jalali/Gregorian UTC storage + Jalali UI display fa-IR, modal focus trapping Escape dismiss, dark-theme proposal not proven glare reduction benefit — design target requires user testing.
- Corrections made before architecture work: CHANGELOG story count 29→27, PROJECT_STATUS branch/base commit updated to 771afa6 and arena/019fed02, PRD scenario title "Search query with Arabic Yeh" → "Search query with Perso-Arabic variant (Yeh) — Perso-Arabic script keyboard-variant normalization for Persian search" with clarification no Arabic product support implied, preflight section added to Phase03 report.
- Working branch for Phase 03: `arena/019fed02-coachos-fitness-coaching-platf` from updated `main`.
- No application code created in preflight.

---

## 2. Post-Merge Repository State & Artifact Verification (Phase03 Complete)

| Area | Post-Merge State | Evidence / Artifact Link |
|------|------------------|--------------------------|
| Main Base Commit | `771afa668e71b0b181218be2e4d768e60f4f36f9` | PR #5 merged into `main` (Phase 02) — Phase 03 branch from updated main |
| Working Branch | `arena/019fed02-coachos-fitness-coaching-platf` | Phase 03 complete, pending review |
| Application Source (Frontend/Backend) | None (by design) | Verified via `find` no backend/frontend dirs, no package.json, no .py/.tsx app source, no migrations — spec only |
| Dependencies / Lockfiles | None (by design) | Verified no package-lock, requirements.txt added |
| Database Migrations | None (by design) | Verified no migrations folder |
| Documentation Suite | Phase 02 complete (34 screens, 14 UX specs, 27 P0 stories) + Phase 03 complete (43 ADRs, SYSTEM_CONTEXT, CONTAINER_ARCHITECTURE, COMPONENT_BOUNDARIES, DATA_FLOW, DEPLOYMENT_ARCHITECTURE, ERD, DOMAIN_MODULES, AUTHORIZATION_ARCHITECTURE, PWA_ARCHITECTURE, MEDIA_STORAGE, OBSERVABILITY, BACKUP_AND_DISASTER_RECOVERY, README, OPENAPI.yaml, JSON_SCHEMAS, THREAT_MODEL, PRIVACY_DATA_LIFECYCLE, SECURITY_CONTROL_MATRIX, ARCHITECTURE_VALIDATION_CHECKLIST, PHASE-03 report) | See section 4 inventory |
| LICENSE | MIT (pre-existing) | ADR-012 pending founder approval — MIT vs Proprietary vs Open-Core vs Private commercial |

---

## 3. Active Non-Negotiable Constraints

1. **Languages:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR) **only**.
2. **Arabic is strictly out of scope:** No Arabic locale files, translations, UI text, or requirements.
3. **No Marketplace, Payments, or Autonomous AI in P0:** Deferred to P1/P2 backlogs (Marketplace P2, Payments Phase10 P1, AI Phase11 P2).
4. **B2B2C SaaS Model:** Organizations/coaches are paying customers; athlete accounts are free/included.
5. **PWA-First Delivery:** Foundation in Phase 04, athlete validation in Phase 07, advanced offline in Phase 12.
6. **Single-Location MVP:** Organizations have a single primary facility in P0; multi-location in P1.
7. **Calendar Strategy:** UTC/Gregorian backend storage with Jalali UI rendering in `fa-IR` locale (ADR-009 accepted conditional).
8. **No Secrets or Real Health Data in Repository:** Synthetic data only, verification via gitleaks proposed in CI.
9. **No Application Code in Phase 03:** Mermaid, OpenAPI YAML, JSON Schema, SQL-like conceptual DDL, threat-model tables allowed as spec artifacts.

---

## 4. Documentation Inventory (Phase 03 Final)

### Product & Requirements (Phase 00–01)
- `README.md`: Project overview and documentation index.
- `PROJECT_STATUS.md`: Active living status (this file) — Phase 03 complete.
- `PROJECT_CHECKLIST.md`: Master phase checklist — Phase 03 [x] complete.
- `CHANGELOG.md`: Keep-a-Changelog — Phase 03 preflight corrections + architecture additions.
- `docs/MASTER_PRODUCT_BRIEF.md`: Core product brief.
- `docs/PRD.md`: Full PRD with P0 stories (27 exact), acceptance criteria, permissions matrix, NFRs, P1/P2 backlogs — preflight correction Persian terminology.
- `docs/PERSONAS.md`: 6 personas.
- `docs/USER_JOURNEYS.md`: 5 journeys.
- `docs/DOMAIN_GLOSSARY.md`: Bilingual domain glossary with Persian normalization definition.
- `docs/COMPETITIVE_LANDSCAPE.md`: Benchmark 10 competitors.
- `docs/DECISIONS.md`: 43 ADRs (ADR-001..ADR-043) — license pending founder approval, UUIDv7 proposed requires validation, backup RTO/RPO proposed requires cost approval.
- `docs/DATA_MODEL.md`: v2.0 Phase03 finalized pointing to ERD authoritative, UUIDv7 proposed, snapshot immutability, consent revocation, private photo storage.
- `docs/API_CONTRACT.md`: v2.0 Phase03 finalized provisional pointing to OPENAPI.yaml, RFC7807 + message_key.
- `docs/SECURITY_AND_PRIVACY.md`: v2.0 Phase03 pointing to threat model, control matrix, privacy lifecycle Tier0-8, pre-DPIA.
- `docs/TRACEABILITY_MATRIX.md`: End-to-end RTM.
- `docs/RELEASE_PLAN.md`: v2.0 Phase03 finalized Milestone M3 complete.
- `docs/PROMPT_LOG.md`: Append-only history — Prompt 004 Phase03.
- `docs/reports/PHASE-00-DISCOVERY-REPORT.md`, `PHASE-01-REQUIREMENTS-REPORT.md`, `PHASE-02-UX-DESIGN-REPORT.md` (34 screens, 14 UX docs, 27 stories verified).

### Architecture, Data, Security, Privacy (Phase 03)
- `docs/architecture/SYSTEM_CONTEXT.md`: C4 context actors P0/P1/P2, external services, trust boundaries, sensitive-data boundaries, Mermaid C4Context + fallback flowchart.
- `docs/architecture/CONTAINER_ARCHITECTURE.md`: C4 container Next.js frontend + Django modular monolith + PG16 + Redis7 Celery + private S3 + email abstraction + future push/payment/AI/wearable dashed, deployment topology, failure modes, NFR targets proposed.
- `docs/architecture/COMPONENT_BOUNDARIES.md`: Frontend Next.js app structure [locale]/(auth)/(app)/(coach)/(org)/(admin) 34 screens mapping + backend Django apps 20 modules + middleware stack RequestID/SecurityHeaders/OrgScope/AuthZ/Audit + dependency rules import-linter + sequence diagram assignment.
- `docs/architecture/DATA_FLOW.md`: Flows auth/invite, exercise search Persian normalization pg_trgm, assignment snapshot JSONB immutable, workout logging offline boundary Phase04/07/12, progress photo consent + signed URL gated, messaging, privacy export/erasure sequence.
- `docs/architecture/DEPLOYMENT_ARCHITECTURE.md`: Logical deployment PaaS vs K8s options, env local/staging/prod distinct VPC/DB/buckets/secrets, Docker + GitHub Actions CI/CD lint/type/unit/integration/security scan Playwright E2E staging auto prod manual gate, TLS HSTS CSP, secrets manager, backup hooks, RPO/RTO proposed table.
- `docs/architecture/ERD.md`: erDiagram 30+ entities relationship, detailed entity specs PK/FK/tenant ownership/sensitive fields/indexes/unique constraints/state machines/soft-delete/archive policy/audit/retention/localization, identifier UUIDv7 proposed not authz substitute, soft-delete archived_at, conceptual DDL illustrative, legend, rendering validation.
- `docs/architecture/DOMAIN_MODULES.md`: 20 modules M01-M20 responsibility owned entities public interfaces read/write deps security boundary events emitted/consumed sensitivity test boundary extraction risk + dependency hierarchy + event bus in-process.
- `docs/architecture/AUTHORIZATION_ARCHITECTURE.md`: RBAC P0 roles platform_admin/owner/coach/athlete/support + future nutritionist P1 consent-gated, org boundaries active context request.org_id, object-level assignment CoachAthleteAssignment, owner aggregate vs raw distinction no automatic raw photo/message, break-glass admin MFA+reason+audit, P1 nutritionist consent, photo consent, export/erasure self-only, audit visibility owner own org only coach/athlete forbidden, suspension immediate 403, invitation permissions owner any coach athlete-only, detailed matrix per sensitive resource create/read/update/archive/export/share/revoke/consent/audited, negative controls.
- `docs/architecture/PWA_ARCHITECTURE.md`: Three-level strategy Phase04 manifest/icons/standalone/SW registration/app-shell caching/offline fallback/install guidance, Phase07 athlete mobile execution touch-optimized 44/48px form-state temp memory network indicator retry no durable queue promise, Phase12 IndexedDB durable queue sync status retry/backoff conflict resolution background sync push limitations HealthKit eval native bridge decision, browser limitations table Security, file structure.
- `docs/architecture/MEDIA_STORAGE.md`: Media types Tier0/2/4 classification buckets private no listing BlockPublicAcls true versioning SSE-S3, signed URL TTL≤15min no caching Tier4 in SW, upload validation MIME magic bytes size limits checksum, thumbnail strategy Pillow ffmpeg, malware scan ClamAV proposed quarantine, provenance/license metadata mandatory, takedown workflow, photo access control matrix, future transcoding CDN rules, retention.
- `docs/architecture/OBSERVABILITY.md`: Structured logging json structlog required fields timestamp level service request_id org_id actor_user_id action entity/id duration status message version redaction processor removes password token Authorization message content health details photo keys signed URLs IP hash, correlation request_id middleware X-Request-ID, audit vs debug separation ELK 30d vs audit PG 1y+, metrics Prometheus counters/histograms http_requests_total duration auth failures program_assignments workout_sessions set_logs media uploads signedURL notifications celery audit export db_connections cache_hit_ratio, error tracking Sentry, healthz/readyz checks DB Redis S3 Celery, alerting categories auth anomaly cross-tenant 403 spike photo 403 spike 5xx>1% latency p95 DB connections Redis S3 Celery queue export fail backup fail disk cert expiry.
- `docs/architecture/BACKUP_AND_DISASTER_RECOVERY.md`: PG daily snapshot 30d retention proposed + WAL PITR RPO 15min RTO 1h restore+30m validation manual pre-migration snapshot, S3 versioning noncurrent expire 30d exports-tmp 7d lifecycle, Redis not source loss acceptable, code git, restore runbooks DB/S3, weekly automated restore testing smoke tests, RPO/RTO proposed table, disaster scenarios PG AZ failure corruption S3 delete Redis failure container crash accidental erasure secrets leaked, incident response detect triage contain investigate recover post-mortem communicate, breach response containment audit notification 72h if GDPR legal required, rollback app previous image + migration reverse 2-step add/dual-write/backfill/switch/drop with pre-migration snapshot, env separation distinct VPC/DB/buckets/secrets, open questions multi-AZ cost cross-region replication legal.
- `docs/architecture/README.md`: Architecture docs index purpose doc index tech decisions summary verification no code rendering notes next phase.
- `docs/architecture/ARCHITECTURE_VALIDATION_CHECKLIST.md`: V01-V22 checklist P0 domains owning modules sensitive entities access rules API groups boundaries stories→domains/APIs UX routes→frontend boundaries cross-tenant auth strategy media types rights export/deletion paths PWA sequencing consistency no Arabic no AI/payment/wearable P0 open legal/license visible no secrets/health data screen 34 UX doc 14 story 27 offline boundary touch 44/48 Jalali/Gregorian modal focus dark-theme Persian terminology.
- `docs/OPENAPI.yaml`: OpenAPI 3.1 provisional /api/v1 covering auth, current user, orgs, locations, memberships, invitations, exercise catalog, moderation, programs, templates, assignments, today, sessions, set logs, substitutions, feedback flags, progress photos/metrics, consents, messages, notifications, audit, privacy export/deletion, media signed URLs — each method/path/purpose/auth/required role/object permission/request/response schema/error responses/localization/idempotency/audit/rate-limit/sensitivity, RFC7807 + message_key.
- `docs/JSON_SCHEMAS.md`: JSON Schema draft 2020-12 snapshot immutable, queue entry offline Phase12, export manifest profile.json workouts.json, notification payload, consent, Persian normalizer pseudocode Perso-Arabic script keyboard-variant normalization.
- `docs/THREAT_MODEL.md`: STRIDE 21 threats T01-T21 + OWASP Top10 mapping + controls preventive/detective/corrective + test strategy + residual risk.
- `docs/PRIVACY_DATA_LIFECYCLE.md`: 11 lifecycle stages, Tier0-8 classification detailed per class purpose/legal assumption/owner/controller/access/encryption/logging retention/export/deletion/consent, consent lifecycle progress photo + nutrition P1, export pipeline ZIP via Celery tmp S3 24h link, erasure pipeline anonymization + S3 delete, retention questions, pre-DPIA checklist large-scale sensitive systematic monitoring profiling multi-prof sharing progress-photo wearable AI.
- `docs/SECURITY_CONTROL_MATRIX.md`: Threat→Requirement→Architecture Control→Phase→Test Type→Evidence→Status including negative controls cross-tenant reads/writes unassigned coach suspended membership unauthorized photo/message/audit/export.
- `docs/ARCHITECTURE_VALIDATION_CHECKLIST.md`: Copy of architecture validation checklist at docs level (required).
- `docs/reports/PHASE-03-ARCHITECTURE-REPORT.md`: 31-section Phase 03 comprehensive report (this phase).

---

## 5. Summary of Phase 03 Architecture Decisions

1. **Modular Monolith Accepted (ADR-001):** Single deployable + strict domain package isolation via import-linter.
2. **Tech Stack Conditionally Accepted (ADR-002):** Next.js 14 App Router + React + TS + Tailwind logical + next-pwa/Workbox proposed; Django 5 + DRF + Python 3.12; PG16 + pg_trgm + btree_gin + pgcrypto; Redis7 Celery; S3 private signed TTL≤15min; REST /api/v1 OpenAPI 3.1 provisional; PWA three-level; Playwright; GitHub Actions — requires Phase04 POC validation, founder infra choice pending.
3. **Locales fa-IR/en-US only Arabic out of scope Accepted (ADR-003):** No Arabic locale/files/translations/requirements, CI lint NFR-I18N-04.
4. **B2B2C Accepted (ADR-004):** Orgs/coaches pay; athletes included.
5. **Auth Channel Email+Password Proposed Conditional (ADR-005, ADR-032):** Argon2id/bcrypt cost≥12, HttpOnly Secure SameSite Lax cookie, JWT rotating refresh 15min access optional, rate limit 5/15min Redis, reset token 15min single-use, invitation 7d SHA256 hashed single-use.
6. **Authorization RBAC+ABAC+Consent Accepted (ADR-006):** Server-side 100%, tenant isolation org_id from auth context, CoachAssignment, Consent, break-glass MFA+reason+audit, owner aggregate vs raw distinction.
7. **AI Deferred Phase11 Accepted (ADR-007):** Human-in-loop copilot, no autonomous medical claims.
8. **Media Rights Provenance Accepted (ADR-008):** License metadata mandatory, admin moderation queue.
9. **Calendar UTC Storage + Jalali UI Accepted Conditional (ADR-009):** Timestamptz UTC, ISO8601 API, frontend date-fns-jalali renders Jalali when locale fa-IR.
10. **Monorepo Proposed (ADR-010):** frontend/ + backend/ + docs/ + .github/ scaffold Phase04.
11. **PWA Sequencing Accepted (ADR-011):** Phase04 foundation manifest/icons/standalone/SW app-shell offline fallback install guidance, Phase07 athlete mobile execution touch-optimized logging temp preservation retry no durable queue, Phase12 durable IndexedDB queue sync status retry conflict background sync push limitations HealthKit eval.
12. **License Pending Founder Approval (ADR-012):** MIT vs Proprietary vs Open-Core vs Private commercial — LICENSE remains MIT until written founder confirmation, do not change without explicit authorization.
13. **Single-Location-First Accepted (ADR-013):** 1 primary location MVP via partial unique index, multi-location P1.
14. **Membership Multi-Role Accepted Conditional (ADR-014):** Membership join table role owner/coach/athlete/support status invited/active/suspended unique (user_id, organization_id, role) allows multi-role.
15. **Snapshot Versioning Accepted Conditional (ADR-015):** Immutable JSONB snapshot on assignment, deep copy phases/weeks/days/workouts/items/prescriptions, frozen_at, version, preserves historical integrity.
16. **Soft-Delete vs Anonymized Hard Delete Accepted Conditional (ADR-016):** Operational entities archived_at soft-archive filtered, user erasure via anonymization pipeline PII wiped photos S3 deleted memberships archived aggregates disassociated, AuditEvent never deleted DB-level REVOKE.
17. **UUIDv7 vs BigInt Proposed Requires Validation Not Authz Substitute (ADR-017):** Time-ordered 128-bit prevents enumeration supports offline client generation Phase12 queue, not authz substitute, validation required Phase04 python uuid6 + PG + JS support, fallback UUIDv4.
18. **Persian Search Normalization Accepted Conditional (ADR-018):** Perso-Arabic script keyboard-variant normalization for Persian search — fold ي/ى→ی ك→ک digits ZWNJ, pg_trgm GIN indexes normalized_alias, precise wording not Arabic product support.
19. **Data Ownership Accepted (ADR-019):** Athlete owns historical logs, org holds revocable operational access.
20. **Multi-Professional Consent Accepted for P1 (ADR-020):** CoachAssignment + NutritionistAssignment + ConsentRecord per type.
21. **Payment Gateway Abstraction Deferred Phase10 Accepted (ADR-021):** Shetab domestic / Stripe international abstraction, webhook idempotency verify signature.
22. **Marketplace Deferred P2 Accepted (ADR-022):** No discovery marketplace in P0.
23-28. **UX Decisions ADR-023..028 Accepted:** Athlete 5-tab bottom nav modal active canvas, coach dual-pane master-detail, Vazirmatn font, non-clinical UX language, explicit affirmative consent modal, dark obsidian #0B0F17 default design target requires user testing.
29-43. **Phase03 Additional ADR-029..043 Proposed/Accepted:** Frontend Next.js boundaries, backend 20 modules, PG16 extensions, auth/session strategy, API error RFC7807 + message_key, media storage private signed, PWA three-level, offline boundary explicit, backup/RTO/RPO proposed requires cost approval, env separation, CI/CD GitHub Actions, observability structlog, OpenAPI 3.1 provisional, threat model STRIDE, privacy lifecycle Tier0-8 + pre-DPIA.

---

## 6. Risks, Blockers & Open Items

| ID | Risk / Decision Item | Severity | Status & Action |
|----|----------------------|----------|-----------------|
| **DEC-01** | Repository License Transition (ADR-012) | Medium | **Pending Founder Approval:** Founder to choose MIT vs Proprietary vs Open-Core before Phase04 scaffold — LICENSE remains MIT until written confirmation. |
| **ADR-017** | UUIDv7 vs UUIDv4/BigInt identifier strategy | Medium | **Proposed Requires Validation:** Validate PG16 + Python uuid6 + JS support for UUIDv7 time-ordered in Phase04 POC; fallback UUIDv4; never use identifier as authz substitute. |
| **ADR-037** | Backup/RTO/RPO targets cost | Medium | **Proposed Requires Validation + Founder Cost Approval:** Multi-AZ PG, cross-region replication for Tier4 bucket, retention 30d vs 7d, RPO 15min vs 5min. |
| **R01** | Brand Legal Name & Trademark | Low | Continue CoachOS codename. |
| **R06** | Persian Font Web Delivery | Medium | Font subsetting + font-display swap benchmarked Phase04 foundation. |
| **R13** | Data Residency Region | Medium | Iran-compatible vs EU/international region selection requires legal review for PII residency. |
| **R14** | Region selection for S3 provider (AWS vs R2 vs MinIO) | Low | Pending founder infra budget. |
| **LEGAL** | Privacy Compliance (GDPR-adjacent Iran/EU) | High | **Requires jurisdiction-specific legal review before handling real health data — pre-DPIA checklist documented in PRIVACY_DATA_LIFECYCLE.md but formal DPIA required before commercial pilot.** |

---

## 7. Next Step

Phase 03 complete. Standing by for founder instruction to begin:
**Phase 04 — Project Foundation and PWA Baseline**
- Do not start Phase04 automatically.
- Await explicit instruction.
- Next phase will scaffold Next.js + Django modular monolith + PWA manifest + SW + DB migrations + CI pipeline — upon approval.
