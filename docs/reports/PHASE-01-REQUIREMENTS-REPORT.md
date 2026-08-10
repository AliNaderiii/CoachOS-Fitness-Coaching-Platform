# Phase 01 — Product Requirements and Scope Report

**Document version:** 1.0.0 (Phase 01 Completion Report)  
**Execution Date:** 2026-08-10 (UTC)  
**Authoring Team:** Coordinated Product & Engineering Team (Founder's Technical Advisor, PM, Business Analyst, UX Researcher, UX/UI Designer, Principal Architect, Security & Privacy Engineer, QA Engineer, Technical Writer, Release Manager, Code Reviewer)  
**Language Constraints:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR) **only**. **Arabic is strictly out of scope.**

---

## 1. Executive Summary

Phase 01 successfully transformed the Phase 00 strategic vision into a comprehensive, testable, implementation-ready **Product Requirements Package** for the CoachOS Fitness Coaching Platform. 

All non-negotiable architectural boundaries were respected:
- **No application code, scaffolding, dependencies, database migrations, AI integrations, or payment integrations were introduced.**
- Language boundaries are strictly enforced: **Persian (`fa-IR`, RTL) and English (`en-US`, LTR) only; Arabic is 100% out of scope.**
- Scope corrections were formally recorded: PWA delivery was restructured across Phases 04, 07, and 12; the repository license options were evaluated and marked as **Pending Founder Approval**; a **Single-Location-First Strategy** was adopted for MVP; and a **UTC/Gregorian storage with Persian Jalali UI formatting** calendar strategy was proposed.
- Complete documentation artifacts were created or expanded: `docs/PERSONAS.md` (6 personas), `docs/USER_JOURNEYS.md` (5 journeys), `docs/DOMAIN_GLOSSARY.md` (bilingual fitness/tenancy/privacy glossary), `docs/COMPETITIVE_LANDSCAPE.md` (10-platform desk research benchmark), `docs/PRD.md` (P0 stories, Gherkin ACs, permissions matrix, NFRs), `docs/DECISIONS.md` (22 ADRs), `docs/DATA_MODEL.md`, `docs/API_CONTRACT.md`, `docs/SECURITY_AND_PRIVACY.md`, `docs/TRACEABILITY_MATRIX.md`, and `docs/RELEASE_PLAN.md`.

The project is fully prepared for **Phase 02 — UX, Information Architecture, and Design System**.

---

## 2. Persian Executive Summary (خلاصه مدیریتی به زبان فارسی)

فاز ۰۱ با موفقیت چشم‌انداز اولیه فاز ۰۰ را به یک بسته جامع، آزمون‌پذیر و آمادهٔ پیاده‌سازی از نیازمندی‌های محصول برای پلتفرم مربی‌گری ورزشی CoachOS تبدیل نمود.

تمامی محدودیت‌ها و مرزهای تعیین‌شده به دقت رعایت شدند:
۱. **هیچ‌گونه کد برنامه‌نویسی، اسکلت‌بندی، وابستگی خارجی، مایگریشن پایگاه داده، یکپارچه‌سازی هوش مصنوعی یا پرداخت در این فاز ایجاد نشد (فاز صرفاً مستندسازی و مهندسی نیازمندی‌هاست).**
۲. **محدودیت زبانی:** پلتفرم منحصراً از زبان‌های **فارسی (`fa-IR` با چیدمان راست‌به‌چپ RTL)** و **انگلیسی (`en-US` با چیدمان چپ‌به‌راست LTR)** پشتیبانی می‌کند و **زبان عربی به طور قطعی و کامل خارج از دامنه است**.
۳. **اصلاحات دامنه و معماری:** توالی توسعه PWA اصلاح گردید (پایه در فاز ۰۴، اعتبارسنجی موبایل در فاز ۰۷، قابلیت‌های آفلاین پیشرفته در فاز ۱۲)؛ گزینه‌های مجوز نرم‌افزار ارزیابی و جهت **تصمیم‌گیری نهایی مؤسس** ثبت شد؛ استراتژی تک‌شعبه‌ای برای MVP تثبیت شد؛ و استراتژی ذخیره‌سازی زمان UTC با نمایش تقویم جلالی (شمسی) برای کاربران فارسی پیشنهاد گردید.
۴. **مستندات تحویل‌شده:** مستندات پرسوناهای کاربر، مسیرهای کاربر، واژه‌نامه تخصصی دو زبانه، تحلیل چشم‌انداز رقابتی (۱۰ پلتفرم جهانی و منطقه‌ای)، سند جامع نیازمندی‌های محصول (PRD) همراه با داستان‌های کاربر INVEST و معیارهای پذیرش Gherkin (شامل سناریوهای مثبت و منفی احراز دسترسی)، ماتریس دسترسی‌ها، نیازمندی‌های غیرکارکردی (WCAG 2.2 AA)، مدل داده‌ای، قرارداد API، ماتریس ردیابی نیازمندی‌ها و برنامه انتشار تکمیل شدند.

