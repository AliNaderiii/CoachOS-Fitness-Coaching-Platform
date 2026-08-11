# Local Development Guide — CoachOS

**Document Version:** 1.0.0 (Phase 04 Baseline)  
**Date:** 2026-08-11 (UTC)  
**Target Environment:** Local Developer Workstation & CI Containers  

---

## 1. Overview

CoachOS is structured as a modular monorepo containing:
- **Frontend:** Next.js 14 App Router, TypeScript, Tailwind CSS, Service Worker PWA (`/frontend`).
- **Backend:** Django 5 + Django REST Framework, Python 3.12 target (`/backend`).
- **Data & Queue:** PostgreSQL 16, Redis 7 (`compose.yaml`).

---

## 2. Prerequisites

| Tool | Recommended Version | Purpose |
|---|---|---|
| **Docker & Docker Compose** | Docker 24+ & Compose v2+ | Containerized local dependencies |
| **Node.js** | Node 22.x LTS (or 20.x+) | Frontend development & Next.js tooling |
| **Python** | Python 3.11+ / 3.12 | Backend development & Pytest suite |
| **Git** | 2.40+ | Version control |

---

## 3. Quick Start (Docker Compose — Recommended)

### 3.1 Clone & Setup Environment
```bash
# Clone the repository
git clone https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform.git
cd CoachOS-Fitness-Coaching-Platform

# Copy template environment variables
cp .env.example .env
```

### 3.2 Start All Services
```bash
# Build and start PostgreSQL, Redis, Backend API, Celery Worker, and Next.js Frontend
docker compose up --build
```

### 3.3 Verify Running Services
| Service | URL / Port | Purpose | Health Check |
|---|---|---|---|
| **Frontend Web App** | `http://localhost:3000` | Next.js Bilingual PWA | Browse `http://localhost:3000` |
| **Backend API** | `http://localhost:8000` | Django REST Framework | `curl http://localhost:8000/healthz` |
| **API Metadata** | `http://localhost:8000/api/v1/meta` | System metadata | `curl http://localhost:8000/api/v1/meta` |
| **Readiness Check** | `http://localhost:8000/readyz` | DB & Redis health | `curl http://localhost:8000/readyz` |
| **PostgreSQL 16** | `localhost:5432` | Relational database | `pg_isready -h localhost -p 5432` |
| **Redis 7** | `localhost:6379` | Cache & task broker | `redis-cli -p 6379 ping` |

---

## 4. Native Local Development (Without Docker)

If you prefer to run services directly on your host machine:

### 4.1 Backend Setup (Python 3.11 / 3.12)
```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Run migrations (initial foundation)
python manage.py migrate

# Start development server
python manage.py runserver 0.0.0.0:8000
```

### 4.2 Frontend Setup (Node 22 / Next.js)
```bash
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

---

## 5. Running Tests and Quality Gates

### 5.1 Backend Tests (Pytest)
```bash
cd backend
source .venv/bin/activate

# Run all backend unit and integration tests
pytest

# Run tests with coverage report
pytest --cov=apps --cov=config --cov-report=term-missing
```

### 5.2 Frontend Tests (Vitest)
```bash
cd frontend

# Run unit tests
npm test

# Run tests in watch mode
npm run test:watch
```

### 5.3 Linting and Type Checking
```bash
# Backend linting
cd backend
ruff check .
ruff format --check .

# Frontend linting & type checking
cd frontend
npm run lint
npm run type-check
```

### 5.4 Cross-Cutting Security & Boundary Checks
```bash
# Run security & Arabic exclusion check script
bash infra/scripts/check-secrets.sh
```

---

## 6. Environment Variables Reference

| Variable | Description | Safe Developer Default |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | Active Django settings module | `config.settings.development` |
| `DJANGO_SECRET_KEY` | Development-only Django secret key | `django-insecure-dev-key-phase04-testing-only` |
| `DEBUG` | Enable debug mode (local only!) | `True` |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://coachos:coachos_dev_pw@localhost:5432/coachos_db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Celery task queue broker | `redis://localhost:6379/1` |
| `CORS_ALLOWED_ORIGINS` | Permitted frontend origins | `http://localhost:3000,http://127.0.0.1:3000` |
| `NEXT_PUBLIC_API_BASE_URL` | Public backend API URL for client | `http://localhost:8000` |
| `NEXT_PUBLIC_APP_NAME` | Client public application name | `CoachOS` |
| `NEXT_PUBLIC_SENTRY_DSN_PUBLIC` | Public frontend Sentry DSN | `""` (empty for local) |

---

## 7. Troubleshooting

- **Database Connection Error on `/readyz`:** Ensure PostgreSQL is running on port 5432 and credentials match `DATABASE_URL`.
- **Redis Connection Error on `/readyz`:** Ensure Redis server is active on port 6379.
- **PWA Service Worker Registration:** Service Workers require `localhost` or an `HTTPS` origin to register. If testing in private/incognito mode, check browser Service Worker permissions.
- **RTL Layout Verification:** Switch language to Persian (`فارسی`) in the header or browse `http://localhost:3000/fa-IR` to verify right-to-left layout reflow.
