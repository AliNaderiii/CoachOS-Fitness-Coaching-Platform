# Prompt Log — CoachOS

Append-only history of founder/supervising-agent prompts and resulting actions.

---

## Prompt 001

- **Date/time:** 2026-08-10 (UTC)
- **Source:** Founder / supervising agent (initial system mission prompt)
- **Phase:** 00 — Discovery and Repository Audit
- **Prompt Summary:** Multi-role founding product-and-engineering mandate for CoachOS bilingual fitness coaching platform. Non-negotiable fa-IR RTL + en-US LTR only; Arabic explicitly out of scope. Phased delivery 00–14 with required documentation set.
- **Requested outcome:** Complete Phase 00 discovery; do not build full product or application code.
- **Actions taken:** Inspected greenfield repository, created full documentation foundation, and merged via PR #3.

---

## Post-Phase-00 Merge Record

- **Date/time:** 2026-08-10T13:57:45Z (UTC)
- **Action:** Pull Request #3 merged into `main` (`f52c4134087b18c4bd1a8aef9e0100fd63f71b8e`)

---

## Prompt 002

- **Date/time:** 2026-08-10 (UTC)
- **Source:** Founder / supervising agent
- **Phase:** 01 — Product Requirements and Scope
- **Actions taken:** Created complete PRD, 6 personas, 5 user journeys, bilingual glossary, competitive landscape benchmark (10 platforms), RTM, and merged via PR #4.

---

## Prompt 003

- **Date/time:** 2026-08-10 (UTC)
- **Source:** Founder / supervising agent
- **Phase:** 02 — UX, Information Architecture, and Design System
- **Actions taken:** Created complete UX design package: 34 screen specs, 14 UX spec documents, navigation models, dark obsidian design tokens, WCAG 2.2 AA accessibility, bidirectional wireframes, and merged via PR #5.

---

## Post-Phase-02 Merge Record

- **Date/time:** 2026-08-10T18:45:01Z (UTC)
- **Action:** Pull Request #5 merged into `main` (`771afa668e71b0b181218be2e4d768e60f4f36f9`)

---

## Prompt 004

- **Date/time:** 2026-08-10 (UTC)
- **Source:** Founder / supervising agent
- **Phase:** 03 — Architecture, Data, Security, and Privacy
- **Actions taken:** Created C4 context/container diagrams, 20 domain modules, normalized ERD, RBAC/ABAC matrix, provisional OpenAPI 3.1 catalog, STRIDE threat model, privacy lifecycle, media storage architecture, PWA 3-level strategy, observability, backup/DR strategy, 43 ADRs, and opened PR #6.

---

## Prompt 005 & 006

