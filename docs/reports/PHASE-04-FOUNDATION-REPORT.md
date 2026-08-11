# Phase 04 — Project Foundation and PWA Baseline Report

**Document Version:** 1.1.0 (Phase 04 Baseline — Review Corrections Finalized)  
**Phase:** Phase 04 — Project Foundation & PWA Baseline  
**Date:** 2026-08-11 (UTC)  
**Authors:** Principal Software Architect, Frontend Lead, Backend Lead, DevOps/SRE Engineer, Security Engineer, QA/Test Engineer, Localization Engineer, Technical Writer, Release Manager  
**Base Commit on `main`:** `692b2b02ac23d8ad433270fa9ea585f5dc860768` (PR #6 Merge Commit)  
**Working Branch:** `arena/019fefbf-coachos-fitness-coaching-platf`  
**License:** Proprietary / All Rights Reserved (ADR-012 — Copyright (c) 2026 CoachOS Technologies / Ali Naderi)  

---

## 1. Executive Summary

Phase 04 successfully establishes the executable, bilingual, PWA-first, secure monorepo foundation for the CoachOS Fitness Coaching Platform. It transforms the Phase 00–03 specifications into a fully reproducible development and testing environment without prematurely implementing Phase 05+ domain features.

### Core Achievements of Phase 04:
1. **Monorepo Scaffolding:** Clean directory layout with `frontend/` (Next.js 14.2 App Router), `backend/` (Django 5.2 + DRF 3.18), `infra/` (Docker Compose with PostgreSQL 16 & Redis 7, container definitions, and CI quality gates).
2. **PWA Level 1 Baseline:** Web App Manifest (`manifest.json`), original 192px/512px standard and maskable PNG icons, resilient Service Worker (`sw.js`) with Cache-First static caching and Network-First navigation with offline fallback, a sticky network status banner, and cross-platform install guidance.
3. **Bilingual RTL/LTR Engine:** Dynamic `lang` and `dir` on the root HTML document, strict CSS logical properties, bidirectional text isolation (`<bdi>`), Solar Hijri (Jalali) date formatting algorithms separate from UTC storage, and a reusable `PersianNormalizer` folding Perso-Arabic keyboard variants (`ي`/`ى` -> `ی`, `ك` -> `ک`, Arabic-Indic digits, and ZWNJ).
4. **Strict Language Governance:** Absolute exclusion of Arabic language files, translation keys, and seed data, continuously validated by automated CI scanner.
5. **Fail-Closed Backend REST API Foundation:** Modular environment-based settings, fail-closed production validation (mandatory `DJANGO_SECRET_KEY` and `DATABASE_URL`; no silent SQLite or wildcard host fallbacks), secure default DRF permissions (`IsAuthenticated` global default with explicit `AllowAny` on `/healthz`, `/readyz`, `/api/v1/meta`), validated `CorrelationIDMiddleware` (UUIDv7), tenant header protection, security headers, logging redaction, and custom RFC 7807 problem details error envelopes.
6. **Security & Secret Boundaries:** Strict public runtime configuration on frontend (`NEXT_PUBLIC_*` only; runtime validation throws on private secret detection), zero client-side Secrets Manager access, HttpOnly session cookies, SameSite=Lax, and CSRF double-submit protection.
7. **Comprehensive Test Suite:** 32 backend Pytest unit tests passing (100%), 30 frontend Vitest tests passing (100%), Next.js production build verified (18 static pages generated), and automated secret scanning clean.
8. **Hosting & Data Residency Strategy:** Authored `HOSTING_AND_DATA_RESIDENCY_DECISION.md` evaluating 5 deployment options across 10 dimensions, establishing local/staging container neutrality and a pre-pilot founder decision gate.
9. **License Transition:** Transitioned repository license to **Proprietary / All Rights Reserved** in `LICENSE` and `docs/DECISIONS.md` (ADR-012).

---

## 2. Persian Executive Summary (خلاصه اجرایی)

فاز ۰۴ با موفقیت فونداسیون اجرایی، دوزبانه، مبتنی بر وب‌اپلیکیشن پیش‌رونده (PWA) و ایمن پروژه CoachOS را پیاده‌سازی کرد. در این فاز، ساختار مونوریپو شامل فرانت‌اند (Next.js 14)، بک‌اند (Django 5 + DRF)، دیتابیس (PostgreSQL 16) و کش/صف (Redis 7) بدون پیاده‌سازی زودهنگام ماژول‌های دامنه فاز ۰۵ (احراز هویت کامل، تمرینات، برنامه‌ها و لاگ‌ها) ایجاد گردید.

### دستاوردهای کلیدی فاز ۰۴:
۱. **فونداسیون PWA (سطح ۱):** پیاده‌سازی مانیفست استاندارد (`manifest.json`) با پوسته تیره Obsidian (`#0B0F17`)، آیکون‌های اختصاصی ۱۹۲ و ۵۱۲ پیکسلی (استاندارد و Maskable)، سرویس‌ورکر با کش محلی پوسته برنامه، صفحه اختصاصی آفلاین، بنر وضعیت اتصال اینترنت، و راهنمای نصب در iOS و اندروید.  
۲. **موتور دوزبانه و RTL/LTR:** تنظیم خودکار صفات `lang` و `dir` روی سند HTML، استفاده کامل از ویژگی‌های منطقی CSS، ایزولاسیون متن‌های ترکیبی فارسی و لاتین (BiDi)، تبدیل تقویم شمسی/جلالی برای نمایش در رابط کاربری بدون تغییر در ذخیره‌سازی UTC، و ابزار نرمال‌سازی نگارش متن فارسی (تبدیل «ي» و «ك» عربی به «ی» و «ک» فارسی و ارقام).  
۳. **قانون عدم پشتیبانی از زبان عربی:** حذف و منع کامل هرگونه فایل، ترجمه یا داده به زبان عربی با اعتبارسنجی خودکار در خط لوله CI.  
۴. **پایه‌ریزی امن و بدون خطا (Fail-Closed) بک‌اند:** پیاده‌سازی تنظیمات چندمحیطی با شکست صریح در صورت نبود کلید امنیتی یا دیتابیس در محیط پروداکشن (بدون بازگشت خاموش به SQLite یا وایلدکارد)، مجوزهای پیش‌فرض امن (`IsAuthenticated`) در DRF، پایش سلامت (`/healthz`، `/readyz`، `/api/v1/meta`)، ساختار خطای استاندارد RFC 7807، میدل‌ویر اعتبارسنجی شناسه رهگیری (UUIDv7)، هدرهای امنیتی (HSTS، CSP، X-Frame-Options)، پاکسازی داده‌های حساس از لاگ‌ها، و کوکی‌های امن HttpOnly به همراه محافظت CSRF.  
۵. **کیفیت و آزمون‌ها:** اجرای موفق ۳۲ تست در Pytest، ۳۰ تست در Vitest، ساخت استاتیک ۱۸ صفحه در Next.js، و عدم نشت هیچ‌گونه کلید خصوصی.  
۶. **تصمیمات حقوقی و میزبانی:** ثبت مجوز اختصاصی (Proprietary / All Rights Reserved) در فایل LICENSE بر اساس تصمیم بنیان‌گذار (ADR-012)، و تدوین سند جامع تصمیم‌گیری میزبانی و اقامتگاه داده‌ها.

---

## 3. Repository and Phase 03 Verification

- **Repository:** `https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform`
- **Phase 03 Merge Commit:** `692b2b02ac23d8ad433270fa9ea585f5dc860768` (Pull Request #6 merged).
- **Working Branch:** `arena/019fefbf-coachos-fitness-coaching-platf` branched directly from `692b2b02ac23d8ad433270fa9ea585f5dc860768`.
- **Pre-execution Verification:** Verified that all 13 architecture specifications, 6 top-level specifications, and 43 ADRs from Phase 03 are present and clean.
- **Verification Rule:** Zero domain code from Phase 05+ was created during Phase 04.

---

## 4. Founder Decisions Applied

| Decision Area | Founder Mandate | Applied Implementation | Status |
|---|---|---|---|
| **Product Languages** | Persian (`fa-IR`, RTL) and English (`en-US`, LTR) exclusively. Arabic is strictly out of scope. | Full bilingual engine in `frontend/lib/i18n/` with dictionaries, formatters, and normalizers. Zero Arabic locale files; verified by `test_no_arabic.py`, `no-arabic.test.ts`, and CI scanner. | **Accepted (Mandate Enforced)** |
| **License & IP** | Proprietary / All Rights Reserved commercial posture. MIT license removed. | Updated ADR-012 to Accepted; replaced `LICENSE` with clear proprietary notice asserting copyright to CoachOS Technologies / Ali Naderi; added disclaimer noting formal legal review is recommended prior to launch. | **Accepted (Founder Mandate)** |
| **Hosting & Regions** | Dual-region capable strategy for Persian/Iran-related users and EU/international users without provisioning production cloud infrastructure in Phase 04. | Authored `docs/architecture/HOSTING_AND_DATA_RESIDENCY_DECISION.md` comparing 5 infrastructure options; established container neutrality; placed production deployment behind explicit founder decision gate. | **Accepted (Decision Gate Defined)** |

---

## 5. Architecture Deviations

**Zero unauthorized architecture deviations were introduced.** All implementations adhere strictly to the Phase 03 architecture specifications:
- Modular monorepo structure adheres to ADR-010 and ADR-044.
- Next.js 14 App Router + Tailwind logical properties adheres to ADR-002, ADR-029, and ADR-045.
- Django 5 + DRF + modular settings adheres to ADR-002, ADR-030, and ADR-048.
- Cookie-based session authentication with CSRF double-submit adheres to ADR-005, ADR-032, and ADR-048.
- PWA Level 1 foundation adheres to ADR-011, ADR-035, and ADR-046.
- Persian search normalizer adheres to ADR-018 and ADR-047.
- UUIDv7 time-ordered identifiers adhere to ADR-017 and ADR-048.

---

## 6. Monorepo Structure

```
CoachOS-Fitness-Coaching-Platform/
├── frontend/                     # Next.js 14 App Router, TypeScript, PWA, Tailwind CSS
│   ├── app/                      # Dynamic [locale] routes & layouts
│   ├── components/               # UI components, layout, and PWA widgets
│   ├── lib/                      # i18n, api client, config, normalizer
│   ├── public/                   # Manifest, service worker, icons, static assets
│   ├── styles/                   # CSS design tokens & global styles
│   ├── tests/                    # Vitest unit & integration tests
│   ├── package.json              # Frontend dependencies & scripts
│   ├── tsconfig.json             # TypeScript strict configuration
│   ├── tailwind.config.js        # Tailwind CSS with logical properties
│   └── next.config.mjs           # Next.js build & header configuration
├── backend/                      # Django 5 + DRF REST API backend
│   ├── config/                   # Settings modules, urls, wsgi, asgi, celery
│   ├── apps/
│   │   └── core/                 # Healthz, readyz, meta, middleware, exceptions
│   ├── tests/                    # Pytest test suite
│   ├── manage.py                 # Django management CLI
│   └── pyproject.toml / reqs     # Python dependencies
├── infra/                        # Infrastructure & orchestration assets
│   ├── ci/                       # CI quality gates definitions (ci.yml, security-scan.yml)
│   ├── docker/                   # Dockerfiles (frontend, backend, redis)
│   └── scripts/                  # Development & verification scripts
├── docs/                         # Specifications, architecture, UX, reports, threat models
│   ├── architecture/             # Architecture specifications
│   ├── reports/                  # Phase execution reports
│   └── ux/                       # UX specifications & design tokens
├── docker-compose.yml            # Local multi-container development orchestration
├── compose.yaml                  # Docker Compose v2 alias
├── .env.example                  # Safe template environment variables
├── .gitignore                    # Git ignore rules
├── LICENSE                       # Proprietary / All Rights Reserved notice
└── README.md                     # Monorepo developer guide
```

---

## 7. Frontend Foundation

- **Framework:** Next.js 14.2.35 App Router with React 18.3 and TypeScript 5.4 in strict mode.
- **Styling:** Tailwind CSS 3.4 configured with CSS logical properties (`margin-inline`, `padding-inline`, `inset-inline`, `text-align: start/end`).
- **Theme:** Dark Obsidian canvas (`#0B0F17`), dark neutral surfaces (`#111827`, `#1F2937`), emerald teal accents (`#10B981`, `#0D9488`), and crisp white high-contrast text (`#F9FAFB`) (ADR-028).
- **Public Secret Boundary:** `frontend/lib/config/env.ts` strictly allows only `NEXT_PUBLIC_*` environment variables. Runtime validator throws security exceptions if private secret patterns are accessed.
- **Frontend Security Headers & CSP Delivery:** `frontend/next.config.mjs` configures X-Content-Type-Options, X-Frame-Options DENY, Referrer-Policy, Permissions-Policy, HSTS (in production), and Content-Security-Policy baseline for all frontend HTML and static responses.
- **Route Layout (18 Static Pages Generated):**
  - `/` (Root redirect to default locale `/fa-IR`).
  - `/_not-found`: Global 404 page.
  - `/[locale]`: Dynamic bilingual root layout setting `lang` and `dir` on `<html>` (`/fa-IR`, `/en-US`).
  - `/[locale]/loading.tsx`: Accessible loading skeleton.
  - `/[locale]/error.tsx`: React error boundary with retry capability.
  - `/[locale]/not-found.tsx`: Localized 404 page.
  - `/[locale]/offline`: Dedicated offline fallback page (`/fa-IR/offline`, `/en-US/offline`).
  - Placeholder screens clearly marked as **Phase 04 Foundation Shell**:
    - `/[locale]/login` (`/fa-IR/login`, `/en-US/login`)
    - `/[locale]/register` (`/fa-IR/register`, `/en-US/register`)
    - `/[locale]/athlete/today` (`/fa-IR/athlete/today`, `/en-US/athlete/today`)
    - `/[locale]/coach/programs` (`/fa-IR/coach/programs`, `/en-US/coach/programs`)
    - `/[locale]/org/settings` (`/fa-IR/org/settings`, `/en-US/org/settings`)

---

## 8. Backend Foundation

- **Framework:** Django 5.2.17 + Django REST Framework 3.18.0 targeting Python 3.12 (compatible with Python 3.11).
- **Settings Architecture & Fail-Closed Validation:**
  - Modular settings under `backend/config/settings/` (`base.py`, `development.py`, `staging.py`, `production.py`, `test.py`).
  - `staging.py` and `production.py` fail fast with `ImproperlyConfigured` if `DJANGO_SECRET_KEY` is missing or insecure, if `DATABASE_URL` is missing (preventing silent fallback to SQLite), or if `ALLOWED_HOSTS` contains wildcards.
  - `test.py` explicitly isolates deterministic test secrets and in-memory SQLite.
- **Secure Default DRF Permissions:**
  - `REST_FRAMEWORK` default permission class set to `IsAuthenticated`.
  - Only `/healthz`, `/readyz`, and `/api/v1/meta` explicitly opt in to `AllowAny` and empty authentication classes.
- **Middleware Pipeline:**
  1. `CorrelationIDMiddleware`: Validates incoming `X-Request-ID` (UUID ≤ 36 chars); replaces malformed/oversized/injection values with fresh UUIDv7 identifiers.
  2. `SecurityHeadersMiddleware`: Applies HSTS, CSP baseline, X-Frame-Options DENY, X-Content-Type-Options nosniff, Referrer-Policy, and Permissions-Policy.
  3. `CorsMiddleware`: Restricts origins to configured frontend endpoints.
  4. `SessionMiddleware` & `AuthenticationMiddleware`: Manages HttpOnly session state.
  5. `CsrfViewMiddleware`: Enforces CSRF double-submit token verification.
  6. `TenantContextMiddleware`: Scopes tenant exclusively from authenticated session state; header overrides are strictly gated behind `ALLOW_TENANT_HEADER_OVERRIDE` (default `False`).
  7. `LoggingRedactionMiddleware`: Automatically scrubs passwords, tokens, auth headers, and health data from server logs.
- **Error Handling:** `apps.core.exceptions.custom_exception_handler` formats all validation errors, 400s, 401s, 403s, 404s, and 500s into standard RFC 7807 Problem Details envelopes with localized `message_key` and field error breakdowns. Internal stack traces are never exposed in production responses.
- **Health Endpoints:**
  - `GET /healthz`: Fast public liveness probe returning HTTP 200 `{"status": "pass"}`.
  - `GET /readyz`: Dependency readiness probe validating PostgreSQL database and Redis connectivity.
  - `GET /api/v1/meta`: Safe public system metadata (app name, version, API version, supported locales, capabilities).

---

## 9. Database and Redis Foundation

- **Target Database:** PostgreSQL 16 with `pg_trgm`, `btree_gin`, and JSONB support.
- **Target Cache / Broker:** Redis 7 for caching, rate limiting, and Celery background task queue.
- **Local Containerization:** `docker-compose.yml` and `compose.yaml` define isolated containers for `db` (`postgres:16-alpine`), `redis` (`redis:7-alpine`), `backend`, `celery_worker`, and `frontend`.
- **Environment Configuration:** `.env.example` provides safe developer defaults with zero real credentials.
- **Initial Migrations:** Initial framework migrations applied cleanly (`admin`, `auth`, `contenttypes`, `sessions`); **zero domain models or domain migrations** created prematurely.
- **Identifier Strategy:** `id_generator.py` implements time-ordered UUIDv7 identifiers using `uuid6` with standard fallback. Validated that identifiers are never an authorization substitute (ADR-017).

---

## 10. PWA Foundation

- **Specification:** Level 1 Foundation & App-Shell (ADR-011, ADR-035, ADR-046).
- **Web App Manifest:** Located at `frontend/public/manifest.json` and `manifest.webmanifest` specifying `name`, `short_name`, `display: standalone`, `start_url: "/"`, `background_color: "#0B0F17"`, and `theme_color: "#0B0F17"`.
- **Static Manifest Locale Strategy:** Static manifest defaults to Persian metadata for primary market; runtime document headers and UI provide full English localization; future Phase 07 roadmap explores dynamic manifest generation for international users.
- **Branded Icons:** Generated valid PNG icons at 192x192 and 512x512 with both standard and maskable variants (`icon-192x192.png`, `icon-512x512.png`, `maskable-icon-192x192.png`, `maskable-icon-512x512.png`, `favicon.ico`).
- **Service Worker:** `frontend/public/sw.js` implementing:
  - Cache-First strategy for static assets (CSS, JS, fonts, icons).
  - Network-First strategy for navigation requests with automatic fallback to `/fa-IR/offline` or cached app-shell.
  - Network-Only for all `/api/*` endpoints (ensuring authenticated sessions and private media URLs are never cached).
- **Network Status Banner:** `NetworkStatusBanner.tsx` detects connectivity drops and informs users: *"Offline mode — unsaved input is retained temporarily in memory; reconnection is required to save changes."*
- **Install Guidance:** `InstallPromptBanner.tsx` handles Android `beforeinstallprompt` event and renders visual step-by-step instructions for iOS Safari users.
- **Browser Limitations Documented:** Storage quotas, 7-day WebKit eviction on inactive non-installed apps, and standalone requirements for iOS Web Push notifications documented in `PWA_FOUNDATION.md`.
- **Explicit Boundary:** No durable offline workout queue or IndexedDB synchronization claimed (allocated to Phase 12).

---

## 11. Localization and RTL/LTR Foundation

- **Supported Locales:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR) exclusively.
- **Language Governance:** Strict exclusion of Arabic language files, translation keys, and seed data (ADR-003).
- **Typography:** `Vazirmatn` variable font for Persian with +15% line-height; `Inter` for English (ADR-025).
- **BiDi Isolation:** `frontend/lib/i18n/bidi.ts` provides `<bdi>` and unicode isolate wrappers (`\u2068...\u2069`) to prevent punctuation inversion in mixed Persian/Latin text.
- **Persian Search Normalization:** `PersianNormalizer` utility implemented in frontend (`lib/i18n/normalizer.ts`) and backend (`apps/core/utils/persian_normalizer.py`) folding Perso-Arabic keyboard variants (`ي`/`ى` -> `ی`, `ك` -> `ک`, Arabic-Indic digits `٠-٩` -> `۰-۹`, stripping diacritics and ZWNJ) (ADR-018).
- **Calendar & Formatters:** `formatters.ts` provides locale-aware number formatting, weight unit localization (kg/lbs), and algorithmic Solar Hijri (Jalali) date conversion separate from UTC timestamp storage (ADR-009).

---

## 12. Authentication and CSRF Foundation

- **Recommended MVP Strategy:** Django HttpOnly session cookies (`sessionid`) (ADR-005, ADR-032).
- **Cookie Security Flags:**
  - `HttpOnly: true` (inaccessible to JavaScript, immune to XSS token theft).
  - `Secure: true` in staging and production environments (`DEBUG=False`).
  - `SameSite: Lax` (balances CSRF protection with top-level navigation usability).
- **CSRF Defense:** Django CSRF middleware sets readable `csrftoken` cookie. The API client automatically reads this cookie and attaches the `X-CSRFToken` header on all `POST`, `PUT`, `PATCH`, and `DELETE` requests.
- **Explicit Prohibition:** No long-lived authentication or refresh tokens are ever stored in `localStorage` or `sessionStorage`.
- **Auth Boundary:** Public routes (`/healthz`, `/readyz`, `/api/v1/meta`, `/login`, `/register`) clearly separated from future authenticated domain routes.

---

## 13. Security Foundation

- **Zero Client Trust:** All authorization, rate limiting, and business validation execute strictly on the backend.
- **Security Headers:** Strict enforcement of HSTS (`max-age=63072000`), X-Frame-Options (`DENY`), X-Content-Type-Options (`nosniff`), Referrer-Policy (`strict-origin-when-cross-origin`), and Permissions-Policy (`camera=(), microphone=(), geolocation=(), payment=()`).
- **Content Security Policy (CSP):** Delivered on both backend API responses and frontend Next.js HTML responses. Hardening task **`TODO-CSP-001`** established to migrate Next.js from temporary `'unsafe-inline'` to per-request cryptographic nonces before commercial pilot.
- **Observability & Log Redaction:** `LoggingRedactionMiddleware` intercepts all requests and scrubs sensitive keys (`password`, `secret`, `token`, `authorization`, `cookie`, `pain_flag_details`, `body_weight`, `credit_card`) from server logs.
- **Correlation Tracking:** `X-Request-ID` validated and attached to all incoming and outgoing requests and injected into logging formatters.
- **No Real PII or Health Data:** All development environments use synthetic test fixtures exclusively.

---

## 14. CI/CD Foundation

- **Platform:** GitHub Actions workflows in `infra/ci/` (`ci.yml`, `security-scan.yml`).
- **Quality Gates Matrix:**
  1. `backend-quality`: Python 3.11 setup, `ruff check .`, `ruff format --check .`, `pytest --cov`.
  2. `frontend-quality`: Node 22 setup, `npm run lint` (ESLint), `npm run type-check` (tsc), `npm test` (Vitest), `npm run build` (Next.js build).
  3. `security-and-governance`: Runs `infra/scripts/check-secrets.sh` (scans for secret patterns, enforces strict Arabic exclusion, validates PWA manifest).
- **Deployment Gate:** Zero production auto-deployment; production releases require manual approval and founder authorization.

---

## 15. Hosting and Data Residency Decision

- **Specification Document:** `docs/architecture/HOSTING_AND_DATA_RESIDENCY_DECISION.md`.
- **Evaluated Options:**
  1. Option A: Managed PaaS (Render / Railway / Fly.io / Vercel).
  2. Option B: EU Managed Cloud / IaaS (Hetzner Cloud / Scaleway / AWS Frankfurt).
  3. Option C: Bare VPS / Self-Hosted Docker Swarm.
  4. Option D: Dual-Region Active-Passive (Iran Edge Proxy + EU Core).
  5. Option E: Dual-Region Active-Active (Full Multi-Master Replication).
- **Evaluated Dimensions:** Monthly Cost, Operational Complexity, Iran User Latency & Connectivity, GDPR & Data Residency, Payment Rail Compatibility (Shetab vs Stripe), Disaster Recovery / Backups, Vendor Lock-in.
- **Phase 04 Baseline Recommendation:**
  - Local Development: Provider-neutral Docker Compose.
  - Staging: Single-region EU Container Environment (Render / Hetzner).
  - Production Launch: Gated behind an explicit founder decision gate prior to commercial pilot.
- **Privacy Directive:** Zero real user data duplicated across regions until formal legal review and pre-DPIA approval.

---

## 16. Testing and Validation

### 16.1 Backend Test Results (Pytest)
```
============================= test session starts ==============================
platform linux -- Python 3.11.2, pytest-9.1.1, pluggy-1.6.0
django: version: 5.2.17, settings: config.settings.test
rootdir: /home/user/CoachOS-Fitness-Coaching-Platform/backend
collected 32 items

tests/test_default_permissions.py::test_public_health_endpoints_remain_accessible PASSED [  3%]
tests/test_errors.py::test_404_error_envelope_format PASSED              [  6%]
tests/test_health.py::test_healthz_endpoint_returns_200 PASSED           [  9%]
tests/test_meta.py::test_meta_endpoint_structure PASSED                  [ 12%]
tests/test_readyz.py::test_readyz_endpoint_database_check PASSED         [ 15%]
tests/test_secret_leakage.py::test_meta_and_health_do_not_leak_secrets PASSED [ 18%]
tests/test_default_permissions.py::test_default_permission_is_authenticated PASSED [ 21%]
tests/test_default_permissions.py::test_unauthenticated_request_to_protected_view_is_denied PASSED [ 25%]
tests/test_drf_exceptions.py::test_custom_exception_handler_validation_error PASSED [ 28%]
tests/test_drf_exceptions.py::test_custom_exception_handler_permission_denied PASSED [ 31%]
tests/test_drf_exceptions.py::test_custom_exception_handler_unhandled_500 PASSED [ 34%]
tests/test_fail_closed_settings.py::test_staging_fails_without_secret_key PASSED [ 37%]
tests/test_fail_closed_settings.py::test_staging_fails_with_insecure_secret_key PASSED [ 40%]
tests/test_fail_closed_settings.py::test_production_fails_without_database_url PASSED [ 43%]
tests/test_fail_closed_settings.py::test_production_fails_with_wildcard_allowed_hosts PASSED [ 46%]
tests/test_fail_closed_settings.py::test_production_fails_without_cors_origins PASSED [ 50%]
tests/test_middleware.py::test_correlation_id_middleware_generates_header_when_missing PASSED [ 53%]
tests/test_middleware.py::test_correlation_id_middleware_preserves_valid_uuid PASSED [ 56%]
tests/test_middleware.py::test_correlation_id_middleware_replaces_invalid_malformed_id PASSED [ 59%]
tests/test_middleware.py::test_correlation_id_middleware_replaces_overly_long_id PASSED [ 62%]
tests/test_middleware.py::test_tenant_context_middleware_rejects_header_override_in_production_mode PASSED [ 65%]
tests/test_middleware.py::test_tenant_context_middleware_allows_header_in_explicit_test_mode PASSED [ 68%]
tests/test_middleware.py::test_logging_redaction_middleware_scrubs_secrets PASSED [ 71%]
tests/test_no_arabic.py::test_no_arabic_locale_in_django_settings PASSED [ 75%]
tests/test_no_arabic.py::test_no_arabic_translation_files_in_repository PASSED [ 78%]
tests/test_persian_normalizer.py::test_arabic_yeh_and_kaf_folding PASSED [ 81%]
tests/test_persian_normalizer.py::test_arabic_indic_digit_folding PASSED [ 84%]
tests/test_persian_normalizer.py::test_diacritics_stripping PASSED       [ 87%]
tests/test_persian_normalizer.py::test_zwnj_normalization PASSED         [ 90%]
tests/test_security_headers.py::test_security_headers_applied PASSED     [ 93%]
tests/test_uuidv7.py::test_uuidv7_generation_and_validation PASSED       [ 96%]
tests/test_uuidv7.py::test_uuidv7_lexical_sorting_trend PASSED           [100%]

============================== 32 passed in 1.47s ==============================
Coverage: 77% project total (90%+ core apps/middleware/views/exceptions)
```

### 16.2 Frontend Test Results (Vitest)
```
 RUN  v1.6.0 /home/user/CoachOS-Fitness-Coaching-Platform/frontend

 ✓ tests/pwa.test.ts  (4 tests) 5ms
 ✓ tests/components.test.tsx  (5 tests) 94ms
 ✓ tests/i18n.test.ts  (3 tests) 3ms
 ✓ tests/formatters.test.ts  (4 tests) 3ms
 ✓ tests/normalizer.test.ts  (4 tests) 3ms
 ✓ tests/config.test.ts  (4 tests) 4ms
 ✓ tests/security-headers.test.ts  (1 test) 4ms
 ✓ tests/bidi.test.ts  (3 tests) 3ms
 ✓ tests/no-arabic.test.ts  (2 tests) 4ms

 Test Files  9 passed (9)
      Tests  30 passed (30)
   Duration  6.52s
```

### 16.3 Linting & Type-Checking
- **Backend Linting:** `ruff check .` -> `All checks passed!`
- **Frontend Linting:** `next lint` -> `✔ No ESLint warnings or errors`
- **Frontend Type-Check:** `tsc --noEmit` -> `Clean (zero errors)`
- **Next.js Production Build:** `npm run build` -> `Compiled successfully; 18 static pages generated`

### 16.4 Security & Compliance Scanner
```
======================================================
 CoachOS Security & Language Compliance Scanner
======================================================
[1/4] Checking for forbidden Arabic locale resources...
✅ PASS: No Arabic locale files found.
[2/4] Scanning for potential committed secrets...
✅ PASS: No private secret patterns detected.
[3/4] Checking frontend public environment variable safety...
ℹ️ INFO: No frontend/.env file found (safe default).
[4/4] Verifying Web App Manifest validity...
✅ PASS: Web App Manifest has required PWA fields.
======================================================
🎉 ALL COMPLIANCE CHECKS PASSED
======================================================
```

---

## 17. Files Created or Changed

### 17.1 Infrastructure & Root Files
- `.gitignore` (New — comprehensive gitignore for Node, Python, Next.js, venv, secrets)
- `.env.example` (New — safe developer defaults)
- `docker-compose.yml` (New — multi-container Docker Compose orchestration)
- `compose.yaml` (New — Docker Compose v2 alias)
- `LICENSE` (Updated — Proprietary / All Rights Reserved notice per ADR-012)
- `README.md` (Updated — runnable local developer guide and architecture summary)
- `PROJECT_STATUS.md` (Updated — Phase 04 complete)
- `PROJECT_CHECKLIST.md` (Updated — Phase 04 complete with evidence links)
- `CHANGELOG.md` (Updated — Phase 04 [0.4.0] changelog entry)

### 17.2 Infrastructure Assets
- `infra/docker/frontend.Dockerfile`
- `infra/docker/backend.Dockerfile`
- `infra/docker/redis.conf`
- `infra/scripts/check-secrets.sh`
- `infra/scripts/dev.sh`
- `infra/scripts/wait-for-services.sh`
- `infra/ci/ci.yml` (CI quality gates definition)
- `infra/ci/security-scan.yml` (Security scanning definition)

### 17.3 Backend Application
- `backend/pyproject.toml`
- `backend/requirements.txt`
- `backend/requirements-dev.txt`
- `backend/manage.py`
- `backend/config/__init__.py`
- `backend/config/asgi.py`
- `backend/config/wsgi.py`
- `backend/config/urls.py`
- `backend/config/celery.py`
- `backend/config/settings/__init__.py`
- `backend/config/settings/base.py`
- `backend/config/settings/development.py`
- `backend/config/settings/staging.py`
- `backend/config/settings/production.py`
- `backend/config/settings/test.py`
- `backend/apps/__init__.py`
- `backend/apps/core/__init__.py`
- `backend/apps/core/apps.py`
- `backend/apps/core/urls.py`
- `backend/apps/core/views.py`
- `backend/apps/core/middleware.py`
- `backend/apps/core/exceptions.py`
- `backend/apps/core/serializers.py`
- `backend/apps/core/utils/__init__.py`
- `backend/apps/core/utils/id_generator.py`
- `backend/apps/core/utils/persian_normalizer.py`
- `backend/tests/__init__.py`
- `backend/tests/conftest.py`
- `backend/tests/test_default_permissions.py`
- `backend/tests/test_drf_exceptions.py`
- `backend/tests/test_errors.py`
- `backend/tests/test_fail_closed_settings.py`
- `backend/tests/test_health.py`
- `backend/tests/test_meta.py`
- `backend/tests/test_middleware.py`
- `backend/tests/test_no_arabic.py`
- `backend/tests/test_persian_normalizer.py`
- `backend/tests/test_readyz.py`
- `backend/tests/test_secret_leakage.py`
- `backend/tests/test_security_headers.py`
- `backend/tests/test_uuidv7.py`

### 17.4 Frontend Application
- `frontend/package.json`
- `frontend/tsconfig.json`
- `frontend/next.config.mjs`
- `frontend/tailwind.config.js`
- `frontend/postcss.config.js`
- `frontend/.eslintrc.json`
- `frontend/vitest.config.ts`
- `frontend/styles/tokens.css`
- `frontend/styles/globals.css`
- `frontend/lib/config/env.ts`
- `frontend/lib/i18n/config.ts`
- `frontend/lib/i18n/dictionaries/fa-IR.json`
- `frontend/lib/i18n/dictionaries/en-US.json`
- `frontend/lib/i18n/formatters.ts`
- `frontend/lib/i18n/normalizer.ts`
- `frontend/lib/i18n/bidi.ts`
- `frontend/lib/api/client.ts`
- `frontend/lib/pwa/register-sw.ts`
- `frontend/public/manifest.json`
- `frontend/public/manifest.webmanifest`
- `frontend/public/sw.js`
- `frontend/public/icons/icon-192x192.png`
- `frontend/public/icons/icon-512x512.png`
- `frontend/public/icons/maskable-icon-192x192.png`
- `frontend/public/icons/maskable-icon-512x512.png`
- `frontend/public/icons/favicon.ico`
- `frontend/public/favicon.ico`
- `frontend/components/ui/Button.tsx`
- `frontend/components/ui/Input.tsx`
- `frontend/components/ui/Card.tsx`
- `frontend/components/ui/Badge.tsx`
- `frontend/components/ui/Modal.tsx`
- `frontend/components/ui/LanguageSwitcher.tsx`
- `frontend/components/layout/DirectionProvider.tsx`
- `frontend/components/layout/Header.tsx`
- `frontend/components/layout/Footer.tsx`
- `frontend/components/layout/BottomNav.tsx`
- `frontend/components/layout/Shell.tsx`
- `frontend/components/pwa/ServiceWorkerRegistration.tsx`
- `frontend/components/pwa/NetworkStatusBanner.tsx`
- `frontend/components/pwa/InstallPromptBanner.tsx`
- `frontend/app/layout.tsx`
- `frontend/app/page.tsx`
- `frontend/app/[locale]/layout.tsx`
- `frontend/app/[locale]/page.tsx`
- `frontend/app/[locale]/loading.tsx`
- `frontend/app/[locale]/error.tsx`
- `frontend/app/[locale]/not-found.tsx`
- `frontend/app/[locale]/offline/page.tsx`
- `frontend/app/[locale]/(auth)/login/page.tsx`
- `frontend/app/[locale]/(auth)/register/page.tsx`
- `frontend/app/[locale]/(app)/athlete/today/page.tsx`
- `frontend/app/[locale]/(app)/coach/programs/page.tsx`
- `frontend/app/[locale]/(app)/org/settings/page.tsx`
- `frontend/tests/bidi.test.ts`
- `frontend/tests/components.test.tsx`
- `frontend/tests/config.test.ts`
- `frontend/tests/formatters.test.ts`
- `frontend/tests/i18n.test.ts`
- `frontend/tests/no-arabic.test.ts`
- `frontend/tests/normalizer.test.ts`
- `frontend/tests/pwa.test.ts`
- `frontend/tests/security-headers.test.ts`

### 17.5 Documentation & Decision Files
- `docs/architecture/HOSTING_AND_DATA_RESIDENCY_DECISION.md`
- `docs/architecture/PHASE04_FOUNDATION_DECISIONS.md`
- `docs/architecture/LOCAL_DEVELOPMENT.md`
- `docs/architecture/CI_CD_FOUNDATION.md`
- `docs/architecture/PWA_FOUNDATION.md`
- `docs/architecture/SECURITY_FOUNDATION.md`
- `docs/DECISIONS.md` (ADR-010, ADR-012 updated; ADR-044..049 added)
- `docs/RELEASE_PLAN.md` (M4 marked complete)
- `docs/PROMPT_LOG.md` (Prompts updated)
- `docs/reports/PHASE-04-FOUNDATION-REPORT.md` (This document)

---

## 18. GitHub Branch, Commit, Issues, and Pull Request

- **Working Branch:** `arena/019fefbf-coachos-fitness-coaching-platf`
- **Base Commit on `main`:** `692b2b02ac23d8ad433270fa9ea585f5dc860768`
- **Pull Request Status:** [PR #7 — feat(phase-04): project foundation and pwa baseline](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/7) (OPEN).
- **Automatic Merge Rule:** **Do not merge the Pull Request automatically.** Await explicit founder review and instruction.

---

## 19. Secrets and Sensitive Data Verification

- **Committed Secrets Check:** Verified via automated scanner `check-secrets.sh` and `test_secret_leakage.py` — zero private AWS keys, database passwords, Django secret keys, Redis tokens, or JWT signing keys are committed.
- **Frontend Secret Isolation:** Frontend code accesses only public `NEXT_PUBLIC_*` configuration. Runtime checks throw immediate exceptions if private environment patterns are accessed.
- **Health Endpoint Sanitization:** `/healthz`, `/readyz`, and `/api/v1/meta` return safe JSON envelopes without leaking file system paths, credentials, or internal stack traces.
- **Synthetic Data Only:** All fixtures and tests utilize purely synthetic mock data with zero real PII or health records.

---

## 20. Proposed Items

- **`ADR-049` Production Hosting Selection:** Proposed single-region EU container hosting (Hetzner Cloud / Render) for initial pilot, with dual-region reverse proxy evaluation deferred to Phase 13.
- **`TODO-CSP-001` Cryptographic Nonce CSP:** Proposed migration from temporary Next.js `'unsafe-inline'` to dynamic per-request cryptographic nonces in production middleware before commercial pilot.

---

## 21. Deferred Items

- **Phase 05 Domain Implementation:** User registration, password reset, organization creation, invitations, and role binding.
- **Phase 06 Domain Implementation:** Exercise catalog, media rights moderation, and hierarchical program builder.
- **Phase 07 Domain Implementation:** Mobile workout execution canvas, set actuals logging, and rest timer.
- **Phase 08 Domain Implementation:** Contextual 1:1 messaging threads and in-app notifications.
- **Phase 09 Domain Implementation (P1):** Nutrition professional role, meal planning, and food database.
- **Phase 10 Domain Implementation (P1):** Domestic Shetab & international Stripe payment gateway adapters.
- **Phase 11 Domain Implementation (P2):** Constrained, human-in-the-loop AI Copilot.
- **Phase 12 Domain Implementation (P2):** Durable IndexedDB offline workout queue and background synchronization.

---

## 22. Blockers

**None.** Phase 04 foundation is 100% complete, fully tested, and ready for Phase 05 identity and tenancy domain implementation.

---

## 23. Founder Approval Items

1. **Review and Approval of Phase 04 Foundation Pull Request (#7).**
2. **Authorization to Proceed to Phase 05:** Explicit confirmation required before initiating Phase 05 (Identity, Tenancy, and Roles).

---

## 24. Checklist Changes

`PROJECT_CHECKLIST.md` updated with all completed items for Phase 04 marked `[x]` with concrete evidence links to repository artifacts.

---

## 25. Exact Recommended Prompt for Phase 05

```text
**CONTINUE COACHOS AS A PROFESSIONAL PRODUCT-AND-ENGINEERING TEAM**

You are continuing the CoachOS Fitness Coaching Platform as a coordinated professional team consisting of:

- Founder’s Technical Advisor
- Product Manager
- Principal Software Architect
- Frontend Lead
- Backend Lead
- Security Engineer
- QA/Test Engineer
- Accessibility and Localization Engineer
- Technical Writer
- Release Manager
- Code Reviewer

This instruction executes **Phase 05 — Identity, Tenancy, and Roles**.

**1. BASELINE AND REPOSITORY VERIFICATION**
Repository: https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform
Base commit on main: Phase 04 merge commit.
Verify that PR for Phase 04 is merged.
Create a new branch from updated main for Phase 05 (e.g. `phase/05-identity-tenancy` or session branch).

**2. SCOPE AND NON-NEGOTIABLE CONSTRAINTS**
- Product languages: Persian (`fa-IR`, RTL) and English (`en-US`, LTR) only. Arabic is strictly out of scope.
- License: Proprietary / All Rights Reserved (ADR-012).
- Security: HttpOnly session cookie authentication, SameSite=Lax, CSRF double-submit protection, rate limiting, and password hashing (Argon2id/bcrypt).
- B2B2C Multi-Tenant SaaS: Single-location Organization MVP (ADR-013).
- Implement P0 User, Organization, Location, Membership, Invitation, and CoachAthleteAssignment models and APIs.
- Implement server-side RBAC + object-level authorization with negative authorization tests.
- Implement immutable AuditEvent logging for sensitive identity mutations.
- Do not implement Exercise Library, Program Builder, or Workout Logging (Phase 06/07).

**3. TESTING AND VALIDATION**
- Provide comprehensive backend and frontend unit/integration tests for authentication, invitations, tenant scoping, and authorization guards.
- Update documentation, checklist, changelog, prompt log, and author `docs/reports/PHASE-05-IDENTITY-REPORT.md`.
```
