# Release Plan and Phased Delivery Strategy — CoachOS

**Document version:** 2.1.0 (Phase 04 Foundation Finalized)  
**Last updated:** 2026-08-11  
**Delivery Model:** Iterative Phased Delivery (Phases 00–14) with strict P0 / P1 / P2 product scope gates.  
**Phase 04 Update:** Milestone M4 Foundation & PWA Baseline now complete — runnable monorepo with Next.js 14, Django 5/DRF, PostgreSQL 16, Redis 7, PWA manifest, service worker, bilingual RTL/LTR engine, CI quality gates, and safe health endpoints.

---

## 1. Phased Delivery Roadmap & Exit Criteria

| Phase | Phase Name | Scope Tier | Core Deliverables & Exit Criteria |
|---|---|---|---|
| **Phase 00** | Discovery & Audit | Baseline | Complete repository audit; vision; fa/en-only policy; baseline docs — **COMPLETED** PR #3 |
| **Phase 01** | Product Requirements & Scope | P0 Spec | Complete personas, journeys, P0 user stories with Gherkin ACs, NFR targets, updated PRD, RTM — **COMPLETED** PR #4 |
| **Phase 02** | UX, Information Architecture & Design System | P0 Design | Navigation architecture, wireframes (34 screens exact), 14 UX spec docs, Persian RTL & English LTR design tokens, WCAG 2.2 AA design target, PWA offline boundary documented — **COMPLETED** PR #5 |
| **Phase 03** | Architecture, Data, Security & Privacy | P0 Arch | Final ADRs (43 ADRs), normalized PostgreSQL ERDs, C4 system/context/container, domain boundaries 20 modules, server-side RBAC/ABAC + consent matrix, threat model STRIDE 21 threats + control matrix, privacy lifecycle Tier0-8 + pre-DPIA, OpenAPI 3.1 provisional /api/v1, media storage private signed TTL≤15min, PWA three-level, observability + backup/DR RPO/RTO proposed — **COMPLETED** PR #6 |
| **Phase 04** | Project Foundation & PWA Baseline | P0 Eng | Next.js 14 + Django 5/DRF monorepo scaffold, CI/CD pipeline, health checks (/healthz, /readyz, /api/v1/meta), **PWA foundation (Manifest, installable shell, SW, offline page)** — **COMPLETED** (this phase) |
| **Phase 05** | Identity, Tenancy & Access Control | P0 Core | User auth, single-location MVP orgs, email invites, server-side RBAC/ABAC tests, audit log pipeline |
| **Phase 06** | Exercise Library & Program Builder | P0 Core | Bilingual exercise catalog, Persian search folding, media rights metadata, hierarchical program builder, templates |
| **Phase 07** | Athlete Mobile App & Progress Logging | P0 Core | Mobile Today view, one-handed set logging, rest timer, pain/fatigue feedback, **installed PWA mobile validation** |
| **Phase 08** | Communication & Notifications | P0 Core | Contextual 1:1 coach-athlete message threads, in-app notification engine, notification preferences |
| **Phase 09** | Nutrition & Multi-Pro Collaboration | P1 Backlog | Nutritionist role, consent-governed collaboration, Persian/international food catalog, meal plans, food logging |
| **Phase 10** | Billing & Coach Monetization | P1 Backlog | Abstracted payment provider adapters (Shetab domestic / Stripe international), subscription tiers, coach storefront |
| **Phase 11** | Constrained AI Copilot & Safety | P2 Backlog | Human-reviewed workout adaptation copilot, approved retrieval databases, zero autonomous medical claims |
| **Phase 12** | Advanced Offline PWA & Integrations | P2 Backlog | Advanced offline sync queues, IndexedDB conflict resolution, background sync, wearable integration review |
| **Phase 13** | QA, Security, Performance & Release | Pilot Prep | Comprehensive E2E suites, RTL visual regression, penetration testing, performance benchmarking, staging deploy |
| **Phase 14** | Pilot Operations & Iteration | Validation | Live pilot cohort (gyms, coaches, athletes), metric collection, user feedback, post-pilot roadmap |

---

## 2. PWA Phasing & Sequencing Architecture

