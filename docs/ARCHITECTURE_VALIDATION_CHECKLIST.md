# Architecture Validation Checklist — CoachOS

**Version:** 1.0.0 Phase 03  
**Status:** Proposed — must pass before Phase04 implementation.

---

## 1. Checklist

| # | Validation Item | Expected Evidence | Status | Notes |
|---|-----------------|-------------------|--------|-------|
| V01 | Every P0 domain has an owning module | `DOMAIN_MODULES.md` lists M01-M16 P0 with owned entities | Proposed Pass | Domain list: Identity, Org, Membership, AuthZ/Consent, Exercise, Media/Rights, Programs, Templates, Assignments/Snapshots, Sessions, Progress/Feedback, Messaging, Notifications, Admin/Moderation, Audit, Privacy Export/Erasure |
| V02 | Every sensitive entity has an access rule | `AUTHORIZATION_ARCHITECTURE.md` matrix includes create/read/update/archive/export/share/revoke + consent + audited for each sensitive resource | Proposed Pass | Covers User, Org, Membership, Assignment, Program, Session, SetLog, FeedbackFlag, BodyMetric, ProgressPhoto, Message, Notification, Audit, Export/Erasure |
| V03 | Every P0 API group has architectural boundary | `OPENAPI.yaml` groups: auth, orgs, locations, memberships, invitations, exercise catalog, moderation, programs, templates, assignments, today, sessions, set logs, feedback flags, progress metrics/photos, messages, notifications, audit, privacy, media | Proposed Pass | Each with method/path/purpose/auth/role/object permission/request/response/error/localization/idempotency/audit/rate-limit/sensitivity |
| V04 | Every P0 user story maps to domain and API area | `UX_TRACEABILITY_MATRIX.md` (27 P0 stories) + `TRACEABILITY_MATRIX.md` (PRD) map to screens + `DOMAIN_MODULES.md` + `OPENAPI.yaml` | Proposed Pass | US-AUTH-001..US-PWA-001 including I18N 001/002 verified no invalid IDs |
| V05 | Every UX route maps to future frontend boundary | `SCREEN_INVENTORY.md` 34 screens routes (/register, /login, /org/*, /coach/*, /app/*, /admin/*) map to `COMPONENT_BOUNDARIES.md` frontend app structure (/app/[locale]/(auth)/..., /(app)/today, /(coach)/programs/[id]/builder) | Proposed Pass | Frontend boundaries not implemented but path mapping documented |
| V06 | Every cross-tenant query has an authorization strategy | `AUTHORIZATION_ARCHITECTURE.md` tenant isolation: OrgScopeMiddleware extracts org_id from membership, TenantScopedModel for_org() helper, import-linter forbids bypass, `THREAT_MODEL.md` T04 cross-tenant IDOR controls, `SECURITY_CONTROL_MATRIX.md` negative tests | Proposed Pass | Pattern `WHERE organization_id = :auth_org_id` |
| V07 | Every media type has a storage/rights strategy | `MEDIA_STORAGE.md` tables: exercise canonical private + org-private custom + progress photo Tier4 isolated + org logos + exports-tmp; private buckets BlockPublicAcls true, signed URLs TTL≤15min, no listing, MIME whitelist, size limits, thumbnail, malware scan proposed, rights metadata mandatory, takedown workflow, CDN rules, retention | Proposed Pass | Tier4 never public, never CDN long-cache |
| V08 | Every export/deletion flow has architecture path | `PRIVACY_DATA_LIFECYCLE.md` export ZIP pipeline (profile.json, workouts.json, set_logs.csv) via Celery + temp S3 + email link 24h, erasure pipeline anonymization + S3 photo deletion, `DATA_FLOW.md` sequence diagrams, `OPENAPI.yaml` /privacy/export-request and /privacy/forget-me, `ERD.md` ExportRequest/ErasureRequest tables | Proposed Pass | Backup retention questions documented, backup destruction 30-day |
| V09 | PWA sequencing is consistent across all documents | `PWA_ARCHITECTURE.md` three-level: Phase04 manifest/icons/standalone/SW registration/app-shell caching/offline fallback/install guidance; Phase07 touch-optimized logging 44/48px, form-state protection temporary memory, network indicator, retry, no durable queue promise; Phase12 IndexedDB durable queue, sync status, retry/backoff, conflict, background sync, push limitations, HealthKit eval; consistent with `RELEASE_PLAN.md` PWA phasing, `STATE_AND_ERROR_MATRIX.md` offline matrix, `SCREEN_INVENTORY.md` offline wording "unsaved input retained temporarily; retry required after reconnection" | Proposed Pass | Wording normalized per preflight |
| V10 | No Arabic implementation scope exists | `DECISIONS.md` ADR-003 fa-IR/en-US only Arabic out of scope accepted, `DOMAIN_GLOSSARY.md` notes Persian normalization handles keyboard-variant but no Arabic localization, `OPENAPI.yaml` locale enum only fa-IR/en-US, search normalization described as "Perso-Arabic script keyboard-variant normalization for Persian search" not Arabic product support, CI lint NFR-I18N-04 verifies zero Arabic locale files | Proposed Pass | Grep for `ar-` locale fails |
| V11 | No AI/payment/wearable implementation is implied in P0 | `SYSTEM_CONTEXT.md` distinguishes P0 vs P1/P2 dashed future components for payment (Phase10), AI (Phase11), wearables (Phase12); `DOMAIN_MODULES.md` marks M17 Nutrition P1, M18 Billing P1 Phase10, M19 Marketplace P2, M20 AI P2; `THREAT_MODEL.md` T12 webhook forgery deferred Phase10, T17 prompt injection deferred Phase11; `OPENAPI.yaml` no payment/AI/wearable endpoints in P0; `DATA_MODEL.md` future extensibility marked P1/P2 | Proposed Pass | No implementation code, no dependencies |
| V12 | Open legal and license decisions remain visible | `DECISIONS.md` ADR-012 license IP pending founder approval, ADR-009 calendar strategy proposed, ADR-010 monorepo deferred Phase04, ADR-017 UUIDv7 proposed requires validation, `SECURITY_AND_PRIVACY.md` disclaimer not legal counsel, `PRIVACY_DATA_LIFECYCLE.md` "privacy-aligned engineering design, requires jurisdiction-specific legal review", pre-DPIA checklist documented | Proposed Pass | Not silently turned Accepted |
| V13 | No secrets or real health data exist in repository | Standing rule checked: `git log --all --patch | grep -i secret` manual? Actually `SECURITY_CONTROL_MATRIX.md` secret scan in CI via gitleaks, `PROJECT_CHECKLIST.md` cross-cutting rule synthetic data only, `SECURITY_AND_PRIVACY.md` no real PII in fixtures, verified empty via `find` no .env files beyond example | Proposed Pass | Verified no .env, no real PII |
| V14 | Screen count exact 34 verified | `SCREEN_INVENTORY.md` grep count 34 rows, `PROJECT_STATUS.md` §1.1 verification confirms 34, Phase02 report 34, no "28+" | Pass | Checked via bash |
| V15 | UX doc count 14 spec + README =15 verified | `docs/ux/` ls count 15 files, spec docs 14 excluding README, `PROJECT_STATUS.md` verification | Pass | |
| V16 | Story count 27 P0 verified (25 core +2 I18N) | PRD enumeration 27, UX_TRACEABILITY 27, no invalid IDs, CHANGELOG corrected from 29 to 27 | Pass | |
| V17 | Offline durability boundary respected | STATE_AND_ERROR_MATRIX, SCREEN_INVENTORY, USER_FLOWS, UX_COPY all use "unsaved input retained temporarily; retry required after reconnection" for Phase07, durable IndexedDB only Phase12 | Pass | |
| V18 | Touch target 44/48 consistency | DESIGN_SYSTEM, NAVIGATION_MODEL, RESPONSIVE_BEHAVIOR, ACCESSIBILITY_SPEC all: minimum 44×44 per WCAG 2.5.5, 48×48 preferred design target for primary CTAs — requires implementation testing | Pass | |
| V19 | Jalali/Gregorian calendar behavior documented | DECISIONS ADR-009 UTC/Gregorian storage with Jalali UI display in fa-IR via frontend date-fns-jalali, API ISO8601 UTC, `DATA_FLOW.md`, `COMPONENT_BOUNDARIES.md` date picker Jalali/Gregorian | Proposed Pass | |
| V20 | Modal and focus behavior consistent | ACCESSIBILITY_SPEC focus trapping, Escape dismiss, DESIGN_SYSTEM ConsentModal, STATE_AND_ERROR_MATRIX error states, SCREEN_INVENTORY modals — all consistent | Pass | |
| V21 | Dark-theme proposal vs validated preference | DECISIONS ADR-028 dark obsidian #0B0F17 default proposed design target for mobile gym-floor glare reduction (requires user testing to validate effectiveness) — not claimed as proven benefit, light tokens remain for desktop | Pass | |
| V22 | Persian terminology precise | PRD search scenario uses "Perso-Arabic script keyboard-variant normalization for Persian search" not "Arabic Yeh/Kaf variant folding"; DOMAIN_GLOSSARY uses same precise phrase + explains variant example; no Arabic product scope | Pass | |

---

## 2. Blockers / Open Issues

- None blocking architecture for Phase04 start, provided preflight corrections applied (screen count, story count, branch reference, precise Persian terminology).
- All proposed technology decisions need Phase04 POC validation (UUIDv7 support in PG/Python/JS, pg_trgm performance, Workbox vs custom SW, PaaS vs K8s).
- Legal decisions pending founder: license (ADR-012), data residency region, backup retention RPO/RTO cost trade-off.

---

## 3. Evidence Links

- `docs/architecture/SYSTEM_CONTEXT.md`
- `docs/architecture/CONTAINER_ARCHITECTURE.md`
- `docs/architecture/COMPONENT_BOUNDARIES.md`
- `docs/architecture/DATA_FLOW.md`
- `docs/architecture/DEPLOYMENT_ARCHITECTURE.md`
- `docs/architecture/ERD.md`
- `docs/architecture/DOMAIN_MODULES.md`
- `docs/architecture/AUTHORIZATION_ARCHITECTURE.md`
- `docs/architecture/PWA_ARCHITECTURE.md`
- `docs/architecture/MEDIA_STORAGE.md`
- `docs/architecture/OBSERVABILITY.md`
- `docs/architecture/BACKUP_AND_DISASTER_RECOVERY.md`
- `docs/OPENAPI.yaml`
- `docs/JSON_SCHEMAS.md`
- `docs/THREAT_MODEL.md`
- `docs/PRIVACY_DATA_LIFECYCLE.md`
- `docs/SECURITY_CONTROL_MATRIX.md`
- `docs/DECISIONS.md` ADR-001..028

---

## 4. Confirmation

No application code created in Phase03, no dependencies installed, no migrations, no Arabic scope, no AI/payment/wearable implementations — specification only Mermaid, OpenAPI YAML, JSON Schema, conceptual DDL.
