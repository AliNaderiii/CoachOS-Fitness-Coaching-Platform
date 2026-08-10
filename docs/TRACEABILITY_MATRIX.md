# Requirements Traceability Matrix (RTM) — CoachOS

**Document version:** 1.0.0 (Phase 01 Baseline)  
**Last updated:** 2026-08-10  
**Purpose:** End-to-end traceability mapping product requirements -> epics -> user stories -> acceptance criteria -> personas -> domain API contracts -> delivery phases -> test strategies -> status.

---

## 1. Traceability Status Taxonomy
- `planned`: Requirement defined and scheduled for implementation in a future phase.
- `designed`: Architectural/UX specifications completed.
- `implemented`: Application code committed to codebase (future phases).
- `tested`: Verified via automated unit, integration, or E2E tests.
- `deferred`: Formally deferred to P1/P2 backlog by architectural decision.
- `accepted constraint`: Core non-negotiable system rule.

---

## 2. Core P0 MVP Traceability Matrix

| Req ID | Epic ID | User Story ID | Acceptance Criteria ID | Target Persona | Design & Spec Artifact | Domain Area | Target API Path | Planned Phase | Verification & Test Type | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| **FR-AUTH-01** | E1 | `US-AUTH-001` | `AC-AUTH-001` | All | `docs/PRD.md` §5 | Auth & Identity | `POST /api/v1/auth/register` | Phase 05 | Unit + Integration (Argon2 Hashing) | planned |
| **FR-AUTH-02** | E1 | `US-AUTH-002` | `AC-AUTH-002` | All | `docs/PRD.md` §5 | Auth & Identity | `POST /api/v1/auth/login` | Phase 05 | Integration + Rate Limit Test | planned |
| **FR-AUTH-03** | E1 | `US-AUTH-003` | `AC-AUTH-003` | All | `docs/PRD.md` §5 | Auth & Identity | `POST /api/v1/auth/password/reset-confirm` | Phase 05 | Token Single-Use Test | planned |
| **FR-ORG-01** | E1 | `US-ORG-001` | `AC-ORG-001` | `P-OWNER` | `docs/DATA_MODEL.md` §3.1 | Tenancy | `POST /api/v1/organizations` | Phase 05 | Multi-Tenant Scoping Test | planned |
| **FR-ORG-02** | E1 | `US-ORG-002` | `AC-ORG-002` | `P-OWNER` | `docs/DECISIONS.md` ADR-013 | Tenancy / Facility | `PATCH /api/v1/organizations/{id}/location` | Phase 05 | Integration (Single-Location MVP) | planned |
| **FR-ORG-03** | E1 | `US-ORG-003` | `AC-ORG-003` | `P-OWNER` | `docs/PRD.md` §5 | Tenancy / Invites | `POST /api/v1/organizations/{id}/invitations` | Phase 05 | Security (Token Expiration & Single-Use) | planned |
| **FR-ORG-04** | E1 | `US-ORG-004` | `AC-ORG-004` | `P-COACH` | `docs/PRD.md` §5 | Tenancy / Invites | `POST /api/v1/organizations/{id}/invitations` | Phase 05 | Integration (Assignment Linking) | planned |
| **FR-AUTHZ-01** | E1 | `US-ORG-005` | `AC-AUTHZ-001` | `P-OWNER` | `docs/SECURITY_AND_PRIVACY.md` §2 | Access Control | `PATCH /api/v1/organizations/{id}/members/{id}` | Phase 05 | **Negative AuthZ Test (Suspended Member Access Denied)** | planned |
| **FR-AUTHZ-02** | E1 | `US-ORG-005` | `AC-AUTHZ-002` | `P-COACH` | `docs/SECURITY_AND_PRIVACY.md` §2 | Access Control | `GET /api/v1/athletes/{id}/logs` | Phase 05 | **Negative AuthZ Test (Unassigned Coach Access Denied - 403)** | planned |
| **FR-AUTHZ-03** | E1 | `US-ORG-005` | `AC-AUTHZ-003` | All | `docs/SECURITY_AND_PRIVACY.md` §2 | Multi-Tenancy | `GET /api/v1/programs/{id}` | Phase 05 | **Negative AuthZ Test (Cross-Tenant Query Returns 404)** | planned |
| **FR-I18N-01** | E2 | `US-I18N-001` | `AC-I18N-001` | All | `docs/PRD.md` §5 | Localization | `GET /api/v1/auth/me` | Phase 04–07 | Visual E2E (Playwright RTL & LTR layout) | planned |
| **FR-I18N-02** | E2 | `US-I18N-001` | `AC-I18N-002` | All | `docs/DECISIONS.md` ADR-003 | Localization Policy | CI Lint Rules | All Phases | CI Policy Check (Zero Arabic locale files) | **accepted constraint** |
| **FR-I18N-03** | E2 | `US-I18N-002` | `AC-I18N-003` | `P-COACH` | `docs/DECISIONS.md` ADR-018 | Search & Indexing | `GET /api/v1/exercises?q=...` | Phase 06 | Unit Test (Perso-Arabic script keyboard-variant normalization for Persian search) | planned |
| **FR-EX-01** | E3 | `US-EX-001` | `AC-EX-001` | `P-COACH` | `docs/DATA_MODEL.md` §3.2 | Exercise Library | `GET /api/v1/exercises` | Phase 06 | Integration (Filtering by muscle/equipment) | planned |
| **FR-EX-02** | E3 | `US-EX-002` | `AC-EX-002` | `P-COACH` | `docs/DECISIONS.md` ADR-008 | Exercise Library | `POST /api/v1/exercises` | Phase 06 | Validation Test (Mandatory rights metadata) | planned |
| **FR-EX-03** | E3 | `US-EX-003` | `AC-EX-003` | `P-ADMIN` | `docs/PRD.md` §5 | Moderation | `POST /api/v1/admin/moderation/exercises/{id}/approve` | Phase 06 | Admin Security & Workflow Test | planned |
| **FR-PRG-01** | E4 | `US-PRG-001` | `AC-PRG-001` | `P-COACH` | `docs/DATA_MODEL.md` §3.3 | Program Builder | `POST /api/v1/programs` | Phase 06 | Schema Validation (Nested phase/workout tree) | planned |
| **FR-PRG-02** | E4 | `US-PRG-002` | `AC-PRG-002` | `P-COACH` | `docs/PRD.md` §5 | Templates | `POST /api/v1/programs/{id}/clone` | Phase 06 | Transactional Clone Test | planned |
| **FR-PRG-03** | E4 | `US-PRG-003` | `AC-PRG-003` | `P-COACH` | `docs/DECISIONS.md` ADR-015 | Versioning | `POST /api/v1/programs/{id}/assign` | Phase 06 | Snapshot Integrity Test (Frozen JSON copy) | planned |
| **FR-ATH-01** | E5 | `US-ATH-001` | `AC-ATH-001` | `P-ATH` | `docs/PRD.md` §5 | Athlete App | `GET /api/v1/athlete/today` | Phase 07 | Mobile E2E Test (Today view rendering) | planned |
| **FR-ATH-02** | E5 | `US-ATH-002` | `AC-ATH-002` | `P-ATH` | `docs/DATA_MODEL.md` §3.4 | Workout Logging | `POST /api/v1/workout-sessions/{id}/sets` | Phase 07 | Low-Bandwidth Logging & Rest Timer Test | planned |
| **FR-ATH-03** | E5 | `US-ATH-003` | `AC-ATH-003` | `P-ATH` | `docs/PRD.md` §5 | Workout Execution | `PATCH /api/v1/workout-sessions/{id}/items/{id}` | Phase 07 | Substitution Workflow Test | planned |
| **FR-ATH-04** | E5 | `US-ATH-004` | `AC-ATH-004` | `P-ATH` | `docs/PRD.md` §5 | Athlete Feedback | `POST /api/v1/workout-sessions/{id}/complete` | Phase 07 | Integration (Pain flag triggers coach alert) | planned |
| **FR-ATH-05** | E5 | `US-ATH-005` | `AC-ATH-005` | `P-ATH` | `docs/SECURITY_AND_PRIVACY.md` §1 | Sensitive Media | `POST /api/v1/athlete/photos` | Phase 07 | **Negative AuthZ Test (Unassigned User Denied Photo URL)** | planned |
| **FR-MSG-01** | E6 | `US-MSG-001` | `AC-MSG-001` | `P-COACH`, `P-ATH` | `docs/PRD.md` §5 | Communication | `POST /api/v1/messages` | Phase 08 | Contextual Reference Linking Test | planned |
| **FR-NTF-01** | E6 | `US-NTF-001` | `AC-NTF-001` | All | `docs/PRD.md` §5 | Notifications | `GET /api/v1/notifications` | Phase 08 | In-App Alert Delivery Test | planned |
| **FR-AUD-01** | E7 | `US-AUD-001` | `AC-AUD-001` | `P-ADMIN`, `P-OWNER` | `docs/SECURITY_AND_PRIVACY.md` §3 | Audit Trail | `GET /api/v1/admin/audit-logs` | Phase 05+ | Immutable Audit Log Verification Test | planned |
| **FR-PRI-01** | E7 | `US-PRI-001` | `AC-PRI-001` | `P-ATH` | `docs/SECURITY_AND_PRIVACY.md` §3 | Privacy Governance | `POST /api/v1/privacy/export-request` | Phase 03/13 | Machine-Readable Export Archive Test | planned |
| **FR-PRI-02** | E7 | `US-PRI-002` | `AC-PRI-002` | `P-ATH` | `docs/SECURITY_AND_PRIVACY.md` §3 | Privacy Governance | `POST /api/v1/privacy/forget-me` | Phase 03/13 | Anonymization Pipeline Test | planned |
| **FR-PWA-01** | E8 | `US-PWA-001` | `AC-PWA-001` | `P-ATH`, `P-COACH` | `docs/DECISIONS.md` ADR-011 | Mobile PWA | `/manifest.json`, Service Worker | Phase 04 | Lighthouse PWA Audit & Installability Test | planned |

