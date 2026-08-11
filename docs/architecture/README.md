# Architecture Documentation — CoachOS

**Version:** 1.0.0 Phase 03 — Architecture, Data, Security, and Privacy  
**Status:** Proposed — modular monolith accepted, stack proposed  
**Last updated:** 2026-08-10  
**Languages:** fa-IR RTL + en-US LTR only, Arabic out of scope

---

## 1. Purpose

This directory holds coherent implementation-ready architecture and security specification transforming Phase 00-02 product, UX, requirements into buildable design.

No application code was created in Phase 03 — only Mermaid/PlantUML diagrams, OpenAPI YAML, JSON Schema, conceptual DDL, threat-model tables, and markdown specs.

---

## 2. Document Index

| Document | Purpose | Status |
|----------|---------|--------|
| `SYSTEM_CONTEXT.md` | C4 Level1 system context, actors P0/P1/P2, external services, trust boundaries, sensitive-data boundaries | Proposed |
| `CONTAINER_ARCHITECTURE.md` | C4 Level2 containers: Next.js frontend, Django modular monolith backend, PostgreSQL, Redis+Celery, S3 private, email abstraction, future push/payment/AI/wearable dashed | Proposed |
| `COMPONENT_BOUNDARIES.md` | Frontend Next.js app structure + backend Django apps layout, middleware stack, domain boundaries enforcement via import-linter, sequence diagram program assignment | Proposed |
| `DATA_FLOW.md` | Data flows: auth/invite, exercise search Persian normalization, assignment snapshot, workout logging offline boundary, progress photo consent, messaging, privacy export/erasure, audit | Proposed |
| `DEPLOYMENT_ARCHITECTURE.md` | Logical deployment topology, env strategy local/staging/prod, PaaS vs K8s options, Docker + CI/CD GitHub Actions, TLS, secrets, RPO/RTO proposed | Proposed |
| `ERD.md` | ER diagram + detailed entity specs identity/tenancy, exercise catalog, programming, athlete execution, communication/ops, future extensibility, index strategy, soft-delete policy, identifier UUIDv7 proposed, conceptual DDL | Proposed |
| `DOMAIN_MODULES.md` | 20 modules M01-M20 responsibility, owned entities, public interfaces, read/write dependencies, security boundary, events emitted/consumed, data sensitivity, test boundary, extraction risk, dependency rules | Proposed |
| `AUTHORIZATION_ARCHITECTURE.md` | RBAC roles P0, org boundaries active context, object-level assignment rules, owner visibility aggregate vs raw, break-glass admin, P1 nutritionist consent, progress-photo consent, export/erasure auth, audit-log visibility, suspension behavior, invitation permissions, negative controls matrix | Proposed/Accepted direction ADR-006 |
| `PWA_ARCHITECTURE.md` | Three-level PWA strategy Phase04 manifest/icons/standalone/SW/app-shell/offline fallback/install guidance, Phase07 athlete mobile execution/touch-optimized/form-state temp/network indicator/retry no durable queue, Phase12 IndexedDB durable queue/sync/status/retry/conflict/background sync/push/wearable eval, browser limitations table, security, file structure | Proposed, ADR-011 accepted sequencing |
| `MEDIA_STORAGE.md` | Media types classification Tier0/2/4, bucket boundaries private no listing, signed URL TTL≤15min, upload validation MIME/magic bytes/size/checksum, thumbnail strategy, malware scan proposed, provenance/license metadata, takedown workflow, photo access control, future transcoding CDN, retention | Proposed |
| `OBSERVABILITY.md` | Structured logging JSON + redaction + request_id correlation, audit vs debug logs separation, metrics Prometheus counters/histograms, error tracking Sentry, health endpoints /healthz /readyz, alerting categories auth anomaly cross-tenant etc | Proposed |
| `BACKUP_AND_DISASTER_RECOVERY.md` | Backup strategy PG snapshots daily + WAL PITR 15min RPO proposed, S3 versioning, Redis not source of truth, restore runbooks DB/S3, automated restore testing weekly, RPO/RTO proposed table, disaster scenarios, incident & breach response, rollback strategy app + migrations | Proposed, targets require validation |
| `ARCHITECTURE_VALIDATION_CHECKLIST.md` | V01-V22 validation checklist: P0 domains owning modules, sensitive entities access rules, API groups boundaries, stories→domains/APIs, UX routes→frontend boundaries, cross-tenant auth strategy, media types rights, export/deletion paths, PWA sequencing consistency, no Arabic, no AI/payment/wearable P0, open legal/license visible, no secrets/health data, screen count 34, UX doc 14, story 27, offline boundary, touch target 44/48, Jalali/Gregorian, modal focus, dark-theme, Persian terminology | Proposed Pass |

