# Project Status — CoachOS

**Last updated:** 2026-08-10 (UTC)  
**Current phase:** Phase 00 — Discovery and Repository Audit (**complete**)  
**Next phase:** Phase 01 — Product Requirements and Scope  
**Working branch:** `arena/019febc6-coachos-fitness-coaching-platf`  
**Base commit (main):** `a6283e8fa75414f9b47a0e40248f833b6438c0f8`  
**Repository:** https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform  
**License:** MIT  

---

## 1. One-line status

Greenfield repository audited; product vision, language constraints, MVP direction, risks, and Phase 00 report recorded. **No application code exists yet.**

## 2. What exists today

| Area | State |
|------|--------|
| Application source (frontend/backend) | None |
| Dependencies / lockfiles | None |
| Database migrations | None |
| Tests | None |
| CI/CD | None |
| Deployment config | None |
| Docker / compose | None |
| Issue tracker / milestones | Created: milestones 1–9; issues #1 (Phase 01), #2 (Phase 00). Bot cannot PATCH/close issues (403) |
| Documentation (Phase 00) | Created — see section 4 |
| LICENSE | MIT (pre-existing) |
| README | Replaced stub with project overview |

## 3. Active constraints

1. **Languages:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR) **only**.  
2. **Arabic is explicitly out of scope** — no Arabic UI, locale, seed data, or requirements.  
3. **No marketplace, advanced AI, wearables, or medical claims** in early phases.  
4. **AI is a copilot** with human review — not an autonomous authority.  
5. **B2B2C SaaS:** coaches/gyms pay; athletes included.  
6. **Modular monolith** preferred for MVP; microservices require ADR justification.  
7. **No third-party proprietary exercise media** without clear rights/provenance.  
8. **No secrets or real health data** in the repository.

## 4. Documentation inventory (Phase 00)

- `README.md`
- `PROJECT_STATUS.md` (this file)
- `PROJECT_CHECKLIST.md`
- `CHANGELOG.md`
- `docs/MASTER_PRODUCT_BRIEF.md`
- `docs/PRD.md` (outline; full PRD in Phase 01)
- `docs/DECISIONS.md`
- `docs/SECURITY_AND_PRIVACY.md`
- `docs/DATA_MODEL.md` (outline)
- `docs/API_CONTRACT.md` (outline)
- `docs/TRACEABILITY_MATRIX.md` (started)
- `docs/RELEASE_PLAN.md`
- `docs/PROMPT_LOG.md`
- `docs/reports/PHASE-00-DISCOVERY-REPORT.md`
- Placeholders under `docs/architecture/`, `docs/ux/`, `docs/testing/`

## 5. Proposed P0 MVP (high level)

See `docs/MASTER_PRODUCT_BRIEF.md` and `docs/RELEASE_PLAN.md` for detail.

1. Auth + org tenancy + RBAC/object permissions + invitations  
2. fa-IR / en-US language switcher and true RTL/LTR  
3. Exercise library (i18n, search, media rights metadata)  
4. Program builder → assign → athlete log  
5. Messaging + in-app notifications  
6. Admin moderation + audit log + basic analytics  
7. Privacy baseline (consent hooks, export/deletion design)

## 6. Proposed stack (not yet scaffolded)

- **Frontend:** Next.js + React + TypeScript + PWA direction  
- **Backend:** Django + DRF + PostgreSQL  
- **Jobs:** Redis + Celery  
- **Media:** S3-compatible + signed URLs  
- **CI:** GitHub Actions  

Final confirmation and ADRs in Phase 03; scaffolding in Phase 04.

## 7. Risks and unknowns

| ID | Risk / unknown | Severity | Mitigation direction |
|----|----------------|----------|----------------------|
| R01 | No product legal name / brand assets | Low | Continue with CoachOS codename |
| R02 | Auth channel choice (email vs phone/OTP) undecided | Medium | Decide in Phase 01/05; default email+password + optional OTP later |
| R03 | Payment gateway and Iran/international constraints | High (P1) | Abstract payments; defer to Phase 10 |
| R04 | Exercise media rights and original content production | High | Schema supports provenance; seed only permitted content |
| R05 | Health-data regulatory classification (jurisdiction) | High | Privacy design + legal counsel TODO; not medical device |
| R06 | Persian typography, digits, Jalali calendar expectations | Medium | Design system + i18n strategy in Phases 02–04 |
| R07 | Low-bandwidth / offline conflict resolution complexity | Medium | Limit offline scope in Phase 12 |
| R08 | Bot cannot update/close GitHub issues (403); create works | Low | Markdown backlog canonical; manual close optional |
| R09 | Empty repo — all velocity is greenfield | Info | Standard phased delivery |
| R10 | Multi-professional athlete profile complexity | Medium | Model early; UI in later phases |

## 8. Blockers

None blocking Phase 01. GitHub milestones 1–9 and issues #1–#2 created; issue update/close restricted for bot. In-repo backlog remains canonical.

## 9. Immediate next step

Execute **Phase 01 — Product Requirements and Scope**:

- Personas, journeys, P0 user stories, acceptance criteria  
- NFR list  
- Expand PRD and traceability matrix  
- Commit `docs/reports/PHASE-01-REQUIREMENTS-REPORT.md`

**Exact next recommended prompt:**

> Execute Phase 01 — Product Requirements and Scope. Produce personas, user journeys, P0 MVP user stories with acceptance criteria, P1/P2 backlog, non-functional requirements, update PRD and traceability matrix, and commit the Phase 01 report. Do not scaffold application code. Persian and English only; Arabic remains out of scope.

## 10. Team operating mode

This project is executed as a multi-role product-and-engineering team (strategy, PM, architecture, UX, backend, frontend, security, QA, DevOps, tech writing, code review). Scope is controlled by phase gates; incomplete work is labeled mocked/deferred/blocked explicitly.
