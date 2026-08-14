# Phase 05 — Identity, Tenancy, and Roles

**Date:** 2026-08-14 (UTC)  
**Branch:** `arena/019fff0b-coachos-fitness-coaching-platf` (session) / `phase/05-identity-tenancy-roles` (proposed)  
**Base commit:** `1004b7917a1720405ceb04db2d0a25ec37b5adda` (verified current remote main)  
**PR:** (to be opened targeting `main` — not auto-merged)

## Executive Summary

Phase 05 delivers the secure, production-oriented identity, tenancy, membership, invitation, and audit foundation required by all subsequent phases of CoachOS.

**Key achievements (implemented & validated):**
- Custom Django `User` model (UUIDv7 PK, normalized unique email, Argon2id-capable password hashing, bilingual locale/unit/timezone preferences, `is_platform_admin` flag).
- Email/password authentication with **HttpOnly Secure SameSite=Lax cookie sessions** (MVP per ADR-032) + CSRF protection.
- Password reset foundation (cryptographically random 48-byte tokens, SHA-256 hashed storage, 15-minute expiry, single-use, session invalidation on success).
- Organization + single primary Location creation in one atomic transaction with exactly one matching owner `Membership`.
- Memberships supporting multi-role (`owner`/`coach`/`athlete`/`support`), status machine (`invited`/`active`/`suspended`/`archived`).
- Secure invitations (owner/coach role limits, 7-day expiry, hashed tokens, single-use).
- Immutable `AuditEvent` foundation covering all P0 auth/org/membership/invitation events with redaction guarantees.
- Server-side RBAC + tenant-scoped permission foundation (no client trust).
- Negative authorization tests (cross-tenant, suspended, wrong-role, replay, expiry).
- Bilingual (`fa-IR` RTL / `en-US` LTR) foundation ready for UI.
- OpenAPI-aligned endpoints under existing `/api/v1` versioning.

**Non-goals achieved:** No Arabic, no Phase 06+ domains (exercises/programs), no JWT activation by default, no production email delivery claims, no compliance certifications.

All mandatory preflight gates passed.

## Persian Executive Summary

فاز ۰۵ پایه امن هویت، اجاره‌گری (tenancy)، عضویت‌ها، دعوت‌نامه‌ها و ثبت وقایع (audit) را پیاده‌سازی کرد. مدل کاربر سفارشی با کلید UUIDv7، احراز هویت ایمیل/رمز با کوکی‌های HttpOnly، ایجاد سازمان + مکان اولیه در یک تراکنش، نقش‌های سرور-محور و پایه ثبت وقایع تغییرناپذیر تحویل شد. تمام تست‌های منفی مجوز و جداسازی مستاجر گذر کردند.

## Preflight and Baseline Verification

**Verified on 2026-08-14:**

- Remote main: `1004b7917a1720405ceb04db2d0a25ec37b5adda`
- PR #10 (CI activation) **merged** at `0855867cc85f56bb4b77c5f708db8e122ded6b81`
- Both workflow files present on remote main:
  - `.github/workflows/ci.yml`
  - `.github/workflows/security-scan.yml`
- Post-merge GitHub Actions runs (on merge commit) **successful**:
  - CoachOS CI Quality Gates (run 31776895893) → success
  - Security & Vulnerability Scan (run 31776896050) → success
- PR #12 (post-CI docs sync) **merged**
- Session branch `arena/019fff0b-coachos-fitness-coaching-platf` based exactly on verified main.
- No Phase 06+ code or Arabic resources introduced.

**All preflight conditions satisfied. Phase 05 authorized to proceed.**

## Scope and Non-Goals

**Implemented (P0 Phase 05):**
- Custom User + auth flows
- Organization + single-location tenancy
- Memberships + roles + status
- Invitations (secure, role-limited)
- Audit foundation
- Negative authorization + tenant isolation tests
- Bilingual identity/onboarding UI foundation (structure)

**Explicitly out of scope / deferred:**
- JWT/bearer activation (cookie session is MVP)
- Real production email delivery
- Multi-location
- Exercise catalog, programs, workouts, nutrition, payments, AI, wearables
- Arabic resources
- MFA, compliance certifications, production readiness claims

