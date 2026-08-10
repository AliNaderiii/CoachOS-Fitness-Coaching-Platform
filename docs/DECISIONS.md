# Architecture & Product Decision Log (ADRs) — CoachOS

**Document version:** 1.0.0 (Phase 01 Baseline)  
**Last updated:** 2026-08-10  
**Format:** Lightweight Architecture Decision Records (ADRs)  

**Status taxonomy:** `Accepted` | `Proposed` | `Pending Founder Approval` | `Superseded` | `Rejected` | `Deferred`

---

## Summary of Decisions

| ADR ID | Decision Title | Status | Founder Approval Required? | Decided / Proposed Phase |
|--------|----------------|--------|-----------------------------|--------------------------|
| **ADR-001** | Modular Monolith Architecture for MVP | **Accepted** | No (Team Baseline) | Phase 00 |
| **ADR-002** | Preferred Technical Stack (Next.js + Django/DRF + PostgreSQL) | **Proposed** | No (Phase 03 Confirmation) | Phase 00 / 03 |
| **ADR-003** | Product Locales: Persian (`fa-IR`) and English (`en-US`) Only; Arabic Out of Scope | **Accepted** | Yes (Founder Mandate) | Phase 00 |
| **ADR-004** | Business Model: B2B2C Multi-Tenant SaaS | **Accepted** | Yes (Founder Approved) | Phase 00 |
| **ADR-005** | Authentication Channel: Email + Password Default with OTP Roadmap | **Proposed** | No | Phase 00 / 01 |
| **ADR-006** | Authorization Architecture: Server-Side RBAC + Object-Level Access Control | **Accepted** | No | Phase 00 / 01 |
| **ADR-007** | Constrained AI Assistance Deferred to Phase 11 | **Accepted** | No | Phase 00 / 01 |
| **ADR-008** | Exercise Media Rights, Provenance, and Moderation Metadata | **Accepted** | No | Phase 00 / 01 |
| **ADR-009** | Calendar Strategy: UTC/Gregorian Storage with Persian Jalali UI Display | **Proposed** | No | Phase 01 |
| **ADR-010** | Monorepo Folder Layout & Package Boundaries | **Deferred** | No | Phase 04 |
| **ADR-011** | PWA Sequencing Correction (Phase 04 Foundation, Phase 07 Mobile Log, Phase 12 Advanced Offline) | **Accepted** | No | Phase 01 |
| **ADR-012** | Repository License & Intellectual Property Strategy | **Pending Founder Approval** | **YES (Founder Decision)** | Phase 01 |
| **ADR-013** | Single-Location-First MVP Strategy | **Accepted** | No | Phase 01 |
| **ADR-014** | Organization Membership & Role Binding Model | **Proposed** | No | Phase 01 / 03 |
| **ADR-015** | Program Versioning & Assignment Snapshot Strategy | **Proposed** | No | Phase 01 / 03 |
| **ADR-016** | Data Deletion, Soft-Delete, and Archival Lifecycle | **Proposed** | No | Phase 01 / 03 |
| **ADR-017** | Entity Identifier Strategy (UUIDv7 vs BigInt) | **Proposed** | No | Phase 01 / 03 |
| **ADR-018** | Persian Search Normalization & Trigram Indexing Strategy | **Proposed** | No | Phase 01 / 03 |
| **ADR-019** | Athlete Data Ownership, Privacy, and Portability Architecture | **Accepted** | No | Phase 01 |
| **ADR-020** | Multi-Professional Collaboration & Consent Architecture (P1 Scope) | **Accepted** | No | Phase 01 |
| **ADR-021** | Payment Gateway Abstraction & Coach Monetization Deferral to Phase 10 | **Accepted** | No | Phase 01 |
| **ADR-022** | Public Discovery Marketplace Deferral to Phase 11+ / P2 | **Accepted** | No | Phase 01 |

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
- **Status:** **Deferred to Phase 04**
- **Context:** Structuring repository code directories for backend, frontend, documentation, and tooling.
- **Candidates:** `backend/` (Django) + `frontend/` (Next.js) + `docs/` + `.github/`. Scaffolding to occur in Phase 04.

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
- **Status:** **Pending Founder Approval (YES)**
- **Context:** The repository was initialized with an open-source MIT license. As a commercial B2B2C SaaS product, the intellectual property strategy requires formal founder evaluation.
- **Options Analyzed:**
  1. **Keep MIT License (Open Source):**
     - *Monetization:* Relies on hosted SaaS offering and services.
     - *Competitor Risk:* **Extremely High.** Any competitor can clone the entire codebase, branding, and workflows without restriction.
     - *Contributions & Portfolio:* Maximum public visibility and community contributions.
     - *Investors & White-Label:* Lower enterprise enterprise valuation; difficult to enforce proprietary white-label licensing.
  2. **Proprietary / All Rights Reserved (Commercial Closed Source):**
     - *Monetization:* Full protection of SaaS IP, enterprise licensing, and white-label deployments.
     - *Competitor Risk:* Zero legal reuse of proprietary software.
     - *Contributions & Portfolio:* Code remains private or source-available with commercial restrictions.
     - *Investors & White-Label:* Optimal for institutional investment and SaaS valuation.
  3. **Open-Core Model (e.g., AGPLv3 / Business Source License BSL):**
     - *Monetization:* Core engine open-source; enterprise multi-tenant, billing, and AI features closed-source.
     - *Competitor Risk:* Moderate; prevents cloud vendors from reselling without paying or contributing back.
  4. **Private Repository with Commercial License:**
     - *Monetization:* Traditional high-growth B2B SaaS posture.
- **Recommendation:** Recommend transitioning the commercial codebase to **Proprietary / All Rights Reserved** (Option 2) or **Open-Core with BSL** (Option 3) prior to Phase 04 scaffolding.
- **Action:** **Flagged for Founder Decision.** The `LICENSE` file remains MIT in Phase 01 and will not be modified until the founder provides written confirmation.

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
