# Changelog

All notable changes to this project are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
This project will follow [Semantic Versioning](https://semver.org/) once the first versioned release is cut.

## [Unreleased]

### Added

- **Phase 01 Product Requirements and Scope Package:**
  - `docs/PRD.md`: Full Product Requirements Document detailing product vision, business goals, measurable success metrics, complete INVEST-style P0 user stories with Gherkin acceptance criteria (positive and negative authorization scenarios), permissions matrix, prioritized P1/P2 backlogs, and non-functional requirements (WCAG 2.2 AA, security, performance).
  - `docs/PERSONAS.md`: 6 detailed user personas (Platform Administrator `P-ADMIN`, Gym/Organization Owner `P-OWNER`, Coach/Trainer `P-COACH`, Athlete/Client `P-ATH`, Nutrition Professional `P-NUT` [P1], Support Staff `P-SUP`).
  - `docs/USER_JOURNEYS.md`: 5 end-to-end user journeys with preconditions, step-by-step main flows, error states, and server-side permission checks.
  - `docs/DOMAIN_GLOSSARY.md`: Bilingual fitness, tenancy, localization, and privacy glossary in English and Persian (`fa-IR`).
  - `docs/COMPETITIVE_LANDSCAPE.md`: Public desk research benchmarking 10 platforms (ABC Trainerize, PT Distinction, Everfit, TrueCoach, My PT Hub, FITR, TrainHeroic, Exercise.com, Liaqa, Nutrium/Practice Better) and defining 8 differentiation hypotheses.
  - `docs/reports/PHASE-01-REQUIREMENTS-REPORT.md`: Comprehensive 27-section Phase 01 report with English and Persian executive summaries.
- **Decision Records & Scope Corrections (`docs/DECISIONS.md`):**
  - ADR-009: Calendar strategy (UTC/Gregorian storage with Persian Jalali UI display formatting for `fa-IR`).
  - ADR-011: PWA sequencing correction (Phase 04 foundation, Phase 07 mobile athlete execution validation, Phase 12 advanced offline/wearables/native).
  - ADR-012: License and IP evaluation (MIT vs Proprietary vs Open-Core vs Private Commercial) marked as **Pending Founder Approval**.
  - ADR-013: Single-location-first MVP strategy with P1 multi-location roadmap.
  - ADR-014 through ADR-022: Membership model, program versioning snapshots, archival lifecycle, UUIDv7 identifiers, Persian search normalization, data ownership, multi-pro collaboration, payment deferral, and marketplace deferral.
- **Architectural & Specification Enhancements:**
  - `docs/DATA_MODEL.md`: Updated entity models (single-location MVP, program snapshots, media rights provenance, feedback flags).
  - `docs/API_CONTRACT.md`: Versioned REST API endpoint specs, error envelopes, and authorization contracts for all P0 stories.
  - `docs/SECURITY_AND_PRIVACY.md`: Comprehensive 9-tier data classification taxonomy, privacy lifecycle, and threat model.
  - `docs/TRACEABILITY_MATRIX.md`: End-to-end mapping from requirements to stories, ACs, APIs, phases, and test types (including negative authZ tests).
  - `docs/RELEASE_PLAN.md`: Updated phased roadmap reflecting corrected PWA milestones and in-repo task backlog.

### Changed

- Updated `PROJECT_STATUS.md` to reflect post-merge state (PR #3 merged into `main` via commit `f52c413`) and Phase 01 completion.
- Updated `PROJECT_CHECKLIST.md` marking all Phase 01 deliverables complete.
- Updated `docs/PROMPT_LOG.md` logging PR #3 merge record and Prompt 002.
- Updated `docs/reports/PHASE-00-DISCOVERY-REPORT.md` with `Post-Phase-00 Merge Addendum`.

### Notes

- Documentation and requirements engineering only; **no application code, dependencies, or database migrations added** (by design).
- Language policy strictly preserved: Persian (`fa-IR`) and English (`en-US`) only; Arabic remains strictly out of scope.

## [0.0.1] — 2026-08-10

### Added

- Phase 00 discovery documentation suite for greenfield CoachOS repository (merged via PR #3, commit `f52c4134087b18c4bd1a8aef9e0100fd63f71b8e`).
- Explicit product constraint: **Persian (`fa-IR`) and English (`en-US`) only**; **Arabic out of scope**.
- Proposed modular-monolith stack direction (Next.js, Django/DRF, PostgreSQL).

## [0.0.0] — 2026-08-10

### Added

- Initial GitHub repository commit by owner: MIT `LICENSE`, stub `README.md`.
