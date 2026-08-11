# Phase 04 Foundation Architecture and Decisions — CoachOS

**Document Version:** 1.0.0 (Phase 04 Baseline)  
**Date:** 2026-08-11 (UTC)  
**Status:** Approved Engineering Specification  
**Governing ADRs:** ADR-010, ADR-012, ADR-044, ADR-045, ADR-046, ADR-047, ADR-048, ADR-049  

---

## 1. Scope & Objective

Phase 04 establishes the executable, bilingual, PWA-first, secure monorepo foundation for CoachOS. It transforms the Phase 00–03 specifications into a runnable system scaffolding without prematurely implementing Phase 05+ domain features (Identity, Tenancy, Programs, Exercises, Workout Logging, Messaging, Billing, AI).

### 1.1 In-Scope Deliverables
- **Monorepo Structure:** `frontend/` (Next.js 14), `backend/` (Django 5 + DRF), `infra/` (Docker + scripts), `.github/workflows/` (CI automation), `.env.example`, `docker-compose.yml`.
- **Frontend Scaffolding:** App Router layout with `[locale]` dynamic routing (`fa-IR` and `en-US`), strict CSS logical properties, design tokens (Dark Obsidian `#0B0F17`), error boundary, loading UI, 404 page, and placeholder dashboard routes clearly marked as foundation-only.
- **Bilingual & RTL/LTR Engine:** Dynamic `lang` and `dir` on HTML root, bidirectional text isolation (BiDi), directional icon mirroring rules, Persian search normalization utility, locale persistence, and zero Arabic resources.
- **PWA Baseline:** Web App Manifest (`manifest.json`), 192px/512px maskable icons, Service Worker (`sw.js`) with Cache-First app-shell caching, Network-First navigation with bilingual offline fallback page, network status indicator banner, install guidance modal.
- **Backend Foundation:** Modular environment settings, secure middleware pipeline (Correlation ID, Security Headers, Logging Redaction, Tenant Context placeholder), RFC 7807 problem details error envelopes, UUIDv7 generator utility, `/healthz` (liveness), `/readyz` (DB/Redis readiness), and `/api/v1/meta` (public metadata).
- **Security & Secret Boundaries:** Strict public runtime configuration on frontend (`NEXT_PUBLIC_*` only), zero frontend Secrets Manager access, HttpOnly cookie auth session configuration baseline, CSRF double-submit protection, log scrubbing.
- **CI/CD Quality Gates:** GitHub Actions workflows running linting, type-checking, backend Pytest, frontend Vitest, PWA manifest validation, secret scanning, and explicit no-Arabic verification.
- **Hosting Strategy:** Comprehensive evaluation of PaaS, EU Cloud, Bare VPS, and Dual-Region architectures in `HOSTING_AND_DATA_RESIDENCY_DECISION.md`.

### 1.2 Explicitly Out-of-Scope (Deferred to Phase 05+)
- Real user registration, login, password reset, or OTP flows (Phase 05).
- Tenant organizations, memberships, invitations, or role-permission assignments (Phase 05).
- Exercise library catalog, media rights moderation, or program builder (Phase 06).
- Athlete workout execution, set actuals logging, rest timers, or progress photos (Phase 07).
- Contextual messaging or push notifications (Phase 08).
- Nutritionist role or meal planning (Phase 09).
- Payment gateways (Shetab / Stripe) (Phase 10).
- AI Copilot features (Phase 11).
- Durable IndexedDB offline workout queuing or background synchronization (Phase 12).
- Real production infrastructure provisioning or cloud credentials (Phase 13).

---

## 2. Monorepo Directory Architecture

```
CoachOS-Fitness-Coaching-Platform/
├── frontend/                     # Next.js 14 App Router client application
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
│   ├── docker/                   # Dockerfiles (frontend, backend, redis)
│   └── scripts/                  # Development & verification scripts
├── docs/                         # Architecture, UX, requirements, decisions
│   ├── architecture/             # Architecture specifications
│   ├── reports/                  # Phase execution reports
│   └── ux/                       # UX specifications & design tokens
├── .github/                      # GitHub automation
│   └── workflows/                # CI / security workflows
├── docker-compose.yml            # Local multi-container development orchestration
├── compose.yaml                  # Docker Compose v2 alias
├── .env.example                  # Safe template environment variables
├── .gitignore                    # Git ignore rules
├── LICENSE                       # Proprietary / All Rights Reserved notice
└── README.md                     # Monorepo onboarding & developer guide
```

---

## 3. Technology Baseline & Compatibility Verification

| Component | Target Version | Sandbox / Runtime Version | Status & Notes |
|---|---|---|---|
| **Python** | 3.12 | 3.11.2 (Sandbox) / 3.12 (Production Docker) | Fully compatible; uses standard type hints & async features |
| **Django** | 5.2+ | 5.2.17 | Stable LTS foundation |
| **Django REST Framework** | 3.18+ | 3.18.0 | REST API contract baseline |
| **PostgreSQL** | 16 | 16-alpine (Docker target) | Full `pg_trgm`, `btree_gin`, JSONB support |
| **Redis** | 7 | 7-alpine (Docker target) | In-memory cache, rate limiting, and Celery broker |
| **Node.js** | 22 LTS | v22.22.3 | Modern JavaScript runtime |
| **Next.js** | 14.2+ | 14.2.35 | App Router, SSR, SSG, and standalone build |
| **React** | 18.3+ | 18.3.1 | React Server Components & client hooks |
| **TypeScript** | 5.4+ | 5.4.5 | Strict type checking enabled |
| **Tailwind CSS** | 3.4+ | 3.4.3 | CSS logical properties for RTL/LTR |
| **Testing Tools** | Vitest + Pytest | Vitest 1.6.0, Pytest 9.1.1 | Fast parallel execution |

---

## 4. Architectural Boundaries and Trust Model

### 4.1 Secret Management Boundary
- **Backend & Worker:** Allowed to access environment variables and secret stores (Secrets Manager / KMS in production; `.env` in local development).
- **Frontend / Client Browser:** **Strictly Forbidden** from accessing Secrets Manager or private environment variables. Only public `NEXT_PUBLIC_*` runtime constants are bundled.
- **Secret Scanning:** Automated CI scanner verifies that no AWS keys, private RSA keys, database connection strings, or JWT secrets are present in client bundles or Git commits.

### 4.2 Auth & Session Transport Baseline
- **Recommended MVP Strategy:** Django HttpOnly session cookies (`sessionid`):
  - `HttpOnly: true` (inaccessible to JavaScript, immune to XSS token theft).
  - `Secure: true` in staging and production environments.
  - `SameSite: Lax` for CSRF mitigation during top-level navigation.
  - State-changing mutations (POST, PUT, PATCH, DELETE) require a double-submitted CSRF token (`X-CSRFToken` header matching the readable `csrftoken` cookie).
  - **Explicit Prohibition:** No long-lived authentication or refresh tokens are ever stored in `localStorage` or `sessionStorage`.

---

## 5. Summary of Phase 04 Status
All foundation components are designed to provide a completely isolated, reproducible, and verifiable engineering platform for the upcoming Phase 05 identity and tenancy domain implementation.
