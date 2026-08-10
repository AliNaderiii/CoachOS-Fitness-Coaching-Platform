# Phase 00 — Discovery and Repository Audit

## 1. Executive Summary

CoachOS starts from a **greenfield** GitHub repository containing only an MIT license and a one-line README stub. There is **no application code**, dependency manifest, test suite, CI/CD pipeline, or deployment configuration to preserve or migrate.

Phase 00 established the product vision, non-negotiable **Persian (`fa-IR`, RTL) + English (`en-US`, LTR)** language policy with **Arabic explicitly out of scope**, initial role and MVP boundaries, risk register, proposed modular-monolith architecture (Next.js + Django/DRF + PostgreSQL), security/privacy baseline, documentation skeleton, checklist, changelog, prompt log, traceability starter, and in-repo backlog.

**Application implementation was intentionally not started.** Next step is Phase 01 (requirements).

## 2. Persian Executive Summary

پروژهٔ CoachOS از یک مخزن خالی GitHub آغاز شده است (فقط مجوز MIT و README اولیه). هیچ کد برنامه، تست یا CI وجود ندارد. در فاز ۰۰ چشم‌انداز محصول، محدودیت زبانی **فقط فارسی و انگلیسی** (عربی خارج از دامنه)، دامنهٔ MVP، ریسک‌ها، معماری پیشنهادی یکپارچهٔ ماژولار، و مجموعهٔ مستندات پایه ثبت شد. پیاده‌سازی نرم‌افزار آغاز نشده است. گام بعدی فاز ۰۱ (نیازمندی‌های محصول) است.

## 3. Prompt(s) Received

- **Prompt 001** (2026-08-10): Full founding mission — operate as multi-role team; execute **Phase 00 only**; audit repository; create required docs/checklist/report/backlog; record fa/en-only and Arabic out of scope; propose P0 MVP and architecture; stop after Phase 00.  
- Logged in `docs/PROMPT_LOG.md`.

## 4. Objectives

| Objective | Result |
|-----------|--------|
| Inspect repository thoroughly | Done |
| Report current state with evidence | Done |
| Identify code/docs/tests/CI/deploy | None present beyond LICENSE + stub README |
| Classify empty vs partial vs unrelated | **Empty greenfield** |
| Create initial project documentation and checklist | Done |
| Create Phase 00 report | This document |
| Create backlog / milestones / issues if possible | In-repo backlog in `docs/RELEASE_PLAN.md`; GitHub Issues may be permission-limited |
| Propose P0 MVP, architecture, next phase | Done |
| Record fa/en only; Arabic out of scope | Done across README, brief, ADR-003, security, PRD |
| Stop after Phase 00 | Done — no app scaffold |

## 5. Product Decisions

Recorded in `docs/DECISIONS.md`:

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-001 | Modular monolith for MVP | Accepted |
| ADR-002 | Next.js + Django/DRF + PostgreSQL + Redis/Celery preferred | Proposed (confirm Phase 03) |
| ADR-003 | Locales `fa-IR` + `en-US` only; **no Arabic** | Accepted |
| ADR-004 | B2B2C SaaS; athletes included | Accepted |
| ADR-005 | Email+password MVP default; OTP later extension | Proposed default |
| ADR-006 | RBAC + object-level server authZ + audit | Accepted direction |
| ADR-007 | AI deferred until Phase 11 activation | Accepted |
| ADR-008 | Media provenance/rights metadata required | Accepted |
| ADR-009 | Jalali display strategy | Deferred Phase 01–02 |
| ADR-010 | Monorepo folder layout | Deferred Phase 04 |

**P0 MVP (proposed):** identity/tenancy/invites; fa/en UI; exercise library; program builder/assign; athlete logging; messaging/notifications; admin moderation; audit; privacy workflow design.

**Deferred:** marketplace, payments, nutrition pro, wearables, advanced AI, native apps, Arabic.

