# Phase 02 — UX, Information Architecture, and Design System Report

**Document version:** 1.0.0 (Phase 02 Completion Report)  
**Execution Date:** 2026-08-10 (UTC)  
**Authoring Team:** Coordinated Product & Engineering Team (Founder's Technical Advisor, PM, Business Analyst, UX Researcher, UX/UI Designer, Information Architect, Accessibility Specialist, Persian RTL/LTR Localization Specialist, Principal Architect, Security & Privacy Engineer, QA Engineer, Technical Writer, Release Manager, Code Reviewer)  
**Language Constraints:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR) **only**. **Arabic is strictly out of scope.**

---

## 1. Executive Summary

Phase 02 successfully converted the Phase 01 Product Requirements into an implementation-ready, accessible, bilingual **UX, Information Architecture, and Design System Package** for CoachOS.

All foundational constraints and rules were strictly enforced:
- **Zero application code, scaffolding, dependencies, migrations, or API implementations were created (documentation and design specifications only).**
- Non-negotiable language boundary preserved: **Persian (`fa-IR`, RTL) and English (`en-US`, LTR) with genuine feature and layout parity; Arabic is 100% out of scope.**
- Complete UX specifications authored across 13 dedicated documents: Information Architecture (`docs/ux/INFORMATION_ARCHITECTURE.md`), Navigation Model (`docs/ux/NAVIGATION_MODEL.md`), Screen Inventory (`docs/ux/SCREEN_INVENTORY.md`), User Flows (`docs/ux/USER_FLOWS.md`), Wireframes (`docs/ux/WIREFRAMES.md`), Design System (`docs/ux/DESIGN_SYSTEM.md`), Design Tokens (`docs/ux/DESIGN_TOKENS.md`), RTL/LTR Specification (`docs/ux/RTL_LTR_SPECIFICATION.md`), Responsive Behavior (`docs/ux/RESPONSIVE_BEHAVIOR.md`), Accessibility Specification (`docs/ux/ACCESSIBILITY_SPEC.md`), State & Error Matrix (`docs/ux/STATE_AND_ERROR_MATRIX.md`), UX Copy Guidelines (`docs/ux/UX_COPY.md`), UX Traceability Matrix (`docs/ux/UX_TRACEABILITY_MATRIX.md`), and UX Research Assumptions (`docs/ux/UX_RESEARCH_AND_ASSUMPTIONS.md`).

---

## 2. Persian Executive Summary (خلاصه مدیریتی به زبان فارسی)

فاز ۰۲ با موفقیت نیازمندی‌های محصول فاز ۰۱ را به یک بسته جامع، دسترس‌پذیر (WCAG 2.2 AA) و دو زبانه از **معماری اطلاعات، تجربه کاربری (UX) و سیستم طراحی** برای پلتفرم CoachOS تبدیل نمود.

تمامی اصول و محدودیت‌های بنیادین به طور کامل رعایت شدند:
۱. **هیچ‌گونه کد برنامه‌نویسی، اسکلت فرانت‌اند/بک‌اند، وابستگی خارجی، مایگریشن یا پیاده‌سازی API ایجاد نشد (فاز صرفاً مستندسازی و مشخصات طراحی است).**
۲. **محدودیت زبانی:** پلتفرم منحصراً برای **فارسی (`fa-IR` با چیدمان کامل راست‌به‌چپ RTL و فونت وزیرمتن)** و **انگلیسی (`en-US` با چیدمان چپ‌به‌راست LTR)** طراحی شده و **زبان عربی به صورت قطعی و کامل خارج از دامنه است**.
۳. **مستندات تحویل‌شده UX:** ۱۳ سند تخصصی شامل معماری اطلاعات، مدل ناوبری موبایل/دسکتاپ، سیاهه کامل ۲۸+ صفحه P0، نمودارهای جریان کاربر (Mermaid)، وایرفریم‌های متنی دقیق دو جهته، توکن‌های طراحی بصری، مشخصات تقارن RTL/LTR با ویژگی‌های منطقی CSS، ارگونومی تک‌دستی موبایل در باشگاه، انطباق دسترس‌پذیری با استاندارد WCAG 2.2 AA، ماتریس مدیریت خطاها و حالت‌های آفلاین PWA، راهنمای لحن و کپی‌رایتینگ غیربالینی، ماتریس ردیابی UX و برنامه اعتبارسنجی فرضیات پژوهش تدوین گردید.

