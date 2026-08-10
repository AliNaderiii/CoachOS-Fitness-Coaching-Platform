# Release Plan and Backlog — CoachOS

**Last updated:** 2026-08-10  
**Model:** Phased delivery (Phase 00–14) with P0/P1/P2 product tiers  

---

## 1. Phase gate overview

| Phase | Name | Product tier | Exit criteria (summary) |
|-------|------|--------------|-------------------------|
| 00 | Discovery | — | Audit + docs + constraints — **DONE** |
| 01 | Requirements | P0 spec | Personas, stories, AC, NFR, PRD filled |
| 02 | UX / Design system | P0 UX | Flows, RTL/LTR, a11y, states |
| 03 | Architecture & security | P0 arch | ADR final, ERD, threat model, API strategy |
| 04 | Foundation | P0 eng | Runnable FE/BE, CI, health, env docs |
| 05 | Identity & tenancy | P0 | Auth, org, invites, authZ tests, audit, locale |
| 06 | Exercises & programs | P0 | Library + builder + assign + version |
| 07 | Athlete app | P0 | Today, logging, adherence, progress |
| 08 | Comms | P0 | Messages, notifications |
| 09 | Nutrition & multi-pro | P1 | Only when activated |
| 10 | Billing | P1 | Only when activated |
| 11 | AI copilot | P2 | Only when activated |
| 12 | PWA / offline | P0 residual / P1 | Manifest, SW, offline scope |
| 13 | QA & release | Pilot-ready | Tests, security, staging, checklist |
| 14 | Pilot | Learn | Feedback, metrics, iterate |

**Note:** Phase 12 may partially overlap earlier phases (e.g., manifest basics in foundation) but full offline is gated.

## 2. MVP (P0) release candidate definition

A coach organization can onboard, program, assign, and communicate; an athlete can train and log in fa-IR and en-US; admin can moderate exercises; authZ and audit hold under test; security baseline documented; no Arabic; no marketplace/payments/AI required.

## 3. In-repo backlog (GitHub Issues equivalent)

> This section is the **canonical backlog**. GitHub mirrors (as of Phase 00): milestones [phase-00 … phase-08](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/milestones), issue [#1 Phase 01](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/issues/1), issue [#2 Phase 00](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/issues/2).

### Milestone M0 — Discovery (Phase 00) — GitHub milestone #1

- [x] AUDIT-001 Repository audit  
- [x] DOC-001 Master brief, status, checklist, security baseline  
- [x] DOC-002 Phase 00 report  

### Milestone M1 — Requirements (Phase 01) — GitHub milestone #2 / issue #1

- [ ] REQ-001 Personas (Admin, Owner, Coach, Athlete)  
- [ ] REQ-002 Journeys for core happy paths  
- [ ] REQ-003 P0 user stories + acceptance criteria  
- [ ] REQ-004 P1/P2 backlog refinement  
- [ ] REQ-005 NFR targets  
- [ ] REQ-006 Traceability matrix expansion  
- [ ] DOC-003 Phase 01 report  

### Milestone M2 — UX (Phase 02)

- [ ] UX-001 Information architecture / nav  
- [ ] UX-002 Coach flows  
- [ ] UX-003 Athlete flows  
- [ ] UX-004 Admin flows  
- [ ] UX-005 RTL/LTR specifications  
- [ ] UX-006 Empty/loading/error/offline states  
- [ ] UX-007 Accessibility baseline  
- [ ] DOC-004 Phase 02 report  

### Milestone M3 — Architecture (Phase 03)

- [ ] ARCH-001 System context + container diagrams  
- [ ] ARCH-002 Finalize ADRs (stack, auth mechanism)  
- [ ] ARCH-003 Physical data model / ERD  
- [ ] ARCH-004 AuthZ matrix  
- [ ] SEC-001 Threat model v1  
- [ ] SEC-002 Privacy lifecycle  
- [ ] API-001 Endpoint catalog v1  
- [ ] DOC-005 Phase 03 report  

### Milestone M4 — Foundation (Phase 04)

- [ ] ENG-001 Backend scaffold + Postgres migrations smoke  
- [ ] ENG-002 Frontend scaffold + i18n shell fa/en  
- [ ] ENG-003 Docker compose dev (optional but preferred)  
- [ ] ENG-004 CI lint/type/test  
- [ ] ENG-005 Health endpoints  
- [ ] DOC-006 Phase 04 report  

### Milestone M5 — Identity (Phase 05)

- [ ] AUTH-001 Register/login/logout/reset  
- [ ] ORG-001 Org create + membership  
- [ ] ORG-002 Invitations  
- [ ] AUTHZ-001 RBAC + object-level tests  
- [ ] AUDIT-001 Audit event pipeline  
- [ ] I18N-001 Locale preference API + UI switcher  
- [ ] DOC-007 Phase 05 report  

### Milestone M6 — Training domain (Phase 06)

- [ ] EX-001 Exercise schema + i18n + search  
- [ ] EX-002 Media rights metadata  
- [ ] PRG-001 Program builder  
- [ ] PRG-002 Templates + version + assign  
- [ ] DOC-008 Phase 06 report  

### Milestone M7 — Athlete (Phase 07)

- [ ] ATH-001 Today + calendar  
- [ ] ATH-002 Session logging  
- [ ] ATH-003 Adherence + feedback  
- [ ] ATH-004 Progress metrics (+ photos if scoped)  
- [ ] DOC-009 Phase 07 report  

### Milestone M8 — Comms (Phase 08)

- [ ] MSG-001 Threads + contextual refs  
- [ ] NTF-001 In-app notifications + prefs  
- [ ] NTF-002 Email/push adapter interface  
- [ ] DOC-010 Phase 08 report  

### Later milestones

- M9 Nutrition (P1)  
- M10 Billing (P1)  
- M11 AI (P2)  
- M12 PWA/Offline  
- M13 QA/Release  
- M14 Pilot  

## 4. Suggested GitHub milestones (create when permitted)

```
phase-00-discovery
phase-01-requirements
phase-02-ux
phase-03-architecture
phase-04-foundation
phase-05-identity
phase-06-training
phase-07-athlete
phase-08-comms
phase-09-nutrition
phase-10-billing
phase-11-ai
phase-12-pwa
phase-13-release
phase-14-pilot
```

## 5. Versioning intent

- `0.1.x` — internal foundation through identity  
- `0.2.x` — training domain  
- `0.3.x` — athlete + comms MVP feature-complete  
- `0.9.x` — release candidate / staging  
- `1.0.0` — pilot production  

## 6. Rollback and release engineering

Documented fully in Phase 13. Until then: prefer forward-fix migrations; never destructive unreviewed migrations on shared environments.