CoachOS follows a progressive PWA deployment strategy:
1. **Phase 04 (Foundation):**
   - Web App Manifest (`manifest.json`) configuration (standalone display, icons, theme colors).
   - Mobile-first responsive viewport and shell layout.
   - Base Service Worker registration for offline asset shell caching.
   - PWA-aware routing and offline network fallback screen.
2. **Phase 07 (Athlete App Validation):**
   - Mobile workout execution and touch-optimized set logging.
   - Rest countdown timer with local notifications.
   - Verification of installed-PWA mobile experience on iOS Safari and Android Chrome.
3. **Phase 12 (Advanced Capabilities):**
   - Local IndexedDB workout caching and background sync queue.
   - Multi-device bidirectional conflict resolution.
   - Background push notifications where supported.
   - Evaluation of native bridge vs standalone PWA for wearable hardware (HealthKit / Health Connect).

---

## 3. Canonical In-Repo Milestone Backlog

### Milestone M0: Discovery (Phase 00) — `[x] Complete`
- [x] `AUDIT-001`: Repository audit and baseline verification
- [x] `DOC-001`: Master brief, status, checklist, security baseline
- [x] `DOC-002`: Phase 00 Discovery Report committed and merged (PR #3)

### Milestone M1: Requirements & Scope (Phase 01) — `[x] Complete`
- [x] `REQ-001`: Comprehensive Personas (`docs/PERSONAS.md`)
- [x] `REQ-002`: Detailed User Journeys (`docs/USER_JOURNEYS.md`)
- [x] `REQ-003`: P0 MVP User Stories with Gherkin Acceptance Criteria (`docs/PRD.md`)
- [x] `REQ-004`: Domain Glossary (`docs/DOMAIN_GLOSSARY.md`)
- [x] `REQ-005`: Competitive Landscape & Benchmarking (`docs/COMPETITIVE_LANDSCAPE.md`)
- [x] `REQ-006`: ADR Decisions & Scope Corrections (`docs/DECISIONS.md`)
- [x] `REQ-007`: Traceability Matrix Expansion (`docs/TRACEABILITY_MATRIX.md`)
- [x] `DOC-003`: Phase 01 Requirements Report (`docs/reports/PHASE-01-REQUIREMENTS-REPORT.md`)

### Milestone M2: UX & Design System (Phase 02) — `[x] Complete`
- [x] `UX-001`: Information architecture & navigation hierarchy (`docs/ux/INFORMATION_ARCHITECTURE.md`, `docs/ux/NAVIGATION_MODEL.md`)
- [x] `UX-002`: Coach desktop/tablet program builder wireframes & user flows (`docs/ux/USER_FLOWS.md`, `docs/ux/WIREFRAMES.md`)
- [x] `UX-003`: Athlete mobile-first workout execution & logging wireframes (`docs/ux/USER_FLOWS.md`, `docs/ux/WIREFRAMES.md`)
- [x] `UX-004`: Organization owner & admin management console wireframes (`docs/ux/USER_FLOWS.md`, `docs/ux/SCREEN_INVENTORY.md`)
- [x] `UX-005`: Persian RTL layout specifications with `Vazirmatn` font & logical CSS (`docs/ux/RTL_LTR_SPECIFICATION.md`)
- [x] `UX-006`: WCAG 2.2 AA accessibility specifications & color palette tokens (`docs/ux/ACCESSIBILITY_SPEC.md`, `docs/ux/DESIGN_TOKENS.md`)
- [x] `UX-007`: Empty, loading, error, and offline state UI designs (`docs/ux/STATE_AND_ERROR_MATRIX.md`)
- [x] `UX-008`: Microcopy & UX guidelines in English & Persian (`docs/ux/UX_COPY.md`)
- [x] `UX-009`: UX requirements traceability matrix (`docs/ux/UX_TRACEABILITY_MATRIX.md`)
- [x] `UX-010`: UX research assumptions & validation plan (`docs/ux/UX_RESEARCH_AND_ASSUMPTIONS.md`)
- [x] `DOC-004`: Phase 02 UX & Design System Report (`docs/reports/PHASE-02-UX-DESIGN-REPORT.md`)

### Milestone M3: Architecture & Security (Phase 03) — `[x] Complete`
- [x] `ARCH-001`: System context and C4 container diagrams — `docs/architecture/SYSTEM_CONTEXT.md`, `CONTAINER_ARCHITECTURE.md`
- [x] `ARCH-002`: Finalized ADR package (stack, auth, database, caching, monorepo, module boundaries, identifier, search normalization, error model, media, PWA, offline, backup, env, CI/CD, observability, OpenAPI, threat, privacy) — `docs/DECISIONS.md` ADR-002..ADR-043, ADR-012 license pending founder approval
- [x] `ARCH-003`: Normalized PostgreSQL physical data model & ERD diagrams — `docs/architecture/ERD.md`, `docs/DATA_MODEL.md` v2.0, `docs/architecture/DOMAIN_MODULES.md`
- [x] `ARCH-004`: Server-side authorization matrix & ABAC rules — `docs/architecture/AUTHORIZATION_ARCHITECTURE.md` RBAC P0 roles + future nutritionist P1 consent-gated + progress-photo consent + break-glass + negative controls
- [x] `SEC-001`: Comprehensive threat model & OWASP Top 10 mitigation — `docs/THREAT_MODEL.md` STRIDE 21 threats + `docs/SECURITY_CONTROL_MATRIX.md` with negative controls for cross-tenant, unassigned coach, suspended, photo, message, audit, export
- [x] `SEC-002`: Privacy lifecycle & data export/erasure pipeline design — `docs/PRIVACY_DATA_LIFECYCLE.md` 11 stages Tier0-8, consent lifecycle, export ZIP via Celery tmp S3 24h link, erasure anonymization pipeline, pre-DPIA checklist, retention questions
- [x] `API-001`: Complete OpenAPI 3.1 specification catalog — `docs/OPENAPI.yaml` /api/v1 provisional covering all P0 groups with purpose/auth/role/object-permission/request/response/error/localization/idempotency/audit/rate-limit/sensitivity + RFC7807 + message_key, `docs/JSON_SCHEMAS.md` snapshot + queue + export manifest
- [x] `DOC-005`: Phase 03 Architecture & Security Report — `docs/reports/PHASE-03-ARCHITECTURE-REPORT.md` 31 sections

### Milestone M4: Foundation & PWA Baseline (Phase 04) — `[x] Complete`
- [x] `FND-001`: Monorepo directory structure (`frontend/`, `backend/`, `infra/`, `.github/`, `docker-compose.yml`, `compose.yaml`)
- [x] `FND-002`: Backend Django 5 + DRF shell with modular settings, middleware pipeline, and RFC 7807 error envelopes
- [x] `FND-003`: Frontend Next.js 14 App Router shell with dynamic `[locale]` routing, TypeScript strict, and dark obsidian theme
- [x] `FND-004`: Safe health check endpoints (`GET /healthz`, `GET /readyz`, `GET /api/v1/meta`)
- [x] `FND-005`: PWA Web App Manifest (`manifest.json`), 192px/512px maskable PNG icons, Service Worker, and `/offline` screen
- [x] `FND-006`: Bilingual RTL/LTR engine (`fa-IR` / `en-US`), zero Arabic resources, and Persian text search normalizer
- [x] `FND-007`: Security boundary enforcement (`NEXT_PUBLIC_*` client isolation, secret scanning, log redaction)
- [x] `FND-008`: CI/CD automation workflows in GitHub Actions (`ci.yml`, `security-scan.yml`)
- [x] `DOC-006`: Phase 04 Foundation Report (`docs/reports/PHASE-04-FOUNDATION-REPORT.md`)

### Milestones M5–M14 (Future Execution Phases)
- **M5 (Identity):** Implement auth, single-location orgs, invites, server-side RBAC.
- **M6 (Training):** Implement bilingual exercises, Persian search, program builder.
- **M7 (Athlete):** Implement Today view, mobile set logging, rest timer, pain flags.
- **M8 (Comms):** Implement contextual 1:1 threads and in-app notification engine.
- **M9 (Nutrition - P1):** Implement nutritionist role, Persian foods, meal plans.
- **M10 (Billing - P1):** Implement payment abstraction and coach subscriptions.
- **M11 (AI - P2):** Implement constrained, human-reviewed workout copilot.
- **M12 (PWA Advanced - P2):** Implement offline sync queue and wearable review.
- **M13 (Release):** Execute full automated test suites, security audit, staging deploy.
- **M14 (Pilot):** Run live cohort pilot and collect empirical business metrics.