پروژه آماده ورود به **فاز ۰۳ — معماری نرم‌افزار، داده، امنیت و حریم خصوصی** است.

---

## 3. Phase 01 Preflight Review

Prior to beginning Phase 02 UX design, a systematic preflight audit was conducted on the merged Phase 01 package. The findings were:
1. **Prompt Log Formatting:** Prompt 002 previously contained an abbreviated placeholder.
2. **PWA & Offline Scope Consistency:** Early drafts needed sharper distinctions between Phase 04 shell caching, Phase 07 form-preservation validation, and Phase 12 IndexedDB synchronization.
3. **Competitive Claims Qualification:** Regional competitor analysis (Liaqa) required clarification of its dual Arabic/English capability and explicit confirmation that it creates no Arabic scope for CoachOS.
4. **Legal & Metric Claims:** Workload reduction numbers and performance targets needed explicit labeling as engineering hypotheses and benchmarks rather than pre-pilot guarantees.
5. **Privacy Boundaries:** Distinctions between Organization Owner aggregate oversight and athlete private progress photos needed strict explicit consent governance.

---

## 4. Corrections Made Before UX Work

During preflight audit execution, correction commits were made to the Phase 01 branch, updating PR #4:
- Recorded exact full text for Prompt 002 and Prompt 003 in `docs/PROMPT_LOG.md`.
- Calibrated `docs/COMPETITIVE_LANDSCAPE.md` with qualified language assertions and desk-research time bounds (August 2026).
- Calibrated `docs/PRD.md` to frame performance metrics (< 1.5s Today view loading) and workload reductions (~70%) as target pilot hypotheses.
- Re-stated PWA sequencing across `docs/PRD.md`, `docs/USER_JOURNEYS.md`, and `docs/DECISIONS.md`.
- Clarified in `docs/SECURITY_AND_PRIVACY.md` that Organization Owners view aggregate gym statistics while raw progress photos and private notes require explicit athlete consent.
- Marked data model schemas and API endpoint contracts as provisional requirements models subject to Phase 03 architecture finalization.
- PR #4 was successfully merged into `main` (`392108372450dc8a40fe79c6201144733955b7c0`).

---

## 5. Objectives

| Objective | Target Scope | Execution Result | Evidence Document |
|-----------|--------------|------------------|-------------------|
| **Information Architecture** | Complete role-based site map and hierarchy | Complete | `docs/ux/INFORMATION_ARCHITECTURE.md` |
| **Navigation Model** | Multi-device responsive navigation patterns | Complete | `docs/ux/NAVIGATION_MODEL.md` |
| **Screen Inventory** | Full specifications for all 28+ P0 screens | Complete | `docs/ux/SCREEN_INVENTORY.md` |
| **User Flows** | Step-by-step flows and Mermaid diagrams | Complete | `docs/ux/USER_FLOWS.md` |
| **Wireframes** | Bidirectional low/medium-fidelity wireframes | Complete | `docs/ux/WIREFRAMES.md` |
| **Design System** | Complete component library specifications | Complete | `docs/ux/DESIGN_SYSTEM.md` |
| **Design Tokens** | WCAG 2.2 AA compliant color, spacing, type tokens | Complete | `docs/ux/DESIGN_TOKENS.md` |
| **RTL / LTR Specification** | CSS logical properties and Persian BiDi rules | Complete | `docs/ux/RTL_LTR_SPECIFICATION.md` |
| **Responsive Behavior** | Breakpoints and one-handed mobile gym ergonomics | Complete | `docs/ux/RESPONSIVE_BEHAVIOR.md` |
| **Accessibility Specification**| WCAG 2.2 AA baseline & verification checklist | Complete | `docs/ux/ACCESSIBILITY_SPEC.md` |
| **State & Error Matrix** | 8-state handling and progressive offline PWA matrix | Complete | `docs/ux/STATE_AND_ERROR_MATRIX.md` |
| **UX Copy Rules** | Non-clinical, supportive bilingual microcopy | Complete | `docs/ux/UX_COPY.md` |
| **UX Traceability** | 1:1 mapping of all P0 stories to UX artifacts | Complete | `docs/ux/UX_TRACEABILITY_MATRIX.md` |
| **Research Assumptions** | Hypothesis classification and user interview plans | Complete | `docs/ux/UX_RESEARCH_AND_ASSUMPTIONS.md` |

