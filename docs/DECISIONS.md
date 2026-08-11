# Architecture & Product Decision Log (ADRs) — CoachOS

**Document version:** 2.0.0 (Phase 03 Architecture Finalized)  
**Last updated:** 2026-08-10  
**Format:** Lightweight Architecture Decision Records (ADRs)  

**Status taxonomy:** `Accepted` | `Proposed` | `Pending Founder Approval` | `Superseded` | `Rejected` | `Deferred`

---

## Summary of Decisions

| ADR ID | Decision Title | Status | Founder Approval Required? | Decided / Proposed Phase |
|--------|----------------|--------|-----------------------------|--------------------------|
| **ADR-001** | Modular Monolith Architecture for MVP | **Accepted** | No (Team Baseline) | Phase 00 |
| **ADR-002** | Preferred Technical Stack (Next.js + Django/DRF + PostgreSQL + Redis + S3 + PWA + Playwright + GitHub Actions) | **Conditionally Accepted (Proposed Pending Phase04 Validation)** | No (Team baseline, founder infra choice pending) | Phase 00 / 03 |
| **ADR-003** | Product Locales: Persian (`fa-IR`) and English (`en-US`) Only; Arabic Out of Scope | **Accepted** | Yes (Founder Mandate) | Phase 00 |
| **ADR-004** | Business Model: B2B2C Multi-Tenant SaaS | **Accepted** | Yes (Founder Approved) | Phase 00 |
| **ADR-005** | Authentication Channel: Email + Password Default with OTP Roadmap (HS: session cookie HttpOnly + JWT rotating refresh) | **Proposed (Conditional Acceptance)** | No | Phase 00 / 01 / 03 |
| **ADR-006** | Authorization Architecture: Server-Side RBAC + Object-Level Access Control + Consent | **Accepted** | No | Phase 00 / 01 / 03 |
| **ADR-007** | Constrained AI Assistance Deferred to Phase 11 | **Accepted** | No | Phase 00 / 01 |
| **ADR-008** | Exercise Media Rights, Provenance, and Moderation Metadata | **Accepted** | No | Phase 00 / 01 |
| **ADR-009** | Calendar Strategy: UTC/Gregorian Storage with Persian Jalali UI Display | **Accepted (Conditional — frontend validation required)** | No | Phase 01 / 03 |
| **ADR-010** | Monorepo Folder Layout & Package Boundaries | **Accepted** | No (Phase 04 Foundation Scaffold) | Phase 03 / 04 |
| **ADR-011** | PWA Sequencing Correction (Phase 04 Foundation, Phase 07 Mobile Log, Phase 12 Advanced Offline) | **Accepted** | No | Phase 01 / 03 |
| **ADR-012** | Repository License & Intellectual Property Strategy | **Accepted (Founder Mandate — Proprietary / All Rights Reserved)** | **YES (Founder Decided)** | Phase 01 / 04 |
| **ADR-013** | Single-Location-First MVP Strategy | **Accepted** | No | Phase 01 |
| **ADR-014** | Organization Membership & Role Binding Model (Multi-Role per Org Allowed) | **Accepted (Conditional — membership multi-role model affirmed)** | No | Phase 01 / 03 |
| **ADR-015** | Program Versioning & Assignment Snapshot Strategy (Immutable JSONB Snapshot) | **Accepted (Conditional — snapshot immutability affirmed)** | No | Phase 01 / 03 |
| **ADR-016** | Data Deletion, Soft-Delete, and Archival Lifecycle (Archive vs Anonymized Hard Delete) | **Accepted (Conditional — soft-archive operational, hard-delete via anonymization pipeline)** | No | Phase 01 / 03 |
| **ADR-017** | Entity Identifier Strategy (UUIDv7 vs BigInt/UUIDv4) | **Proposed (Requires Validation — not authz substitute)** | No | Phase 01 / 03 |
| **ADR-018** | Persian Search Normalization & Trigram Indexing Strategy (Perso-Arabic script keyboard-variant normalization for Persian search) | **Accepted (Conditional — pg_trgm + normalizer)** | No | Phase 01 / 03 |
| **ADR-019** | Athlete Data Ownership, Privacy, and Portability Architecture | **Accepted** | No | Phase 01 |
| **ADR-020** | Multi-Professional Collaboration & Consent Architecture (P1 Scope) | **Accepted for P1** | No | Phase 01 |
| **ADR-021** | Payment Gateway Abstraction & Coach Monetization Deferral to Phase 10 | **Accepted** | No | Phase 01 |
| **ADR-022** | Public Discovery Marketplace Deferral to Phase 11+ / P2 | **Accepted** | No | Phase 01 |
| **ADR-023** | Athlete Mobile Navigation & Active Workout Canvas Pattern | **Accepted** | No | Phase 02 |
| **ADR-024** | Coach Program Builder Desktop Dual-Pane Master-Detail Pattern | **Accepted** | No | Phase 02 |
| **ADR-025** | Persian Typography Strategy: Vazirmatn Variable Web Font | **Accepted** | No | Phase 02 |
| **ADR-026** | Non-Clinical UX Language Standard for Subjective Feedback | **Accepted** | No | Phase 02 |
| **ADR-027** | Explicit Affirmative Consent Interaction Model for Sensitive Photos | **Accepted** | No | Phase 02 |
| **ADR-028** | Dark-Neutral Visual Theme for Mobile Gym-Floor Glare Reduction (Design Target) | **Accepted** (Design target, requires user testing) | No | Phase 02 |
| **ADR-029** | Frontend Architecture — Next.js App Boundaries | **Proposed (Pending Phase04 scaffold)** | No | Phase 03 |
| **ADR-030** | Backend Architecture — Django Module Boundaries (20 Modules M01-M20) | **Proposed (Accepted Orientation)** | No | Phase 03 |
| **ADR-031** | PostgreSQL Version/Extension Strategy (16 + pg_trgm, btree_gin, pgcrypto) | **Proposed (Requires Validation)** | No | Phase 03 |
| **ADR-032** | Auth/Session Strategy (Argon2id, HttpOnly cookie, JWT rotating refresh 15min, rate limit 5/15min) | **Proposed (Conditional Acceptance)** | No | Phase 03 |
| **ADR-033** | API Error Model (RFC7807 + message_key extension) | **Accepted** | No | Phase 03 |
| **ADR-034** | Media Storage Architecture (Private buckets, no listing, signed URLs TTL≤15min, MIME whitelist, thumbnail, rights metadata, takedown) | **Accepted** | No | Phase 03 |
| **ADR-035** | PWA Architecture (Manifest + SW + three-level offline boundary) | **Accepted** | No | Phase 03 |
| **ADR-036** | Offline Boundary (Phase04 shell only, Phase07 temp in-memory, Phase12 durable IndexedDB queue) | **Accepted** | No | Phase 03 |
| **ADR-037** | Backup/RTO/RPO Targets (PITR 15min RPO proposed, 1h RTO DB, versioned S3, Redis loss acceptable) | **Proposed (Requires Validation + Founder Approval on Cost)** | Yes (Cost approval) | Phase 03 |
| **ADR-038** | Environment Separation (local/staging/prod distinct VPC/DB/buckets/secrets) | **Proposed** | No | Phase 03 |
| **ADR-039** | CI/CD Strategy (GitHub Actions lint/type/unit/integration/security scan, Playwright E2E, staging auto deploy, prod manual gate) | **Proposed** | No | Phase 03 |
| **ADR-040** | Observability Strategy (structlog JSON + redaction + request_id, Prometheus metrics, Sentry, healthz/readyz, alerting categories) | **Proposed** | No | Phase 03 |
| **ADR-041** | OpenAPI 3.1 Contract Structure (/api/v1 versioned, endpoint groups P0, RFC7807 error) | **Proposed (Accepted as Provisional)** | No | Phase 03 |
| **ADR-042** | Threat Model & Security Control Matrix (STRIDE + OWASP mapping, 21 threats, negative authorization controls) | **Accepted** | No | Phase 03 |
| **ADR-043** | Privacy & Data Lifecycle (11 lifecycle stages, Tier0-8, consent, export/erasure, pre-DPIA checklist, retention questions) | **Accepted** | No | Phase 03 |
| **ADR-044** | Monorepo Structure & Local Workspace Scaffolding | **Accepted** | No | Phase 04 |
| **ADR-045** | Frontend Foundation Architecture & Public Runtime Configuration Boundary | **Accepted** | No | Phase 04 |
| **ADR-046** | PWA Baseline Architecture, App-Shell Caching, and Offline Fallback Strategy | **Accepted** | No | Phase 04 |
| **ADR-047** | Bilingual RTL/LTR Execution & Persian Search Normalization Architecture | **Accepted** | No | Phase 04 |
| **ADR-048** | Backend Foundation, Error Sanitization Envelope, Middleware Pipeline, and Health Endpoints | **Accepted** | No | Phase 04 |
| **ADR-049** | Hosting and Dual-Region Deployment Strategy (Evaluation & Phase 04 Baseline) | **Accepted (Decision Gate Defined)** | Yes (Production Gate) | Phase 04 |