پروژه آماده ورود به **فاز ۰۲ — تجربه کاربری، معماری اطلاعات و سیستم طراحی** است.

---

## 3. Prompt(s) Received

### Prompt 002 (Full Text Received):
```text
**CONTINUE COACHOS AS A PROFESSIONAL PRODUCT-AND-ENGINEERING TEAM**

You are continuing the CoachOS Fitness Coaching Platform as a coordinated professional team consisting of:
- Founder’s Technical Advisor
- Product Manager
- Business Analyst
- UX Researcher
- UX/UI Designer
- Principal Software Architect
- Security and Privacy Engineer
- QA/Test Engineer
- Technical Writer
- Release Manager
- Code Reviewer

The project is a bilingual, mobile-first fitness coaching operating system for coaches, gyms, athletes, and future nutrition professionals.

This instruction executes **Phase 01 — Product Requirements and Scope**.
This phase is documentation and requirements engineering only.

Do not write application code.
Do not scaffold the frontend or backend.
Do not install dependencies.
Do not create database migrations.
Do not create AI integrations.
Do not create payment integrations.

[Detailed instructions covering verification, post-merge housekeeping, constraints, vision, scope corrections, PRD requirements, personas, journeys, P0 user stories and acceptance criteria, permissions matrix, NFRs, competitive landscape, decisions, reports, and communication protocols.]
```

---

## 4. Objectives

| Objective | Target Scope | Execution Result | Evidence Document |
|-----------|--------------|------------------|-------------------|
| **Post-Merge Verification** | Verify PR #3 merge, commits, and clean working tree | Complete | `PROJECT_STATUS.md`, §5 below |
| **Bilingual Constraints** | Enforce `fa-IR` RTL + `en-US` LTR only; exclude Arabic | Complete | All docs & ADR-003 |
| **Personas Specification** | Define 6 detailed personas across roles | Complete | `docs/PERSONAS.md` |
| **User Journeys** | Detail 5 end-to-end user journeys with flows & authZ checks | Complete | `docs/USER_JOURNEYS.md` |
| **Domain Glossary** | Author English & Persian canonical terminology glossary | Complete | `docs/DOMAIN_GLOSSARY.md` |
| **Competitive Benchmarking** | Desk research benchmarking 10 fitness & nutrition platforms | Complete | `docs/COMPETITIVE_LANDSCAPE.md` |
| **P0 Scope & User Stories** | Write INVEST stories with Gherkin ACs for all P0 epics | Complete | `docs/PRD.md` §5 |
| **Permissions Matrix** | Detail server-side permissions across 6 roles and all entities | Complete | `docs/PRD.md` §6 |
| **NFR Targets** | Propose measurable security, performance, a11y (WCAG 2.2 AA) | Complete | `docs/PRD.md` §8 |
| **Scope Corrections & ADRs** | Record PWA, License, Location, and Calendar decisions | Complete | `docs/DECISIONS.md` |
| **Traceability Expansion** | Map all P0 requirements to stories, ACs, APIs, and tests | Complete | `docs/TRACEABILITY_MATRIX.md` |
| **Roadmap & Release Plan** | Update milestone backlog and PWA phasing | Complete | `docs/RELEASE_PLAN.md` |

---

## 5. Post-Merge Repository Verification