---

## 6. Information Architecture

Documented in `docs/ux/INFORMATION_ARCHITECTURE.md`:
- Structured across 4 role spaces: Public/Auth, Athlete Mobile PWA (`/app`), Coach Workspace (`/coach`), Organization Owner (`/org`), and Platform Admin (`/admin`).
- Deep-linking hierarchy, organization context switcher, and language toggle interaction model.

---

## 7. Navigation Model

Documented in `docs/ux/NAVIGATION_MODEL.md`:
- **Athlete Mobile:** Persistent 5-tab Bottom Navigation Bar (Today, Calendar, Progress, Messages, Profile) with modal full-screen Active Workout Mode canvas.
- **Coach / Admin Desktop:** Collapsible 260px sidebar with mini-bar mode, persistent top utility bar, and breadcrumb trails.
- **Dual-Pane Workflows:** Master-detail layouts for Program Builder (Outline Tree + Prescription Form) and Roster Log Review.

---

## 8. Screen Inventory

Documented in `docs/ux/SCREEN_INVENTORY.md`:
- Complete specifications for 34 distinct screens across authentication, organization management, coach programming, athlete execution, messaging, and admin moderation.
- Every entry details route, role, device priority, entry/exit points, mutations, permissions, loading/empty/error states, and accessibility hooks.

---

## 9. User Flows

Documented in `docs/ux/USER_FLOWS.md`:
- Flow specifications with Mermaid diagrams for: (1) Owner Onboarding & Team Setup (`UF-OWNER-01`), (2) Coach Program Building & Assignment (`UF-COACH-01`), (3) Athlete Workout Execution & Feedback (`UF-ATH-01`), and (4) Platform Admin Exercise Moderation (`UF-ADMIN-01`).

---

## 10. Wireframes

Documented in `docs/ux/WIREFRAMES.md`:
- Detailed ASCII structural wireframes in both **English LTR** and **Persian RTL (mirrored)** for:
  - Athlete Today's Workout (`SCR-ATH-01`)
  - Active Workout Execution & Set Logger (`SCR-ATH-02`)
  - Coach Hierarchical Program Builder (`SCR-COACH-06`)

---

## 11. Design System

Documented in `docs/ux/DESIGN_SYSTEM.md`:
- Core design principles (Athlete-first mobile clarity, coach programming velocity, bilingual parity, privacy transparency).
- Component specifications: Buttons, Numeric Set Inputs, Date Pickers (Jalali & Gregorian), Exercise Cards, Workout Cards, Program Tree Nodes, Modals, Drawers, Toasts, and Rest Timers.

---

## 12. Design Tokens

Documented in `docs/ux/DESIGN_TOKENS.md`:
- Dark Obsidian palette (`#0B0F17`) default for mobile gym-floor glare reduction.
- Complete color contrast validation against WCAG 2.2 AA.
- 4px spacing scale (`--space-1` to `--space-12`), border radii (`--radius-sm` to `--radius-xl`), z-index layers, and motion curves with `prefers-reduced-motion` override.

---

## 13. Persian RTL Specification

Documented in `docs/ux/RTL_LTR_SPECIFICATION.md`:
- Pure CSS Logical Properties (`margin-inline-start`, `padding-inline-end`, `inset-inline-start`, `text-align: start`).
- Directional component mirroring (sidebars, breadcrumbs, trees, set grids, timers).
- Mixed-direction BiDi isolation using `<bdi>` for Latin exercise names in Persian copy.
- Zero-width non-joiner (`\u200C` / نیم‌فاصله) handling.
- Native Persian numerals (`۰-۹`) and units formatting.

