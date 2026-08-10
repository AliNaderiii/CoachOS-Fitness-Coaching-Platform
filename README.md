# CoachOS (working name)

Bilingual, mobile-first fitness coaching operating system for coaches, gyms, and athletes.

> **Product name:** not finalized. Working codename: **CoachOS**.  
> **License:** MIT  
> **Status:** Phase 00 complete — discovery and repository audit. No application code yet.

## Vision

CoachOS is a B2B2C SaaS platform that connects training programming, athlete logging, progress tracking, coach–athlete communication, and (later) nutrition, billing, and carefully governed AI assistance.

**Paying customers:** coaches, gyms, and professional teams.  
**Athletes/clients:** free or included in the coach’s plan.

Long-term differentiation:

- Shared athlete profile with permissioned multi-professional collaboration
- Excellent **Persian (fa-IR, RTL)** and **English (en-US, LTR)** support
- Localized training and nutrition content
- Low-bandwidth and PWA-first delivery
- Coach business tools and monetization
- Safe, explainable, human-reviewed AI assistance
- Strong data ownership, consent, and portability

## Language policy (non-negotiable)

| Locale | Direction | Status |
|--------|-----------|--------|
| `fa-IR` (Persian) | RTL | In scope |
| `en-US` (English) | LTR | In scope |
| Arabic and all other languages | — | **Out of scope** until explicitly requested |

Do not add Arabic translation, locale, seed data, or UI. Architecture may remain extensible for future locales.

## Current phase

| Phase | Name | Status |
|-------|------|--------|
| 00 | Discovery and Repository Audit | **Complete** |
| 01 | Product Requirements and Scope | Next |
| 02–14 | See [`PROJECT_CHECKLIST.md`](./PROJECT_CHECKLIST.md) | Not started |

## Repository state (as of Phase 00)

This repository was a **greenfield** GitHub project:

- Initial commit only (`LICENSE` + stub `README.md`)
- No application source, dependencies, CI, tests, or deployment config
- No prior architecture to preserve or migrate

All product documentation in this tree was created during Phase 00.

## Documentation map

| Document | Purpose |
|----------|---------|
| [`PROJECT_STATUS.md`](./PROJECT_STATUS.md) | Living project status |
| [`PROJECT_CHECKLIST.md`](./PROJECT_CHECKLIST.md) | Phase checklist with evidence |
| [`CHANGELOG.md`](./CHANGELOG.md) | Human-readable change log |
| [`docs/MASTER_PRODUCT_BRIEF.md`](./docs/MASTER_PRODUCT_BRIEF.md) | Product vision and principles |
| [`docs/PRD.md`](./docs/PRD.md) | Product requirements (stub → Phase 01) |
| [`docs/DECISIONS.md`](./docs/DECISIONS.md) | Architecture and product decision log (ADRs) |
| [`docs/DATA_MODEL.md`](./docs/DATA_MODEL.md) | Domain model (Phase 03) |
| [`docs/API_CONTRACT.md`](./docs/API_CONTRACT.md) | API strategy and contracts (Phase 03+) |
| [`docs/SECURITY_AND_PRIVACY.md`](./docs/SECURITY_AND_PRIVACY.md) | Security and privacy baseline |
| [`docs/TRACEABILITY_MATRIX.md`](./docs/TRACEABILITY_MATRIX.md) | Requirements ↔ evidence |
| [`docs/RELEASE_PLAN.md`](./docs/RELEASE_PLAN.md) | Phased release plan |
| [`docs/PROMPT_LOG.md`](./docs/PROMPT_LOG.md) | Founder/agent prompt history |
| [`docs/reports/`](./docs/reports/) | Phase completion reports |

## Proposed technical stack (pending Phase 03 confirmation)

| Layer | Preferred choice | Notes |
|-------|------------------|-------|
| Frontend | React / Next.js + TypeScript | Coach desktop + athlete mobile-first PWA |
| Backend | Django + Django REST Framework | Modular monolith, strong auth/admin/ORM |
| Database | PostgreSQL | Primary system of record |
| Jobs | Redis + Celery | Async email, notifications, exports |
| Media | S3-compatible object storage | Signed URLs; rights metadata required |
| API docs | OpenAPI (DRF spectacular or equivalent) | API-first |
| PWA | Web App Manifest + Service Worker | Offline workout logging (later phase) |
| Tests | Pytest, frontend unit/component, Playwright E2E | |
| CI | GitHub Actions | |
| Architecture | Modular monolith | No microservices for MVP |

Alternatives (e.g. FastAPI) require a written ADR before adoption.

## MVP (P0) summary

1. Identity, organizations/tenancy, roles, invitations  
2. Bilingual UI (fa-IR RTL / en-US LTR)  
3. Exercise library with i18n names and media rights metadata  
4. Training program builder, templates, assignment  
5. Athlete today-view, workout logging, adherence  
6. Coach–athlete messaging and in-app notifications  
7. Admin moderation, audit events, basic analytics  
8. Security/privacy baseline (export/deletion design, consent hooks)

**Out of MVP:** marketplace, payments, nutrition professional workflows, wearables, advanced AI, native apps, Arabic.

## Local development

Application scaffolding is **not** present yet. It will be added in **Phase 04 — Project Foundation**.

After Phase 04, this section will document:

- Prerequisites (Node, Python, PostgreSQL, Redis, Docker optional)
- Environment variables (via `.env.example` only — never commit secrets)
- `make` / script targets for migrate, run, test, lint
- Health-check endpoints

## Security notice

- Never commit secrets, production credentials, or real personal health data.
- Treat body composition, injury notes, nutrition, sleep, and progress photos as sensitive.
- See [`docs/SECURITY_AND_PRIVACY.md`](./docs/SECURITY_AND_PRIVACY.md).

## Contributing / workflow

1. Read `PROJECT_STATUS.md` and `PROJECT_CHECKLIST.md` before starting work.  
2. Work on the active session branch or a documented feature branch policy.  
3. Prefer small, reviewable commits: `type(scope): imperative description`.  
4. Update docs, checklist, and changelog with every meaningful change.  
5. Do not mark work complete without tests and evidence.

## License

MIT — see [`LICENSE`](./LICENSE). Copyright (c) 2026 Ali Naderi.
