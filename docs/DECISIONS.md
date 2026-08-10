# Decision Log (ADRs) — CoachOS

**Last updated:** 2026-08-10  
**Format:** Lightweight Architecture Decision Records  

Status values: `Proposed` | `Accepted` | `Superseded` | `Rejected` | `Deferred`

---

## ADR-001 — Modular monolith for MVP

| Field | Value |
|-------|--------|
| Status | **Accepted** (Phase 00) |
| Date | 2026-08-10 |
| Deciders | Architect, Founding team |

### Context

CoachOS needs multiple domains (identity, exercises, programming, logging, messaging, admin) delivered quickly with strong consistency for tenancy and authZ. Team size is small.

### Decision

Build a **modular monolith** with clear domain package boundaries and an API-first HTTP surface. Do **not** split into microservices for MVP.

### Consequences

- Simpler deploy, transactions, and local dev  
- Must enforce module boundaries via code ownership and import discipline  
- Can extract services later if scale or team topology demands (new ADR)  

---

## ADR-002 — Preferred technical stack

| Field | Value |
|-------|--------|
| Status | **Proposed** (confirm in Phase 03; scaffold Phase 04) |
| Date | 2026-08-10 |

### Context

Need productive full-stack delivery with strong auth, admin, ORM, i18n-friendly frontend, and PWA path.

### Decision (preferred)

| Layer | Choice | Why |
|-------|--------|-----|
| Frontend | Next.js + React + TypeScript | App Router, strong ecosystem, PWA-capable |
| Backend | Django + Django REST Framework | Batteries-included auth/admin, mature permissions, excellent PostgreSQL story |
| DB | PostgreSQL | Reliability, JSON, full-text options |
| Jobs | Redis + Celery | Common Django pairing for email/notify/export |
| Media | S3-compatible + signed URLs | Decouple binary storage; support rights-checked delivery |
| API docs | OpenAPI | Contract for web and future native clients |
| CI | GitHub Actions | Native to GitHub repo |
| E2E | Playwright | Solid RTL and multi-locale testing |

### Alternatives considered

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| FastAPI + SQLAlchemy | Fast async, flexible | More DIY for admin/auth/permissions | Acceptable if ADR revisits with strong justification |
| NestJS full stack | One language | Weaker fitness for complex relational + admin speed | Rejected for MVP |
| Separate mobile native first | UX polish | Cost; PWA first is principle | Deferred to post-PWA decision |

### Consequences

- Python + TypeScript dual toolchain in monorepo or sibling folders  
- Dependency additions require license/maintenance/security note  
- Final folder layout decided in Phase 04  

---

## ADR-003 — Product languages: Persian and English only

| Field | Value |
|-------|--------|
| Status | **Accepted** |
| Date | 2026-08-10 |

### Context

Founder mandate: support Persian and English with true RTL/LTR. Arabic must not be implemented now.

### Decision

- Locales: `fa-IR` (RTL), `en-US` (LTR) only  
- **No** Arabic translation, locale, seed data, UI, or requirements  
- i18n framework may be multi-locale capable, but only fa/en resource files ship  
- All UI strings from resource files; no hardcoded user-facing copy  

### Consequences

- Design system must validate both directions  
- Search normalization includes Persian/Arabic *script variant folding* for Persian UX (character compatibility), which is **not** the same as shipping an Arabic locale  
- Future languages need explicit founder request + new ADR  

---

## ADR-004 — Business model B2B2C

| Field | Value |
|-------|--------|
| Status | **Accepted** |
| Date | 2026-08-10 |

### Decision

Coaches, gyms, and professional teams are paying customers. Athlete accounts are free or included. Marketplace is future (P2) and must not be precluded by schema, but is not built in MVP.

---

## ADR-005 — Authentication channel for MVP

| Field | Value |
|-------|--------|
| Status | **Proposed default** |
| Date | 2026-08-10 |

### Decision (default until Phase 01/05 confirms)

- MVP: **email + password** with secure reset flow  
- Phone/OTP: designed as extension point; implement if pilot geography demands  
- MFA: strategy documented for professional/admin; enforcement timing TBD (security baseline)  

### Rationale

Email is universally supported in frameworks, easier deliverability testing in sandbox, and avoids SMS cost/provider complexity in Phase 05.

---

## ADR-006 — Authorization model

| Field | Value |
|-------|--------|
| Status | **Accepted** (direction) |
| Date | 2026-08-10 |

### Decision

Combine **RBAC** (role within organization / platform) with **object-level permissions** (e.g., coach↔athlete assignment). Enforce exclusively on the server. Audit sensitive access and mutations.

### Consequences

- Frontend hiding is UX only, never security  
- Test matrix must include cross-tenant negative tests  

---

## ADR-007 — AI deferred until data and human workflow stable

| Field | Value |
|-------|--------|
| Status | **Accepted** |
| Date | 2026-08-10 |

### Decision

No AI feature implementation before Phase 11 activation. When built: retrieval from approved content, human review for professional outputs, logging of prompt template versions, rate/cost limits, off switch, no medical claims.

---

## ADR-008 — Content and media provenance

| Field | Value |
|-------|--------|
| Status | **Accepted** |
| Date | 2026-08-10 |

### Decision

Exercise media and instructional content must store **provenance and rights metadata**. Do not copy third-party proprietary videos/images/recipes. Seed data must be original, licensed, or clearly permitted — documented in-repo without binary bloat where possible.

---

## ADR-009 — Calendar system (Jalali vs Gregorian)

| Field | Value |
|-------|--------|
| Status | **Deferred** (decide Phase 01–02) |
| Date | 2026-08-10 |

### Notes

Persian users often expect Jalali (Solar Hijri) calendars. Options: (a) first-class Jalali in athlete/coach UI with UTC storage; (b) Gregorian storage/display with fa locale. Default lean: **store UTC/Gregorian internally; display per locale with Jalali UI components if Phase 02 research confirms necessity for MVP.**

---

## ADR-010 — Monorepo layout

| Field | Value |
|-------|--------|
| Status | **Deferred** to Phase 04 |
| Date | 2026-08-10 |

### Candidates

- `backend/` (Django) + `frontend/` (Next.js) + `docs/`  
- Optional `docker-compose.yml` for Postgres/Redis  

Exact choice at foundation scaffolding time.

---

## Rejected / out of scope reminders

| Topic | Status |
|-------|--------|
| Arabic product locale | Rejected for current roadmap |
| Microservices MVP | Rejected |
| Medical diagnosis features | Rejected |
| Building marketplace in P0 | Rejected (deferred P2) |
