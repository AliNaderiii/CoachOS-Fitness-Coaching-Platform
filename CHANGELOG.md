# Changelog

All notable changes to this project are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
This project will follow [Semantic Versioning](https://semver.org/) once the first versioned release is cut.

## [Unreleased]

### Added

- Phase 00 discovery documentation suite for greenfield CoachOS repository:
  - `README.md` project overview
  - `PROJECT_STATUS.md`, `PROJECT_CHECKLIST.md`
  - `docs/MASTER_PRODUCT_BRIEF.md`, `docs/PRD.md` (outline)
  - `docs/DECISIONS.md`, `docs/SECURITY_AND_PRIVACY.md`
  - `docs/DATA_MODEL.md`, `docs/API_CONTRACT.md` (outlines)
  - `docs/TRACEABILITY_MATRIX.md`, `docs/RELEASE_PLAN.md`
  - `docs/PROMPT_LOG.md`
  - `docs/reports/PHASE-00-DISCOVERY-REPORT.md`
  - Directory placeholders: `docs/architecture/`, `docs/ux/`, `docs/testing/`
- Explicit product constraint: **Persian (`fa-IR`) and English (`en-US`) only**; **Arabic out of scope**
- Proposed modular-monolith stack direction (Next.js, Django/DRF, PostgreSQL)
- Initial P0/P1/P2 scope boundaries and phased release plan

### Changed

- Replaced stub README (`# CoachOS-Fitness-Coaching-Platform`) with full project documentation entry point

### Notes

- No application source code, tests, or CI in this change set (documentation-only phase by design)

## [0.0.0] — 2026-08-10

### Added

- Initial GitHub repository commit by owner: MIT `LICENSE`, stub `README.md`