## 6. Assumptions

1. Repository owner intends this empty repo to host CoachOS (name matches; no conflicting code).  
2. MIT license remains acceptable for the product.  
3. Automation may lack full GitHub Issues/Projects write scope; markdown backlog is authoritative until issues exist.  
4. Session work continues on branch `arena/019febc6-coachos-fitness-coaching-platf` per environment policy.  
5. Preferred stack will be accepted unless Phase 03 finds a blocking reason.  
6. Pilot geography may include Persian-first users; English must remain fully usable.  

## 7. Work Completed

1. **Remote and git audit** via `git` and `gh api`  
2. **Filesystem audit** — only `LICENSE`, `README.md` pre-existed  
3. **Documentation suite** created (see §8)  
4. **Language constraint** propagated to all key docs  
5. **Risk register** in `PROJECT_STATUS.md`  
6. **Backlog** milestones M0–M8+ in `docs/RELEASE_PLAN.md`  
7. **Traceability** starter matrix for P0 FR/NFR IDs  
8. **Security/privacy baseline** drafted  
9. **Prompt log** initialized  

## 8. Files Created or Changed

| Path | Action |
|------|--------|
| `README.md` | Replaced stub |
| `PROJECT_STATUS.md` | Created |
| `PROJECT_CHECKLIST.md` | Created |
| `CHANGELOG.md` | Created |
| `docs/MASTER_PRODUCT_BRIEF.md` | Created |
| `docs/PRD.md` | Created (outline) |
| `docs/DECISIONS.md` | Created |
| `docs/SECURITY_AND_PRIVACY.md` | Created |
| `docs/DATA_MODEL.md` | Created (conceptual) |
| `docs/API_CONTRACT.md` | Created (strategy) |
| `docs/TRACEABILITY_MATRIX.md` | Created |
| `docs/RELEASE_PLAN.md` | Created |
| `docs/PROMPT_LOG.md` | Created |
| `docs/reports/PHASE-00-DISCOVERY-REPORT.md` | Created (this file) |
| `docs/architecture/README.md` | Created placeholder |
| `docs/ux/README.md` | Created placeholder |
| `docs/testing/README.md` | Created placeholder |
| `LICENSE` | Unchanged (MIT, pre-existing) |

## 9. GitHub Issues, Branches, Commits, and Pull Requests

### Repository metadata (evidence)

| Field | Value |
|-------|--------|
| Remote | `https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform.git` |
| Default branch | `main` |
| Session branch | `arena/019febc6-coachos-fitness-coaching-platf` |
| Main HEAD (base) | `a6283e8fa75414f9b47a0e40248f833b6438c0f8` — `Initial commit` |
| Author (initial) | Ali Naderi |
| Created at | 2026-08-10T13:03:36Z |
| License | MIT |
| Language / size | `null` / `0` (no code) |
| Pre-existing files | `LICENSE`, `README.md` |

### Issues / milestones