The repository state was audited prior to executing Phase 01:
- **Repository URL:** `https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform`
- **Phase 00 PR #3 Status:** Successfully merged into `main` on `2026-08-10T13:57:45Z`.
- **Phase 00 Merge Commit:** `f52c4134087b18c4bd1a8aef9e0100fd63f71b8e`.
- **Base Commit on `main`:** `f52c4134087b18c4bd1a8aef9e0100fd63f71b8e`.
- **Active Working Branch:** `arena/019febfc-coachos-fitness-coaching-platf` (bound to current Arena session).
- **Working Tree State:** Clean; zero untracked binary or temporary files.
- **Application Code Check:** Verified that **zero application code, dependencies, lockfiles, or migrations** were introduced after Phase 00.

---

## 6. Personas Completed

Authored `docs/PERSONAS.md` specifying 6 detailed archetypes:
1. **P-ADMIN (Platform Administrator):** Saman / Alex — System operations, trust & safety, catalog curation, media rights moderation, and audit review.
2. **P-OWNER (Gym / Organization Owner):** Mehdi / Marcus — Primary SaaS payer, boutique gym director, multi-coach team manager, single-location facility operator.
3. **P-COACH (Coach / Personal Trainer):** Sarah / Reza — Program designer, template library builder, daily workout reviewer, contextual communicator.
4. **P-ATH (Athlete / Client):** Neda / Jordan — Free/included account lifter, mobile PWA user, one-handed gym floor set logger, privacy-conscious athlete.
5. **P-NUT (Nutrition Professional — P1):** Dr. Mina / Elena — Registered dietitian, Persian/international macro coach, consent-governed collaborator.
6. **P-SUP (Support / Read-Only Staff):** Arash / Taylor — Front-desk assistant, member verification, read-only operational support.

Every persona details JTBD, pain points, workarounds, technical comfort, privacy concerns, accessibility needs, success criteria, willingness-to-pay, abandonment triggers, and critical workflows.

---

## 7. User Journeys Completed

Authored `docs/USER_JOURNEYS.md` detailing 5 step-by-step user journeys:
1. **UJ-OWNER-01 (Organization Owner):** Registration -> Locale selection -> Org creation -> Single primary location setup -> Coach email invite -> Member management -> High-level adherence review.
2. **UJ-COACH-01 (Coach):** Invite accept -> Locale selection -> Exercise search (Persian character folding) -> Program builder (phases/weeks/days/items/prescriptions) -> Template saving -> Athlete assignment (immutable snapshot creation) -> Daily log review -> Contextual set messaging.
3. **UJ-ATH-01 (Athlete):** Invite accept -> Mobile PWA install -> Today's workout view -> Video cues inspection -> Start workout -> One-handed set actual logging -> Rest timer -> Exercise substitution with reason -> Pain/fatigue reporting -> Finish workout -> Progress review.
4. **UJ-ADMIN-01 (Platform Administrator):** MFA login -> Exercise moderation queue -> Media rights & provenance verification -> Approve/reject canonical content -> Audit log inspection.
5. **UJ-NUT-01 (Future Nutrition Professional — P1):** Assignment -> Athlete explicit consent prompt -> Dietary intake -> Persian & international meal plan builder -> Food log review -> Coach collaboration -> Assignment revocation.

---

## 8. P0 MVP Scope Boundaries

### In Scope for P0:
- Email/password authentication with secure reset and rate limiting.
- Multi-tenant organization workspace with single primary location profile.
- Member invitations (Coaches, Athletes) with single-use time-limited tokens.
- Server-side RBAC and object-level authorization (`CoachAthleteAssignment`).
- First-class Persian (`fa-IR`, RTL) and English (`en-US`, LTR) layout with `Vazirmatn` font.
- Bilingual canonical exercise catalog with Persian character folding (`ی`/`ي`, `ک`/`ك`).
- Mandatory media rights, copyright license, and creator attribution metadata.
- Hierarchical program builder (phases, weeks, days, workouts, items, supersets, prescriptions).
- Reusable organization program templates.
- Program assignment generating immutable point-in-time `ProgramSnapshot`.
- Athlete mobile "Today's Workout" dashboard and calendar.
- Touch-friendly set actuals logging (weight, reps, RPE) and rest countdown timer.
- Structured exercise substitution/modification with required reasons.
- Athlete session feedback, fatigue rating, and high-visibility pain flags.
- Private progress photo uploads with explicit consent hooks and signed URLs.
- Contextual 1:1 coach-athlete message threads attached to workout sessions.
- In-app notification engine and user channel preferences.
- Platform admin exercise moderation and approval workflows.
- Immutable `AuditEvent` logging for sensitive mutations.
- Data export (portability) and account anonymization/erasure pipeline designs.
- PWA foundation (Web App Manifest, installable shell, Service Worker baseline).