---

## Detailed ADR Records

### ADR-001 — Modular Monolith Architecture for MVP
- **Status:** **Accepted**
- **Context:** CoachOS encompasses distinct sub-domains (identity, tenancy, catalog, programming, workout logging, messaging, notifications, admin). Team size is small and execution velocity is paramount.
- **Decision:** Build a single deployable modular monolith with strict domain package isolation.
- **Consequences:** Eliminates network latency, distributed transaction complexity, and multi-service DevOps overhead. Requires architectural linting to prevent cyclic dependencies between domain modules.

---

### ADR-002 — Preferred Technical Stack
- **Status:** **Proposed** (to be finalized in Phase 03 ADR package; scaffolded in Phase 04)
- **Context:** Need robust full-stack productivity, enterprise-grade relational integrity, fast server-side authorization, and modern mobile-first frontend rendering.
- **Recommendation:**
  - **Frontend:** Next.js (App Router) + React + TypeScript + Tailwind CSS (configured for RTL logical properties).
  - **Backend:** Django + Django REST Framework (DRF) + Python 3.12.
  - **Database:** PostgreSQL 16 (with `pg_trgm` and JSONB support).
  - **Task Queue & Cache:** Redis 7 + Celery.
  - **Storage:** S3-compatible object storage with presigned URLs.
- **Consequences:** Provides mature ORM, built-in admin, battle-tested security controls, and excellent developer velocity.

---

### ADR-003 — Product Locales: Persian (`fa-IR`) and English (`en-US`) Only; Arabic Out of Scope
- **Status:** **Accepted** (Founder Mandate)
- **Context:** The product must deliver an uncompromising bilingual experience for Persian speakers and international English speakers. Arabic is frequently conflated with Persian due to shared script, but involves different grammar, vocabulary, typography, and regional market dynamics.
- **Decision:**
  - Support `fa-IR` (RTL) and `en-US` (LTR) as the exclusive product locales.
  - **Arabic is strictly out of scope.** No Arabic locale files, seed data, translations, or requirements will be created.
  - Search engines must support character folding for Persian Unicode variants (`ی`/`ي`, `ک`/`ك`).
- **Consequences:** Focuses product development on high-quality Persian/English fitness ergonomics without dilution.

---

### ADR-004 — Business Model: B2B2C SaaS
- **Status:** **Accepted** (Founder Mandate)
- **Context:** Determining who pays for the platform and how athlete access is governed.
- **Decision:** B2B2C SaaS model. Organizations and coaches are the paying subscribers. Athletes receive free/included access via coach invitations. Marketplace monetization and program sales are deferred to P2.
- **Consequences:** Eliminates payment friction for athletes, maximizing workout logging adherence and client onboarding speed.

---

### ADR-005 — Authentication Channel for MVP
- **Status:** **Proposed Default**
- **Context:** In international markets, email/password is the universal standard. In Iran and regional mobile markets, SMS/phone OTP is frequently used.
- **Options Considered:**
  1. *Email + Password only for MVP (with optional TOTP MFA for admins).*
  2. *Phone number + SMS OTP only.*
  3. *Hybrid email + phone authentication.*
- **Recommendation:** Implement **Email + Password with secure tokenized reset** for MVP (P0). Design the `User` identity model with an optional `phone_number` field to allow SMS OTP integration in Phase 05/10 when regional SMS gateways are configured.
- **Consequences:** Avoids third-party SMS gateway costs, latency, and carrier deliverability risks during early development and testing.

---

