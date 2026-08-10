# Testing docs

This directory will hold test strategy, pyramid, critical path matrices, accessibility checks, and performance baselines.

**Status:** Empty pending foundation (Phase 04) and expanded in Phase 13.

Target layers:

| Layer | Tools (proposed) |
|-------|------------------|
| Backend unit/integration | Pytest + Django/DRF test client |
| Frontend unit/component | Vitest/Jest + Testing Library |
| E2E | Playwright (fa-IR and en-US) |
| API contract | OpenAPI validation / schemathesis (candidate) |
| Security | dependency scan, authZ negative tests |
| a11y | axe + manual RTL review |

No production tests exist yet (greenfield as of Phase 00).
