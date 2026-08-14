# Project Status — CoachOS

**Last updated:** 2026-08-14 (UTC)
**Current phase:** Phase 05 — **Identity, Tenancy, and Roles — Complete** (PR open for review)
**Next step:** Await founder review of Phase 05 PR. Do not begin Phase 06.
**Working branch:** `arena/019fff00-coachos-fitness-coaching-platf`
**Base commit (main):** `0855867cc85f56bb4b77c5f708db8e122ded6b81` (PR #10 merge — CI activation)
**Repository:** https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform
**License:** Proprietary / All Rights Reserved (ADR-012 — Copyright (c) 2026 CoachOS Technologies / Ali Naderi)

---

## 1. One-Line Status

The Phase 04 foundation and CI activation are **complete**: remediation PR #8 (`dd7dea56945d96a6a2d595afb5154b6828c4e3b6`, 2026-08-11) is merged; docs synchronization PR #9 (`0eae53b89343ec0a4eb1200086b769011012c406`, 2026-08-12) is merged; CI activation PR #10 (`chore/activate-github-actions-manual`) is **merged** into `main` at `0855867cc85f56bb4b77c5f708db8e122ded6b81` (2026-08-14T06:36:42Z). Both canonical workflow files — `.github/workflows/ci.yml` and `.github/workflows/security-scan.yml` — are present on remote `main`, GitHub Actions workflows are active, and both post-merge workflow runs on the merge commit succeeded: **CoachOS CI Quality Gates** (run ID `31776895893`, conclusion `success`) and **Security & Vulnerability Scan** (run ID `31776896050`, conclusion `success`). The `frontend/lib/` files implement exact `fa-IR`/`en-US` locale governance, matching bilingual dictionaries, deterministic Jalali/Gregorian display, Persian normalization, Unicode BiDi isolation, public-only configuration validation, a foundation-only typed API client, and SSR-safe `/sw.js` registration, tracked through narrow `/frontend/lib/` exceptions inside the retained broad `lib/` ignore rule. The remediation is a founder-authorized specification-based reimplementation — not a restoration; provenance and corrections remain recorded in `docs/reports/POST-MERGE-PHASE-04-FRONTEND-REIMPLEMENTATION-REPORT.md` (original Phase 04 report unchanged). **Phase 05 remains unstarted, unauthorized, and awaits explicit founder authorization; no Phase 05 implementation has been added.**

---

## 2. Phase 04 Implementation Summary

| Area | Implemented Artifacts | Verification / Tests |
|---|---|---|
| **Monorepo Architecture** | `frontend/`, `backend/`, `infra/`, `docker-compose.yml`, `compose.yaml`, `.env.example`, `.gitignore` | Local development verified via Docker & direct runtime |
| **Frontend Shell** | Next.js 14.2 App Router, TypeScript strict, Tailwind logical CSS, dark obsidian theme (`#0B0F17`), placeholder dashboard screens clearly marked as foundation-only | 49 Vitest tests passing; Next.js static build verified (18 static pages generated) |
| **PWA Baseline** | `manifest.json`, `manifest.webmanifest`, `sw.js` (Cache-First static, Network-First navigation), 192px/512px maskable PNG icons, `/offline` page, `NetworkStatusBanner`, `InstallPromptBanner` | Manifest validation test passing; PWA icon dimension test passing; Service worker caching verified |
| **Bilingual RTL/LTR Engine** | Dynamic `lang` and `dir` on HTML root, `fa-IR` RTL, `en-US` LTR, BiDi text isolation (`<bdi>`), Persian search normalizer (`PersianNormalizer`), Jalali date conversion | i18n tests passing; dictionary 100% key parity; Jalali converter test passing |
| **Language Governance** | Strict exclusion of Arabic locale files (`ar-*.json`, `ar.json`, `ar.po`) across frontend and backend | `test_no_arabic.py` passing; `no-arabic.test.ts` passing; CI check-secrets scanner passing |
| **Backend REST API** | Django 5.2 + DRF 3.18, modular settings (`base`, `dev`, `staging`, `prod`, `test`), `CorrelationIDMiddleware`, `SecurityHeadersMiddleware`, `LoggingRedactionMiddleware`, `TenantContextMiddleware` | 37 Pytest tests passing; 78% overall test coverage (90%+ core) |
| **Fail-Closed Configuration** | Mandatory `DJANGO_SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` in production/staging | `test_fail_closed_settings.py` (10 tests passing) |
| **Secure Default Permissions** | `REST_FRAMEWORK` default permission class set to `IsAuthenticated`; public health endpoints opt in explicitly | `test_default_permissions.py` (3 tests passing) |
| **Safe Health Endpoints** | `GET /healthz` (200 OK liveness), `GET /readyz` (DB + Redis check), `GET /api/v1/meta` (safe public metadata) | `test_health.py`, `test_readyz.py`, `test_meta.py` passing |
| **Frontend CSP & Headers** | Environment-specific CSP (dev HMR vs production without `unsafe-eval`), object-src 'none', frame-ancestors 'none' | `security-headers.test.ts` (3 tests passing) |
| **Error Handling & Security** | RFC 7807 Problem Details envelope with `message_key`, zero internal stack traces in client responses, log redaction, HttpOnly session cookie config | `test_errors.py`, `test_drf_exceptions.py`, `test_security_headers.py`, `test_secret_leakage.py` passing |
| **Entity Identifiers** | Time-ordered UUIDv7 generator (`id_generator.py`) with validation | `test_uuidv7.py` passing; verified time-ordering trend |
| **CI Quality Gates (Active)** | `.github/workflows/ci.yml`, `.github/workflows/security-scan.yml` (canonical, on remote `main` via PR #10 merge `0855867c...`), mirrored definitions `infra/ci/ci.yml`, `infra/ci/security-scan.yml`, `infra/scripts/check-secrets.sh` | GitHub Actions active; post-merge runs on merge commit succeeded — CoachOS CI Quality Gates run `31776895893` (success), Security & Vulnerability Scan run `31776896050` (success) |
| **License & IP** | Transitioned to Proprietary / All Rights Reserved notice in `LICENSE` and ADR-012 | `LICENSE` file updated; ADR-012 accepted per founder mandate |
| **Hosting & Data Residency** | Comprehensive 10-dimension evaluation of PaaS, EU Cloud, Bare VPS, Dual-Region in `HOSTING_AND_DATA_RESIDENCY_DECISION.md` | Decision gate established; zero cloud credentials in Git |

---

## 3. Active Non-Negotiable Constraints

1. **Languages:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR) **only**.
2. **Arabic is strictly out of scope:** No Arabic locale files, translations, UI text, or requirements.
3. **No Marketplace, Payments, or Autonomous AI in P0:** Deferred to P1/P2 backlogs.
4. **B2B2C SaaS Model:** Organizations/coaches are paying customers; athlete accounts are free/included.
5. **PWA-First Delivery:** Level 1 Foundation (Phase 04 complete), Level 2 Athlete Execution (Phase 07), Level 3 Advanced Offline Sync (Phase 12).
6. **Single-Location MVP:** Organizations have a single primary facility in P0; multi-location in P1.
7. **Calendar Strategy:** UTC/Gregorian backend storage with Jalali UI rendering in `fa-IR` locale (ADR-009).
8. **No Secrets or Real Health Data in Repository:** Synthetic data only; verified via automated CI security scanner.
9. **License:** Proprietary / All Rights Reserved (ADR-012).

---

## 4. Risks, Blockers & Open Items

| ID | Item | Severity | Status & Action |
|---|---|---|---|
| **ADR-012** | Proprietary License Legal Review | Low | **Founder Decision Applied:** Proprietary notice in place; formal IP counsel review recommended prior to commercial launch. |
| **ADR-049** | Production Hosting Provider Selection | Medium | **Evaluation Complete:** Comparative matrix in `HOSTING_AND_DATA_RESIDENCY_DECISION.md`; production deployment gated until Phase 13 founder approval. |
| **TODO-CSP-001** | CSP Strict Nonce Migration | Low | Next.js development uses `'unsafe-inline'`; production eliminates `unsafe-eval`; migration to per-request cryptographic nonce planned before production pilot. |
| **LEGAL** | Privacy Compliance (GDPR & Iran Data Residency) | High | Formal pre-DPIA documented; jurisdiction-specific legal review required before handling real production health telemetry. |
| **P04-REMEDIATION** | Missing original `frontend/lib/` source | Low | **Closed — merged:** PR #8 (`dd7dea56945d96a6a2d595afb5154b6828c4e3b6`, 2026-08-11) merged the specification-based reimplementation; PR #9 (`0eae53b89343ec0a4eb1200086b769011012c406`, 2026-08-12) merged docs synchronization. All nine `frontend/lib/` files verified tracked on remote `main`. Provenance/correction record: `docs/reports/POST-MERGE-PHASE-04-FRONTEND-REIMPLEMENTATION-REPORT.md`. |
| **CI-ACTIVATION** | GitHub Actions activation | — | **Closed — PR #10 merged:** PR #10 (`chore/activate-github-actions-manual`) merged into `main` at `0855867cc85f56bb4b77c5f708db8e122ded6b81` (2026-08-14T06:36:42Z). `.github/workflows/ci.yml` and `.github/workflows/security-scan.yml` verified present on remote `main` (`git ls-tree origin/main`); GitHub Actions workflows are active; post-merge runs on the merge commit succeeded — CoachOS CI Quality Gates run ID `31776895893` (`success`) and Security & Vulnerability Scan run ID `31776896050` (`success`); no deployment job or real secret exists. Phase 05 stays unstarted and unauthorized. |

---

## 5. Next Step

CI activation is complete; Phase 05 stays gated on explicit founder authorization:

1. PR #9 (docs synchronization) is merged at `0eae53b89343ec0a4eb1200086b769011012c406` (2026-08-12).
2. PR #10 (`chore/activate-github-actions-manual`) is **merged** into `main` at `0855867cc85f56bb4b77c5f708db8e122ded6b81` (2026-08-14T06:36:42Z), adding exactly `.github/workflows/ci.yml` and `.github/workflows/security-scan.yml`; no deployment job or real secret exists.
3. CI is **active**: both workflow files exist on remote `main`, and real GitHub Actions runs on the merge commit are visible and passing — CoachOS CI Quality Gates (run ID `31776895893`, `success`) and Security & Vulnerability Scan (run ID `31776896050`, `success`).
4. Phase 04 foundation and CI activation are complete. Phase 05 remains **unstarted** and awaits explicit founder authorization; no Phase 05 implementation has been added. Do not begin Phase 05 automatically.
