# Product Requirements Document (PRD) — CoachOS

**Status:** Outline / living stub — **full elaboration in Phase 01**  
**Last updated:** 2026-08-10  
**Source of vision:** `docs/MASTER_PRODUCT_BRIEF.md`  
**Languages:** `fa-IR` (RTL), `en-US` (LTR) only — **Arabic out of scope**

---

## 1. Purpose

This PRD will define measurable product requirements for CoachOS MVP (P0) and ordered backlogs for P1/P2. Phase 00 establishes structure and non-negotiable constraints; Phase 01 fills personas, journeys, stories, and acceptance criteria.

## 2. Problem statement

Coaches and gyms lack a bilingual, tenancy-aware operating system for programming, athlete logging, communication, and adherence — with production-grade Persian RTL and English LTR.

## 3. Goals (MVP)

| ID | Goal | Measurable outcome (draft) |
|----|------|----------------------------|
| G1 | Coach can create org, invite athletes/coaches | End-to-end invite accept < 5 minutes |
| G2 | Coach can build and assign a program | Template → assign happy path tested |
| G3 | Athlete can complete today’s workout log | Log persisted; coach can view |
| G4 | Full UI available in fa-IR and en-US | No hardcoded UI strings; RTL/LTR verified |
| G5 | Authorization enforced server-side | Object-level tests for coach/athlete isolation |
| G6 | Sensitive actions auditable | Audit events for authZ-sensitive mutations |

## 4. Non-goals (MVP)

- Marketplace, payments, nutritionist workflows  
- Wearables, native iOS/Android apps  
- Autonomous AI recommendations without human review  
- Arabic locale or content  
- Clinical/medical features  

## 5. Personas

*To be written in Phase 01.* Placeholder IDs:

- P-ADMIN — Platform Administrator  
- P-OWNER — Gym / Organization Owner  
- P-COACH — Coach / Trainer  
- P-ATH — Athlete / Client  

## 6. User journeys

*To be written in Phase 01.* Critical paths:

1. Owner signs up → creates organization → invites coach  
2. Coach accepts invite → builds program from library → assigns to athlete  
3. Athlete accepts invite → sets language → completes today’s workout  
4. Coach reviews log → messages athlete  
5. Admin moderates public exercise content  

## 7. User stories (index only)

Detailed stories and acceptance criteria: **Phase 01**.

### Epic E1 — Identity & tenancy

- Registration, login, password reset  
- Organization create/update  
- Invitations (coach, athlete)  
- Roles and object-level permissions  
- Profile + locale preference  

### Epic E2 — Exercise library

- CRUD canonical exercises (admin)  
- Coach-private exercises  
- i18n names, aliases, search normalization  
- Media references + rights/provenance metadata  
- Filter by muscle, equipment, pattern, difficulty  
- Publish/archive/moderate  

### Epic E3 — Training programming

- Program structure (phase/week/day/workout/prescription)  
- Sets/reps/load/RPE/RIR/tempo/rest/notes  
- Templates, duplicate, version  
- Assign individual (group depth TBD)  
- Draft/published/archived  

### Epic E4 — Athlete experience

- Today + calendar  
- Start/pause/complete/skip/modify-with-reason  
- Actuals logging + notes + pain/fatigue flags  
- Rest timer (nice-to-have if timeboxed)  
- Progress metrics; photos with consent (scope TBD)  

### Epic E5 — Communication

- Threads coach↔athlete  
- Contextual links to workout/check-in  
- In-app notifications + preferences  
- Email/push adapter interface (implementation may mock)  

### Epic E6 — Admin & quality

- Admin dashboard  
- User/org management  
- Audit log viewer (role-gated)  
- Basic analytics  
- Export/deletion request workflow (design + minimal implementation TBD)  

## 8. Functional requirements (draft IDs for traceability)