**Related top-level architecture docs:**

- `docs/OPENAPI.yaml` — provisional OpenAPI 3.1 API catalog /api/v1 all P0 groups, RFC7807 error + message_key
- `docs/JSON_SCHEMAS.md` — snapshot, queue entry, export manifest, notification payload, consent, Persian normalizer pseudocode
- `docs/THREAT_MODEL.md` — STRIDE 21 threats T01-T21 + OWASP mapping + controls
- `docs/PRIVACY_DATA_LIFECYCLE.md` — 11 lifecycle stages, Tier0-8 classification, consent lifecycle, export/erasure pipelines, retention questions, pre-DPIA checklist
- `docs/SECURITY_CONTROL_MATRIX.md` — threat→requirement→control→phase→test type→evidence→status including negative controls
- `docs/ARCHITECTURE_VALIDATION_CHECKLIST.md` — validation checklist (also in this dir for convenience — same file duplicated? Actually canonical is docs/architecture/ARCHITECTURE_VALIDATION_CHECKLIST.md but requirement says docs/ARCHITECTURE_VALIDATION_CHECKLIST.md — we will create symlink or copy both locations)

---

## 3. Technology Decisions Summary (Pointer)

Detailed in `docs/DECISIONS.md` ADR-001..028 plus Phase03 updates needed (see DECISIONS.md update in Phase03 report).

Proposed Stack:
- Frontend: Next.js 14 App Router + React + TypeScript + Tailwind logical properties + next-pwa/Workbox (proposed)
- Backend: Django 5 + DRF + Python 3.12 modular monolith
- DB: PostgreSQL 16 + pg_trgm + btree_gin
- Cache/Queue: Redis 7 + Celery
- Media: S3-compatible private buckets, presigned URLs TTL≤15min
- API: REST /api/v1 OpenAPI 3.1 provisional
- PWA: Manifest + Service Worker + three-level sequencing
- E2E: Playwright proposed
- CI/CD: GitHub Actions

All marked Proposed until Phase04 POC validation, except modular monolith Accepted (ADR-001), RBAC+ABAC accepted (ADR-006), PWA sequencing accepted (ADR-011), license pending founder approval (ADR-012).

---

## 4. Verification — No Code

- No `backend/`, `frontend/` directories created in Phase03 (verified via `find`).
- No `package.json`, `requirements.txt`, `poetry.lock` added.
- No `*.py`, `*.tsx` app source beyond docs.
- No database migrations (`migrations/` folder).
- No secrets, no real health data — synthetic only.

Phase03 output is documentation and specification only.

---

## 5. Rendering Notes

- Mermaid diagrams use `C4Context`, `C4Container`, `flowchart`, `sequenceDiagram`, `erDiagram` — GitHub Markdown supports `mermaid` code fences; C4 extensions may need `C4Context` renderer plugin but fallback generic diagrams included in SYSTEM_CONTEXT, CONTAINER_ARCHITECTURE.
- OpenAPI YAML can be previewed via Swagger Editor.

---

## 6. Next Phase

Phase04 — Project Foundation and PWA Baseline — upon founder approval after Phase03 review. Do not start automatically.

---

## 7. References

- `docs/MASTER_PRODUCT_BRIEF.md`, `docs/PRD.md`, `docs/PERSONAS.md`, `docs/USER_JOURNEYS.md`, `docs/DOMAIN_GLOSSARY.md`
- `docs/ux/` 14 spec docs + README, 34 screens, 27 stories
- `docs/DECISIONS.md`, `docs/DATA_MODEL.md`, `docs/API_CONTRACT.md`, `docs/SECURITY_AND_PRIVACY.md`
- `docs/reports/PHASE-00-DISCOVERY-REPORT.md`, `PHASE-01-REQUIREMENTS-REPORT.md`, `PHASE-02-UX-DESIGN-REPORT.md`