- **Date/time:** 2026-08-10 (UTC)
- **Source:** Founder / supervising agent — Phase 03 Architecture Review Corrections
- **Phase:** 03 — Architecture Review Corrections (PR #6)
- **Actions taken:** Applied correction-only commits: secret manager boundary (FE --> SecretMgr forbidden), CSP nonce/hash preferred, auth transport consistency (cookie session MVP + optional JWT), data-model invariants (owner source of truth, multi-role union, assignment partial unique), backup wording, and OpenAPI response consistency. Merged into `main` at `692b2b02ac23d8ad433270fa9ea585f5dc860768`.

---

## Post-Phase-03 Merge Record

- **Date/time:** 2026-08-11T06:23:50Z (UTC)
- **Action:** Pull Request #6 merged into `main` (`692b2b02ac23d8ad433270fa9ea585f5dc860768`)
- **Merge Commit:** `692b2b02ac23d8ad433270fa9ea585f5dc860768`
- **Result:** Phase 03 Architecture package officially merged into main repository.

---

## Prompt 007

- **Date/time:** 2026-08-11 (UTC)
- **Source:** Founder / supervising agent
- **Phase:** 04 — Project Foundation and PWA Baseline
- **Prompt Summary:**
  Execute Phase 04 — Project Foundation and PWA Baseline.
  - Apply founder decisions: Product languages fa-IR (RTL) and en-US (LTR) only; Arabic strictly out of scope; Proprietary / All Rights Reserved license (ADR-012); dual-region-capable strategy evaluation in `HOSTING_AND_DATA_RESIDENCY_DECISION.md`.
  - Create reproducible, secure, bilingual, PWA-first monorepo foundation (`frontend/` Next.js 14, `backend/` Django 5/DRF, `infra/` Docker Compose, CI quality gates).
  - PWA Level 1 foundation: Web App Manifest, 192px/512px maskable icons, Service Worker app-shell caching, offline fallback screen, network status banner, install guidance.
  - Backend foundation: modular settings, security headers, correlation ID middleware, logging redaction, RFC 7807 problem details error envelopes, UUIDv7 utility, Persian text search normalizer, `/healthz`, `/readyz`, `/api/v1/meta`.
  - Quality gates & verification: Vitest frontend tests, Pytest backend tests, Ruff linting, ESLint, TypeScript strict checking, secret scanning, Arabic exclusion check.
  - Comprehensive documentation & Phase 04 report (`docs/reports/PHASE-04-FOUNDATION-REPORT.md`).
  - Do not implement Phase 05+ domain features (users, orgs, programs, workouts).
  - Open Pull Request and stop for founder review.

- **Actions Taken:** Initial Phase 04 foundation delivered and PR #7 opened.

---

## Prompt 008

- **Date/time:** 2026-08-11 (UTC)
- **Source:** Founder / supervising agent — Phase 04 Foundation Review — Correction-Only Task
- **Phase:** 04 — Project Foundation and PWA Baseline (Review Corrections)
- **Prompt Summary:**
  Perform focused security, configuration, and documentation correction review on PR #7:
  1. Fail-closed secret configuration (production/staging fail fast on missing `DJANGO_SECRET_KEY` or `DATABASE_URL`, no wildcard `ALLOWED_HOSTS`).
  2. Secure default DRF permissions (`IsAuthenticated` default; `/healthz`, `/readyz`, `/api/v1/meta` explicit `AllowAny`).
  3. Tenant-context header safety (`ALLOW_TENANT_HEADER_OVERRIDE=False`; session-only active organization derivation).
  4. Correlation ID validation (reject malformed, oversized, or log-injection IDs; generate fresh UUIDv7).
  5. Frontend security headers and CSP delivery on HTML responses via `next.config.mjs`.
  6. PWA and locale validation (verify manifest, icons, service worker, static manifest Persian default metadata documentation).
  7. Normalize static-page count to 18 verified pages and update test counts.
  8. Do not create Phase 05 domain code, push correction to PR #7, and keep PR #7 open.

- **Actions Taken:**
  - Implemented fail-closed validation in `staging.py` and `production.py` (mandatory secret key & DB URL, explicit allowed hosts, no wildcard fallback).
  - Updated `base.py` DRF default permission class to `IsAuthenticated`; public health endpoints explicitly use `AllowAny`.
  - Updated `CorrelationIDMiddleware` to validate UUID format and length ≤ 36 chars, replacing malformed strings with clean UUIDv7.
  - Updated `TenantContextMiddleware` to derive tenant context from session state and gate client headers behind `ALLOW_TENANT_HEADER_OVERRIDE` (default `False`).
  - Configured frontend CSP and security headers on Next.js HTML responses in `next.config.mjs`.
  - Added unit tests for fail-closed settings (`test_fail_closed_settings.py`), DRF default permissions (`test_default_permissions.py`), correlation ID validation, tenant header safety, and frontend security headers (`security-headers.test.ts`).
  - Total test suite: 32 backend Pytest tests (100% pass), 30 frontend Vitest tests (100% pass), 18 static pages generated in Next.js build.
  - Updated documentation, checklist, changelog, and Phase 04 report.

---

## Prompt 009

- **Date/time:** 2026-08-11 (UTC)
- **Source:** Founder / supervising agent — Phase 04 Post-Merge Remediation
- **Phase:** 04 — Project Foundation and PWA Baseline (Post-Merge Correction)
- **Prompt Summary:**
  - Audit merged `main` and address the absence of nine documented `frontend/lib/` source files.
  - Because authoritative original source was unrecoverable, perform an explicitly founder-authorized **specification-based reimplementation**, not a restoration.
  - Reimplement only the named public configuration, i18n dictionaries/helpers, API client, and service-worker registration files; preserve tracked tests and call sites as hard contracts.
  - Retain the general `lib/` ignore rule and add only narrow `frontend/lib/` exceptions.
  - Add focused tests, a separate correction report, and narrow tracking-document updates.
  - Validate from a clean tracked-only checkout; push one remediation PR to `main` without merging it.
  - Keep workflow activation separate and do not begin Phase 05.
- **Actions Taken:**
  - Verified current `origin/main` and merge base at `1c4a552ab86f6bca7b522492c8488614ae0d97de`.
  - Reimplemented and tracked exactly nine `frontend/lib/` files from Phase 00–04 documentation, architecture decisions, UX copy, existing tests, and call sites; recorded all behavior assumptions in the correction report.
  - Added narrow `.gitignore` exceptions, focused API client/service-worker tests, and expanded security, formatter, normalization, locale metadata, and exhaustive 54-key bilingual dictionary governance tests.
  - Clean-validated implementation commit `8c268db973530157fb1468bc1838f8bca59f7310`: frontend `npm ci`, lint, type-check, 49 tests, and 18-page build passed; backend Ruff and 37 Pytest tests passed; secret/language/PWA/scope/ignore/tracked-file audits passed.
  - Added `docs/reports/POST-MERGE-PHASE-04-FRONTEND-REIMPLEMENTATION-REPORT.md`; retained the original Phase 04 report unchanged.
  - Did not add workflow files or Phase 05 domain code.