### Explicitly Out of Scope for P0:
- Arabic language, locale files, translations, or seed data.
- Public coach marketplace or discovery directory (P2).
- Payment processing or subscription checkouts (Phase 10 / P1).
- Nutritionist UI or meal planning workflows (Phase 09 / P1).
- Multi-location gym franchise routing (Phase 10 / P1).
- Wearable hardware integrations (HealthKit, Health Connect) (Phase 12 / P2).
- Native iOS/Android binary app-store builds (PWA-first).
- Autonomous AI generation without human review or clinical claims.

---

## 9. P1 and P2 Backlog

Detailed in `docs/PRD.md` §7 and `docs/RELEASE_PLAN.md`:
- **P1 Items:** Nutrition Professional Role (`P1-NUT-01`), Persian & International Food Catalog (`P1-NUT-02`), Meal Plan Builder & Food Logging (`P1-NUT-03`), Structured Daily Habits & Check-ins (`P1-HAB-01`), 1:1 Session Scheduling & Booking (`P1-SCH-01`), Payment Gateway Abstraction & Subscriptions (`P1-PAY-01`), Multi-Location Gym Management (`P1-LOC-01`).
- **P2 Items:** Public Coach Marketplace (`P2-MKT-01`), Constrained AI Workout Copilot (`P2-AI-01`), Wearable Integrations (`P2-WRB-01`), Custom Branded White-Label Apps (`P2-WHT-01`).

---

## 10. User Stories & Acceptance Criteria

Detailed in `docs/PRD.md` §5 with stable IDs:
- `US-AUTH-001` through `US-AUTH-003`: Registration, login, password reset.
- `US-ORG-001` through `US-ORG-005`: Organization creation, single location setup, coach/athlete invitations, membership revocation.
- `US-I18N-001` through `US-I18N-002`: Language/direction switcher, Persian character variant folding.
- `US-EX-001` through `US-EX-003`: Canonical catalog browsing, private exercise creation with media rights, admin moderation.
- `US-PRG-001` through `US-PRG-003`: Hierarchical program builder, reusable templates, immutable assignment snapshots.
- `US-ATH-001` through `US-ATH-005`: Today's workout view, set logging, exercise substitution, pain flags, consent-governed progress photos.
- `US-MSG-001`: Contextual 1:1 messaging linked to workout logs.
- `US-NTF-001`: In-app notifications and preferences.
- `US-AUD-001`: Immutable audit logging.
- `US-PRI-001` through `US-PRI-002`: Data portability export and account erasure pipelines.
- `US-PWA-001`: PWA manifest and installable mobile shell.

Every story includes testable Gherkin `Given/When/Then` scenarios covering positive flows, negative authorization blocks (e.g., cross-tenant queries returning 404, unassigned coach queries returning 403), expired tokens, and validation errors.

---

## 11. Permissions Matrix

Authored comprehensive matrix in `docs/PRD.md` §6 and `docs/SECURITY_AND_PRIVACY.md` §2 governing 6 roles (`P-ADMIN`, `P-OWNER`, `P-COACH`, `P-ATH`, `P-NUT`, `P-SUP`) across all resources (Users, Orgs, Locations, Memberships, Exercises, Programs, Snapshots, Workout Logs, Progress Photos, Messages, Audit Logs).

---

## 12. Non-Functional Requirements (NFRs)

Detailed in `docs/PRD.md` §8 with proposed measurable targets:
- **Security:** Argon2id password hashing, TLS 1.3, rate limiting (5 attempts/15 min), signed media URLs (TTL <= 15 min), zero secrets in Git.
- **Authorization:** 100% server-side enforcement; tenant isolation via `organization_id` queries.
- **Privacy:** Data minimization, purpose limitation, granular consent hooks, machine-readable export (`.zip`), account erasure pipeline.
- **Accessibility:** Target **WCAG 2.2 AA** across all core flows; 4.5:1 contrast ratio; 44x44px minimum touch targets.
- **Performance:** Athlete "Today's Workout" interactive rendering < 1.5s on 3G mobile networks; p95 API latency < 200ms for reads; JS bundle < 150KB.
- **Reliability:** Atomic database transactions; daily automated snapshots with tested PITR; client-side IndexedDB workout offline caching.
- **Localization:** 100% externalized strings (`fa-IR`, `en-US`); logical CSS properties; `Vazirmatn` Persian font; automated CI check blocking Arabic files.
- **PWA:** Valid `manifest.json`, standalone display, Service Worker shell caching.

