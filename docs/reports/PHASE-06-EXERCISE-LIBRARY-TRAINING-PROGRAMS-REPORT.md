# Phase 06 — Exercise Library and Training Programs Report

**Date:** 2026-08-14
**Base SHA:** `86503b3930192dd46de7ce500384c246d236fcd4`
**Branch:** `arena/019fffa4-coachos-fitness-coaching-platf`
**Original reviewed head:** `368fe57e2a6901c41a3aa24044770c4891a050e8`
**Corrected implementation SHA:** `f962478ee8a91f13fa65828cbf5b7519fbf955e3`
**Pull request:** [#15](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/15) — open, mergeable, targeting `main`

**Status:** The unapproved frontend toolchain migration is removed. Corrected isolated-checkout and published-head GitHub Actions validation pass under the unchanged Phase 05 baseline. PR #15 remains open and Phase 06 is **not merged and not declared complete**.

## 1. Safe recovery evidence

The requested initial inspection was performed before modification:

- `git status --short --branch`: `## arena/019fffa4-coachos-fitness-coaching-platf` (no changed/untracked paths)
- `git rev-parse HEAD`: `86503b3930192dd46de7ce500384c246d236fcd4`
- `git log --oneline --decorate -20`: HEAD/current `origin/main` at `86503b3`; checkout was shallow at the verified merge commit
- `git diff --stat`: empty
- `git diff --check`: empty, exit 0

No interrupted Phase 06 diff, report, Stage 0 plan, app, migration, test, or Stage 7 frontend source existed in this checkout. Nothing was reset, cleaned, force-pushed, deleted, or falsely treated as a passed gate. `git fetch origin main` confirmed `origin/main` and merge-base at the same base SHA; `gh pr list` confirmed no Phase 06 PR.

## 2. Gate results

| Gate | Result | Evidence |
|---|---|---|
| 0 — plan/matrix | Pass | `PHASE-06-STAGE-0-PLAN.md` records recovery, scope boundary, sequential gates, and PRD/ADR traceability. |
| 1 — exercise schema | Pass | `Exercise`, translation, alias, media, and rights models; migration `exercises/0001_initial.py`; model/API tests. |
| 2 — bilingual search | Pass | `fa-IR`/`en-US` exact requirement, normalized indexed names/aliases, `ي→ی`/`ك→ک` query folding, search/filter tests. |
| 3 — provenance/moderation | Pass | One-to-one rights, license/source/reviewer validation, commercial-use publication gate, private storage keys write-only, platform-admin moderation and audit tests. |
| 4 — hierarchy | Pass | Atomic Program → Phase → Week → Day → Workout → Item → SetPrescription creation/replacement and sibling-order constraints. |
| 5 — templates/version/snapshot | Pass | Deep clone independence, edit version increment, ordered server snapshot, model-level snapshot payload immutability test. |
| 6 — API/authz/tenancy | Pass | Active owner/coach controls, athlete/suspended denial, canonical+current tenant visibility, cross-tenant 404/403, owner/linked-coach assignment policy, bounded-query tests. |
| 7 — frontend | Pass | Coach/owner responsive dual-pane workspace, bilingual catalog filtering, normalized Persian search, prescription controls, keyboard reorder alternatives, dictionaries/tests; clean `npm ci`, lint, type-check, 56 tests, build. |
| 8 — adversarial review | Pass under corrected baseline | Domain negative tests, repository scanner, localization tests, baseline lint, and accessibility-target tests pass. No dependency-audit remediation is claimed in Phase 06. |
| 9 — docs/clean validation/PR/checks | Pass; founder review pending | Fresh isolated clone of corrected implementation SHA `f962478e…` passed all required commands. Corrected published head `2d904736…` passed pull-request runs `31879015578`/`31879015703` and push run `31879013603`. PR remains open. |

## 3. Delivered behavior

### Exercise catalog

- Canonical (`organization_id = NULL`) plus organization-private visibility, always intersected with active membership.
- Exactly two translation resources per API-created exercise: Persian and English only.
- Raw aliases plus normalized indexed aliases and names.
- Search normalizes Perso-Arabic keyboard variants without adding Arabic localization.
- Muscle, equipment, movement, difficulty, and locale filters; response cap of 100.
- Owner/coach private exercise creation; athletes and suspended users denied.
- Media asset checksum/relative-private-key validation; storage keys are write-only in API responses.
- Mandatory rights for every attached asset; non-original source URL and commercial permission enforced.
- Platform-admin pending queue, approve/reject transaction, rights review stamp, and immutable audit events. Admin MFA remains a pre-existing deferred identity capability and is not claimed.

### Training programs

- Organization-scoped nested program hierarchy and set targets for reps/load/RPE/RIR/tempo/rest.
- Atomic nested create and full-tree replacement; program version increments on edits.
- Deep organization template clone with independent IDs and child records.
- Minimal `CoachAthleteAssignment` authorization relation used only to gate assignment; no execution/logging semantics.
- Owner assignment to active tenant athletes; coaches only to active linked athletes.
- Complete ordered JSON snapshot with schema/source version; source changes do not alter it and model save rejects payload mutation.
- No `WorkoutSession`, `SetLog`, calendar execution, timer, pain/fatigue, or durable offline implementation.

### Coach/owner frontend

- Responsive master/detail program workspace under both `/fa-IR/coach/programs` and `/en-US/coach/programs`.
- Persian-normalized bilingual catalog search, equipment filter, selected exercise and prescription editing preview.
- Semantic tree, live result count, visible focus inherited from design system, 44px controls, and button alternatives to drag-and-drop.
- Typed training API adapter for catalog list, program create, and clone.
- The Phase 06 UI is adapted to the unchanged Phase 05 frontend baseline: Next.js 14.2.35, the existing React/TypeScript/Vite/Vitest versions, `.eslintrc.json`, and `next lint`. No lint rules are disabled and no generated/config route-type migration remains.

## 4. Migrations

1. `backend/apps/exercises/migrations/0001_initial.py`
   - Exercise, ExerciseTranslation, ExerciseAlias, MediaAsset, MediaRights
   - visibility/filter/search indexes and locale/alias uniqueness constraints
2. `backend/apps/programs/migrations/0001_initial.py`
   - Program hierarchy, WorkoutItem, SetPrescription, CoachAthleteAssignment, ProgramAssignment
   - tenant/assignment indexes and sibling-order uniqueness constraints

Evidence:

```text
python manage.py makemigrations --check --dry-run -> No changes detected
python manage.py migrate --noinput -> exercises.0001_initial OK; programs.0001_initial OK
python manage.py check -> System check identified no issues (0 silenced)
```

## 5. Backend validation

Environment: isolated repository-local virtual environment, Python 3.11.2, Django 5.2.17.

```text
ruff check .                                           -> All checks passed
ruff format --check .                                  -> 66 files already formatted
python manage.py check                                 -> 0 issues
python manage.py makemigrations --check --dry-run      -> No changes detected
pytest --cov=apps --cov=config --cov-report=term-missing
                                                       -> 69 passed in 3.51s; 83% total coverage
pytest tests/exercises tests/programs -q -k
  'tenant or role or suspens or media or moderation or query or coach'
                                                       -> 8 passed, 5 deselected
pip-audit -r requirements.txt -r requirements-dev.txt  -> No known vulnerabilities found
```

Phase 06-specific final targeted suite: **14 tests passed** (8 exercise + 6 program). Full suite: **69 passed**.

Bounded-query assertions: catalog list ≤9 SQL queries for five exercises; nested program detail ≤15 SQL queries.

## 6. Frontend validation

Baseline-preserving local correction validation:

```text
npm ci              -> baseline lockfile installed (562 packages)
npm run lint        -> Next.js 14 `next lint`; no warnings/errors
npm run type-check  -> exit 0 under baseline TypeScript
npm test            -> Vitest 1.6.0; 12 files and 56 tests passed
npm run build       -> Next.js 14.2.35; 18 static pages generated
```

`npm ci` reports the known baseline dependency-audit findings. Phase 06 does not alter dependencies or claim to remediate them; any major toolchain/security migration requires a separate proposal and review.

### Isolated clean-checkout validation

A fresh clone of corrected implementation SHA `f962478ee8a91f13fa65828cbf5b7519fbf955e3` was created at `/tmp/coachos-pr15-corrected-validation` without copied dependency directories. A new Python virtual environment and baseline `npm ci` install were used. Backend Ruff/format/check/migration drift/69 tests, frontend baseline `next lint`/type-check/Vitest 1.6.0 56 tests/Next.js 14.2.35 build, and repository compliance all passed. Final clone status was clean. The earlier Next.js 16 validation is superseded and not acceptance evidence.

## 7. Stage 8 adversarial review

- **Authentication/authorization:** all APIs retain authenticated-active defaults; mutation requires active owner/coach; platform moderation requires `is_platform_admin`; athletes/suspended users denied.
- **Tenant isolation:** private exercise and all program queries are organization-scoped after active membership checks; foreign detail is concealed with 404 where applicable; negative tests cover separate tenants.
- **Assignment isolation:** owner policy and active coach-athlete relationship are checked server-side in the transaction; request headers cannot authorize access.
- **Media rights/security:** source required for non-original assets; commercial use required before publication; reviewer must be platform admin; private object keys reject URL/absolute/traversal syntax and are not returned.
- **Snapshot integrity:** server-generated only and mutation rejected after insertion; assignment and source organization must match.
- **Query count:** explicit bounded-query tests pass; deep reads use prefetches; list response caps are present.
- **Localization:** dictionary key parity test passes; scanner finds no Arabic locale resources; normalizer behavior does not imply Arabic product support.
- **Accessibility target:** semantic labels/tree/live status, keyboard alternatives, focus design, logical CSS, RTL/LTR tests, and minimum touch controls are covered. Formal WCAG certification and device/manual screen-reader testing remain Phase 13 validation work.
- **Supply chain/secrets:** repository scanner and `pip-audit` passed. Frontend dependencies are restored byte-for-byte to the Phase 05 baseline; its existing npm audit findings are not silently remediated or presented as Phase 06 success.

## 8. Exact implementation file inventory

### Added

- `backend/apps/exercises/{__init__.py,apps.py,models.py,serializers.py,urls.py,views.py}`
- `backend/apps/exercises/migrations/{__init__.py,0001_initial.py}`
- `backend/apps/programs/{__init__.py,apps.py,models.py,serializers.py,urls.py,views.py}`
- `backend/apps/programs/migrations/{__init__.py,0001_initial.py}`
- `backend/tests/exercises/test_exercise_api.py`
- `backend/tests/programs/test_program_api.py`
- `frontend/components/training/TrainingWorkspace.tsx`
- `frontend/lib/api/training.ts`
- `frontend/tests/training-workspace.test.tsx`
- `docs/reports/PHASE-06-STAGE-0-PLAN.md`
- this report

### Modified/replaced

- `backend/apps/core/urls.py`
- `backend/config/settings/base.py`
- `frontend/app/[locale]/(app)/coach/programs/page.tsx`
- `frontend/lib/i18n/dictionaries/en-US.json`
- `frontend/lib/i18n/dictionaries/fa-IR.json`
- `PROJECT_STATUS.md`, `PROJECT_CHECKLIST.md`, `CHANGELOG.md`, `docs/PROMPT_LOG.md`

## 9. Deferred and explicitly excluded

- Platform-admin MFA (identity/security roadmap prerequisite) and admin moderation UI; moderation API is present.
- Real object upload/signing/thumbnail processing; only metadata/provenance and safe private keys are implemented.
- PostgreSQL `pg_trgm` relevance/GIN optimization; deterministic normalized indexed matching is implemented and tested portably. Production load tuning remains later performance validation.
- Formal WCAG 2.2 AA certification, manual screen-reader/device matrix, penetration testing, and production hosting validation remain Phase 13.
- Frontend active-organization/session wiring remains dependent on the broader onboarding/effective-org context; the typed API boundary and coach/owner workspace are present.

No Arabic localization and no Phase 07+ code was added. Specifically absent: workout execution, actual-set logging, timers, pain/fatigue, advanced offline sync, messaging, nutrition, billing, marketplace, AI, and wearables.

## 10. Review correction record

The original PR head included an unapproved major frontend dependency/configuration migration. During correction, an Arena workspace materialized the PR diff as uncommitted files while local HEAD was the base SHA. That complete state was preserved in stash `preserve-materialized-pr15-before-review-correction-2026-08-14`, the remote PR branch was fetched and fast-forwarded without reset or force, and baseline frontend files were restored from `origin/main`.

Restored unchanged relative to Phase 05: `package.json`, `package-lock.json`, `.eslintrc.json`, `tsconfig.json`, `next-env.d.ts`, and locale layout parameter typing. `eslint.config.mjs` is removed. No baseline lint rule is disabled.

## 11. Publication record

- PR: https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/15
- State at verification: `OPEN`, non-draft, `MERGEABLE`, base `main`, head `arena/019fffa4-coachos-fitness-coaching-platf`
- Published head verified: `a2d8b0a42d2e374290101d1112f9132ca08b3165`
- Pull-request Security & Vulnerability Scan `31790374656`: success
- Pull-request CoachOS CI Quality Gates `31790374657`: success (backend, frontend, language compliance)
- Push CoachOS CI Quality Gates `31790363694`: success
- **Corrected baseline-preserving head `2d90473651de2e94b1a3aca375c7552a1edb3e81`:** Security run `31879015578`, pull-request CI `31879015703`, and push CI `31879013603` all succeeded. These corrected runs supersede the original toolchain-migration checks.
- Non-blocking GitHub annotation: GitHub-hosted actions using Node.js 20 internals are forced to Node.js 24; application checks still succeeded. Workflow action-major modernization is deferred maintenance.

The PR remains open for founder review and was not merged by this session.