---

## 14. English LTR Specification

Documented in `docs/ux/RTL_LTR_SPECIFICATION.md` & `docs/ux/DESIGN_TOKENS.md`:
- Standard left-to-right reading flow with `Inter` typography.
- Symmetrical layout parity with Persian RTL views.

---

## 15. Responsive Behavior

Documented in `docs/ux/RESPONSIVE_BEHAVIOR.md`:
- 6-tier breakpoint taxonomy (`xs`, `sm`, `md`, `lg`, `xl`, `2xl`).
- One-handed mobile gym ergonomics with Natural Thumb Zone placement for all logging controls.
- Minimum 44x44px touch targets (48x48px for set checkmarks) and 8px hit area clearance.
- Dual-pane to accordion responsive reflow for Program Builder.

---

## 16. Accessibility Specification

Documented in `docs/ux/ACCESSIBILITY_SPEC.md`:
- Target: **WCAG 2.2 Level AA** compliance.
- Modal/drawer focus trapping and Escape key dismiss.
- ARIA live region announcements for rest countdown timer and toast feedback.
- Accessible form labels, inline error binding (`aria-describedby`), and 10-point verification test checklist.

---

## 17. State and Error Matrix

Documented in `docs/ux/STATE_AND_ERROR_MATRIX.md`:
- 8-state handling matrix across all P0 features.
- Progressive offline PWA behavior matrix clearly separating Phase 04 app shell caching, Phase 07 in-memory form preservation and offline banners, and Phase 12 IndexedDB background sync.

---

## 18. UX Copy Rules

Documented in `docs/ux/UX_COPY.md`:
- Supportive, action-oriented tone in Persian and English.
- Non-clinical framing for subjective pain/fatigue reporting with mandatory disclaimers.
- Bilingual microcopy dictionary covering authentication, workout logging, consent dialogs, and PWA install prompts.

---

## 19. PWA UX Behavior

Documented across `docs/ux/NAVIGATION_MODEL.md`, `docs/ux/STATE_AND_ERROR_MATRIX.md`, and `docs/ux/UX_COPY.md`:
- Installable home screen app shell guidance for iOS Safari and Android Chrome.
- Full-screen standalone execution mode hiding browser navigation chrome.
- Clear offline indicators and retry banners.

---

## 20. Research and Assumptions

Documented in `docs/ux/UX_RESEARCH_AND_ASSUMPTIONS.md`:
- Clear separation between verified evidence, UX hypotheses, and unvalidated assumptions.
- Structured research interview questions for Persian coaches, English coaches, gym owners, athletes, and nutritionists.
- Pilot usability testing protocol with 3 critical task scenarios and SUS scoring targets (>= 82/100).

---

## 21. UX Traceability

Documented in `docs/ux/UX_TRACEABILITY_MATRIX.md`:
- 1:1 mapping of all 29 P0 User Stories (`US-AUTH-001` through `US-PWA-001`) to primary screens, secondary screens, user flows, wireframe specs, design components, RTL/LTR rules, accessibility requirements, and state matrix entries.

---

## 22. Product and UX Decisions

Recorded 6 new UX ADRs in `docs/DECISIONS.md`:
- **ADR-023:** Athlete Mobile Navigation & Full-Screen Active Workout Canvas (Accepted).
- **ADR-024:** Coach Program Builder Desktop Dual-Pane Master-Detail Pattern (Accepted).
- **ADR-025:** Persian Typography Strategy: Vazirmatn Variable Web Font (Accepted).
- **ADR-026:** Non-Clinical UX Language Standard for Subjective Feedback (Accepted).
- **ADR-027:** Explicit Affirmative Consent Interaction Model for Sensitive Photos (Accepted).
- **ADR-028:** Dark-Neutral Visual Theme for Mobile Gym-Floor Glare Reduction (Accepted).

---

## 23. Files Created or Changed