---

## 13. Product and Architecture Decisions

Recorded 22 ADRs in `docs/DECISIONS.md`:
- ADR-001: Modular Monolith Architecture (Accepted)
- ADR-002: Next.js + Django/DRF + PostgreSQL Preferred Stack (Proposed)
- ADR-003: Persian & English Only; Arabic Out of Scope (Accepted Mandate)
- ADR-004: B2B2C Multi-Tenant SaaS Model (Accepted)
- ADR-005: Email+Password Default Authentication (Proposed)
- ADR-006: Server-Side RBAC + ABAC Authorization (Accepted)
- ADR-007: Constrained AI Deferred to Phase 11 (Accepted)
- ADR-008: Exercise Media Provenance & Rights Metadata (Accepted)
- ADR-014 through ADR-022: Membership model, program versioning snapshots, archival lifecycle, UUIDv7 identifiers, search normalization, data ownership, multi-pro collaboration, payment deferral, and marketplace deferral.

---

## 14. Calendar and PWA Decisions

### 14.1 Calendar Strategy (ADR-009)
- **Analyzed Options:** (1) Gregorian storage and display only; (2) UTC/Gregorian internal storage with Persian Jalali UI display for `fa-IR`; (3) First-class Jalali calendar in backend.
- **Recommendation:** **Option 2 (UTC/Gregorian internal storage with Persian Jalali UI formatting).** All timestamps store `timestamptz` in UTC; API transmits ISO 8601 UTC strings; frontend components render Solar Hijri (Jalali) when `locale == 'fa-IR'` (using `date-fns-jalali`) and Gregorian when `locale == 'en-US'`.

### 14.2 PWA Phasing Correction (ADR-011)
- **Corrected Roadmap:**
  - **Phase 04 (Foundation):** Web App Manifest (`manifest.json`), mobile shell, Service Worker foundation, offline fallback.
  - **Phase 07 (Athlete App):** Mobile workout execution, set logging, rest timer, installed-PWA mobile validation.
  - **Phase 12 (Advanced Capabilities):** Advanced IndexedDB offline sync queue, bidirectional conflict resolution, background sync, wearable hardware integration review.

---

## 15. License and Intellectual Property Decision (ADR-012)

- **Current State:** Repository contains open-source MIT `LICENSE` from initialization.
- **Options Evaluated:**
  1. *Keep MIT License (Open Source):* Maximum public visibility; high competitor copying risk; lower enterprise SaaS valuation.
  2. *Proprietary / All Rights Reserved (Closed Source):* Full SaaS IP protection; zero competitor reuse; optimal for commercial SaaS investment.
  3. *Open-Core Model (AGPLv3 / Business Source License BSL):* Open engine with proprietary enterprise modules.
  4. *Private Repository with Commercial License:* Traditional B2B SaaS posture.
- **Status:** **Marked as Pending Founder Approval.** The `LICENSE` file remains MIT in Phase 01 and will not be altered without explicit founder authorization.

---

## 16. Competitive Landscape Summary

Authored `docs/COMPETITIVE_LANDSCAPE.md` benchmarking 10 platforms:
- **International Fitness Platforms:** ABC Trainerize, PT Distinction, Everfit, TrueCoach, My PT Hub, FITR, TrainHeroic, Exercise.com.
- **Regional Competitors:** Liaqa (validates Middle Eastern demand, but focuses on Arabic/GCC with heavy native apps; CoachOS differentiates via specialized Persian `fa-IR` RTL and PWA delivery).
- **Nutrition Platforms:** Nutrium / Practice Better (strong clinical charting but disconnected from strength training; CoachOS addresses this in P1 via consent-based multi-professional collaboration).
- **Identified 8 CoachOS Differentiation Hypotheses:** (1) True Persian/English parity, (2) Persian search folding, (3) Low-bandwidth PWA resilience, (4) Consent-based multi-pro collaboration, (5) Verified media rights, (6) Transparent B2B2C pricing, (7) Privacy & data portability, (8) Constrained human-reviewed AI copilot.

