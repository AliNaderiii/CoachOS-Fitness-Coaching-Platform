# Traceability Matrix — CoachOS

**Last updated:** 2026-08-10  
**Purpose:** Map requirements → design → implementation → tests → evidence  

Status: `planned` | `designed` | `implemented` | `tested` | `deferred` | `blocked`

---

## Legend

| Column | Meaning |
|--------|---------|
| Req ID | From PRD |
| Description | Short text |
| Priority | P0/P1/P2 |
| Phase | Delivery phase |
| Design docs | Spec links |
| Impl | Code paths (future) |
| Tests | Test paths (future) |
| Evidence | Report/PR/commit |
| Status | Current |

---

## P0 requirements

| Req ID | Description | Priority | Phase | Design docs | Impl | Tests | Evidence | Status |
|--------|-------------|----------|-------|-------------|------|-------|----------|--------|
| FR-AUTH-01 | Register and authenticate | P0 | 05 | PRD, SECURITY | — | — | Phase 00 scoped | planned |
| FR-AUTH-02 | Password reset or OTP | P0 | 05 | PRD, ADR-005 | — | — | Phase 00 scoped | planned |
| FR-ORG-01 | Create organization | P0 | 05 | PRD, DATA_MODEL | — | — | Phase 00 scoped | planned |
| FR-ORG-02 | Invite coaches/athletes | P0 | 05 | PRD | — | — | Phase 00 scoped | planned |
| FR-AUTHZ-01 | Server-side RBAC | P0 | 05 | ADR-006, SECURITY | — | — | Phase 00 scoped | planned |
| FR-AUTHZ-02 | Coach limited to assigned athletes | P0 | 05 | ADR-006 | — | — | Phase 00 scoped | planned |
| FR-I18N-01 | fa-IR RTL + en-US LTR UI | P0 | 04–07 | ADR-003, brief | — | — | Phase 00 constraint recorded | planned |
| FR-I18N-02 | No Arabic locale/resources | P0 | all | ADR-003 | n/a | policy | Phase 00 report | **accepted constraint** |
| FR-EX-01 | Bilingual exercises + search | P0 | 06 | DATA_MODEL | — | — | Phase 00 scoped | planned |
| FR-EX-02 | Media rights metadata | P0 | 06 | ADR-008 | — | — | Phase 00 scoped | planned |
| FR-PRG-01 | Program builder hierarchy | P0 | 06 | DATA_MODEL | — | — | Phase 00 scoped | planned |
| FR-PRG-02 | Assign program to athlete | P0 | 06 | DATA_MODEL | — | — | Phase 00 scoped | planned |
| FR-ATH-01 | Today workout view | P0 | 07 | PRD | — | — | Phase 00 scoped | planned |
| FR-ATH-02 | Log set actuals | P0 | 07 | PRD | — | — | Phase 00 scoped | planned |
| FR-MSG-01 | Coach–athlete threads | P0 | 08 | PRD | — | — | Phase 00 scoped | planned |
| FR-NTF-01 | In-app notifications + prefs | P0 | 08 | PRD | — | — | Phase 00 scoped | planned |
| FR-ADM-01 | Exercise moderation | P0 | 06+ | PRD | — | — | Phase 00 scoped | planned |
| FR-AUD-01 | Audit sensitive actions | P0 | 05+ | SECURITY | — | — | Phase 00 scoped | planned |
| FR-PRI-01 | Export/deletion design | P0 | 03/13 | SECURITY | — | — | Phase 00 baseline | planned |
| NFR-SEC-01 | TLS, hashing, no secrets in git | P0 | 04+ | SECURITY | — | — | Phase 00 policy | planned |
| NFR-API-01 | Versioned API + OpenAPI | P0 | 03–04 | API_CONTRACT | — | — | Phase 00 strategy | planned |
| NFR-TEST-01 | Unit+API+E2E before pilot | P0 | 13 | — | — | — | Phase 00 plan | planned |

## P1+ (index only until activated)

| Req ID | Description | Priority | Phase | Status |
|--------|-------------|----------|-------|--------|
| FR-NUT-01 | Nutrition professional features | P1 | 09 | deferred |
| FR-PAY-01 | Billing and packages | P1 | 10 | deferred |
| FR-AI-01 | AI copilot human-reviewed | P2 | 11 | deferred |
| FR-PWA-01 | PWA install + offline scope | P1/P2 | 12 | deferred |

## Phase 00 discovery evidence

| Item | Evidence | Status |
|------|----------|--------|
| Repository audit | `docs/reports/PHASE-00-DISCOVERY-REPORT.md` | tested (inspection) |
| Vision recorded | `docs/MASTER_PRODUCT_BRIEF.md` | complete |
| Language constraint | ADR-003, README, brief | complete |
| Checklist created | `PROJECT_CHECKLIST.md` | complete |

## Update rule

Every completed story in later phases must add impl path, test path, and evidence link before checklist item is marked `[x]`.
