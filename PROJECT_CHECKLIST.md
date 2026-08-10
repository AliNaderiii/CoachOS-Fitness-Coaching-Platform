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

**Phase 00 status:** `[x]` Complete (2026-08-10)

---

## Phase 01 — Product Requirements and Scope

- [ ] Personas written
- [ ] User journeys written
- [ ] P0 MVP defined (detailed stories)
- [ ] P1 and P2 backlog defined
- [ ] User stories written
- [ ] Acceptance criteria written
- [ ] Non-functional requirements written
- [ ] Traceability matrix started/expanded
- [ ] Phase 01 report committed

**Phase 01 status:** `[ ]` Not started

---

## Phase 02 — UX, Information Architecture, and Design System

- [ ] Navigation model defined
- [ ] Coach flows designed
- [ ] Athlete flows designed
- [ ] Organization/admin flows designed
- [ ] Persian RTL reviewed
- [ ] English LTR reviewed
- [ ] Accessibility baseline defined
- [ ] Responsive breakpoints defined
- [ ] Empty/loading/error/offline states designed
- [ ] Phase 02 report committed

**Phase 02 status:** `[ ]` Not started

---

## Phase 03 — Architecture, Data, Security, and Privacy

- [ ] Architecture diagram created
- [ ] ADRs created/finalized
- [ ] Domain boundaries defined
- [ ] Data model created
- [ ] Authorization model defined
- [ ] Threat model completed
- [ ] Privacy/data lifecycle documented
- [ ] API strategy documented
- [ ] Backup/restore strategy documented
- [ ] Phase 03 report committed

**Phase 03 status:** `[ ]` Not started

---

## Phase 04 — Project Foundation

- [ ] Local development setup works
- [ ] Environment configuration documented
- [ ] Frontend scaffold works
- [ ] Backend scaffold works
- [ ] Database and migrations work
- [ ] CI pipeline works
- [ ] Lint/type/test commands work
- [ ] Health checks work
- [ ] Phase 04 report committed

**Phase 04 status:** `[ ]` Not started

---

## Phase 05 — Identity, Tenancy, and Roles

- [ ] Authentication works
- [ ] Organization creation works
- [ ] Invitations work
- [ ] Role permissions work server-side
- [ ] Object-level access tests exist
- [ ] Audit events exist
- [ ] Persian/English settings work
- [ ] Phase 05 report committed

**Phase 05 status:** `[ ]` Not started

---

## Phase 06 — Exercise Library and Training Programs

- [ ] Exercise schema works
- [ ] Exercise search/filter works
- [ ] Media rights metadata exists
- [ ] Program builder works
- [ ] Templates work
- [ ] Assignments work
- [ ] Versioning works
- [ ] Coach tests exist
- [ ] Phase 06 report committed

**Phase 06 status:** `[ ]` Not started

---

## Phase 07 — Athlete App and Progress

- [ ] Today view works
- [ ] Workout logging works
- [ ] Completion/adherence works
- [ ] Progress metrics work
- [ ] Feedback and notes work
- [ ] Progress photos are permissioned
- [ ] Mobile responsiveness tested
- [ ] Phase 07 report committed

**Phase 07 status:** `[ ]` Not started

---

## Phase 08 — Communication and Notifications

- [ ] Message threads work
- [ ] Contextual references work
- [ ] In-app notifications work
- [ ] Notification preferences work
- [ ] Email/push adapter documented
- [ ] Abuse/rate limits considered
- [ ] Phase 08 report committed

**Phase 08 status:** `[ ]` Not started

---

## Phase 09 — Nutrition and Multi-Professional Collaboration

- [ ] Nutritionist role implemented
- [ ] Consent-based collaboration implemented
- [ ] Meal plans work
- [ ] Food/recipe data model works
- [ ] Macro calculations are tested
- [ ] Persian food content strategy documented
- [ ] Health-data privacy review completed
- [ ] Phase 09 report committed

**Phase 09 status:** `[ ]` Not started — **P1, deferred until activated**

---

## Phase 10 — Billing and Coach Monetization

- [ ] Products/packages exist
- [ ] Subscriptions exist
- [ ] Payment adapter exists
- [ ] Webhooks are idempotent
- [ ] Entitlements are tested
- [ ] Refund/cancellation logic exists
- [ ] Coach storefront exists
- [ ] Phase 10 report committed

**Phase 10 status:** `[ ]` Not started — **P1/P2, deferred until activated**

---

## Phase 11 — AI Copilot

- [ ] AI use cases prioritized
- [ ] Safety boundaries documented
- [ ] Approved data sources defined
- [ ] Human-review workflow exists
- [ ] Prompt/version logging exists
- [ ] Cost/rate limits exist
- [ ] Evaluation cases exist
- [ ] Fallback behavior exists
- [ ] Phase 11 report committed

**Phase 11 status:** `[ ]` Not started — **P2, deferred until activated**

---

## Phase 12 — PWA, Offline, and Platform Integrations

- [ ] Manifest works
- [ ] Install flow works
- [ ] Service worker works
- [ ] Offline scope documented
- [ ] Sync/conflict behavior tested
- [ ] Push limitations documented
- [ ] Native app decision recorded
- [ ] Phase 12 report committed

**Phase 12 status:** `[ ]` Not started

---

## Phase 13 — QA, Security, Performance, and Release

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] RTL/LTR tests pass
- [ ] Accessibility review pass
- [ ] Security review pass
- [ ] Dependency scan pass
- [ ] Performance baseline recorded
- [ ] Backup/restore tested
- [ ] Staging deployment works
- [ ] Release checklist completed
- [ ] Phase 13 report committed

**Phase 13 status:** `[ ]` Not started

---

## Phase 14 — Pilot and Iteration

- [ ] Pilot users defined
- [ ] Feedback mechanism exists
- [ ] Usage metrics defined
- [ ] Critical bugs resolved
- [ ] Onboarding documented
- [ ] Pricing hypothesis tested
- [ ] Pilot report committed

**Phase 14 status:** `[ ]` Not started

---

## Cross-cutting standing rules (always on)

- [x] No Arabic content or locale work
- [x] No secrets committed
- [ ] All user-facing strings via i18n resources (enforced once UI exists)
- [ ] Server-side authorization for every sensitive action
- [ ] Audit log for sensitive access/changes
- [ ] Phase report + checklist + changelog + prompt log updated per phase