| Artifact | URL / ID |
|----------|----------|
| Milestone `phase-00-discovery` (closed) | [#1](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/milestone/1) |
| Milestone `phase-01-requirements` … `phase-08-comms` | [#2](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/milestone/2)–[#9](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/milestone/9) |
| Issue — Phase 01 requirements | [#1](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/issues/1) |
| Issue — Phase 00 discovery (tracking; create-only; PATCH close may 403 for bot) | [#2](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/issues/2) |

- Bot can **create** issues/milestones; **update/close** issue via API returned `403 Resource not accessible by integration` in this environment.  
- **Canonical backlog remains** `docs/RELEASE_PLAN.md` §3 (source of truth if GitHub drifts).

### Commits / PR

- Phase 00 documentation commit(s) on session branch (see git log after commit).  
- PR optional after push; environment tracks session branch.

## 10. Tests and Validation Commands

No application tests exist. Validation performed:

```bash
# From repository root
git status
git branch -a
git log --oneline -5
git remote -v
find . -type f -not -path './.git/*' | sort
gh api repos/AliNaderiii/CoachOS-Fitness-Coaching-Platform --jq '{name,private,default_branch,language,size,license:.license.spdx_id}'
gh api repos/AliNaderiii/CoachOS-Fitness-Coaching-Platform/contents/ --jq '.[].name'
```

Expected pre-doc state: only `LICENSE`, `README.md`.  
Post-doc state: documentation tree as in §8.

## 11. Evidence and Results

| Check | Result |
|-------|--------|
| Unrelated existing product? | **No** — empty |
| Partial scaffold? | **No** |
| Docs prior to Phase 00? | **No** (stub README only) |
| CI workflows? | **No** `.github/workflows` |
| Secrets in repo? | **None observed** |
| Arabic content introduced? | **No** (and forbidden going forward) |
| App code introduced in Phase 00? | **No** (by design) |

## 12. Requirements Traceability

- Draft FR/NFR IDs issued in `docs/PRD.md`  
- Matrix rows created in `docs/TRACEABILITY_MATRIX.md` with status `planned`  
- Constraint FR-I18N-02 (no Arabic) marked accepted  

## 13. Security and Privacy Considerations

- Baseline document: `docs/SECURITY_AND_PRIVACY.md`  
- Sensitive health-related data classes defined  
- No production credentials or personal health data added  
- AuthZ and audit called out as MVP-critical  
- Legal counsel TODO explicitly listed (not claimed complete)  
- AI surface deferred with safety constraints pre-documented  

## 14. Known Limitations

1. PRD is an **outline**, not full stories/AC (Phase 01).  
2. No ERD diagrams yet (Phase 03).  
3. Stack is **proposed**, not scaffolded.  
4. GitHub Issues/milestones may not be created by bot token.  
5. No PDF/DOCX export of this report (Markdown is canonical).  
6. Pricing, final brand name, and Jalali UX depth unresolved.  
7. Payment geography and regulatory classification unresolved (not MVP-blocking for docs).  

## 15. Risks and Blockers

See `PROJECT_STATUS.md` §7.  

**Blockers for Phase 01:** none.  

**Notable risks:** content rights (R04), health-data regulation (R05), payments later (R03), i18n/Jalali UX (R06).

## 16. Deferred Items

| Item | Defer to |
|------|----------|
| Full personas/stories/AC | Phase 01 |
| UX wireframes / design system | Phase 02 |
| Final ADRs + ERD + threat model deep dive | Phase 03 |
| Code scaffolding | Phase 04 |
| P1 nutrition/billing | Phases 09–10 when activated |
| P2 marketplace/AI/wearables | Phases 10–11+ when activated |
| Arabic locale | Not on roadmap unless founder requests |
| Native mobile apps | Post-PWA decision |

## 17. Exact Next Recommended Prompt

> Execute **Phase 01 — Product Requirements and Scope**.  
> Deliverables: personas; user journeys; detailed P0 MVP user stories with acceptance criteria; P1/P2 backlog; non-functional requirements with targets; expanded `docs/PRD.md` and `docs/TRACEABILITY_MATRIX.md`; update `PROJECT_STATUS.md`, `PROJECT_CHECKLIST.md`, `CHANGELOG.md`, `docs/PROMPT_LOG.md`; commit `docs/reports/PHASE-01-REQUIREMENTS-REPORT.md`.  
> **Do not** scaffold application code, add Arabic, or implement P1/P2 features.  
> Record defaults in `docs/DECISIONS.md` for any non-blocking open questions (auth channel, Jalali lean, group assignment depth).

## 18. Checklist Changes

Phase 00 items in `PROJECT_CHECKLIST.md` marked `[x]` complete with evidence links.  
Phases 01–14 remain `[ ]` / deferred as appropriate.  
Standing rule “No Arabic” and “No secrets committed” marked enforced for this phase.