### ADR-006 — Authorization Architecture: Server-Side RBAC + Object-Level Access Control
- **Status:** **Accepted**
- **Context:** Multi-tenant fitness platforms require strict isolation between gyms and fine-grained access control between coaches and athletes.
- **Decision:** Enforce authorization strictly on the server using a two-tier model:
  1. **Role-Based Access Control (RBAC):** Organization-level permissions (`Owner`, `Coach`, `Athlete`, `Support`).
  2. **Object-Level Access Control (ABAC/ACL):** Explicit binding checks (e.g., coach must have an active `CoachAthleteAssignment` to view an athlete's logs).
- **Consequences:** Frontend route guards serve as UX hints only; API handlers reject unauthorized access with `403 Forbidden` or `404 Not Found` to prevent entity enumeration.

---

### ADR-007 — Constrained AI Assistance Deferred to Phase 11
- **Status:** **Accepted**
- **Context:** AI generation in fitness presents severe hallucination, safety, and legal risks if applied autonomously to exercise prescriptions or clinical health advice.
- **Decision:** Defer all AI implementations to Phase 11. When implemented, AI must operate strictly as a copilot under mandatory human-in-the-loop review, using verified exercise retrieval, and with zero autonomous medical/rehabilitation claims.
- **Consequences:** Protects athlete safety, ensures compliance, and keeps MVP engineering focused on core coaching execution.

---

### ADR-008 — Exercise Media Rights, Provenance, and Moderation Metadata
- **Status:** **Accepted**
- **Context:** Video/image demonstrations of exercises carry copyright and quality risks if scraped or uploaded without clearance.
- **Decision:** Every exercise media record must store structured provenance metadata (license type, source URL, creator attribution, and moderation status). Platform admins must moderate and approve all public catalog content.
- **Consequences:** Protects CoachOS and gym owners from copyright liability and maintains high instructional quality.

---

### ADR-009 — Calendar Strategy: UTC/Gregorian Storage with Persian Jalali UI Display
- **Status:** **Proposed**
- **Context:** Persian users in Iran operate daily on the Solar Hijri (Jalali / شمسی) calendar, while international users and backend databases operate on UTC Gregorian timestamps.
- **Options Analyzed:**
  1. *Gregorian storage and display only:* Lowest complexity, but alienates Persian-first coaches and athletes accustomed to Jalali dates for weekly training schedules and booking.
  2. *UTC/Gregorian internal storage with Persian Jalali display in Persian locale:* Backend stores all timestamps in ISO 8601 UTC. API transmits UTC ISO strings. Frontend date picker and calendar components render Solar Hijri (Jalali) when `locale == 'fa-IR'` (using `date-fns-jalali` or `moment-jalaali`) and Gregorian when `locale == 'en-US'`.
  3. *First-class Jalali calendar stored in backend:* Complex custom date calculations, breaks standard PostgreSQL date/time indexing, difficult international interoperability.
- **Recommendation:** **Option 2 (UTC/Gregorian internal storage with Jalali UI rendering in `fa-IR`).**
  - All database columns store `timestamptz` (UTC).
  - All API contracts use standard ISO 8601 UTC strings (e.g., `2026-08-10T14:00:00Z`).
  - Frontend components format dates using Persian Jalali calendar algorithms when active locale is `fa-IR`.
  - Weekly schedules map to standard Monday–Sunday or Saturday–Friday based on locale settings.
- **Consequences:** Clean backend architecture, robust time zone math, full international compatibility, and seamless native experience for Persian users.

---

### ADR-010 — Monorepo Layout & Package Boundaries
- **Status:** **Accepted** (Phase 04 Scaffolding Layout Finalized)
- **Context:** Structuring repository code directories for backend, frontend, documentation, infrastructure, and tooling.
- **Decision:** Scaffold a clean monorepo structure:
  - `frontend/`: Next.js 14 App Router + React + TypeScript + Tailwind CSS (configured for RTL logical properties) + Vitest tests.
  - `backend/`: Django 5 + Django REST Framework + Python 3.12 target + Pytest tests.
  - `infra/`: Docker compose orchestration, container definitions (`infra/docker/`), utility scripts (`infra/scripts/`).
  - `docs/`: Architecture specifications, requirements, UX designs, reports, and threat models.
  - `.github/workflows/`: CI/CD automation for linting, typing, testing, security scanning, manifest validation, and no-Arabic verification.
- **Consequences:** Clear separation of concerns, independent frontend and backend dependency trees, unified CI/CD, and strict security boundaries.

---

### ADR-011 — PWA Sequencing Correction
- **Status:** **Accepted**
- **Context:** The original roadmap deferred all PWA work to Phase 12. However, CoachOS is fundamentally a PWA-first platform where mobile responsiveness, installability, and low-bandwidth resilience are core to the athlete experience.
- **Decision:** Restructure PWA delivery across three progressive milestones:
  - **Phase 04 (Foundation):** Web App Manifest (`manifest.json`), installable application shell, mobile-first responsive viewport, Service Worker foundation, PWA metadata, PWA-aware routing and offline fallback page.
  - **Phase 07 (Athlete App Validation):** Mobile workout execution, touch-optimized logging, responsive workout cards, and installed-PWA mobile experience validation.
  - **Phase 12 (Advanced Capabilities):** Advanced offline workout logging with local IndexedDB queuing, bidirectional conflict resolution, background synchronization, push notifications, and wearable integrations.
- **Consequences:** Ensures solid mobile architectural foundation from day one without premature complexity.

---

### ADR-012 — Repository License & Intellectual Property Strategy
- **Status:** **Accepted (Founder Mandate — Proprietary / All Rights Reserved)**
- **Context:** The repository was initialized with an open-source MIT license during early prototyping. As a commercial B2B2C SaaS product, the intellectual property strategy was reviewed by the founder in Phase 04.
- **Decision:**
  - The commercial codebase and all proprietary assets transition to **Proprietary / All Rights Reserved**.
  - Copyright is formally asserted: `Copyright (c) 2026 CoachOS Technologies / Ali Naderi. All rights reserved.`
  - Unauthorized copying, reproduction, distribution, redistribution, modification, reverse engineering, decompilation, public display, sublicensing, or commercial reuse is strictly prohibited.
  - The repository `LICENSE` file is replaced with a clear proprietary license notice.
  - The wording serves as an operational placeholder; formal legal review by qualified IP counsel in relevant jurisdictions is recommended before commercial launch and customer deployment.
  - No Open-Core, BSL, or dual-license model is introduced unless explicitly mandated in the future by the founder.
- **Consequences:** Protects proprietary software, data models, UX workflows, and competitive advantages while maintaining clear ownership boundaries.

---

### ADR-013 — Single-Location-First MVP Strategy
- **Status:** **Accepted**
- **Context:** Gym management software often becomes bloated by attempting complex multi-franchise, multi-location resource scheduling in version 1.0.
- **Decision:** Implement a **Single-Location-First Strategy** for MVP (P0):
  - Each Organization has exactly one primary location profile.
  - The data model includes an optional `Location` entity linked to `Organization` to ensure clean database forward-compatibility.
  - Advanced multi-location features (location managers, cross-branch member roaming, branch-specific analytics) are explicitly allocated to **P1**.
- **Consequences:** Radically simplifies MVP authorization, member routing, and admin UI while preserving a frictionless migration path for multi-location expansion in P1.

---

### ADR-014 — Organization Membership & Role Binding Model
- **Status:** **Proposed**
- **Context:** Users may belong to multiple organizations or hold different roles in different gyms (e.g., Coach in Gym A, Athlete in Gym B).
- **Decision:** Model `Membership` as an explicit join table between `User` and `Organization` with fields: `role` (`owner`, `coach`, `athlete`, `support`), `status` (`invited`, `active`, `suspended`), and `created_at`. A user has a single active tenant context per session, switchable via an organization picker.
- **Consequences:** Supports multi-tenant gym coaches cleanly and prevents cross-tenant credential duplication.

---

### ADR-015 — Program Versioning & Assignment Snapshot Strategy
- **Status:** **Proposed**
- **Context:** When a coach edits a master program template, athletes currently executing that program must not have their active workouts or past workout logs unexpectedly altered.
- **Decision:** Implement an **Immutable Snapshot Strategy on Assignment**:
  - When a coach assigns a program to an athlete, the system generates a point-in-time immutable `ProgramSnapshot` / `ProgramVersion`.
  - The athlete's workout execution and set logs attach strictly to the snapshot version ID.
  - Coaches may push explicit version updates to active athletes with confirmation.
- **Consequences:** Guarantees historical data integrity for workout logs while allowing coaches to freely iterate on master templates.

---

### ADR-016 — Data Deletion, Soft-Delete, and Archival Lifecycle
- **Status:** **Proposed**
- **Context:** Fitness records require audit compliance, yet users possess legal rights to data erasure (GDPR / privacy regulations).
- **Decision:**
  - Operational entities (Programs, Exercises, Workouts) use soft-deletion / archiving (`archived_at` timestamp).
  - User deletion requests execute a multi-stage **Anonymization & Hard Deletion Pipeline**: personal identifiers (email, name, phone, photos) are permanently wiped; historical workout telemetry is disassociated from PII and retained only for aggregated audit/financial integrity.
- **Consequences:** Satisfies legal privacy requirements without corrupting relational integrity.

---

### ADR-017 — Entity Identifier Strategy (UUIDv7 vs BigInt)
- **Status:** **Proposed**
- **Context:** Public-facing URLs and APIs must not leak sequential business metrics (e.g., total athlete count) through auto-incrementing integer IDs.
- **Decision:** Use **UUIDv7** (time-ordered 128-bit identifiers) as primary keys across all public and tenant entities.
- **Consequences:** Prevents sequential enumeration attacks, supports client-side ID generation for offline PWA syncing, and maintains high B-tree database index locality in PostgreSQL.

---

### ADR-018 — Persian Search Normalization & Trigram Indexing Strategy
- **Status:** **Proposed**
- **Context:** Persian text search frequently fails due to character variance between Arabic and Persian keyboards (`ی` vs `ي`, `ک` vs `ك`, zero-width non-joiners).
- **Decision:** Implement a two-layer search engine:
  1. Python/PostgreSQL text normalization pre-processing pipeline folding Unicode variants and stripping diacritics.
  2. PostgreSQL `pg_trgm` (trigram) and full-text search indexes on exercise names, aliases, and tags in both `fa-IR` and `en-US`.
- **Consequences:** Instant, typo-tolerant search across Persian and English exercise libraries with zero external search cluster maintenance in MVP.

---

### ADR-019 — Athlete Data Ownership, Privacy, and Portability Architecture
- **Status:** **Accepted**
- **Context:** Athletes own their personal physiological and fitness history. If an athlete switches gyms or coaches, they must not lose their historical training data.
- **Decision:**
  - Athlete profile and historical workout logs belong fundamentally to the Athlete `User` identity.
  - Coaches and Organizations hold revocable operational access during active coaching terms.
  - Athletes can trigger automated machine-readable data exports (`.zip` containing JSON/CSV and media assets) at any time.
- **Consequences:** Establishes strong consumer trust and adheres to international privacy standards.

---

### ADR-020 — Multi-Professional Collaboration & Consent Architecture (P1 Scope)
- **Status:** **Accepted for P1**
- **Context:** Modern athletes often work with both a strength coach and a nutrition professional.
- **Decision:** The data model allows multiple professional assignments per athlete (`CoachAssignment`, `NutritionistAssignment`), gated by explicit, granular athlete consent records (`ConsentRecord`).
- **Consequences:** Lays the architectural groundwork in P0 schemas so that P1 nutrition features can plug in without breaking schema migrations.

---

### ADR-021 — Payment Gateway Abstraction & Coach Monetization Deferral to Phase 10
- **Status:** **Accepted**
- **Context:** Payment integrations in Iran (Shetab/Shaparak gateways) and international markets (Stripe/Paddle) have distinct regulatory, currency, and API requirements.
- **Decision:** Defer all payment integration code to Phase 10. Design a unified payment gateway interface abstraction (`PaymentProviderAdapter`) in architecture phases to support dual domestic/international payment backends cleanly.
- **Consequences:** Eliminates payment gateway compliance bottlenecks from early core coaching validation.

---

### ADR-022 — Public Discovery Marketplace Deferral to Phase 11+ / P2
- **Status:** **Accepted**
- **Context:** Building a two-sided marketplace (coach discovery, public ratings, booking, dispute resolution) before perfecting the core 1:1 coaching operating system risks premature failure.
- **Decision:** Public marketplace, reviews, and client discovery are classified strictly as **P2 Backlog** and will not be developed until P0 and P1 operating system workflows achieve high pilot retention.
- **Consequences:** Focuses team execution 100% on software quality for existing coach-client relationships.

---

### ADR-023 — Athlete Mobile Navigation & Active Workout Canvas Pattern
- **Status:** **Accepted** (Phase 02 UX)
- **Context:** Mobile athletes on gym floors need fast navigation between Today, Calendar, Progress, and Messages, but during an active workout session, accidental tab navigation leads to friction and lost training focus.
- **Decision:** Use a persistent 5-tab Bottom Navigation Bar for general athlete browsing, and switch to a full-screen modal **Active Workout Canvas** when "Start Workout" is tapped (hiding the bottom nav until the session is finished or paused).
- **Consequences:** Maximizes gym-floor focus, eliminates misclicks, and anchors timer and set-logging controls in the natural thumb zone.

---

### ADR-024 — Coach Program Builder Desktop Dual-Pane Master-Detail Pattern
- **Status:** **Accepted** (Phase 02 UX)
- **Context:** Strength coaches drafting multi-week periodization need simultaneous visibility of the overarching mesocycle structure and granular set prescriptions.
- **Decision:** Implement a dual-pane layout on desktop/tablet (>= 1024px) with a sticky Program Outline Tree on `inline-start` (35% width) and an Exercise Prescription Editor on `inline-end` (65% width). Reflow into an accordion stack on mobile viewports.
- **Consequences:** Accelerates program creation speed and maintains periodization context.

---

### ADR-025 — Persian Typography Strategy: Vazirmatn Variable Web Font
- **Status:** **Accepted** (Phase 02 UX)
- **Context:** Persian text readability on high-DPI mobile screens and desktop monitors requires specialized font metrics to prevent clipping of vertical diacritics and ascenders/descenders.
- **Decision:** Adopt **`Vazirmatn`** (OFL licensed) as the primary Persian font family, augmented with +15% line-height relative to Latin text and zero letter-spacing. Pair with `Inter` for English text.
- **Consequences:** Delivers crisp, legible Persian typography across all viewport sizes without font-licensing liability.

---

### ADR-026 — Non-Clinical UX Language Standard for Subjective Feedback
- **Status:** **Accepted** (Phase 02 UX)
- **Context:** Collecting pain, soreness, and fatigue data must not cross into medical diagnosis or clinical treatment claims.
- **Decision:** All subjective health reporting in the UI is strictly labeled as **"Discomfort & Readiness Feedback for Coach Review"** accompanied by mandatory non-clinical disclaimers.
- **Consequences:** Protects the platform from medical device regulatory liabilities while maintaining high coaching utility.

---

### ADR-027 — Explicit Affirmative Consent Interaction Model for Sensitive Photos
- **Status:** **Accepted** (Phase 02 UX)
- **Context:** Physique progress photos are highly sensitive personal assets requiring unambiguous privacy boundaries.
- **Decision:** The UI mandates an explicit modal consent dialog before any photo upload, stating clearly that photos are accessible only to the assigned coach. Progress photos default to strictly private, and athletes can unilaterally revoke coach access at any time.
- **Consequences:** Establishes strong consumer trust and adheres to international privacy standards.

---

### ADR-028 — Dark-Neutral Visual Theme for Mobile Gym-Floor Glare Reduction (Design Target)
- **Status:** **Accepted** (Phase 02 UX — design target; requires implementation validation and user testing)
- **Context:** Gyms frequently have intense overhead lighting and athletes operate devices with sweaty hands and variable screen brightness. Whether a dark theme measurably reduces perceived glare is a *hypothesis* requiring pilot validation, not an established proven benefit.
- **Decision:** Implement a **Dark Obsidian Neutral Canvas** (`#0B0F17`) as the default *proposed* visual theme for the Athlete PWA, using high-contrast Emerald/Teal status accents and crisp typography with design-target contrast ratios intended to meet WCAG 2.2 AAA (requires implementation contrast testing).
- **Consequences:** *Proposed* to reduce perceived screen glare and reduce battery consumption on OLED mobile devices during 60+ minute training sessions; actual effectiveness requires user testing and device validation. Light-theme tokens remain specified for desktop administration.

---

### ADR-002 (Phase 03 Update) — Preferred Technical Stack Finalized Conditionally

- **Status:** **Conditionally Accepted — Proposed pending Phase 04 validation**
- **Context:** Need final stack for implementation.
- **Decision Final:** Frontend Next.js 14 App Router + React + TS + Tailwind logical properties + next-pwa/Workbox proposed; Backend Django 5 + DRF + Python 3.12; DB PostgreSQL 16 + pg_trgm + btree_gin + pgcrypto; Cache/Queue Redis 7 + Celery; Media S3-compatible private buckets presigned TTL ≤15min; API REST /api/v1 OpenAPI 3.1 provisional; PWA Manifest + SW three-level; E2E Playwright; CI/CD GitHub Actions.
- **Options Considered:** Alternative frontend Remix, SvelteKit; backend FastAPI, Rails; DB MySQL; cache in-memory only; media local FS.
- **Recommendation:** Stack as above for MVP velocity, mature ecosystem, security best practices.
- **Consequences:** Mature ORM, built-in admin, battle-tested security, excellent velocity; operational cost managed via PaaS; licensing: all MIT/Apache/BSD except PostgreSQL PostgreSQL License permissive.
- **Security:** Django CSRF, XSS protections, Argon2 support; Next.js CSP; S3 private.
- **Migration:** If need to replace frontend, API contract stable; if DB change, ORM migrations needed.
- **Status:** Conditionally Accepted — requires POC validation of UUIDv7, pg_trgm perf, Workbox bundle size, PaaS vs K8s infra cost.

---

### ADR-005 (Phase 03 Update) — Auth/Session Strategy (Corrected Transport Consistency)

- **Status:** **Proposed (Conditional Acceptance) — Correction for Auth Transport Consistency**
- **Context:** Email+password MVP but need session security and clear transport choice between cookies and Bearer tokens.
- **Decision (Corrected):**
  - **Recommended MVP Strategy:** HttpOnly/Secure/SameSite cookie sessions (Django `sessionid`):
    - HttpOnly true (JS inaccessible, prevents XSS theft of session), Secure true (HTTPS only), SameSite=Lax (CSRF mitigation for cross-site POST, balances usability; Strict for sensitive actions optional).
    - No long-lived tokens in localStorage/sessionStorage — explicit prohibition.
    - CSRF strategy for cookie-based mutations: double-submit token or Django CSRF middleware — frontend reads `csrftoken` cookie (non-HttpOnly) and sends `X-CSRFToken` header for POST/PATCH/DELETE; SameSite=Lax additional layer; verify CSRF on server.
    - Frontend/backend trust boundary: browser untrusted, backend authoritative, all auth checks server-side.
    - Rate limit 5/15min per IP/email via Redis, password strength validation, Argon2id/bcrypt cost ≥12, single-use reset token 15min TTL, invitation token 7d single-use SHA256 hashed.
  - **Optional Alternative (Bearer/JWT):** If bearer/JWT retained:
    - Short-lived access tokens ≤15min in memory (React state/memory, not localStorage), rotating refresh tokens in HttpOnly Secure SameSite cookie with reuse detection revoking all sessions on reuse.
    - Explicit prohibition: never store long-lived refresh or access tokens in localStorage/sessionStorage.
    - CSRF not applicable if using Authorization header Bearer (not auto-sent cross-origin), but still need XSS protections (HttpOnly refresh).
  - **Which Recommended for First Implementation:** Cookie sessions (simpler CSRF handling via Django built-in, no token storage complexity).
- **Consequences:** Secure, UX reasonable, cost low, no SMS gateway complexity, clear cookie vs bearer guidance.
- **Security:** Prevents credential stuffing (rate limit), session theft (HttpOnly Secure SameSite + no localStorage), CSRF (SameSite + CSRF token), invitation reuse.
- **Status:** Proposed conditional — requires Phase04 validation. OPENAPI.yaml securitySchemes keeps both cookieAuth and bearerAuth but documents recommendation.

---

### ADR-009 (Phase 03 Update) — Calendar Strategy

- **Status:** **Accepted Conditional — frontend validation required**
- **Context:** Jalali UI vs Gregorian storage.
- **Decision:** UTC/Gregorian timestamptz storage, ISO8601 API, frontend date-fns-jalali renders Jalali when locale fa-IR, Gregorian when en-US; week layout Saturday-Friday fa-IR or Monday-Sunday configurable.
- **Consequences:** Clean backend, robust tz math, native Persian experience.
- **Status:** Accepted conditional.

---

### ADR-010 — Monorepo Layout & Package Boundaries (Phase 03 Final Orientation)

- **Status:** **Proposed (Accepted Orientation — scaffold in Phase04)**
- **Context:** Need code organization without implementing.
- **Decision:** Proposed `frontend/` Next.js + `backend/` Django + `docs/` + `.github/` + `scripts/` + `docker-compose.yml` (Phase04). Monorepo tooling: npm workspaces or pnpm? For frontend only. Backend separate venv/poetry. Lint config root.
- **Consequences:** Simple for MVP, easy CI cache, clear separation docs vs code.
- **Security:** No secrets in repo, .env.example only placeholders.
- **Status:** Proposed — scaffold Phase04.

---

### ADR-014 — Organization Membership & Role Binding Model (Multi-Role) — Corrected Owner Source Truth + Multi-Role Behavior + Assignment Reactivation Reference

- **Status:** **Accepted Conditional — multi-role affirmed — Correction for Data-Model Integrity (Tasks 4.1, 4.2, 4.3)**
- **Context:** Users may belong to multiple orgs, may have multiple roles per org (coach+athlete same org). Need to avoid drift between Organization.owner_user_id and owner Membership, define effective permissions for multi-role, and define reactivation invariant for CoachAthleteAssignment.
- **Decision (Corrected):**
  - **Organization Owner Source of Truth (4.1):** `Organization.owner_user_id` is authoritative source of truth for single owner MVP (legal/billing owner). There must exist exactly one active Membership with `role=owner` per org, and its `user_id` must equal `owner_user_id`. Membership owner row is derived/automatically managed, not independently mutable — kept in sync via transactional `OrganizationService.transferOwnership()` which updates owner_user_id and swaps Membership rows atomically, audit `org.owner_transferred`. No two independent mutable ownership fields drifting.
  - **Membership Multi-Role Behavior (4.2):**
    - Schema allows multi-role per user+org via `UNIQUE(user_id, organization_id, role)`, e.g., coach+athlete same org.
    - MVP policy: single primary role per org recommended for simplicity; multi-role allowed but not required, explicitly enabled via owner action.
    - Effective permissions = union of all active roles for that user in that org (most permissive, priority owner>coach>support>athlete for UI display). Backend computes via `AuthZService.effectivePermissions()` server-side, not trusting frontend.
    - Role elevation audited: any Membership creation, role change, status change logs `membership.created`, `status_changed`, `role_changed` with actor/target/old/new/IP hash.
    - Active org + active role: session stores `active_organization_id` + optional `active_role` if multiple roles; frontend receives `memberships` array + `effective_permissions` computed server-side; UI shows role switcher if multiple roles, default highest privilege.
    - Frontend receives effective permissions but backend authoritative.
  - **CoachAthleteAssignment Reactivation (4.3) (Reference — detailed in ERD.md):**
    - Previous permanent unique `UNIQUE(org, coach, athlete)` prevented recreation after archival.
    - Corrected: partial unique for active only `UNIQUE(organization_id, coach_user_id, athlete_user_id) WHERE status='active'` (or WHERE archived_at IS NULL) — allows historical archived rows + recreation, only one active per triple.
    - Workflow: archival sets status archived + archived_at/ended_at + audit; reactivation creates new row preserving history (preferred) or reactivates archived if no active exists, audit reactivated; reassignment archives old + creates new.
    - No migrations in Phase03 — conceptual invariant only, proposed for Phase04/05.
- **Consequences:** Avoids ownership drift, supports multi-tenant gym coaches cleanly, prevents cross-tenant credential duplication, enables future multi-role, preserves assignment history while allowing reactivation.
- **Status:** Accepted conditional — corrections documented in ERD.md 3.1 Identity & Tenancy, DATA_MODEL.md 3.1, and this ADR.

---

### ADR-015 — Program Versioning & Assignment Snapshot Strategy (Immutable JSONB)

- **Status:** **Accepted Conditional**
- **Decision:** Snapshot JSONB immutable on assignment — deep copy of phases/weeks/days/workouts/items/prescriptions at instant of assignment. Athlete logs attach to snapshot version ID. Explicit version push requires confirmation. ProgramVersion optional table for push history.
- **Consequences:** Historical integrity, future edits don't corrupt logs.
- **Status:** Accepted.

---

### ADR-016 — Data Deletion, Soft-Delete, and Archival Lifecycle

- **Status:** **Accepted Conditional**
- **Decision:** Operational entities Programs, Exercises, Organizations use soft-archive archived_at timestamp filtered from active queries. User erasure via multi-stage anonymization & hard deletion: PII wiped, photos S3 deleted, memberships archived, historical telemetry disassociated anonymized aggregates retained, audit user.anonymized. AuditEvent never deleted. Export TMP 7-day lifecycle.
- **Consequences:** GDPR-adjacent, relational integrity preserved.
- **Status:** Accepted conditional.

---

### ADR-017 — Entity Identifier Strategy (UUIDv7 vs BigInt/UUIDv4)

- **Status:** **Proposed — requires validation — not authz substitute**
- **Context:** Prevent enumeration, support offline client-side ID generation for Phase12 queue.
- **Decision:** Proposed UUIDv7 time-ordered 128-bit for all public tenant entities. Must NOT be used as authz substitute — server-side RBAC/ABAC still mandatory. Time-ordered improves B-tree locality in PG. Validation required in Phase04: PG + Python (uuid6 package) + JS support.
- **Fallback:** UUIDv4 if UUIDv7 libraries immature.
- **Security:** Non-guessable but not security boundary.
- **Status:** Proposed.

---

### ADR-018 — Persian Search Normalization & Trigram Indexing Strategy

- **Status:** **Accepted Conditional — pg_trgm + normalizer**
- **Decision:** Two-layer: Python/PostgreSQL normalizer PersianNormalizer folding Perso-Arabic variants (ي/ى → ی, ك → ک, Arabic-Indic digits, ZWNJ → space, strip diacritics) — precise wording Perso-Arabic script keyboard-variant normalization for Persian search, no Arabic product support implied. Second layer pg_trgm GIN indexes on ExerciseAlias.normalized_alias and ExerciseTranslation.name.
- **Consequences:** Instant typo-tolerant Persian/English search zero external cluster.
- **Status:** Accepted conditional.

---

### ADR-029 — Frontend Architecture — Next.js App Boundaries

- **Status:** **Proposed pending Phase04 scaffold**
- **Context:** Need frontend component boundaries without implementing.
- **Decision:** Structure /app/[locale]/(auth)/(app)/(coach)/(org)/(admin) routes mapping 34 P0 screens SCR-... ; /components/ui (Btn, Input, Modal focus-trapped, DatePicker Jalali/Gregorian) + /components/domain (WorkoutCard, ProgramTree, ExerciseCard, RestTimer, ConsentModal) + /components/layout (BottomNav 5 tabs Today/Calendar/Progress/Messages/Profile, Sidebar collapsible 260px, TopBar OrgSwitcher LangSwitcher); /lib/api apiClient fetch wrapper auth Accept-Language idempotency-key X-Request-ID, /lib/auth session, /lib/i18n next-intl, fa-IR.json/en-US.json, /lib/pwa manifest SW registration offline fallback network hook, /lib/search Persian normalization helper; /styles design tokens CSS variables logical properties only Vazirmatn Inter. Pages import only from components, lib/api, lib/i18n, lib/pwa — never direct DB. apiClient centralizes error RFC7807, rate-limit retry, correlation ID.
- **Consequences:** Clear separation, RTL/LTR parity, PWA-ready.
- **Status:** Proposed.

---

### ADR-030 — Backend Architecture — Django Module Boundaries (20 Modules)

- **Status:** **Proposed Accepted Orientation**
- **Context:** Modular monolith need domain isolation without microservices.
- **Decision:** 20 modules M01-M20 as documented in DOMAIN_MODULES.md: Identity, Org, Membership, AuthZ/Consent, Exercise Catalog, Media/Rights, Programs, Templates, Assignments/Snapshots, Sessions, Progress/Feedback, Messaging, Notifications, Admin/Moderation, Audit, Privacy Export/Erasure, Future Nutrition P1, Future Billing Phase10, Future Marketplace P2, Future AI Phase11. Each owns entities, service layer public interface, permissions.py, serializers, events emitted/consumed, test boundary, extraction risk. Dependency hierarchy lowest to highest: Identity → Org → Membership → AuthZ/Consent → Exercise/Media → Programs → Assignments → Sessions/Progress → Messaging/Notifications → Admin/Audit/Privacy → Future. No circular imports enforced via import-linter in CI.
- **Consequences:** Maintain velocity + extraction path.
- **Status:** Proposed.

---

### ADR-031 — PostgreSQL Version/Extension Strategy

- **Status:** **Proposed requires validation**
- **Decision:** PostgreSQL 16 proposed (managed RDS/Supabase/Neon). Extensions: pg_trgm for trigram search, btree_gin, pgcrypto/uuid-ossp for ID gen. JSONB for snapshot_payload. Timestamptz UTC for all timestamps. Partial unique index for single primary location. GIN indexes for normalized alias. B-tree for scheduled_date, audit created_at.
- **Alternatives:** PG15 still ok, PG17 maybe newer but 16 stable. MySQL considered but JSONB + trigram weaker.
- **Operational cost:** Managed PG cost ~ $15-50/mo for pilot.
- **Security:** At-rest encryption provider, TLS.
- **Status:** Proposed pending POC of pg_trgm performance + UUIDv7 generation.

---

### ADR-032 — Auth/Session Strategy (Corrected — Recommended MVP Cookie Sessions + Optional JWT Alternative)

- **Status:** **Proposed Conditional Acceptance — Correction for Auth Transport Consistency**
- **Context:** Need to reconcile docs mentioning both cookies and Bearer tokens — define one recommended MVP and one optional alternative with explicit security properties.
- **Decision (Corrected):**
  - **Recommended MVP:** Cookie sessions:
    - Cookie behavior: `sessionid` HttpOnly true (JS inaccessible), Secure true (HTTPS only), SameSite=Lax (CSRF mitigation, Lax for usability, Strict for sensitive state-changing? Documented as Lax per Django default but with CSRF token). No long-lived token in localStorage/sessionStorage — explicit prohibition.
    - CSRF: double-submit token or Django CSRF middleware. Flow: backend sets `csrftoken` cookie (non-HttpOnly, readable by JS), frontend reads and sends `X-CSRFToken` header for POST/PATCH/DELETE, backend verifies. SameSite=Lax additional layer.
    - Trust boundary: frontend untrusted, backend authoritative, all RBAC/ABAC server-side.
    - Rate limit 5/15min per IP/email via Redis, password strength, Argon2id/bcrypt cost≥12, reset 15min single-use, invitation 7d SHA256 single-use.
  - **Optional Alternative — Bearer/JWT:**
    - Short-lived access ≤15min in memory (not localStorage), rotating refresh in HttpOnly Secure SameSite cookie with reuse detection — if refresh reuse detected, revoke all sessions and alert.
    - Explicit prohibition: never store long-lived refresh/access tokens in localStorage/sessionStorage (prevents XSS theft).
    - When using bearer, Authorization header `Bearer <access_token>` not auto-sent cross-origin, therefore intrinsically CSRF-resistant, but still need XSS protections and HttpOnly refresh.
  - **Explicit Prohibitions:** No `FE --> SecretMgr`, no private secrets in frontend bundle, no long-lived tokens in localStorage, no `unsafe-inline` as accepted CSP.
  - **Final Choice for First Implementation:** Cookie sessions (simpler, Django built-in). JWT alternative remains optional, marked proposed/conditional requiring Phase04 validation.
- **Consequences:** Clear guidance prevents implementation drift between cookie vs bearer, reduces XSS/session theft risk, aligns with OPENAPI.yaml securitySchemes.
- **Final Review Fix (Task 2 + Task 1 Final):**
  - **Secret Manager Boundary Final:** Corrected misleading `FE -->|Public runtime config only NEXT_PUBLIC_* NO private secrets| BE` arrow — public config is not a secret-management flow from frontend to backend. Correct notation: `PublicConfigProvider --> FE` (public config only), `BE --> SecretMgr` (private secrets), `Worker --> SecretMgr` (private secrets), `FE --> BE : HTTPS /api/v1 requests only`. Applied to DEPLOYMENT_ARCHITECTURE, CONTAINER_ARCHITECTURE, SYSTEM_CONTEXT, COMPONENT_BOUNDARIES. Verified no FE --> SecretMgr remains in architecture diagrams (only explanatory text about forbidden).
  - **AuthResponse Consistency Final:** `OPENAPI.yaml` AuthResponse previously presented access_token/refresh_token as ordinary properties. Corrected to make tokens optional/nullable, documented present only when optional bearer strategy selected, recommended MVP uses HttpOnly session cookie + CSRF token, not tokens in body. Added csrf_token optional/nullable present only when cookieAuth MVP, added separate schemas CookieAuthResponse (recommended MVP — no tokens in body, HttpOnly cookie via Set-Cookie, CSRF token) and BearerAuthResponse (optional alternative — short-lived access ≤15min memory + rotating HttpOnly refresh cookie). Updated /auth/register and /auth/login endpoint descriptions to clarify MVP cookie session no tokens in body, optional bearer tokens optional, explicit prohibitions no long-lived tokens in localStorage, FE --> SecretMgr forbidden, public config PublicConfigProvider --> FE, private secrets BE/Worker --> SecretMgr, FE --> BE HTTPS /api/v1 only, provisional until Phase04. Security schemes consistent, error responses RFC7807 message_key, P0 groups align, no payment/AI/wearable P0.
  - **Validation:** YAML parses (manual regex validation due to no-install rule), OpenAPI 3.1 OK, all local $ref resolve (137 total, 137 local, 0 missing, 61 defined schemas after adding CookieAuthResponse/BearerAuthResponse), no frontend-to-Secrets-Manager relationship remains in architecture diagrams (grep for actual mermaid arrow shows none, correct notation present), no app code/dependencies/migrations/secrets/real health data added.
- **Status:** Proposed conditional — requires Phase04 validation. Security sections in OPENAPI.yaml updated to document recommendation. Final review corrections applied in commit b6ea570 + new correction commit (current).

---

### ADR-033 — API Error Model

- **Status:** **Accepted**
- **Decision:** RFC7807 style `type` (URI), `title`, `status`, `detail`, `instance` + extension `message_key` for localized frontend i18n + optional `field_errors` object. Consistent across all endpoints. Example in OPENAPI.yaml.
- **Consequences:** Standards-aware, actionable, prevents leakage (generic auth errors, 404 for cross-tenant obscurity).
- **Status:** Accepted.

---

### ADR-034 — Media Storage Architecture

- **Status:** **Accepted**
- **Decision:** Private S3-compatible buckets BlockPublicAcls true no listing, versioning enabled, SSE-S3, buckets: coachos-media-private, coachos-progress-private Tier4 isolated, org-logos, exports-tmp lifecycle 7d. Signed URLs TTL ≤15min private, no caching Tier4 in SW, MIME whitelist image/jpeg/png/webp video/mp4, magic bytes validation, size limits 10MB image 100MB video, checksum SHA256, thumbnail 256/512 webp via Pillow worker, video poster via ffmpeg, optional ClamAV scan quarantine, rights metadata mandatory for exercise media, takedown workflow, CDN optional for canonical with signed URLs but no long cache for Tier4, retention archive vs hard delete.
- **Status:** Accepted.

---

### ADR-035 — PWA Architecture

- **Status:** **Accepted**
- **Decision:** Three-level: Phase04 manifest.json standalone display start_url /app/today theme #0B0F17 icons 192/512 maskable, SW registration Workbox or custom, app-shell caching CacheFirst fonts/icons StaleWhileRevalidate JS/CSS, offline fallback localized page, install guidance via beforeinstallprompt defer + iOS Share → Add to Home Screen instructions. Phase07 touch-optimized 44×44 min 48×48 preferred CTA, numeric keypad inputmode decimal, rest timer client-side JS + SVG ring + haptic, form-state protection temporary in-memory React state not durable, network status hook useNetworkStatus online/offline events + yellow banner offline unsaved input retained temporarily retry required, retry failed set log toast, video demo requires network fallback text cues. Phase12 IndexedDB Dexie durable queue pending/syncing/synced/failed, sync status UI, exponential backoff, conflict resolution last-write-wins for set logs append-only, background sync API if supported fallback foreground sync, push Web Push VAPID limitations iOS 16.4+ standalone only, HealthKit/Health Connect eval native bridge decision.
- **Status:** Accepted.

---

### ADR-036 — Offline Boundary

- **Status:** **Accepted**
- **Decision:** Explicit boundaries: Phase04 cached shell + offline fallback only; Phase07 temporary/in-memory preservation of unsaved input + network status + retry behavior no durable offline queue or guaranteed message queue; Phase12 durable IndexedDB workout queue offline persistence message queue if approved sync retries conflict resolution. Replace wording sets saved locally or message queued with unsaved input retained temporarily retry required after reconnection unless Phase12 queue explicitly described.
- **Status:** Accepted — enforced in STATE_AND_ERROR_MATRIX, SCREEN_INVENTORY, USER_FLOWS, UX_COPY.

---

### ADR-037 — Backup/RTO/RPO Targets

- **Status:** **Proposed Requires Validation + Founder Approval on Cost**
- **Decision:** PG daily snapshot retention 30d proposed + WAL PITR RPO 15min (or 5min if WAL frequency) RTO 1h restore+30m validation, manual snapshot pre-migration; S3 versioning enabled noncurrent expire 30d proposed, retention Tier4 hard delete bypass versioning for erasure compliance; exports-tmp 7d lifecycle; Redis not source of truth loss acceptable; code git; restore runbooks DB/S3 + weekly automated restore testing to staging smoke tests; RTO full platform 2-4h infra rebuild; incident response steps detect triage contain investigate recover post-mortem communicate; breach response containment audit notification within 72h if GDPR legal required; rollback app previous image + migration reverse 2-step add/dual-write/backfill/switch/drop pattern with pre-migration snapshot.
- **Cost:** Multi-AZ PG cost extra, cross-region replication deferred P1.
- **Status:** Proposed pending founder infra budget approval.

---

### ADR-038 — Environment Separation

- **Status:** **Proposed**
- **Decision:** local developer docker-compose synthetic seed only no real secrets; staging pre-prod integration auto deploy from main or arena branch anonymized synthetic copy no prod PII E2E Playwright security scans; production live pilot tag v0.x.x + manual approval gate real user data Tier1-4 PITR backups audit enforced. Distinct VPC DB buckets secrets per env. No prod data copied to local. Access to prod secrets limited founder/SRE via Secrets Manager IAM.
- **Status:** Proposed.

---

### ADR-039 — CI/CD Strategy

- **Status:** **Proposed**
- **Decision:** GitHub Actions workflows: ci.yml lint/type/unit/integration/security scan (ruff/mypy, tsc eslint, pip audit npm audit gitleaks, Dependabot Snyk) on every PR; e2e.yml Playwright RTL/LTR visual checks fa-IR en-US; deploy-staging.yml auto deploy on merge to main; deploy-prod.yml manual workflow_dispatch tag + health check /healthz /readyz. Use OIDC to AWS/GCP not secrets in repo. Docker images FE+BE keep last 5 tags for rollback. Frontend Vercel/Netlify auto.
- **Status:** Proposed — not created in Phase03.

---

### ADR-040 — Observability Strategy

- **Status:** **Proposed**
- **Decision:** Structured logging JSON structlog + pino, required fields timestamp level service request_id org_id actor_user_id action entity_type/id duration status message version, redaction processor removes password, token, Authorization, message content, health flag details, photo keys, signed URLs, IP hash. Correlation request_id middleware UUIDv7 X-Request-ID propagate response. Audit vs debug logs separation: debug ELK/CloudWatch 30d proposed no Tier3/4 payloads, audit immutable PG table 1y+ retention. Metrics Prometheus django-prometheus /metrics protected counters http_requests_total http_request_duration_seconds auth_login_failures auth_rate_limit_hits program_assignments workout_sessions set_logs media_uploads notifications celery_tasks audit_events export_requests db_connections cache_hit_ratio. Error tracking Sentry DSN env scrub sensitive, release tracking commit hash. Health endpoints /healthz liveness public 200 if up, /readyz readiness checks DB Redis S3 Celery returns JSON version timestamp protected. Alerting categories auth anomaly >20 fails IP 15min, cross-tenant attempts spike, unauthorized photo 403 spike, 5xx >1% 5min, latency p95 read>400ms write>800ms 10min, DB connections >80%, Redis down >1min, S3 upload fail >5%, Celery queue >100 10min, export fail >3, backup fail, disk >80%, cert expiry <14d. Frontend Web Vitals LCP CLS INP via next/web-vitals optional analytics endpoint.
- **Status:** Proposed requires validation.

---

### ADR-041 — OpenAPI 3.1 Contract Structure

- **Status:** **Proposed Accepted as Provisional**
- **Decision:** API versioned under /api/v1, REST + JSON, auth via bearerAuth + cookieAuth HttpOnly, localization via Accept-Language fa-IR/en-US, error model RFC7807 + message_key, endpoint groups P0: auth, current user/profile, organizations, locations, memberships, invitations, exercise catalog, exercise moderation, programs, templates, assignments, today view, workout sessions, set logs, feedback flags, progress metrics/photos, messages, notifications, audit events, privacy export/deletion, media signed URLs, consents. For every endpoint documented purpose authentication required role object permission request/response schema error responses localization idempotency expectation audit event rate-limit category data sensitivity. Idempotency-Key optional for critical writes invite assign payment future. Rate limit categories auth 5/15min search 30/min messages 10/min export 2/day.
- **Status:** Provisional — requires implementation review Phase04.

---

### ADR-042 — Threat Model & Security Control Matrix

- **Status:** **Accepted**
- **Decision:** STRIDE method + OWASP Top10 mapping, 21 threats T01-T21 covering account takeover, credential stuffing, session theft, invitation abuse, cross-tenant IDOR, unassigned coach, owner overreach, photo exposure, malicious uploads, stored XSS, CSRF, SSRF, webhook forgery future Phase10, notification abuse, export abuse, erasure abuse, insider/admin misuse, prompt injection future Phase11, supply-chain, backup leakage, search enumeration. For each: asset, actor, attack path, impact, likelihood, risk, preventive/detective/corrective controls, test strategy, owner, residual risk. Control matrix maps threat→requirement→architecture control→phase→test type→evidence→status including negative controls for cross-tenant reads/writes, unassigned coach, suspended membership, unauthorized photo/message/audit/export.
- **Status:** Accepted.

---

### ADR-043 — Privacy & Data Lifecycle

- **Status:** **Accepted**
- **Decision:** Lifecycle stages 11: collection, consent, storage, use, sharing, export, retention, revocation, deletion, anonymization, backup destruction. Classification Tier0 public metadata, Tier1 account/identity, Tier2 coaching operational, Tier3 sensitive health-adjacent pain flags body metrics, Tier4 progress media most sensitive, Tier5 audit immutable, Tier6 secrets, Tier7 payment future P1 Phase10, Tier8 AI future Phase11. For each class purpose legal/privacy assumption owner/controller assumption access rules encryption logging restriction retention question export/deletion behavior consent requirement documented. No legal compliance claim — privacy-aligned engineering design requires jurisdiction-specific legal review. Explicit consent model for progress photos + nutrition P1 multi-prof, revocation immediate, export ZIP via Celery tmp S3 24h link, erasure pipeline hard delete PII + anonymized aggregates. Pre-DPIA checklist large-scale sensitive, systematic monitoring, automated profiling, multi-prof sharing, progress-photo processing, wearable future, AI.

---

### ADR-044 — Monorepo Structure & Local Workspace Scaffolding
- **Status:** **Accepted** (Phase 04 Baseline)
- **Context:** Establishing an executable, reproducible, and secure monorepo structure separating frontend, backend, infrastructure, and CI workflows without coupling independent runtime dependencies.
- **Decision:** Adopt the standard modular monorepo layout:
  - `frontend/`: Next.js 14 App Router, TypeScript strict mode, Tailwind CSS with logical properties, Vitest test suite.
  - `backend/`: Django 5 + Django REST Framework, Python 3.12 target, Pytest test suite.
  - `infra/`: Docker compose orchestration, container definitions (`infra/docker/`), utility scripts (`infra/scripts/`).
  - `.github/workflows/`: GitHub Actions CI pipeline running lint, type-check, tests, manifest validation, secret scanning, and no-Arabic verification.
- **Consequences:** Provides clean isolation between client and server dependencies, enables independent container builds, and preserves straightforward local development ergonomics.

---

### ADR-045 — Frontend Foundation Architecture & Public Runtime Configuration Boundary
- **Status:** **Accepted** (Phase 04 Baseline)
- **Context:** Need strict client-side security boundaries preventing private server secrets from leaking into client JavaScript bundles or runtime memory.
- **Decision:**
  - All client-side runtime variables must start with the `NEXT_PUBLIC_` prefix (e.g., `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_APP_NAME`, `NEXT_PUBLIC_SENTRY_DSN_PUBLIC`).
  - A strict runtime environment validator (`lib/config/env.ts`) throws runtime errors if private secret patterns (e.g., database URLs, secret keys, AWS private keys) are accessed or detected on the client.
  - Client-side code never communicates directly with Secrets Manager or internal database services.
  - No long-lived authentication tokens are stored in `localStorage` or `sessionStorage`.
- **Consequences:** Eliminates client-side secret exposure risk (T02) and guarantees clear separation between public and private configuration.

---

### ADR-046 — PWA Baseline Architecture, App-Shell Caching, and Offline Fallback Strategy
- **Status:** **Accepted** (Phase 04 Baseline)
- **Context:** Phase 04 must deliver a fully installable, mobile-responsive PWA foundation without prematurely implementing Phase 12 durable offline queuing or background sync.
- **Decision:**
  - Implement a standard Web App Manifest (`manifest.json`) supporting `standalone` display mode, dark theme `#0B0F17`, and original 192x192 / 512x512 maskable icons.
  - Deploy a resilient Service Worker (`sw.js`) utilizing:
    - Cache-First strategy for static immutable assets (fonts, icons, CSS, JS).
    - Network-First strategy for navigational document requests, gracefully falling back to a dedicated bilingual Offline Fallback Page (`/offline` or cached offline shell).
  - Implement a network status indicator hook and UI banner (`NetworkStatusBanner.tsx`) warning users when offline that unsaved input is retained temporarily in memory only and requires reconnection to save.
  - Explicitly document iOS and Android PWA limitations (WebKit 7-day storage eviction on inactive non-installed web apps, iOS push notifications requiring standalone mode in iOS 16.4+).
  - Do not claim that durable offline workout queues or IndexedDB synchronization exist in Phase 04 (deferred to Phase 12).
- **Consequences:** Delivers rock-solid installability and offline resilience while maintaining accurate architectural truth.

---

### ADR-047 — Bilingual RTL/LTR Execution & Persian Search Normalization Architecture
- **Status:** **Accepted** (Phase 04 Baseline)
- **Context:** Delivering an uncompromising bilingual user experience supporting Persian (`fa-IR`, RTL) and English (`en-US`, LTR) with zero Arabic resources or conflation.
- **Decision:**
  - Dynamically inject `lang` (`fa-IR` | `en-US`) and `dir` (`rtl` | `ltr`) on the root HTML document.
  - Enforce CSS logical properties (`margin-inline-start`, `padding-inline-end`, `border-start-start-radius`) across all UI styling.
  - Directional icons (arrows, chevrons, navigation flows) mirror automatically in RTL, while non-directional physical icons (dumbbells, weights, timers) remain unmirrored.
  - Mixed Persian and Latin text (e.g., "ست 1: 100 kg x 5 reps") uses BiDi isolation (`<bdi>` / unicode-bidi) to prevent visual punctuation distortion.
  - Provide a reusable `PersianNormalizer` utility in both frontend (`lib/i18n/normalizer.ts`) and backend (`apps/core/utils/persian_normalizer.py`) that folds Perso-Arabic script keyboard variants (`ي`/`ى` → `ی`, `ك` → `ک`, Arabic-Indic digits `٠-٩` → `۰-۹` / `0-9`, and strips zero-width non-joiners where appropriate for search indexing).
  - Separate Jalali UI presentation from UTC/Gregorian storage: API and database store timestamps in UTC ISO 8601; frontend formatters render Solar Hijri (Jalali) when `locale == 'fa-IR'`.
  - CI test fails build if any Arabic locale file, translation, or fixture is introduced.
- **Consequences:** Flawless RTL/LTR rendering, crisp Persian typography via Vazirmatn, and robust search preparation for Phase 06.

---

### ADR-048 — Backend Foundation, Error Sanitization Envelope, Middleware Pipeline, and Health Endpoints
- **Status:** **Accepted** (Phase 04 Baseline)
- **Context:** Establishing the core Django 5 / DRF foundation with enterprise security headers, correlation IDs, error sanitization, and health check endpoints without building Phase 05 domain entities prematurely.
- **Decision:**
  - Implement modular settings (`config.settings.base`, `development`, `staging`, `production`, `test`) reading from environment variables.
  - Establish a secure middleware stack:
    - `CorrelationIDMiddleware`: generates/propagates `X-Request-ID` (UUIDv7/UUIDv4) across requests, responses, and log records.
    - `SecurityHeadersMiddleware`: enforces strict HSTS, CSP baseline, X-Content-Type-Options, Referrer-Policy, and Permissions-Policy.
    - `LoggingRedactionMiddleware`: automatically scrubs passwords, tokens, authorization headers, and health data from logs.
    - `TenantContextMiddleware`: foundation interface for tenant context extraction.
  - Standardize error responses to RFC 7807 problem details with `type`, `title`, `status`, `detail`, `instance`, `message_key`, and `field_errors`.
  - Provide safe foundation endpoints:
    - `GET /healthz`: Public liveness endpoint returning HTTP 200 `{"status": "pass"}` without leaking infrastructure secrets.
    - `GET /readyz`: Dependency readiness check validating PostgreSQL database and Redis connectivity.
    - `GET /api/v1/meta`: Safe public API metadata (version, supported locales, auth strategy).
- **Consequences:** Robust, observable, secure backend shell ready for Phase 05 identity and tenancy.

---

### ADR-049 — Hosting and Dual-Region Deployment Strategy (Evaluation & Phase 04 Baseline)
- **Status:** **Accepted (Decision Gate Defined)**
- **Context:** Founder mandated dual-region capability for Persian/Iran-related users and European/international users without prematurely provisioning duplicate production cloud infrastructure in Phase 04.
- **Decision:**
  - Build a strictly provider-neutral containerized architecture (`Dockerfile` + `docker-compose.yml`).
  - Compare Managed PaaS, EU Cloud (Hetzner/AWS EU), Bare VPS, Dual-Region Active-Passive (Iran Edge Proxy + EU Core), and Dual-Region Active-Active across 10 evaluation dimensions in `docs/architecture/HOSTING_AND_DATA_RESIDENCY_DECISION.md`.
  - Establish Phase 04 baseline: Local Docker Compose + EU Staging Container Environment.
  - Production deployment and multi-region routing remain behind an explicit founder decision gate prior to commercial launch.
  - Zero real cloud credentials or sensitive data duplicated across regions in Phase 04.
- **Consequences:** Preserves maximum architectural agility, avoids premature infrastructure expenditure, and maintains strict GDPR/data residency compliance.

