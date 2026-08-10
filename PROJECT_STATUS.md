# Project Status — CoachOS

**Last updated:** 2026-08-10 (UTC)  
**Current phase:** Phase 01 — Product Requirements and Scope (**complete**)  
**Next phase:** Phase 02 — UX, Information Architecture, and Design System  
**Working branch:** `arena/019febfc-coachos-fitness-coaching-platf`  
**Base commit (main):** `f52c4134087b18c4bd1a8aef9e0100fd63f71b8e` (PR #3 merged)  
**Repository:** https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform  
**License:** MIT (Review Pending Founder Decision — see ADR-012)  

---

## 1. One-Line Status

Phase 01 requirements package complete: detailed personas, user journeys, INVEST-style P0 user stories with Gherkin acceptance criteria, permissions matrix, NFR targets, domain glossary, competitive landscape, and decision records committed. **No application code exists yet (documentation-only phase).**

---

## 2. Post-Merge Repository State & Artifact Verification

| Area | Post-Merge State | Evidence / Artifact Link |
|------|------------------|--------------------------|
| Main Base Commit | `f52c4134087b18c4bd1a8aef9e0100fd63f71b8e` | PR #3 merged into `main` |
| Working Branch | `arena/019febfc-coachos-fitness-coaching-platf` | Active session working branch (PR #4 open) |
| Application Source (Frontend/Backend) | None (by design) | Verified empty via `find` / `git status` |
| Dependencies / Lockfiles | None (by design) | Verified |
| Database Migrations | None (by design) | Verified |
| Documentation Suite | Substantially expanded & complete | See section 4 inventory |
| LICENSE | MIT (pre-existing) | ADR-012 pending founder approval |

---

## 3. Active Non-Negotiable Constraints

1. **Languages:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR) **only**.
2. **Arabic is strictly out of scope:** No Arabic locale files, translations, UI text, or requirements.
3. **No Marketplace, Payments, or Autonomous AI in P0:** Deferred to P1/P2 backlogs.
4. **B2B2C SaaS Model:** Organizations/coaches are paying customers; athlete accounts are free/included.
5. **PWA-First Delivery:** Foundation in Phase 04, athlete validation in Phase 07, advanced offline in Phase 12.
6. **Single-Location MVP:** Organizations have a single primary facility in P0; multi-location in P1.
7. **Calendar Strategy:** UTC/Gregorian backend storage with Jalali UI rendering in `fa-IR` locale.
8. **No Secrets or Real Health Data in Repository:** Synthetic data only.

---

## 4. Documentation Inventory (Phase 01)

- `README.md`: Project overview and documentation index.
- `PROJECT_STATUS.md`: Active post-merge project status (this file).
- `PROJECT_CHECKLIST.md`: Master phase checklist.
- `CHANGELOG.md`: Keep-a-Changelog release history.
- `docs/MASTER_PRODUCT_BRIEF.md`: Core product brief.
- `docs/PRD.md`: Full product requirements document with P0 user stories, acceptance criteria, permissions matrix, NFRs, and P1/P2 backlogs.
- `docs/PERSONAS.md`: 6 comprehensive user personas.
- `docs/USER_JOURNEYS.md`: 5 end-to-end user journeys.
- `docs/DOMAIN_GLOSSARY.md`: Bilingual domain terminology glossary (English & Persian).
- `docs/COMPETITIVE_LANDSCAPE.md`: Public desk research benchmarking 10 competitor platforms.
- `docs/DECISIONS.md`: 22 ADRs and pending decision records.
- `docs/DATA_MODEL.md`: Conceptual and logical data model specifications.
- `docs/API_CONTRACT.md`: Versioned REST API endpoint contracts and error envelopes.
- `docs/SECURITY_AND_PRIVACY.md`: Security baseline, data classification taxonomy, and privacy lifecycle.
- `docs/TRACEABILITY_MATRIX.md`: End-to-end requirements traceability matrix.
- `docs/RELEASE_PLAN.md`: Phased delivery roadmap and in-repo milestone backlog.
- `docs/PROMPT_LOG.md`: Append-only history of prompts and actions.
- `docs/reports/PHASE-00-DISCOVERY-REPORT.md`: Phase 00 report with Post-Merge Addendum.
- `docs/reports/PHASE-01-REQUIREMENTS-REPORT.md`: Phase 01 comprehensive requirements report.

---

## 5. Summary of Scope Corrections

1. **PWA Phasing:** Corrected from deferring all PWA to Phase 12. Phase 04 now includes PWA manifest and shell; Phase 07 validates mobile execution; Phase 12 contains advanced offline/background sync.
2. **License Strategy:** Detailed evaluation of MIT vs Proprietary vs Open-Core vs Private Commercial recorded in ADR-012; flagged as **Pending Founder Approval**.
3. **Single-Location Scope:** Locked to 1 primary location per organization for MVP; multi-location management allocated to P1.
4. **Calendar Strategy:** Analyzed 3 options; recommended UTC/Gregorian backend storage with Persian Jalali UI formatting for `fa-IR` locale (ADR-009).

---

## 6. Risks, Blockers & Open Items

| ID | Risk / Decision Item | Severity | Status & Action |
|----|----------------------|----------|-----------------|
| **DEC-01** | Repository License Transition (ADR-012) | Medium | **Pending Founder Approval:** Founder to choose MIT vs Proprietary vs Open-Core. |
| **R01** | Brand Legal Name & Trademark | Low | Continue using CoachOS codename. |
| **R02** | Payment Gateway Provider Selection (P1) | High (P1) | Gateway abstraction designed (ADR-021); implementation in Phase 10. |
| **R03** | Exercise Media Copyright Clearance | High | Mandatory rights metadata schema enforced (ADR-008, US-EX-002). |
| **R04** | Health Data Regulatory Classification | High | Privacy baseline & consent hooks designed; legal counsel TODO before live pilot. |

---

## 7. Next Step

Awaiting founder review of Phase 01. Next execution phase:
**Phase 02 — UX, Information Architecture, and Design System**
