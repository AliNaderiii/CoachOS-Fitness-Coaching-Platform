# Changelog

All notable changes to this project are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
This project will follow [Semantic Versioning](https://semver.org/) once the first versioned release is cut.

## [Unreleased]

### Added

- **Phase 02 UX, Information Architecture, and Design System Package:**
  - `docs/ux/INFORMATION_ARCHITECTURE.md`: Role-based information architecture, routing hierarchy, and site map covering athlete, coach, owner, and admin workspaces.
  - `docs/ux/NAVIGATION_MODEL.md`: Multi-device navigation paradigms (mobile bottom navigation, active workout canvas, desktop collapsible sidebar, breadcrumbs, dual-pane builder).
  - `docs/ux/SCREEN_INVENTORY.md`: Comprehensive inventory and technical specifications for 34 P0 screens.
  - `docs/ux/USER_FLOWS.md`: Step-by-step user flows with Mermaid sequence and flowchart diagrams for owner onboarding, coach programming, athlete workout execution, and admin moderation.
  - `docs/ux/WIREFRAMES.md`: Detailed bidirectional ASCII wireframes for core athlete and coach screens in both English LTR and Persian RTL (mirrored).
  - `docs/ux/DESIGN_SYSTEM.md`: Core design principles, component library specifications (buttons, inputs, datepickers, program tree nodes, consent dialogs, rest timers).
  - `docs/ux/DESIGN_TOKENS.md`: Visual tokens (colors, dark obsidian canvas, typography, 4px spacing scale, elevation, z-index, motion) with WCAG 2.2 AA contrast validation tables.
  - `docs/ux/RTL_LTR_SPECIFICATION.md`: CSS logical properties, bidirectional mirroring rules, mixed-direction BiDi isolation (`<bdi>`), and Persian character normalization.
  - `docs/ux/RESPONSIVE_BEHAVIOR.md`: 6-tier breakpoint taxonomy, one-handed mobile gym floor ergonomics, natural thumb zone analysis, and component reflows.
  - `docs/ux/ACCESSIBILITY_SPEC.md`: WCAG 2.2 Level AA compliance specifications, modal focus trapping, ARIA live announcements, and 10-point test checklist.
  - `docs/ux/STATE_AND_ERROR_MATRIX.md`: 8-state handling matrix and progressive offline PWA matrix across Phase 04/07/12.
  - `docs/ux/UX_COPY.md`: Non-clinical bilingual microcopy dictionary and content guidelines in English and Persian.
  - `docs/ux/UX_TRACEABILITY_MATRIX.md`: 1:1 mapping from all 29 P0 user stories to UX specifications.
  - `docs/ux/UX_RESEARCH_AND_ASSUMPTIONS.md`: Hypothesis categorization, research questions by persona, and pilot usability protocol.
  - `docs/reports/PHASE-02-UX-DESIGN-REPORT.md`: Comprehensive 31-section Phase 02 completion report with English and Persian executive summaries.
- **UX Architecture Decision Records (`docs/DECISIONS.md`):**
  - ADR-023: Athlete mobile navigation & full-screen active workout canvas pattern.
  - ADR-024: Coach program builder desktop dual-pane master-detail pattern.
  - ADR-025: Persian typography strategy using Vazirmatn variable web font.
  - ADR-026: Non-clinical UX language standard for subjective feedback.
  - ADR-027: Explicit affirmative consent interaction model for sensitive photos.
  - ADR-028: Dark-neutral visual theme for mobile gym-floor glare reduction.

### Changed

- Updated `PROJECT_STATUS.md` reflecting Phase 02 completion and post-merge base commit `3921083`.
- Updated `PROJECT_CHECKLIST.md` marking all Phase 02 deliverables complete with evidence links.
- Updated `docs/RELEASE_PLAN.md` marking Milestone M2 complete.

### Notes

- Documentation and design specifications only; **zero application source code, dependencies, or database migrations added** (by design).
- Strict language constraint: Persian (`fa-IR`) and English (`en-US`) only; Arabic remains strictly out of scope.

## [0.0.2] — 2026-08-10

### Added

- Phase 01 Product Requirements and Scope Package (merged via PR #4, commit `392108372450dc8a40fe79c6201144733955b7c0`).
- 22 Architecture Decision Records (ADR-001 through ADR-022).
- Personas (`docs/PERSONAS.md`), user journeys (`docs/USER_JOURNEYS.md`), domain glossary (`docs/DOMAIN_GLOSSARY.md`), and competitive landscape (`docs/COMPETITIVE_LANDSCAPE.md`).

## [0.0.1] — 2026-08-10

### Added

- Phase 00 discovery documentation suite for greenfield CoachOS repository (merged via PR #3, commit `f52c4134087b18c4bd1a8aef9e0100fd63f71b8e`).
- Explicit product constraint: **Persian (`fa-IR`) and English (`en-US`) only**; **Arabic out of scope**.
- Proposed modular-monolith stack direction (Next.js, Django/DRF, PostgreSQL).

## [0.0.0] — 2026-08-10

### Added

- Initial GitHub repository commit by owner: MIT `LICENSE`, stub `README.md`.