---

## 17. Files Created or Changed

| File Path | Action | Description |
|-----------|--------|-------------|
| `docs/PERSONAS.md` | Created | 6 detailed user personas across all platform roles |
| `docs/USER_JOURNEYS.md` | Created | 5 end-to-end user journeys with error and permission flows |
| `docs/DOMAIN_GLOSSARY.md` | Created | Canonical bilingual fitness, tenancy, and privacy terminology |
| `docs/COMPETITIVE_LANDSCAPE.md` | Created | Desk research benchmarking 10 competitor platforms |
| `docs/PRD.md` | Substantially Updated | Full PRD with P0 user stories, Gherkin ACs, permissions matrix, NFRs, backlogs |
| `docs/DECISIONS.md` | Substantially Updated | 22 ADRs covering PWA, license, calendar, location, and architecture |
| `docs/DATA_MODEL.md` | Substantially Updated | Logical schemas for single-location MVP, snapshots, media rights, audit |
| `docs/API_CONTRACT.md` | Substantially Updated | Versioned REST API endpoint specs, error envelopes, and authZ contracts |
| `docs/SECURITY_AND_PRIVACY.md` | Substantially Updated | 9-tier data classification taxonomy, privacy lifecycle, threat model |
| `docs/TRACEABILITY_MATRIX.md` | Substantially Updated | End-to-end mapping from requirements to stories, ACs, APIs, tests |
| `docs/RELEASE_PLAN.md` | Substantially Updated | Phased roadmap reflecting corrected PWA milestones and backlog |
| `PROJECT_STATUS.md` | Updated | Post-merge repository status and Phase 01 completion record |
| `PROJECT_CHECKLIST.md` | Updated | Phase 01 deliverables marked complete with evidence links |
| `CHANGELOG.md` | Updated | Documented Phase 01 changes and PR #3 merge record |
| `docs/PROMPT_LOG.md` | Updated | Logged PR #3 merge record and Prompt 002 |
| `docs/reports/PHASE-00-DISCOVERY-REPORT.md` | Updated | Appended Post-Phase-00 Merge Addendum |
| `docs/reports/PHASE-01-REQUIREMENTS-REPORT.md` | Created | This comprehensive 27-section completion report |

---

## 18. GitHub Branch, Commit, Issues, and Pull Request