| ID | Requirement | Priority | Phase |
|----|-------------|----------|-------|
| FR-AUTH-01 | Users can register and authenticate | P0 | 05 |
| FR-AUTH-02 | Password reset or OTP flow exists | P0 | 05 |
| FR-ORG-01 | Users can create an organization | P0 | 05 |
| FR-ORG-02 | Owners can invite coaches and athletes | P0 | 05 |
| FR-AUTHZ-01 | Server-side RBAC enforced | P0 | 05 |
| FR-AUTHZ-02 | Coach access limited to assigned athletes by default | P0 | 05 |
| FR-I18N-01 | UI supports fa-IR RTL and en-US LTR | P0 | 04–07 |
| FR-I18N-02 | No Arabic locale or resources | P0 (constraint) | all |
| FR-EX-01 | Bilingual exercise records with search | P0 | 06 |
| FR-EX-02 | Media rights/provenance metadata required | P0 | 06 |
| FR-PRG-01 | Hierarchical program builder | P0 | 06 |
| FR-PRG-02 | Assign program to athlete with schedule | P0 | 06 |
| FR-ATH-01 | Athlete today workout view | P0 | 07 |
| FR-ATH-02 | Athlete can log set actuals | P0 | 07 |
| FR-MSG-01 | Coach–athlete message threads | P0 | 08 |
| FR-NTF-01 | In-app notifications with preferences | P0 | 08 |
| FR-ADM-01 | Admin moderation for exercises | P0 | 06/08 |
| FR-AUD-01 | Audit events for sensitive actions | P0 | 05+ |
| FR-PRI-01 | Data export/deletion workflow designed | P0 | 03/13 |
| FR-NUT-01 | Nutrition professional features | P1 | 09 |
| FR-PAY-01 | Billing and packages | P1 | 10 |
| FR-AI-01 | AI copilot with human review | P2 | 11 |
| FR-PWA-01 | Installable PWA + defined offline scope | P1/P2 | 12 |

## 9. Non-functional requirements (draft)

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-SEC-01 | Security | TLS in transit; secure password hashing; no secrets in repo |
| NFR-SEC-02 | Security | CSRF/CORS/secure headers configured |
| NFR-SEC-03 | Security | Rate limiting on auth and sensitive endpoints |
| NFR-PRV-01 | Privacy | Data minimization; purpose-limited sharing |
| NFR-PRV-02 | Privacy | Audit access to sensitive health-related fields |
| NFR-I18N-01 | i18n | All UI strings externalized |
| NFR-I18N-02 | i18n | Logical CSS; verified RTL/LTR |
| NFR-A11Y-01 | Accessibility | WCAG 2.2 AA target for core flows |
| NFR-PERF-01 | Performance | Athlete today view usable on mid-tier mobile / 3G-class |
| NFR-AVL-01 | Reliability | Documented backup/restore before production |
| NFR-API-01 | API | Versioned HTTP API + OpenAPI |
| NFR-TEST-01 | Quality | Unit + API + critical E2E paths before pilot |
| NFR-OBS-01 | Observability | Structured logs without sensitive payloads |

## 10. Authorization rules (normative draft)

1. Never trust client-supplied `role`, `organization_id`, or `athlete_id` without server verification.  
2. Coach sees only assigned athletes unless org-level permission granted.  
3. Org owners manage members and org settings within their org.  
4. Athletes control or consent to sharing sensitive data (photos, deep notes).  
5. Sensitive notes may have stricter visibility than basic profile.  
6. Platform admin actions are audited.  

## 11. AI requirements (future — not MVP build)

See product brief. First safe features only after stable data model: summarize check-in, adherence highlights, draft coach reply, suggest program variation from **approved** library, monthly summary with source links. Always label AI-generated content; human approve professional recommendations.

## 12. Compliance disclaimer

This PRD is not legal advice. Health-data handling requires jurisdiction-specific counsel before production launch with real users.

## 13. Phase 01 deliverables checklist

When Phase 01 completes, this document must include:

- [ ] Full personas  
- [ ] Journey maps  
- [ ] INVEST-style user stories + acceptance criteria for all P0 epics  
- [ ] Prioritized P1/P2 backlog  
- [ ] Refined NFRs with targets  
- [ ] Open questions resolved or explicitly deferred with defaults  

## 14. Traceability

Requirement IDs above feed `docs/TRACEABILITY_MATRIX.md`.