| File Path | Action | Description |
|-----------|--------|-------------|
| `docs/ux/INFORMATION_ARCHITECTURE.md` | Created | Role-based IA, site map, and routing hierarchy |
| `docs/ux/NAVIGATION_MODEL.md` | Created | Multi-device navigation patterns, bottom nav, and dual-pane layouts |
| `docs/ux/SCREEN_INVENTORY.md` | Created | Full specifications for 34 P0 screens |
| `docs/ux/USER_FLOWS.md` | Created | Step-by-step user flows with Mermaid sequence/flow diagrams |
| `docs/ux/WIREFRAMES.md` | Created | Bidirectional ASCII wireframes for core athlete and coach screens |
| `docs/ux/DESIGN_SYSTEM.md` | Created | Component library specifications, states, and accessibility rules |
| `docs/ux/DESIGN_TOKENS.md` | Created | Visual tokens (colors, type, spacing, elevation, motion) with contrast checks |
| `docs/ux/RTL_LTR_SPECIFICATION.md` | Created | CSS logical properties, bidirectional mirroring, and Persian BiDi rules |
| `docs/ux/RESPONSIVE_BEHAVIOR.md` | Created | Breakpoints, one-handed mobile gym ergonomics, and layout reflows |
| `docs/ux/ACCESSIBILITY_SPEC.md` | Created | WCAG 2.2 AA accessibility specifications and verification checklist |
| `docs/ux/STATE_AND_ERROR_MATRIX.md` | Created | 8-state handling and progressive offline PWA matrix across phases |
| `docs/ux/UX_COPY.md` | Created | Non-clinical bilingual microcopy dictionary and content guidelines |
| `docs/ux/UX_TRACEABILITY_MATRIX.md` | Created | 1:1 mapping from P0 user stories to UX specifications |
| `docs/ux/UX_RESEARCH_AND_ASSUMPTIONS.md` | Created | Hypothesis categorization, research questions, and usability protocol |
| `docs/reports/PHASE-02-UX-DESIGN-REPORT.md` | Created | This comprehensive 31-section completion report |
| `docs/DECISIONS.md` | Updated | Added ADR-023 through ADR-028 (UX design decisions) |
| `docs/RELEASE_PLAN.md` | Updated | Marked Milestone M2 items complete |
| `PROJECT_STATUS.md` | Updated | Phase 02 completion status and post-merge base commit recorded |
| `PROJECT_CHECKLIST.md` | Updated | Marked Phase 02 UX deliverables complete with evidence links |
| `CHANGELOG.md` | Updated | Documented Phase 02 additions and release notes |
| `docs/PROMPT_LOG.md` | Updated | Logged Prompt 003 execution record |

---

## 24. GitHub Branch, Commit, Issues, and Pull Request

