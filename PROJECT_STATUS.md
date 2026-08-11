# Project Status — CoachOS

**Last updated:** 2026-08-11 (UTC)  
**Current phase:** Phase 04 — Project Foundation and PWA Baseline (**complete**)  
**Next phase:** Phase 05 — Identity, Tenancy, and Roles (awaiting explicit founder instruction)  
**Working branch:** `arena/019fefbf-coachos-fitness-coaching-platf`  
**Base commit (main):** `692b2b02ac23d8ad433270fa9ea585f5dc860768` (PR #6 merged)  
**Repository:** https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform  
**License:** Proprietary / All Rights Reserved (ADR-012 — Copyright (c) 2026 CoachOS Technologies / Ali Naderi)

---

## 1. One-Line Status

Phase 04 foundation complete: Modular monorepo established (`frontend/` Next.js 14 App Router + `backend/` Django 5 DRF + `infra/` Docker Compose + CI quality gates), runnable bilingual PWA shell (`fa-IR` RTL / `en-US` LTR with dynamic HTML attributes and zero Arabic resources), Web App Manifest + Service Worker app-shell caching with offline fallback page, 37 backend Pytest tests passing (100%), 32 frontend Vitest tests passing (100%), Next.js production build verified (18 static pages generated), fail-closed secret, DB, host, CSRF, and Redis/Celery configuration (no silent SQLite or localhost Redis fallback, mandatory `DJANGO_SECRET_KEY`, `DATABASE_URL`, `CSRF_TRUSTED_ORIGINS`, `REDIS_URL`, and `CELERY_BROKER_URL`), secure default DRF permissions (`IsAuthenticated` global default with explicit `AllowAny` on `/healthz`, `/readyz`, `/api/v1/meta`), environment-specific CSP (development HMR vs production script-src without `unsafe-eval`), validated `CorrelationIDMiddleware` (UUIDv7), tenant header protection (`ALLOW_TENANT_HEADER_OVERRIDE=False`), security headers, logging redaction, strict frontend secret boundary (`NEXT_PUBLIC_*` only), ADR-012 Proprietary license applied, and comprehensive Hosting & Data Residency evaluation documented with pre-pilot decision gate. **Zero Phase 05 domain features (users, orgs, programs, workouts) created prematurely — foundation only.**

---

## 2. Phase 04 Implementation Summary

| Area | Implemented Artifacts | Verification / Tests |
|---|---|---|
| **Monorepo Architecture** | `frontend/`, `backend/`, `infra/`, `docker-compose.yml`, `compose.yaml`, `.env.example`, `.gitignore` | Local development verified via Docker & direct runtime |
| **Frontend Shell** | Next.js 14.2 App Router, TypeScript strict, Tailwind logical CSS, dark obsidian theme (`#0B0F17`), placeholder dashboard screens clearly marked as foundation-only | 32 Vitest tests passing; Next.js static build verified (18 static pages generated) |
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
| **CI/CD Quality Gates** | `infra/ci/ci.yml`, `infra/ci/security-scan.yml`, `infra/scripts/check-secrets.sh` | Lint (Ruff + ESLint), Type-check (tsc), Unit tests (Vitest + Pytest), Secret scanning, Arabic exclusion |
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

---

## 5. Next Step

Phase 04 complete + all review corrections applied. Standing by for explicit founder instruction to begin:
**Phase 05 — Identity, Tenancy, and Roles**
- Do not start Phase 05 automatically.
- Await explicit founder instruction.
- Next phase will implement User model, single-location Organization tenancy, secure invitation tokens, session authentication, and server-side RBAC/ABAC authorization tests.
