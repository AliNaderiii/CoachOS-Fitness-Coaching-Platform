# Project Status — CoachOS

**Last updated:** 2026-08-18 (UTC)
**Current phase:** Phase 11 (Governed AI Copilot) — **merged and complete for its documented scope** (PR #21). The parallel 08–12 wave has otherwise merged: Phase 12 rode the same PR #21, Phase 10 via PR #20, and Phase 08 via PR #19; per-phase tracking syncs for Phases 08/10/12 are owned by their own sessions and may still be pending.
**Next step:** Phase 09 (nutrition and multi-professional collaboration) is the only remaining unstarted wave phase; it is **not started** and requires explicit founder authorization in a new dedicated branch. Do not start Phase 09 automatically.
**Working branch:** `arena/01a00a2c-coachos-fitness-coaching-platf` (environment-imposed Arena session branch for Phase 11, merged via PR #21; shared with the Phase 12 session in this wave)
**Base commit (main):** `326babce7bcfaae9e1c7d5f04e7d059e2e00af93` (PR #19 merge commit; verified current remote `main` at the time of this sync)
**Repository:** https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform
**License:** Proprietary / All Rights Reserved (ADR-012 — Copyright (c) 2026 CoachOS Technologies / Ali Naderi)

---

## 1. One-Line Status

**Phase 11 — Governed AI Copilot is merged and complete for its documented scope.** PR #21 merged into `main` at `6005936ab573df65a68de9b6266e9321506c7432` on 2026-08-18T16:22:09Z; post-merge CoachOS CI Quality Gates run `32159920173` and Security & Vulnerability Scan run `32159920192` on the merge SHA are successful. PR #21 came from the shared environment-imposed session branch and also carried Phase 12 — Durable Offline and Integrations (its own tracking sync is owned by the Phase 12 session). Sibling wave sessions merged Phase 10 via PR #20 (`8c1106a`) and Phase 08 via PR #19 (`326babce7bcfaae9e1c7d5f04e7d059e2e00af93`, verified current remote `main` at time of this sync). All Phase 11 stage gates passed (backend 167 tests / 86% coverage, frontend 84 tests, eval harness 16/16). Phase 09 is not started and is the only remaining unstarted wave phase.

---

## 2. Phase 06 Completion Evidence

| Evidence | Verified result |
|---|---|
| **Merge chain** | PR #13 merged at `d7f72b3fcfd6667df524af5adf71328c5de6edba`; PR #14 merged at `86503b3930192dd46de7ce500384c246d236fcd4`; PR #15 merged at `9e09c4785283ffd688e355cb9c1cf7af39c83d3c` |
| **OpenAPI** | OpenAPI 3.1 contract reconciled to 13 implemented Phase 06 operations; specification validated and all 191 local references resolved; Phase 07+ paths remain marked planned |
| **Backend** | 72 tests passed, including Phase 06 tenant, media-rights, assignment-snapshot, cross-tenant, and effective multi-role authorization coverage |
| **Frontend** | 59 tests plus lint, type-check, and production build passed under the unchanged Phase 05 frontend toolchain |
| **Final candidate validation** | Clean-checkout validation and PR/push Actions runs `31880019393`, `31880019224`, and `31880015763` succeeded |
| **Post-merge CI on `main`** | **CoachOS CI Quality Gates** run [`31888177718`](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31888177718) succeeded (backend, frontend, and security/language jobs); **Security & Vulnerability Scan** run [`31888175915`](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31888175915) succeeded (secret/pattern scan). Both are completed push runs on merge SHA `9e09c4785283ffd688e355cb9c1cf7af39c83d3c`. |
| **Scope boundary** | No Arabic resources and no Phase 07+ implementation were added |

Deferred items remain deferred: formal accessibility certification; device-matrix validation; penetration testing; production media storage, upload, signing, and transcoding; production `pg_trgm` load tuning; broader coach-athlete assignment lifecycle/UI; and every Phase 07+ domain.

---

## 2.5 Phase 07 — Implementation Summary (Athlete App and Progress Logging)

**Phase 07 is merged and complete for its documented scope via PR #17 at `0949abeead5ba74a3deb0d2439a464ab6bbd99dd`; post-merge CI and security runs on the merge SHA succeeded. Phase 08+ is not started.**

| Evidence | Result |
|---|---|
| **Models & migrations** | New `apps.execution` (`WorkoutSession`, `SetLog`, `Substitution`, `FeedbackFlag`, `BodyMetric`, `ProgressPhoto`, `ConsentRecord`) + migration `0001_initial.py`; audit action migration `0003_alter_auditevent_action.py`; all migrations apply cleanly |
| **Today dashboard** | `GET /api/v1/athlete/today` reads real authorized immutable assignment snapshots (loading/empty/error/forbidden/offline states) |
| **Session lifecycle** | Idempotent, race-safe start; detail/complete; active-membership + own-active-assignment gating; completed sessions immutable |
| **Set actuals** | One-handed logging with keyboard alternative, localized units, kg unit-conversion policy; set-index uniqueness/idempotency; bounded writes |
| **Substitution/Skip** | Mandatory reason persisted; replacement exercise visibility validated |
| **Feedback flags** | Subjective non-clinical pain/fatigue reports with severity/location; not diagnosis |
| **Progress metrics/photos** | Consent-gated (`ConsentRecord`), mock storage adapter, no public storage key, signed URLs only under active consent, revocation blocks reads/URLs, sensitive-view + consent-change audit |
| **Authorization** | Athlete self, assigned coach (consent-gated sensitive), owner (consent + audit escalation), support/unassigned/cross-tenant denied (safe 403/404), suspended denied |
| **PWA offline boundary** | Temporary in-memory preservation/retry only; no IndexedDB/localStorage/background sync (scope-scanner test enforces) |
| **Bilingual UI** | fa-IR RTL / en-US LTR parity (202 keys each); no Arabic; 44px touch targets; focus/keyboard/screen-reader/live regions |
| **Tests & gates** | Backend 106 tests (34 new execution; 85% coverage); frontend 75 tests (14 new); lint/type-check/build pass; OpenAPI 3.1 validates (88 local refs); Django routes match OpenAPI; security/language compliance passes |
| **Post-merge CI on `main`** | **CoachOS CI Quality Gates** run [`31940418392`](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31940418392) succeeded (backend, frontend, and security/language jobs); **Security & Vulnerability Scan** run [`31940418535`](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31940418535) succeeded (secret/pattern scan). Both are completed push runs on merge SHA `0949abeead5ba74a3deb0d2439a464ab6bbd99dd` (PR #17 merge commit). |
| **Report** | `docs/reports/PHASE-07-ATHLETE-APP-PROGRESS-REPORT.md` |
| **Scope boundary** | No Phase 08+ implementation, no Arabic, no production media storage |

---

## 2.6 Phase 11 — Implementation Summary (Governed AI Copilot)

**Phase 11 is merged and complete for its documented scope via PR #21 at `6005936ab573df65a68de9b6266e9321506c7432` (2026-08-18T16:22:09Z); post-merge CI and security runs on the merge SHA succeeded.** PR #21 is shared with Phase 12 — Durable Offline and Integrations (merged in the same wave from the same environment-imposed session branch); the Phase 12 evidence table is owned by the Phase 12 session's own sync. Phase 09 remains not started.

| Evidence | Result |
|---|---|
| **Merge chain** | Phases 11+12 via PR #21 at `6005936ab573df65a68de9b6266e9321506c7432`; Phase 10 via PR #20 at `8c1106a`; Phase 08 via PR #19 at `326babce7bcfaae9e1c7d5f04e7d059e2e00af93` (verified current `main` at time of this sync) |
| **Copilot domain** | New `apps.copilot`: `AIProviderAdapterConfig` (config only, no secrets), `PromptTemplateVersion` (seeded per capability, fa-IR + en-US), `AIRun`, `AIOutput` (draft/edited/approved/rejected/quarantined/expired states), `AISourceReference`, `AIFeedback`, `AIPolicyDecision`, immutable `AIAuditEvent`, `AIUsageMeter`; migration `0001_initial.py` + seed migration `0002_seed_defaults.py`; `makemigrations --check` reports no changes |
| **API (10 operations)** | `/api/v1/copilot/...` — run request (idempotent), run detail, context inspection, regenerate, edit, approve, reject, report-as-unsafe, feedback, and usage summary; professional roles (owner/coach) only; coach scope = own runs, owner scope = org runs; RFC 7807 + `message_key` error envelope |
| **Governance controls** | Draft-only output (nothing auto-applied or auto-sent); prohibited-topic blocking (medical diagnosis/treatment, injury, medication, supplement, eating-disorder, emergency); redaction before provider call; per-actor rate limit; org+actor daily run quotas; daily micro-USD budget cap; context retention window with `purge_copilot_runs` management command; org kill switch (`settings.copilot_disabled`); capability kill switch (`COPILOT_DISABLED_CAPABILITIES`); `COPILOT_ENABLED` env gate default **off** outside tests |
| **Provider seam** | Provider-neutral adapter Protocol with fail-closed registry; fake-deterministic provider as default/test double; **no live provider credentials, no outbound provider calls, no training on CoachOS data** |
| **Frontend console** | Coach Copilot console: capability run request, context inspection, draft result cards with source references, regenerate/edit/reject/report/approve actions; nav entries; fa-IR + en-US dictionary parity (+150 keys each); generation language explicit — never Arabic |
| **Evaluation harness** | `apps/copilot/eval`: 16 labeled synthetic cases on fabricated `*.synthetic.test` fixtures — **16/16 PASS**; proves control wiring, not model accuracy (stated explicitly in the report) |
| **Tests & gates** | Backend 167 tests (53 new copilot tests: 34 API + 9 security + eval harness gate; 86% coverage) and frontend 84 tests (9 new) passing; ruff lint/format, ESLint, `tsc` strict, and `next build` pass; OpenAPI bumped to v1.1.0-phase11 (10 `/copilot/*` operations, 98/98 local `$refs` resolve, Django routes reconciled 10/10); `infra/scripts/check-secrets.sh` ALL PASS |
| **Post-merge CI on `main`** | **CoachOS CI Quality Gates** run [`32159920173`](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/32159920173) succeeded; **Security & Vulnerability Scan** run [`32159920192`](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/32159920192) succeeded; pages deployment succeeded — all on PR #21 merge SHA `6005936ab573df65a68de9b6266e9321506c7432` |
| **Reports** | `docs/reports/PHASE-11-AI-COPILOT-REPORT.md`, `docs/reports/PHASE-11-AI-COPILOT-CONTRACTS.md`, `docs/architecture/AI_GOVERNANCE.md` |
| **Deferred (by decision)** | Live provider integration, async AI processing queue, athlete-erasure disassociation of AI records, admin audit UI, and any escalation beyond draft-only autonomy |
| **Scope boundary** | No Phase 08/09/10/12 functionality added by Phase 11; no message sending; no autonomous program/billing/consent mutation; no athlete-facing chatbot; no medical advice; no accuracy, provider zero-retention, HIPAA, GDPR, or certification claims |

---

## 3. Phase 04 Implementation Summary

| Area | Implemented Artifacts | Verification / Tests |
|---|---|---|
| **Monorepo Architecture** | `frontend/`, `backend/`, `infra/`, `docker-compose.yml`, `compose.yaml`, `.env.example`, `.gitignore` | Local development verified via Docker & direct runtime |
| **Frontend Shell** | Next.js 14.2 App Router, TypeScript strict, Tailwind logical CSS, dark obsidian theme (`#0B0F17`), placeholder dashboard screens clearly marked as foundation-only | 49 Vitest tests passing; Next.js static build verified (18 static pages generated) |
| **PWA Baseline** | `manifest.json`, `manifest.webmanifest`, `sw.js` (Cache-First static, Network-First navigation), 192px/512px maskable PNG icons, `/offline` page, `NetworkStatusBanner`, `InstallPromptBanner` | Manifest validation test passing; PWA icon dimension test passing; Service worker caching verified |
| **Bilingual RTL/LTR Engine** | Dynamic `lang` and `dir` on HTML root, `fa-IR` RTL, `en-US` LTR, BiDi text isolation (`<bdi>`), Persian search normalizer (`PersianNormalizer`), Jalali date conversion | i18n tests passing; dictionary 100% key parity; Jalali converter test passing |
| **Language Governance** | Strict exclusion of Arabic locale files (`ar-*.json`, `ar.json`, `ar.po`) across frontend and backend | `test_no_arabic.py` passing; `no-arabic.test.ts` passing; CI check-secrets scanner passing |
| **Backend REST API** | Django 5.2 + DRF 3.18, modular settings (`base`, `dev`, `staging`, `prod`, `test`), `CorrelationIDMiddleware`, `SecurityHeadersMiddleware`, `LoggingRedactionMiddleware`, `TenantContextMiddleware` | 37 Pytest tests passing; 78% overall test coverage (90%+ core) |
| **Fail-Closed Configuration** | Mandatory `DJANGO_SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`, `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` in production/staging | `test_fail_closed_settings.py` (10 tests passing) |
| **Secure Default Permissions** | `REST_FRAMEWORK` default permission class set to `IsAuthenticated`; public health endpoints opt in explicitly | `test_default_permissions.py` (3 tests passing) |
| **Safe Health Endpoints** | `GET /healthz` (200 OK liveness), `GET /readyz` (DB + Redis check), `GET /api/v1/meta` (safe public metadata) | `test_health.py`, `test_readyz.py`, `test_meta.py` passing |
| **Frontend CSP & Headers** | Environment-specific CSP (dev HMR vs production without `unsafe-eval`), object-src 'none', frame-ancestors 'none' | `security-headers.test.ts` (3 tests passing) |
| **Error Handling & Security** | RFC 7807 Problem Details envelope with `message_key`, zero internal stack traces in client responses, log redaction, HttpOnly session cookie config | `test_errors.py`, `test_drf_exceptions.py`, `test_security_headers.py`, `test_secret_leakage.py` passing |
| **Entity Identifiers** | Time-ordered UUIDv7 generator (`id_generator.py`) with validation | `test_uuidv7.py` passing; verified time-ordering trend |
| **CI Quality Gates (Active)** | `.github/workflows/ci.yml`, `.github/workflows/security-scan.yml` (canonical, on remote `main` via PR #10 merge `0855867c...`), mirrored definitions `infra/ci/ci.yml`, `infra/ci/security-scan.yml`, `infra/scripts/check-secrets.sh` | GitHub Actions active; post-merge runs on merge commit succeeded — CoachOS CI Quality Gates run `31776895893` (success), Security & Vulnerability Scan run `31776896050` (success) |
| **License & IP** | Transitioned to Proprietary / All Rights Reserved notice in `LICENSE` and ADR-012 | `LICENSE` file updated; ADR-012 accepted per founder mandate |
| **Hosting & Data Residency** | Comprehensive 10-dimension evaluation of PaaS, EU Cloud, Bare VPS, Dual-Region in `HOSTING_AND_DATA_RESIDENCY_DECISION.md` | Decision gate established; zero cloud credentials in Git |

---

## 4. Active Non-Negotiable Constraints

1. **Languages:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR) **only**.
2. **Arabic is strictly out of scope:** No Arabic locale files, translations, UI text, or requirements.
3. **No Marketplace, Payments, or Autonomous AI in P0:** Deferred to P1/P2 backlogs.
4. **B2B2C SaaS Model:** Organizations/coaches are paying customers; athlete accounts are free/included.
5. **PWA-First Delivery:** Level 1 Foundation (Phase 04 complete), Level 2 Athlete Execution (Phase 07), Level 3 Advanced Offline Sync (Phase 12).
6. **Single-Location MVP:** Organizations have a single primary facility in P0; multi-location in P1.
7. **Calendar Strategy:** UTC/Gregorian backend storage with Jalali UI rendering in `fa-IR` locale (ADR-009).
8. **No Secrets or Real Health Data in Repository:** Synthetic data only; verified via automated CI security scanner.
9. **License:** Proprietary / All Rights Reserved (ADR-012).

---

## 5. Risks, Blockers & Open Items

| ID | Item | Severity | Status & Action |
|---|---|---|---|
| **ADR-012** | Proprietary License Legal Review | Low | **Founder Decision Applied:** Proprietary notice in place; formal IP counsel review recommended prior to commercial launch. |
| **ADR-049** | Production Hosting Provider Selection | Medium | **Evaluation Complete:** Comparative matrix in `HOSTING_AND_DATA_RESIDENCY_DECISION.md`; production deployment gated until Phase 13 founder approval. |
| **TODO-CSP-001** | CSP Strict Nonce Migration | Low | Next.js development uses `'unsafe-inline'`; production eliminates `unsafe-eval`; migration to per-request cryptographic nonce planned before production pilot. |
| **LEGAL** | Privacy Compliance (GDPR & Iran Data Residency) | High | Formal pre-DPIA documented; jurisdiction-specific legal review required before handling real production health telemetry. |
| **P04-REMEDIATION** | Missing original `frontend/lib/` source | Low | **Closed — merged:** PR #8 (`dd7dea56945d96a6a2d595afb5154b6828c4e3b6`, 2026-08-11) merged the specification-based reimplementation; PR #9 (`0eae53b89343ec0a4eb1200086b769011012c406`, 2026-08-12) merged docs synchronization. All nine `frontend/lib/` files verified tracked on remote `main`. Provenance/correction record: `docs/reports/POST-MERGE-PHASE-04-FRONTEND-REIMPLEMENTATION-REPORT.md`. |
| **CI-ACTIVATION** | GitHub Actions activation | — | **Closed — PR #10 merged:** PR #10 (`chore/activate-github-actions-manual`) merged into `main` at `0855867cc85f56bb4b77c5f708db8e122ded6b81` (2026-08-14T06:36:42Z). `.github/workflows/ci.yml` and `.github/workflows/security-scan.yml` are present on remote `main`; GitHub Actions remain active and passing through the PR #17 merge commit (`0949abee...`), with post-merge runs `31940418392` and `31940418535` successful; no deployment job or real secret exists. |
| **P05-DEFERRED** | Phase 05 deferred scope | Low | **Open — deferred by decision:** Phase 05 merged complete for its documented scope via PR #13 (`d7f72b3fcfd6667df524af5adf71328c5de6edba`). Deferred items remain deferred pending later authorized phases: frontend onboarding UI, ownership transfer, full effective-permissions/active-org context, production email delivery, MFA, and compliance certification. Phase 06 supplied only the minimal tenant-scoped `CoachAthleteAssignment` relation required to authorize program assignment; broader lifecycle/UI remains deferred. |
| **P06-DEFERRED** | Phase 06 deferred scope | Low | **Open — deferred by decision:** Formal accessibility certification, device-matrix validation, penetration testing, production media storage/upload/signing/transcoding, production `pg_trgm` load tuning, broader assignment lifecycle/UI, and all Phase 07+ domains (at the time of the Phase 06 merge) remain deferred. None is implied complete by the Phase 06 merge; Phase 07 was subsequently authorized and merged for its documented scope via PR #17 — see P07-DEFERRED. |
| **P07-DEFERRED** | Phase 07 deferred scope | Low | **Open — deferred by decision:** Durable offline sync and conflict resolution (Phase 12), messaging/notifications (Phase 08), nutrition (Phase 09), billing/payments (Phase 10), AI (Phase 11), wearables, native apps, marketplace, production media storage/signing/transcoding, formal accessibility certification, device-matrix validation, and penetration testing remain deferred. None is implied complete by the Phase 07 merge. Since then, Phase 08 (PR #19), Phase 10 (PR #20), and Phases 11+12 (PR #21) were authorized and merged by their dedicated wave sessions; nutrition (Phase 09), wearables, native apps, marketplace, production media storage/signing/transcoding, formal accessibility certification, device-matrix validation, and penetration testing remain deferred — see P11-DEFERRED for Phase 11 residual deferrals. |
| **P11-DEFERRED** | Phase 11 deferred scope | Low | **Open — deferred by decision:** Phase 11 merged complete for its documented scope via PR #21 (`6005936ab573df65a68de9b6266e9321506c7432`). Deferred items remain deferred pending explicit authorization: live AI provider integration (requires provider agreement and fresh security/privacy review), async AI processing queue, athlete-erasure disassociation hook for AI-run records, admin audit UI for copilot runs, and any escalation beyond draft-only autonomy. No accuracy, medical-safety, provider zero-retention, HIPAA, or GDPR claims are made — see `docs/reports/PHASE-11-AI-COPILOT-REPORT.md` residual risks. |

---

## 6. Next Step

Phase 11 is merged and complete for its documented scope (PR #21); the parallel 08–12 wave has otherwise merged (Phase 12 via the same PR #21, Phase 10 via PR #20, Phase 08 via PR #19).

1. Current remote `main` is `326babce7bcfaae9e1c7d5f04e7d059e2e00af93` (PR #19 merge commit), verified at the time of this docs-only Phase 11 synchronization.
2. Post-merge GitHub Actions on the PR #21 merge SHA `6005936ab573df65a68de9b6266e9321506c7432` succeeded: **CoachOS CI Quality Gates** run `32159920173` and **Security & Vulnerability Scan** run `32159920192` (both `success`); pages deployment succeeded.
3. Phase 09 (nutrition and multi-professional collaboration) is the only remaining unstarted wave phase; it is **not started** and requires explicit founder authorization in a new dedicated branch. Do not begin Phase 09 automatically.
4. Phase 13 (QA, security, performance, release) and Phase 14 (pilot) remain pending; production deployment stays gated until Phase 13 founder approval. Per-phase tracking syncs for Phases 08, 10, and 12 are owned by their respective sessions.
