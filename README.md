# CoachOS (working name)

Bilingual, mobile-first fitness coaching operating system for coaches, gyms, and athletes.

> **Product name:** not finalized. Working codename: **CoachOS**.  
> **License:** MIT (Review Pending Founder Decision — see `docs/DECISIONS.md` ADR-012)  
> **Status:** Phase 01 complete — Product Requirements and Scope. No application code yet.

## Vision

CoachOS is a B2B2C SaaS platform that connects training programming, athlete logging, progress tracking, coach–athlete communication, and (later) nutrition, billing, and carefully governed AI assistance.

**Paying customers:** coaches, gyms, and professional teams.  
**Athletes/clients:** free or included in the coach’s plan.

Long-term differentiation:

- Shared athlete profile with permissioned multi-professional collaboration
- Excellent **Persian (`fa-IR`, RTL)** and **English (`en-US`, LTR)** support
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
| 00 | Discovery and Repository Audit | **Complete** (PR #3 merged) |
| 01 | Product Requirements and Scope | **Complete** |
| 02 | UX, Information Architecture, and Design System | Next |
| 03–14 | See [`PROJECT_CHECKLIST.md`](./PROJECT_CHECKLIST.md) | Not started |

## Repository state

This repository is currently in the documentation and requirements engineering stage:

- PR #3 merged into `main` (commit `f52c4134087b18c4bd1a8aef9e0100fd63f71b8e`)
- Phase 01 complete on working branch `arena/019febfc-coachos-fitness-coaching-platf`
- No application source, dependencies, CI, tests, or deployment config (by design)
- Complete Product Requirements Package authored in `docs/`

## Documentation map

| Document | Purpose |
|----------|---------|
| [`PROJECT_STATUS.md`](./PROJECT_STATUS.md) | Living project status |
| [`PROJECT_CHECKLIST.md`](./PROJECT_CHECKLIST.md) | Phase checklist with evidence |
| [`CHANGELOG.md`](./CHANGELOG.md) | Human-readable change log |
| [`docs/MASTER_PRODUCT_BRIEF.md`](./docs/MASTER_PRODUCT_BRIEF.md) | Product vision and principles |
| [`docs/PRD.md`](./docs/PRD.md) | Full product requirements document (P0 stories, ACs, NFRs) |
| [`docs/PERSONAS.md`](./docs/PERSONAS.md) | 6 comprehensive user personas |
| [`docs/USER_JOURNEYS.md`](./docs/USER_JOURNEYS.md) | 5 end-to-end user journeys |
| [`docs/DOMAIN_GLOSSARY.md`](./docs/DOMAIN_GLOSSARY.md) | Bilingual domain terminology glossary (English & Persian) |
| [`docs/COMPETITIVE_LANDSCAPE.md`](./docs/COMPETITIVE_LANDSCAPE.md) | Competitive benchmarking (10 platforms) & differentiation |
| [`docs/DECISIONS.md`](./docs/DECISIONS.md) | Architecture and product decision log (ADRs) |
| [`docs/DATA_MODEL.md`](./docs/DATA_MODEL.md) | Conceptual and logical domain entity models |
| [`docs/API_CONTRACT.md`](./docs/API_CONTRACT.md) | Versioned REST API specifications and error contracts |
| [`docs/SECURITY_AND_PRIVACY.md`](./docs/SECURITY_AND_PRIVACY.md) | Security baseline, data classification taxonomy, and privacy lifecycle |
| [`docs/TRACEABILITY_MATRIX.md`](./docs/TRACEABILITY_MATRIX.md) | End-to-end requirements traceability matrix |
| [`docs/RELEASE_PLAN.md`](./docs/RELEASE_PLAN.md) | Phased release plan and milestone backlogs |
| [`docs/PROMPT_LOG.md`](./docs/PROMPT_LOG.md) | Founder/agent prompt history |
| [`docs/reports/PHASE-00-DISCOVERY-REPORT.md`](./docs/reports/PHASE-00-DISCOVERY-REPORT.md) | Phase 00 completion report |
| [`docs/reports/PHASE-01-REQUIREMENTS-REPORT.md`](./docs/reports/PHASE-01-REQUIREMENTS-REPORT.md) | Phase 01 completion report |

## Proposed technical stack (pending Phase 03 confirmation)

| Layer | Preferred choice | Notes |
|-------|------------------|-------|
| Frontend | React / Next.js + TypeScript | Coach desktop + athlete mobile-first PWA |
| Backend | Django + Django REST Framework | Modular monolith, strong auth/admin/ORM |
| Database | PostgreSQL 16 | Primary system of record (pg_trgm for search) |
| Jobs | Redis 7 + Celery | Async email, notifications, exports |
| Media | S3-compatible object storage | Signed URLs; rights metadata required |
| API docs | OpenAPI (DRF spectacular or equivalent) | API-first |
| PWA | Web App Manifest + Service Worker | Phase 04 shell, Phase 07 mobile, Phase 12 sync |
| Tests | Pytest, frontend unit/component, Playwright E2E | RTL and LTR visual testing |
| CI | GitHub Actions | Lint, typecheck, security scanning |
| Architecture | Modular monolith | No microservices for MVP |

## MVP (P0) summary

1. Identity, organizations/tenancy, roles, invitations (single-location MVP)  
2. Bilingual UI (`fa-IR` RTL / `en-US` LTR) with Persian font (`Vazirmatn`)  
3. Exercise library with i18n names, Persian search normalization, and media rights metadata  
4. Training program builder, templates, version snapshots, assignment  
5. Athlete today-view, mobile set logging, rest timer, pain/fatigue feedback  
6. Coach–athlete messaging and in-app notifications  
7. Admin moderation, immutable audit events, basic analytics  
8. Security/privacy baseline (export/deletion design, consent hooks)  
9. PWA foundation (Web App Manifest, installable shell)

**Out of MVP:** Arabic locale, marketplace, payments, nutrition professional workflows, wearables, advanced AI, native apps.

## Security notice

- Never commit secrets, production credentials, or real personal health data.
- Treat body composition, injury notes, nutrition, sleep, and progress photos as sensitive.
- See [`docs/SECURITY_AND_PRIVACY.md`](./docs/SECURITY_AND_PRIVACY.md).

## License

MIT — see [`LICENSE`](./LICENSE). Copyright (c) 2026 Ali Naderi. (Review pending founder approval per ADR-012).
