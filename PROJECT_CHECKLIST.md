# Project Checklist — CoachOS

**Legend**

| Mark | Meaning |
|------|---------|
| `[ ]` | Not started |
| `[~]` | In progress |
| `[x]` | Completed and evidenced |
| `[!]` | Blocked |
| `[-]` | Deferred by decision |

**Last updated:** 2026-08-10 (UTC)

Evidence links point to repository paths, commits, or GitHub artifacts. Update after every meaningful task and at phase end.

---

## Phase 00 — Discovery and Repository Audit

- [x] Repository audit completed — evidence: `docs/reports/PHASE-00-DISCOVERY-REPORT.md`
- [x] Existing code, docs, tests, and deployment inspected — **none present** beyond MIT `LICENSE` + stub README
- [x] Product vision recorded — `docs/MASTER_PRODUCT_BRIEF.md`
- [x] Persian/English-only constraint recorded — README, brief, decisions, security doc
- [x] Arabic explicitly marked out of scope — same
- [x] User roles and initial scope recorded — brief + PRD outline
- [x] Risks and unknowns recorded — `PROJECT_STATUS.md`, Phase 00 report
- [x] Initial technical options evaluated — `docs/DECISIONS.md` (ADR-001 draft)
- [x] Initial GitHub issues/milestones created **or** in-repo backlog equivalent — milestones [1–9](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/milestones); issues [#1](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/issues/1), [#2](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/issues/2); canonical backlog `docs/RELEASE_PLAN.md`
- [x] Phase 00 report committed — `docs/reports/PHASE-00-DISCOVERY-REPORT.md`
- [x] Phase 00 merged to main via PR #3 (commit `f52c4134087b18c4bd1a8aef9e0100fd63f71b8e`)

**Phase 00 status:** `[x]` Complete (2026-08-10)

---

## Phase 01 — Product Requirements and Scope

- [x] Personas written — evidence: `docs/PERSONAS.md`
- [x] User journeys written — evidence: `docs/USER_JOURNEYS.md`
- [x] Domain glossary written — evidence: `docs/DOMAIN_GLOSSARY.md`
- [x] Competitive landscape & market benchmarking written — evidence: `docs/COMPETITIVE_LANDSCAPE.md`
- [x] P0 MVP defined (detailed stories) — evidence: `docs/PRD.md` §5
- [x] P1 and P2 backlog defined — evidence: `docs/PRD.md` §7, `docs/RELEASE_PLAN.md`
- [x] User stories written with stable IDs — evidence: `docs/PRD.md` §5
- [x] Acceptance criteria written in Gherkin with positive/negative authZ — evidence: `docs/PRD.md` §5
- [x] Non-functional requirements written with measurable targets — evidence: `docs/PRD.md` §8
- [x] Permissions matrix written — evidence: `docs/PRD.md` §6, `docs/SECURITY_AND_PRIVACY.md`
- [x] Decisions updated with PWA, License, Location, Calendar ADRs — evidence: `docs/DECISIONS.md`
- [x] Traceability matrix expanded with all P0 mappings — evidence: `docs/TRACEABILITY_MATRIX.md`
- [x] Phase 01 report committed — evidence: `docs/reports/PHASE-01-REQUIREMENTS-REPORT.md`

**Phase 01 status:** `[x]` Complete (2026-08-10)

---

## Phase 02 — UX, Information Architecture, and Design System

- [x] Navigation model defined — evidence: `docs/ux/NAVIGATION_MODEL.md`, `docs/ux/INFORMATION_ARCHITECTURE.md`
- [x] Coach flows designed — evidence: `docs/ux/USER_FLOWS.md`, `docs/ux/WIREFRAMES.md`
- [x] Athlete flows designed — evidence: `docs/ux/USER_FLOWS.md`, `docs/ux/WIREFRAMES.md`
- [x] Organization/admin flows designed — evidence: `docs/ux/USER_FLOWS.md`, `docs/ux/SCREEN_INVENTORY.md`
- [x] Persian RTL reviewed (typography & layout) — evidence: `docs/ux/RTL_LTR_SPECIFICATION.md`
- [x] English LTR reviewed — evidence: `docs/ux/RTL_LTR_SPECIFICATION.md`, `docs/ux/DESIGN_TOKENS.md`
- [x] Accessibility baseline defined (WCAG 2.2 AA) — evidence: `docs/ux/ACCESSIBILITY_SPEC.md`
- [x] Responsive breakpoints defined — evidence: `docs/ux/RESPONSIVE_BEHAVIOR.md`
- [x] Empty/loading/error/offline states designed — evidence: `docs/ux/STATE_AND_ERROR_MATRIX.md`
- [x] Phase 02 report committed — evidence: `docs/reports/PHASE-02-UX-DESIGN-REPORT.md`

**Phase 02 status:** `[x]` Complete (2026-08-10)

---

## Phase 03 — Architecture, Data, Security, and Privacy

- [ ] Architecture diagram created (C4 System Context & Container)
- [ ] ADRs created/finalized
- [ ] Domain boundaries defined
- [ ] Normalized PostgreSQL data model & ERD created
- [ ] Authorization model (RBAC + ABAC) defined
- [ ] Threat model completed
- [ ] Privacy/data lifecycle documented
- [ ] API strategy & OpenAPI catalog documented
- [ ] Backup/restore strategy documented
- [ ] Phase 03 report committed

**Phase 03 status:** `[ ]` Not started

---

## Phase 04 — Project Foundation & PWA Baseline

- [ ] Local development setup works
- [ ] Environment configuration documented
- [ ] Frontend scaffold works (Next.js + TypeScript + Tailwind)
- [ ] Backend scaffold works (Django + DRF)
- [ ] PWA foundation (Manifest, installable shell, Service Worker) works
- [ ] Database and migrations work
- [ ] CI pipeline works
- [ ] Lint/type/test commands work
- [ ] Health checks work
- [ ] Phase 04 report committed

**Phase 04 status:** `[ ]` Not started

---

## Phase 05 — Identity, Tenancy, and Roles

- [ ] Authentication works (Email + Password)
- [ ] Single-location organization creation works
- [ ] Invitations work (single-use tokens)
- [ ] Role permissions work server-side
- [ ] Object-level access tests exist (negative authZ tests)
- [ ] Audit events exist (immutable logging)
- [ ] Persian/English settings work
- [ ] Phase 05 report committed

**Phase 05 status:** `[ ]` Not started

---

## Phase 06 — Exercise Library and Training Programs

- [ ] Exercise schema works
- [ ] Bilingual exercise search & Persian character variant folding works
- [ ] Media rights metadata exists
- [ ] Program builder works (hierarchical phases/weeks/days/items/prescriptions)
- [ ] Reusable templates work
- [ ] Program assignments work (immutable snapshot creation)
- [ ] Admin moderation queue works
- [ ] Coach tests exist
- [ ] Phase 06 report committed

**Phase 06 status:** `[ ]` Not started

---

## Phase 07 — Athlete App and Progress

- [ ] Today workout view works
- [ ] Mobile set actuals logging works
- [ ] Rest timer works
- [ ] Exercise substitution/modification works with reasons
- [ ] Completion/adherence tracking works
- [ ] Feedback and pain/fatigue flags work
- [ ] Progress photos are permissioned and consent-governed
- [ ] Mobile responsiveness & installed-PWA mobile experience tested
- [ ] Phase 07 report committed

**Phase 07 status:** `[ ]` Not started

---

## Phase 08 — Communication and Notifications

- [ ] Contextual 1:1 message threads work
- [ ] Workout session contextual references work
- [ ] In-app notifications work
- [ ] Notification preferences work
- [ ] Email/push adapter interface documented
- [ ] Abuse/rate limits considered
- [ ] Phase 08 report committed

**Phase 08 status:** `[ ]` Not started

---

## Phase 09 — Nutrition and Multi-Professional Collaboration

- [ ] Nutritionist role implemented
- [ ] Consent-based collaboration implemented
- [ ] Meal plans work
- [ ] Persian & international food/recipe data model works
- [ ] Macro calculations are tested
- [ ] Health-data privacy review completed
- [ ] Phase 09 report committed

**Phase 09 status:** `[ ]` Not started — **P1, deferred until activated**

---

## Phase 10 — Billing and Coach Monetization

- [ ] Payment provider abstraction (Shetab domestic / Stripe international) exists
- [ ] Products and packages exist
- [ ] Subscriptions exist
- [ ] Webhooks are idempotent
- [ ] Entitlements are tested
- [ ] Multi-location gym support implemented
- [ ] Coach storefront exists
- [ ] Phase 10 report committed

**Phase 10 status:** `[ ]` Not started — **P1, deferred until activated**

---

## Phase 11 — AI Copilot

- [ ] AI use cases prioritized
- [ ] Safety boundaries & human-in-the-loop review workflow documented
- [ ] Approved retrieval data sources defined
- [ ] Prompt/version logging exists
- [ ] Cost/rate limits exist
- [ ] Evaluation cases exist
- [ ] Fallback behavior exists
- [ ] Phase 11 report committed

**Phase 11 status:** `[ ]` Not started — **P2, deferred until activated**

---

## Phase 12 — Advanced Offline PWA & Integrations

- [ ] Advanced IndexedDB offline workout caching works
- [ ] Sync queues & conflict resolution work
- [ ] Background sync where supported works
- [ ] Push notification limitations documented
- [ ] Wearable integrations (HealthKit / Health Connect) evaluated
- [ ] Native application strategy decision recorded
- [ ] Phase 12 report committed

**Phase 12 status:** `[ ]` Not started — **P2, deferred until activated**

---

## Phase 13 — QA, Security, Performance, and Release

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] RTL/LTR visual regression tests pass
- [ ] Accessibility review pass (WCAG 2.2 AA)
- [ ] Security review & penetration testing pass
- [ ] Dependency scan pass
- [ ] Performance baseline recorded (< 1.5s Today view on 3G)
- [ ] Backup/restore tested
- [ ] Staging deployment works
- [ ] Release checklist completed
- [ ] Phase 13 report committed

**Phase 13 status:** `[ ]` Not started

---

## Phase 14 — Pilot and Iteration

- [ ] Pilot cohort defined (gyms, coaches, athletes)
- [ ] Feedback mechanism exists
- [ ] Empirical usage and business metrics collected
- [ ] Critical bugs resolved
- [ ] Onboarding documented
- [ ] Pricing hypothesis tested
- [ ] Pilot report committed

**Phase 14 status:** `[ ]` Not started

---

## Cross-Cutting Standing Rules (Always On)

- [x] No Arabic content, locale files, or requirements
- [x] No secrets committed to Git repository
- [x] Synthetic test data only (no real PII/health data)
- [ ] All user-facing strings via i18n resources (`fa-IR`, `en-US`)
- [ ] Server-side authorization for every sensitive action
- [ ] Immutable audit log for sensitive access/mutations
- [ ] Phase report + checklist + changelog + prompt log updated per phase