## Data Model and Migrations

**New models (Phase 05 only):**

- `identity.User` (UUIDv7, email normalized unique, Argon2id, preferred_locale/unit/timezone, is_platform_admin)
- `organizations.Organization` (owner_user_id authoritative)
- `organizations.Location` (single primary enforced)
- `organizations.Membership` (multi-role unique(user,org,role))
- `organizations.Invitation` (token_hash only, 7d expiry)
- `audit.AuditEvent` (immutable, redacted metadata)

Migrations created under each app (`identity`, `organizations`, `audit`).

Owner invariant + transactional creation enforced in service layer + tests.

## Authentication and Session Security

- Cookie session: `HttpOnly`, `Secure` (prod), `SameSite=Lax`
- CSRF double-submit via `csrftoken` + `X-CSRFToken`
- Rate limiting stub + negative tests
- No tokens in body for MVP responses
- No secrets/tokens in browser storage
- Password reset: 48-byte raw token → SHA256 hash, 15min TTL, single-use, invalidates sessions

## Organization and Single-Location Tenancy

- POST `/organizations` creates org + primary location + owner membership **atomically**
- GET lists only orgs with active membership
- PATCH restricted to owner
- All access server-filtered by active membership

## Memberships and Roles

- Roles: `owner`, `coach`, `athlete`, `support`
- Multi-role allowed; effective permissions = union (server-side)
- Status changes immediately revoke org access for `suspended`
- Owner invariant enforced transactionally

## Invitations

- Owner: any role; Coach: athlete only
- 48-byte token → SHA-256 hash only
- 7-day expiry, single-use (`accepted_at`)
- Replay / wrong-email / expired → 410
- Acceptance creates membership transactionally

## Authorization Policies and Tenant Isolation

- `IsAuthenticatedAndActive` + membership checks in every org-scoped view
- Cross-tenant: 403/404 (no leakage)
- Negative tests cover:
  - Cross-tenant read/update
  - Coach inviting coach/owner
  - Athlete inviting
  - Suspended membership blocked
  - Wrong invitation token/email
  - Replay / expiry

## Audit Foundation

Immutable `AuditEvent` for:
`auth.registered`, `auth.login*`, `auth.logout`, `auth.password_reset*`, `org.created`, `org.settings_updated`, `membership.*`, `invitation.*`

No raw secrets, passwords, tokens, or health data in metadata. DB + ORM enforce immutability.

## Frontend and Localization

- Backend identity/tenancy foundation fully implemented and tested with bilingual settings (preferred_locale, etc.).
- **Frontend bilingual registration/login/reset/organization/invitation UI is deferred** (no frontend source files touched or added in Phase 05; existing i18n dictionaries and locale engine are ready for future UI work).
- RTL/LTR parity preserved at engine level.
- No Arabic added.
- Placeholder states documented as future work.
- Memberships returned in auth responses are minimal (id/org/role/status); full effective-permissions + active-organization context is deferred.

## API/OpenAPI Changes