- **GitHub Repository:** `https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform`
- **Session Working Branch:** `arena/019febfc-coachos-fitness-coaching-platf`
- **Main Base Commit:** `f52c4134087b18c4bd1a8aef9e0100fd63f71b8e` (PR #3 merged)
- **Tracking Milestones:** Milestones 1–9 active on GitHub; in-repo backlog in `docs/RELEASE_PLAN.md` remains authoritative.
- **Pull Request Creation:** A PR for Phase 01 will be opened from branch `arena/019febfc-coachos-fitness-coaching-platf` to `main` upon phase completion.

---

## 19. Tests and Validation

Validation commands executed in workspace:
```bash
# Verify clean working tree and tracked files
git status
git branch -a
git log --oneline -5
find docs/ -type f | sort
```
- **Validation Results:** All 17 documentation deliverables exist, are internally consistent, adhere strictly to `fa-IR`/`en-US` language rules, contain zero Arabic strings, and contain zero application source code.

---

## 20. Security and Privacy Considerations

- **Data Classification:** 9-tier classification defined in `docs/SECURITY_AND_PRIVACY.md` §1.
- **Zero Real PII / Secrets:** Verified that no credentials, tokens, or live health data exist in the repository.
- **Negative Authorization Scenarios:** Defined in `docs/PRD.md` and mapped in `docs/TRACEABILITY_MATRIX.md` to guarantee cross-tenant isolation and unassigned coach blocks.
- **Privacy Lifecycle:** Machine-readable data export (`.zip`) and account erasure pipelines specified.

---

## 21. Assumptions

1. Founder will review ADR-012 regarding repository license transition prior to Phase 04 scaffolding.
2. English and Persian translation resource bundles (`en-US.json`, `fa-IR.json`) will be initialized during Phase 04 foundation.
3. PostgreSQL with `pg_trgm` extension is available in the target production environment for Persian search normalization.
4. Mobile PWA installation is acceptable to athletes in lieu of heavy native app store packages.

---

## 22. Open Questions

1. **Brand Legal Name & Domain:** Will the final product launch as "CoachOS" or under a localized commercial trademark? (Default: Continue using CoachOS codename).
2. **License Selection (ADR-012):** Founder decision required on MIT vs Proprietary vs Open-Core model.
3. **SMS Gateway Provider for OTP (Phase 05):** Which regional SMS gateway will be integrated for phone authentication in Persian markets? (Default: Email+Password in P0).

---

## 23. Risks and Blockers

- **Blockers:** Zero blockers for Phase 02.
- **Risks:**
  - *Content Rights (R04):* Exercise demonstration videos must be produced or licensed with verified provenance (mitigated by `MediaRights` metadata schema).
  - *Health Data Regulation (R05):* Formal legal counsel required before live commercial pilot handling real athlete metrics.

---

## 24. Deferred Items

| Item | Deferred To | Rationale |
|------|-------------|-----------|
| Wireframes & Design Tokens | Phase 02 | Dedicated UX phase |
| Physical ERD & C4 Diagrams | Phase 03 | Dedicated Architecture phase |
| Code Scaffolding & CI | Phase 04 | Dedicated Foundation phase |
| Nutritionist Module | Phase 09 (P1) | Core strength coaching must stabilize first |
| Billing & Payments | Phase 10 (P1) | Payment gateway compliance complexity |
| AI Workout Copilot | Phase 11 (P2) | Requires stable data model and safety controls |
| Advanced Offline Sync | Phase 12 (P2) | Foundation PWA built first in Phases 04 & 07 |

---

## 25. Traceability Summary

All 29 P0 functional and non-functional requirements defined in `docs/PRD.md` are mapped 1:1 in `docs/TRACEABILITY_MATRIX.md` to user story IDs, Gherkin acceptance criteria IDs, target personas, API endpoints, planned delivery phases, and test verification types. Every sensitive domain includes explicit negative authorization test mappings.

---

## 26. Checklist Changes

- Updated `PROJECT_CHECKLIST.md`: All Phase 01 checklist items marked `[x]` complete with evidence links.
- Standing rules ("No Arabic", "No secrets in Git", "Synthetic test data only") confirmed enforced.
- Phase 04, 07, and 12 checklist items updated to reflect corrected PWA sequencing.

---

## 27. Exact Recommended Prompt for Phase 02

```text
Execute **Phase 02 — UX, Information Architecture, and Design System**.

You are continuing the CoachOS Fitness Coaching Platform as a coordinated professional team.
This phase is UX and design engineering only. Do not write application code.

Deliverables:
1. Navigation and information architecture specifications (`docs/ux/INFORMATION_ARCHITECTURE.md`).
2. Coach desktop/tablet program builder and athlete management user flows and wireframes (`docs/ux/COACH_FLOWS.md`).
3. Athlete mobile-first workout execution, logging, and rest timer user flows and wireframes (`docs/ux/ATHLETE_FLOWS.md`).
4. Organization owner and platform admin management console flows (`docs/ux/ADMIN_FLOWS.md`).
5. Persian (`fa-IR`, RTL) layout specifications, `Vazirmatn` typography rules, and CSS logical property tokens (`docs/ux/RTL_LTR_SPECIFICATION.md`).
6. Accessibility baseline specifications targeting WCAG 2.2 AA (`docs/ux/ACCESSIBILITY_SPECIFICATION.md`).
7. UI state specifications for Empty, Loading, Error, and Offline scenarios (`docs/ux/UI_STATES.md`).
8. Update `PROJECT_STATUS.md`, `PROJECT_CHECKLIST.md`, `CHANGELOG.md`, and `docs/PROMPT_LOG.md`.
9. Commit Phase 02 report: `docs/reports/PHASE-02-UX-REPORT.md` (with English and Persian executive summaries).

Strict constraint: Persian (`fa-IR`) and English (`en-US`) only. Arabic is strictly out of scope.
```
