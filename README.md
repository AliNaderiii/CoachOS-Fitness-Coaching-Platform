# CoachOS (working name)

Bilingual, mobile-first fitness coaching operating system for coaches, gyms, and athletes.

> **Product name:** not finalized. Working codename: **CoachOS**.  
> **License:** Proprietary / All Rights Reserved (ADR-012 — Copyright (c) 2026 CoachOS Technologies / Ali Naderi)  
> **Status:** Phase 04 complete — Project Foundation & PWA Baseline. Runnable monorepo with Next.js 14, Django 5, PostgreSQL 16, Redis 7, PWA shell, and bilingual RTL/LTR engine.

---

## 1. Vision and Architecture

CoachOS is a B2B2C SaaS platform that connects training periodization, workout execution, athlete telemetry, coach–athlete communication, and (later) nutrition, monetization, and carefully governed AI assistance.

- **Paying Customers:** Gym organizations and independent strength coaches.
- **Athletes / Clients:** Free/included via coach invitations.
- **Architecture:** Modular monolith with Next.js 14 App Router frontend, Django 5 REST Framework backend, PostgreSQL 16 relational database, Redis 7 task cache/broker, and a PWA-first mobile delivery engine.

---

## 2. Language Policy (Non-Negotiable)

| Locale | Direction | Status |
|---|---|---|
| `fa-IR` (Persian) | RTL | **In scope** (Primary) |
| `en-US` (English) | LTR | **In scope** (International) |
| Arabic and all other languages | — | **Strictly out of scope** (ADR-003) |

---

## 3. Quick Start (Local Development)

### 3.1 Start with Docker Compose
```bash
# 1. Copy template environment variables
cp .env.example .env

# 2. Build and run all services (DB, Redis, Backend, Celery, Frontend)
docker compose up --build
```

### 3.2 Access Services
| Service | URL / Host | Health / Status |
|---|---|---|
| **Frontend PWA** | `http://localhost:3000` | Browse `http://localhost:3000/fa-IR` |
| **Backend REST API** | `http://localhost:8000` | `curl http://localhost:8000/healthz` |
| **API Metadata** | `http://localhost:8000/api/v1/meta` | `curl http://localhost:8000/api/v1/meta` |
| **Readiness Check** | `http://localhost:8000/readyz` | `curl http://localhost:8000/readyz` |

See [`docs/architecture/LOCAL_DEVELOPMENT.md`](./docs/architecture/LOCAL_DEVELOPMENT.md) for direct host (non-Docker) setup.

---

## 4. Running Quality Gates and Tests

### 4.1 Backend Tests & Linting
```bash
cd backend
source .venv/bin/activate
ruff check .
pytest --cov=apps --cov=config
```

### 4.2 Frontend Tests & Linting
```bash
cd frontend
npm run lint
npm run type-check
npm test
```

### 4.3 Security & Arabic Exclusion Scanner
```bash
bash infra/scripts/check-secrets.sh
```

---

## 5. Repository Structure

```
CoachOS-Fitness-Coaching-Platform/
├── frontend/                     # Next.js 14 App Router, TypeScript, PWA, Tailwind CSS
├── backend/                      # Django 5 + DRF, Python 3.12 target, modular settings
├── infra/                        # Dockerfiles, scripts, container configurations
├── docs/                         # Specifications, architecture, UX, reports, threat models
│   ├── architecture/             # Architecture specifications (ADRs, C4, PWA, CI/CD, Hosting)
│   ├── reports/                  # Phase execution reports
│   └── ux/                       # UX design system, wireframes, and design tokens
├── .github/workflows/            # GitHub Actions CI quality gates
├── docker-compose.yml            # Multi-container orchestration
├── .env.example                  # Environment variable template
└── LICENSE                       # Proprietary / All Rights Reserved notice
```

---

## 6. Phase Status

| Phase | Description | Status | Evidence Link |
|---|---|---|---|
| **00** | Discovery & Audit | **Complete** | [`docs/reports/PHASE-00-DISCOVERY-REPORT.md`](./docs/reports/PHASE-00-DISCOVERY-REPORT.md) |
| **01** | Requirements & PRD | **Complete** | [`docs/reports/PHASE-01-REQUIREMENTS-REPORT.md`](./docs/reports/PHASE-01-REQUIREMENTS-REPORT.md) |
| **02** | UX & Design System | **Complete** | [`docs/reports/PHASE-02-UX-DESIGN-REPORT.md`](./docs/reports/PHASE-02-UX-DESIGN-REPORT.md) |
| **03** | Architecture & Security | **Complete** | [`docs/reports/PHASE-03-ARCHITECTURE-REPORT.md`](./docs/reports/PHASE-03-ARCHITECTURE-REPORT.md) |
| **04** | Project Foundation & PWA | **Complete** | [`docs/reports/PHASE-04-FOUNDATION-REPORT.md`](./docs/reports/PHASE-04-FOUNDATION-REPORT.md) |
| **05** | Identity, Tenancy & Roles | **Next** | Awaiting explicit founder authorization |

---

## 7. License & Intellectual Property

Proprietary / All Rights Reserved.  
Copyright (c) 2026 CoachOS Technologies / Ali Naderi. All rights reserved.  
See [`LICENSE`](./LICENSE) and [`docs/DECISIONS.md`](./docs/DECISIONS.md) ADR-012.