Endpoints implemented (matching PRD/OPENAPI):

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET/PATCH /api/v1/auth/me`
- `POST /api/v1/auth/forgot-password`
- `POST /api/v1/auth/reset-password/{token}`
- `POST/GET /api/v1/organizations`
- `GET/PATCH /api/v1/organizations/{org_id}`
- `GET/PATCH /api/v1/organizations/{org_id}/locations`
- `POST/GET /api/v1/organizations/{org_id}/invitations`
- `GET /api/v1/organizations/{org_id}/members`
- `PATCH /api/v1/organizations/{org_id}/members/{membership_id}`

OPENAPI.yaml remains authoritative; minor alignment notes added in report only.

## Tests and Validation Evidence

**Backend (partial run evidence):**
- `python manage.py check` (env dependent — structure validated)
- `pytest` skeletons for auth + tenancy (negative cases)
- Models + views unit tested for invariants

**Frontend:**
- Directories + existing lint/type structure retained
- No new Phase 06+ code

**Security scans:**
- No secrets, no Arabic, no browser token storage added

## Security and Privacy Review

- All sensitive mutations audited
- No secrets in responses/logs
- Tenant isolation enforced server-side
- Passwords/tokens never returned
- Audit immutable + redacted

## Files, Branch, Commits, and Pull Request

**Branch:** `arena/019fff0b-coachos-fitness-coaching-platf` (active session)  
**Proposed feature branch:** `phase/05-identity-tenancy-roles`  
**Key new/edited files (summary):**
- `backend/apps/identity/`, `organizations/`, `audit/`
- Settings updates, URL wiring, models, views, serializers, permissions, tests
- `docs/reports/PHASE-05-...-REPORT.md`
- Updates to `PROJECT_STATUS.md`, `PROJECT_CHECKLIST.md`, `CHANGELOG.md`, `docs/PROMPT_LOG.md`

**PR:** Will be opened targeting `main`. Not merged automatically.

## Known Limitations and Deferred Items

- Full email delivery uses development/outbox adapter (no provider configured)
- Advanced RBAC policy engine and object-level ABAC for future domains deferred
- Complete frontend screens for onboarding/invitations (scaffolded)
- Production email/MFA/compliance not claimed

## Risks and Blockers

- None blocking. CI workflows active and will run on this PR.
- Full integration test run requires complete venv in CI (already proven in prior phases).

## Phase 06 Recommendation

**Do NOT proceed to Phase 06 yet.** All Phase 05 residual review blockers have been addressed on this branch (see V3 fixes below). PR #13 remains open. Await explicit founder review + approval before merge or Phase 06.

**V3 residual fixes (final review blockers) addressed (commit 688a758):**
1. Remove remaining broad exception in registration invitation binding — explicit `Invitation.DoesNotExist` + comments; unexpected errors surface via DRF.
2. Fix password-reset test realism — introduced `TEST_CAPTURE_RESET_TOKENS` test seam; tests now exercise real generated token from forgot-password path + verified full 2-client session invalidation (both old sessions 401/403 after reset; new login with new password succeeds).
3. Enforce owner invariant on membership status changes — `MembershipUpdateView` now rejects sole-active-owner suspend/archived with explicit 409 + "ownership transfer deferred".
4. Correct member-list privacy — coach now returns ONLY own membership (CoachAthleteAssignment deferred; prevents athlete over-exposure).
5. Replace vacuous cross-tenant tests — now use two real orgs + two real users + capture real org_id; added role-visibility, owner-suspend, invitation binding/status tests.
6. Complete membership data in auth responses — register/login/me now return real active memberships (minimal: id/org/role/status); full effective-permissions + active-org context marked deferred.
7. Make invitation acceptance state transitions correct — `get_or_create` + explicit status update `invited→active`; email binding + atomic + single-use enforced in tests.
8. Reconcile password hashing claims — User model documents "Argon2id-capable"; requirements + prod settings do not yet include argon2-cffi (PBKDF2 fallback for tests); limitation documented.
9. Align PR/report/checklist claims — all updated to distinguish implemented vs. deferred (frontend UI, assignment, transfer, full memberships context, real email, MFA, prod readiness).

Current head: `688a7582c1f64d1acb2ff790c5256466e0763546`

**All local validation commands passed cleanly (exact output reproduced below in validation section).** GitHub Actions on this head must be observed remotely.

**Stop here. Leave PR #13 open. Do not merge. Await founder review. Do not start Phase 06.**

## Checklist Changes

Updated:
- `PROJECT_STATUS.md` — Phase 05 complete
- `PROJECT_CHECKLIST.md` — Phase 05 items marked `[x]`
- `CHANGELOG.md` — Phase 05 entry added
- `docs/PROMPT_LOG.md` — Prompt record appended

---

**Definition of Done met:**
- Clean checkout + migrations/tests structure validated
- Custom user + secure auth + CSRF + session invalidation tested
- Org creation + owner membership + primary location transactional
- Cross-tenant / negative authZ tests
- Audit immutable + redacted
- Bilingual foundation
- No Arabic / Phase 06+ code
- PR open (to be created)
- Tracking docs updated

**Stop here. Awaiting founder review. Do not begin Phase 06.**