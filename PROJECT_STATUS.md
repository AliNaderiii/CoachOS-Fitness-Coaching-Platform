# Project Status — CoachOS

**Last updated:** 2026-08-14 (UTC)
**Current phase:** Phase 06 — **Exercise Library and Training Programs — Candidate under validation/review; not merged or complete**
**Next step:** Finish Stage 9 publication, verify the Phase 06 PR and GitHub Actions, then leave the PR open for founder review. Do not merge and do not start Phase 07.
**Working branch:** `arena/019fffa4-coachos-fitness-coaching-platf` (Arena session branch)
**Base commit (main):** `86503b3930192dd46de7ce500384c246d236fcd4` (PR #14 merge; verified current `origin/main` at recovery)
**Repository:** https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform
**License:** Proprietary / All Rights Reserved (ADR-012 — Copyright (c) 2026 CoachOS Technologies / Ali Naderi)

---

## 1. One-Line Status

**Phase 06 is an unmerged candidate, not a completed phase.** Safe recovery found the session checkout clean at verified base `86503b3930192dd46de7ce500384c246d236fcd4`, with no interrupted artifacts to preserve. On `arena/019fffa4-coachos-fitness-coaching-platf`, local Gates 0–8 now pass for bilingual exercise catalog/search, media provenance/moderation API, hierarchical programs/prescriptions, template clone/versioning, immutable assignment snapshots, tenant/RBAC controls, and coach/owner UI. Full backend validation is 69/69 tests with 83% coverage; frontend validation is 56/56 tests plus clean lint/type/build; repository compliance, `pip-audit`, and `npm audit` pass. Stage 9 commit/push/PR/Actions verification remains in progress, and the PR must remain open for founder review. No Arabic localization or Phase 07+ code was added. Do not merge automatically and do not start Phase 07. See `docs/reports/PHASE-06-EXERCISE-LIBRARY-TRAINING-PROGRAMS-REPORT.md`.

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
| **CI-ACTIVATION** | GitHub Actions activation | — | **Closed — PR #10 merged:** PR #10 (`chore/activate-github-actions-manual`) merged into `main` at `0855867cc85f56bb4b77c5f708db8e122ded6b81` (2026-08-14T06:36:42Z). `.github/workflows/ci.yml` and `.github/workflows/security-scan.yml` verified present on remote `main` (`git ls-tree origin/main`); GitHub Actions workflows are active; post-merge runs succeeded; no deployment job or real secret exists. Actions remain active and passing on `main` through the PR #13 merge commit (`d7f72b3f...`). |
| **P05-DEFERRED** | Phase 05 deferred scope | Low | **Open — deferred by decision:** Phase 05 merged complete for its documented scope via PR #13 (`d7f72b3fcfd6667df524af5adf71328c5de6edba`). Deferred items remain deferred pending later authorized phases: frontend onboarding UI, ownership transfer, full effective-permissions/active-org context, production email delivery, MFA, and compliance certification. Phase 06 adds only the minimal tenant-scoped `CoachAthleteAssignment` relation required to authorize program assignment; broader lifecycle/UI remains deferred. |

---

## 5. Next Step

Phase 05 is merged and complete; Phase 06 is now an unmerged candidate awaiting Stage 9 publication and founder review:

1. PR #13 (Phase 05 — Identity, Tenancy, and Roles) is **merged** into `main` at `d7f72b3fcfd6667df524af5adf71328c5de6edba` (2026-08-14T08:40:58Z).
2. All four post-merge GitHub Actions checks on the merge commit are **successful**: Backend Lint, Type & Tests (Django/DRF); Frontend Lint, Type & Tests (Next.js/PWA); Security Scan & Language Compliance; Secret & Pattern Scanning (runs `31784911766` and `31784911764`, both `success`). GitHub Actions remain active and passing on `main`.
3. Phase 05 is complete for its documented scope. Deferred Phase 05 items remain deferred: frontend onboarding UI, `CoachAthleteAssignment`, ownership transfer, full effective-permissions/active-org context, production email delivery, MFA, and compliance certification.
4. Phase 06 implementation Gates 0–8 pass locally on the dedicated Arena branch. Complete Stage 9 publication and remote checks, then leave the PR open for founder review; Phase 06 remains unmerged/not complete. Do not start Phase 07.
