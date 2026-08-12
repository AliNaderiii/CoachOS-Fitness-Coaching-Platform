# Project Status — CoachOS

**Last updated:** 2026-08-11 (UTC)
**Current phase:** Phase 04 — Post-merge frontend reimplementation remediation (**merged and complete via PR #8**)
**Next step:** GitHub Actions workflow activation (separate PR; `.github/workflows/` still absent on `main`); Phase 05 remains unstarted and awaits explicit founder authorization after CI activation review
**Working branch:** `chore/close-phase04-remediation-status` (delivered via session branch `arena/019ff171-coachos-fitness-coaching-platf`)
**Base commit (main):** `dd7dea56945d96a6a2d595afb5154b6828c4e3b6` (PR #8 merge)
**Repository:** https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform
**License:** Proprietary / All Rights Reserved (ADR-012 — Copyright (c) 2026 CoachOS Technologies / Ali Naderi)

---

## 1. One-Line Status

The Phase 04 post-merge remediation is **merged and complete**: PR [#8](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/8) was merged into `main` on 2026-08-11T15:20:23Z at merge commit `dd7dea56945d96a6a2d595afb5154b6828c4e3b6`, and all nine `frontend/lib/` files are verified present and tracked on remote `main` (GitHub Contents API + `git ls-tree origin/main`). The files implement exact `fa-IR`/`en-US` locale governance, matching bilingual dictionaries, deterministic Jalali/Gregorian display, Persian normalization, Unicode BiDi isolation, public-only configuration validation, a foundation-only typed API client, and SSR-safe `/sw.js` registration, tracked through narrow `/frontend/lib/` exceptions inside the retained broad `lib/` ignore rule. The remediation is a founder-authorized specification-based reimplementation — not a restoration; provenance and corrections remain recorded in `docs/reports/POST-MERGE-PHASE-04-FRONTEND-REIMPLEMENTATION-REPORT.md` (original Phase 04 report unchanged). **GitHub Actions are still inactive because `.github/workflows/` is absent from `main`; `infra/ci/` definitions are local command references only, not activation evidence. CI workflow activation is the next gated task via its own PR, and Phase 05 remains unstarted awaiting explicit founder authorization after CI activation review.**

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
| **Local Quality-Gate Definitions** | `infra/ci/ci.yml`, `infra/ci/security-scan.yml`, `infra/scripts/check-secrets.sh` | Commands pass locally; GitHub Actions are not active and workflow activation requires a separate PR |
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
| **P04-REMEDIATION** | Missing original `frontend/lib/` source | Medium | **Closed — merged:** PR [#8](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/8) merged 2026-08-11T15:20:23Z at merge commit `dd7dea56945d96a6a2d595afb5154b6828c4e3b6`; all nine `frontend/lib/` files verified tracked on remote `main`. Provenance/correction record: `docs/reports/POST-MERGE-PHASE-04-FRONTEND-REIMPLEMENTATION-REPORT.md`. |
| **CI-ACTIVATION** | GitHub Actions not active | Medium | **Inactive — next gated task:** `.github/workflows/` is absent from `main`. Activation requires a separate post-merge workflow PR creating exactly `.github/workflows/ci.yml` and `.github/workflows/security-scan.yml` from the validated `infra/ci/` definitions, plus visible remote check results as evidence; `infra/ci/` and `infra/scripts/copy-workflows.sh` alone are not activation evidence. |

---

## 5. Next Step

Execute the GitHub Actions activation sequence (Phase 05 stays gated):

1. Merge the docs-only Phase 04 status synchronization PR (PR A) after founder review; do not merge automatically.
2. After PR A is merged, open a separate workflow PR (PR B) creating exactly `.github/workflows/ci.yml` and `.github/workflows/security-scan.yml` from the validated `infra/ci/` definitions, targeting `main`; leave it open for founder review.
3. Treat CI as active only when the workflow files exist on remote `main` and real GitHub check results are visible and passing on a PR — file existence on an unmerged branch is not activation evidence.
4. If pushing workflow files is rejected for missing GitHub Workflows permission, stop and report; the repository owner must reconnect the GitHub integration with Workflows Read & Write permission.
5. Do not start Phase 05 until: PR A is merged, workflow files are present on remote `main`, GitHub Actions checks are visible and passing, `PROJECT_STATUS.md` reflects that evidence, and the founder explicitly authorizes Phase 05.