---

## 3. P1 & P2 Backlog Traceability Index

| Backlog ID | Description | Priority Tier | Target Phase | Status |
|---|---|---|---|---|
| **P1-NUT-01** | Nutrition Professional Role & Consent-Based Access | P1 | Phase 09 | deferred |
| **P1-NUT-02** | Persian & International Food Catalog & Macro Calculator | P1 | Phase 09 | deferred |
| **P1-NUT-03** | Meal Plan Builder & Client Food Logging | P1 | Phase 09 | deferred |
| **P1-HAB-01** | Structured Daily Habits & Weekly Check-ins | P1 | Phase 07 / 09 | deferred |
| **P1-SCH-01** | 1:1 Session Scheduling & Calendar Booking | P1 | Phase 08 / 10 | deferred |
| **P1-PAY-01** | Payment Gateway Abstraction & Coach Subscriptions | P1 | Phase 10 | deferred |
| **P1-LOC-01** | Multi-Location Gym & Staff Management | P1 | Phase 10 | deferred |
| **P2-MKT-01** | Public Coach Marketplace & Discovery Directory | P2 | Phase 11+ | deferred |
| **P2-AI-01** | Constrained AI Workout Adaptation Copilot | P2 | Phase 11 | deferred |
| **P2-WRB-01** | Wearable Integrations (HealthKit, Health Connect) | P2 | Phase 12 | deferred |
| **P2-WHT-01** | Custom Branded Mobile Apps & White-Label Domains | P2 | Phase 12+ | deferred |