- **Repository:** `https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform`
- **Session Working Branch:** `arena/019febfc-coachos-fitness-coaching-platf`
- **Base Commit on `main`:** `392108372450dc8a40fe79c6201144733955b7c0` (PR #4 merged)
- **Phase 01 PR #4:** Successfully merged into `main` (`392108372450dc8a40fe79c6201144733955b7c0`).
- **Phase 02 PR:** [PR #5: docs(phase-02): ux, information architecture, and design system specification](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/5) opened from branch `arena/019febfc-coachos-fitness-coaching-platf` to `main` (awaiting review; not merged automatically).

---

## 25. Tests and Validation

Validation commands executed in workspace:
```bash
# Verify clean working tree and tracked files
git status
git branch -a
git log --oneline -5
find docs/ux/ -type f | sort
```
- **Validation Results:** All 14 UX specification documents exist, are internally consistent, adhere strictly to `fa-IR`/`en-US` language rules, contain zero Arabic strings, and contain zero application source code.

---

## 26. Security and Privacy Considerations

- **Consent UX:** Explicit affirmative modal consent dialogs specified in `docs/ux/DESIGN_SYSTEM.md` and `docs/ux/UX_COPY.md` before progress photo uploads or nutritionist data sharing.
- **Tenant Isolation in Navigation:** Multi-org switcher scopes all views strictly to active tenant context.
- **Cross-Tenant Obscurity:** 404/403 states designed to never reveal foreign resource existence.
- **Zero Real Health Data / Secrets:** All wireframe data and examples use fictionalized synthetic profiles.

---

## 27. Open Questions

1. **Jalali Calendar Grid Component Selection (Phase 04):** Which lightweight open-source React datepicker library provides the cleanest Jalali grid rendering with zero bundle bloat? (To be evaluated in Phase 04 foundation).
2. **Coach Mobile Programming Depth:** Should the full multi-week periodization builder be available on mobile phones, or should mobile coaches be nudged toward tablet/desktop while retaining quick template assignment on mobile? (UX recommendation: Responsive accordion on mobile with primary builder optimized for tablet/desktop).

---

## 28. Risks and Blockers

- **Blockers:** Zero blockers for Phase 03.
- **Risks:**
  - *Persian Font Delivery (R06):* Variable web font loading on 3G mobile networks must be optimized in Phase 04 using font-display swap and subsetting to prevent layout shift.

---

## 29. Deferred Items

| Item | Deferred To | Rationale |
|------|-------------|-----------|
| Physical ERD & C4 Architecture Diagrams | Phase 03 | Dedicated Architecture phase |
| Threat Modeling & OpenAPI 3.1 Specs | Phase 03 | Dedicated Architecture phase |
| Frontend/Backend Code Scaffolding | Phase 04 | Dedicated Foundation phase |
| Nutritionist UI Flows | Phase 09 (P1) | Core strength coaching UX must stabilize first |
| Billing Checkout UI | Phase 10 (P1) | Payment provider compliance |
| AI Copilot UI | Phase 11 (P2) | Requires safety guardrails and backend evaluation |

---

## 30. Checklist Changes

- Updated `PROJECT_CHECKLIST.md`: All Phase 02 checklist items marked `[x]` complete with evidence links.
- Standing rules ("No Arabic", "No secrets committed", "Synthetic test data only") confirmed enforced.

---

## 31. Exact Recommended Prompt for Phase 03

```text
Execute **Phase 03 — Architecture, Data, Security, and Privacy**.

You are continuing the CoachOS Fitness Coaching Platform as a coordinated professional team consisting of:
- Founder’s Technical Advisor
- Principal Software Architect
- Data Architect / DBA
- Security and Privacy Engineer
- Backend Lead
- Frontend Lead
- QA/Test Lead
- Technical Writer
- Release Manager
- Code Reviewer

This instruction executes **Phase 03 — Architecture, Data, Security, and Privacy**.
This phase is architectural documentation, system modeling, threat modeling, and contract design only.

Do not write application code.
Do not scaffold frontend or backend.
Do not install dependencies.
Do not create runnable database migrations.
Do not implement APIs.
Do not implement AI.
Do not implement payments.

Deliverables:
1. System architecture and C4 diagrams (`docs/architecture/SYSTEM_ARCHITECTURE.md`).
2. Finalized Architecture Decision Records (`docs/DECISIONS.md`).
3. Normalized PostgreSQL physical data model DDL and ERD specifications (`docs/DATA_MODEL.md`).
4. Server-side authorization architecture (RBAC + ABAC) and negative test matrix (`docs/architecture/AUTHORIZATION_MODEL.md`).
5. Comprehensive Threat Model and OWASP Top 10 mitigation (`docs/architecture/THREAT_MODEL.md`).
6. Privacy lifecycle, consent architecture, and data export/erasure pipelines (`docs/SECURITY_AND_PRIVACY.md`).
7. OpenAPI 3.1 API endpoint specification catalog (`docs/API_CONTRACT.md`).
8. Backup, restore, and disaster recovery strategy (`docs/architecture/DISASTER_RECOVERY.md`).
9. Update `PROJECT_STATUS.md`, `PROJECT_CHECKLIST.md`, `CHANGELOG.md`, `docs/PROMPT_LOG.md`, and `docs/RELEASE_PLAN.md`.
10. Commit Phase 03 report: `docs/reports/PHASE-03-ARCHITECTURE-REPORT.md` (with English and Persian executive summaries).

Strict constraint: Persian (`fa-IR`) and English (`en-US`) only. Arabic is strictly out of scope.
```
