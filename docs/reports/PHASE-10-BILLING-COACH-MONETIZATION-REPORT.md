# Phase 10 — Billing and Coach Monetization Report

**Candidate status:** Gate 0 passed; implementation and local validation complete; human financial/security review required; do not merge automatically  
**Date:** 2026-08-16 UTC  
**Arena-fixed branch:** `arena/01a00a2b-coachos-fitness-coaching-platf`  
**Requested logical branch:** `phase/10-billing-coach-monetization` (not created because the execution environment requires the Arena-fixed branch)  
**Verified baseline:** `f7ccaf457cbd2e67de2708d5367f6c1386a3edce`

## 1. Gate 0 remote preflight

| Check | Actual evidence | Result |
|---|---|---|
| Remote fetched | `git fetch origin --prune` | Pass |
| Remote `main` | `f7ccaf457cbd2e67de2708d5367f6c1386a3edce` | Pass; exact authorized baseline |
| PR #17 | `MERGED`, merge SHA `0949abeead5ba74a3deb0d2439a464ab6bbd99dd` | Pass |
| PR #18 | `MERGED`, merge SHA `f7ccaf457cbd2e67de2708d5367f6c1386a3edce` | Pass |
| Checkout isolation | Arena dedicated checkout and fixed session branch; clean initial worktree | Pass |
| Identity/tenancy/roles | `identity`, `organizations`, active memberships, owner invariant and tenant tests present | Pass |
| Phase 06/07 | Programs/snapshots and athlete execution/progress apps, migrations, APIs and tests present | Pass |
| OpenAPI | `docs/OPENAPI.yaml` declares OpenAPI 3.1 | Pass |
| CI/security | GitHub Actions and `infra/scripts/check-secrets.sh` present | Pass |
| Existing billing | Repository search found only deferred references; no billing models, routes, checkout, webhook or entitlement implementation | Pass; no duplicate implementation |

The prompt listed `docs/architecture/THREAT_MODEL.md`, `SECURITY_CONTROL_MATRIX.md`, and
`PRIVACY_DATA_LIFECYCLE.md`. In the actual baseline those three documents are at top-level `docs/`;
the required content was reviewed there. All other minimum documents were read at the listed paths.
The baseline owner invariant is authoritative `Organization.owner_user` plus exactly one matching active
owner membership.

## 2. Commercial policy fixed for this candidate

These are conservative implementation policies, not invented prices or legal advice:

1. **Payer:** one organization billing account. An independent coach is represented by the organization
they own. Athletes are never billing customers and there is no athlete checkout, marketplace, payout,
commission or transfer flow.
2. **Catalog:** no price, currency, trial length, grace length, seat cap or client cap is seeded or hard-coded.
Platform operators must create an approved `Plan` and `Price` catalog. Inactive or unmapped prices cannot
start checkout.
3. **Trials:** opt-in per approved Price (`trial_days`, default zero). No implicit trial.
4. **Limits:** staff seats are distinct active owner/coach users; clients are distinct active athlete users.
Caps are optional plan entitlements. Missing caps mean unlimited, not zero. Athletes already admitted retain
their data and access when billing changes; billing never deletes athlete data.
5. **Cancellation:** hosted-provider self-service is the management boundary. The candidate represents
`cancel_at_period_end`; entitlement remains through the verified current period end. A verified immediate
`canceled` state disables paid organization features. A browser return parameter cannot change state.
6. **Grace:** opt-in per Price (`grace_period_days`, default zero), bounded from the verified `past_due`
transition. Grace never applies to `unpaid`, `incomplete`, or `canceled`. It cannot extend itself without a
newer verified provider state.
7. **Entitlement:** server-side only. `trialing` and `active` allow paid entitlements; `past_due` allows them
only until the bounded grace deadline; `incomplete`, `unpaid`, and `canceled` fail closed for paid features.
Provider unavailability does not mutate the last verified state. Core athlete access is always included.
8. **Refunds, tax and invoices:** refunds/disputes are documented event boundaries only. Tax calculation,
VAT/GST advice, statutory invoice compliance, accounting treatment and retention periods require specialist
legal/accounting decisions and are not claimed complete.
9. **Provider:** deterministic fake provider only for this candidate. The domain adapter is provider-neutral.
No live calls or credentials are introduced. A production adapter remains gated.
10. **Authorization:** active owner and explicitly delegated active billing admin may manage billing. A
billing admin must also retain an active organization membership. Coaches and athletes have no billing-record
access by default. Platform operators require a separately reviewed support capability; no hidden support
bypass is added.

## 3. Benchmark lessons and CoachOS decisions

Official Stripe material was inspected on 2026-08-16:

- <https://docs.stripe.com/billing/subscriptions/webhooks>
- <https://docs.stripe.com/customer-management/integrate-customer-portal>
- <https://docs.stripe.com/checkout/quickstart>

Lessons adopted: hosted collection; server-created checkout and portal sessions; server-owned catalog;
asynchronous lifecycle driven by verified webhooks; customer portal for payment-method/subscription actions;
and a pending return state until webhook confirmation. CoachOS does not copy provider branding or copy.
Provider event semantics terminate at an adapter and normalized DTO. Trainerize/Practice Better patterns are
used only as product heuristics: organization-centered plans, clear included-client language, visible current
plan/usage and one primary next action.

## 4. Gate 0 financial risk register

| ID | Risk | Control / test requirement | Residual/deferred |
|---|---|---|---|
| F10-01 | Browser forges payment success | Redirect return is display-only; only verified webhook mutates subscription/entitlement | Production adapter review deferred |
| F10-02 | Duplicate/replayed webhook | HMAC/timestamp check in fake adapter, unique `(provider,event_id)`, transaction, idempotent response | Distributed replay telemetry deferred |
| F10-03 | Out-of-order event regresses state | Provider event creation watermark; stale state events ignored and reconciliation issue recorded | Provider fetch strategy adapter-specific |
| F10-04 | Cross-tenant customer reference | Unique provider reference maps to one org; org is never selected from client/provider metadata | Penetration test deferred |
| F10-05 | Raw payment data leakage | Hosted collection only; schema/test/scan forbid PAN/CVV/bank credential fields and raw webhook payload retention | PCI certification explicitly not claimed |
| F10-06 | Unbounded grace bypass | Grace starts from verified transition, has configured finite days, does not apply to terminal/incomplete states | Commercial duration awaits catalog approval |
| F10-07 | Billing failure blocks athlete | Evaluator always returns included athlete access; regression tests | Future founder policy would require new ADR |
| F10-08 | Limit race | Account row lock plus count inside transaction in capacity service; existing members/data are not deleted | PostgreSQL concurrency load test deferred |
| F10-09 | Open redirect / malicious provider URL | Return URLs generated from configured base; hosted URL scheme/host allowlist checked server-side | Production allowlist deployment gate |
| F10-10 | Session abuse/duplicate charge | required idempotency key, unique account/key, payload conflict check, bounded cache rate limit | Shared distributed throttling required in production |
| F10-11 | Secret/PII in logs | payload digest only; sanitized error code; correlation and external event IDs only | Central log redaction verification deferred |
| F10-12 | Owner/admin removed mid-flow | Webhook maps provider customer to org independently; new management action rechecks active permission | In-flight provider session cannot be revoked by fake adapter |
| F10-13 | Provider outage causes revocation | checkout/portal fail without state mutation; last verified subscription state remains authoritative | Reconciliation worker scheduling deferred |
| F10-14 | Legal/accounting overclaim | explicit disclaimers and metadata-only invoice model | Legal, tax, accounting and retention approval open |
| F10-15 | Event collision | provider-scoped global event uniqueness and customer/subscription consistency checks | Multi-account provider namespace policy required before launch |

## 5. Requirements traceability matrix

| Requirement | Model/service | Route/contract | Screen | Test evidence target |
|---|---|---|---|---|
| Org is payer; athlete included | `BillingAccount`, entitlement evaluator | workspace + entitlement response | included-athletes plan copy | athlete authorization and access regression |
| Catalog, no invented price | `Plan`, `Price`, `PlanEntitlement` | `GET /billing/plans` | plan comparison | no seed/hard-coded money scan |
| Hosted checkout | adapter + `CheckoutAttempt` | checkout session POST | select-plan action | idempotency, timeout, URL validation |
| Hosted portal | adapter/customer reference | portal session POST | manage billing action | authorization/provider failure |
| Lifecycle | `Subscription` state machine | verified webhook | current plan/status | full transition matrix |
| Invoices | `InvoiceSummary` | workspace bounded list | invoice history | tenant scope, bounded query |
| Entitlements/usage | evaluator + snapshot | workspace | seats/clients | grace, caps, race service |
| Webhook security | `WebhookEvent`, verifier | public provider webhook | operational status only | unsigned/malformed/replay/stale |
| Delegated admin | `BillingRoleAssignment` | billing-admin routes | owner workflow boundary | owner/admin/coach/athlete matrix |
| Audit/hooks | `BillingAuditEvent`, `BillingDomainEvent` | internal + workspace issue summary | owner status guidance | immutable audit + no notification engine |
| Reconciliation | `ReconciliationIssue` | bounded workspace summary/reconcile | provider degraded guidance | stale/unknown/failure scenarios |
| Bilingual accessible UX | n/a | typed API client | `/[locale]/org/billing` | i18n parity, keyboard/live status, responsive build |

## 6. Data classification and lifecycle

Billing records are **Tier 7 financial metadata**. Provider customer/subscription/invoice IDs are confidential
pseudonymous references, not authentication secrets. Billing email is optional Tier 1 PII and never an auth
credential. Money is integer minor units plus ISO currency. Raw payment credentials and raw webhook bodies
are prohibited from persistence and application logs. The request body exists in memory only for verification;
a SHA-256 digest is retained.

Exports may include organization-visible catalog, subscription, invoice summary and audit metadata but never
provider secrets or payment instruments. Organization/user erasure must not blindly delete financial/audit
records: an approved jurisdictional retention and pseudonymization policy is required first. This candidate
supports archive/status boundaries but makes no retention-period claim. Production backup deletion,
accounting retention and data-subject handling require legal review.

## 7. Failure policy and test strategy

- Unverified input: reject without mutation.
- Verified duplicate: acknowledge idempotently without reprocessing.
- Verified unknown/irrelevant type: retain minimal ignored record and acknowledge.
- Verified process failure: mark failed, create reconciliation visibility and return retryable 5xx.
- Provider timeout/malformed response: mark attempt failed with sanitized code; keep entitlement unchanged.
- Stale lifecycle event: ignore state mutation, record reconciliation visibility, acknowledge.
- Browser return: always pending/rechecking copy; fetch server workspace.

Candidate validation budgets are p95 below 250 ms for normalized webhook ingestion and below 200 ms for the
bounded billing workspace on the local SQLite test profile, with workspace query count at or below 12.
These are regression budgets, not production SLOs; PostgreSQL/provider load validation remains a deployment
gate. The implemented workspace uses 9 queries with invoice/issue caps independent of row count.

Tests use Django/DRF, frozen deterministic fake payloads and HMAC signatures. No network or live provider.
Backend targets constraints, migration, state transitions, permissions, replay/order, URL safety, secret/data
minimization, bounded query behavior and entitlement scenarios. Frontend targets all state surfaces, bilingual
parity, accessible names/live regions and external transition warning. Full repository gates are recorded at
finalization with exact outputs rather than predicted here.

## 8. Specialist Gate 0 review record

The coordinator explicitly simulated the requested principal review panel. Product/monetization fixed the
no-price catalog and athlete-included policy; domain/state-machine defined normalized states; provider and
webhook reviewers required raw-body verification and provider DTOs; backend/authz reviewers selected org
owner/delegation checks; privacy prohibited payload/card storage; UX/i18n/a11y required bilingual parity and
pending/error states; contract/QA reviewers required OpenAPI and event matrices; reliability/observability
required bounded lists, reconciliation and correlation IDs; threat/independent reviewers rejected client-side
success and unsupported compliance claims. **Gate 0 recommendation: PASS** under the explicit conservative
policies above. Final financial/security approval cannot be self-issued and remains founder/reviewer gated.

## 9. Shared tracker policy and proposed post-merge entries

This implementation PR will not modify `PROJECT_STATUS.md`, `PROJECT_CHECKLIST.md`, `CHANGELOG.md`, or
`docs/PROMPT_LOG.md`. Proposed post-merge docs-only PR entries:

- Phase 10 implementation merged via its founder-approved PR at the actual merge SHA.
- Organization-level provider-neutral billing foundation, fake provider, verified/idempotent webhooks,
  server entitlements and bilingual owner workspace delivered.
- Athletes remain free/included; no athlete billing/marketplace/payout/tax/accounting certification.
- Production provider, prices, legal/tax/accounting/retention review, penetration testing and formal
  accessibility certification remain deferred.

## 10. Implemented candidate

### 10.1 Domain and provider boundary

The candidate adds one organization-owned `BillingAccount`, application-owned `Plan`, `Price` and
`PlanEntitlement` catalog records, provider customer references, subscription and invoice projections,
checkout attempts, entitlement snapshots, delegated billing roles, immutable billing audits, durable future
notification hooks, webhook envelopes and reconciliation issues. No price rows or commercial values are
seeded. Money uses nonnegative integer minor units with an explicit ISO currency and exponent.

The provider protocol exposes only customer/session/subscription DTOs. The fake adapter is deterministic,
network-free and settings-gated, returns `.invalid` hosted URLs, and verifies exact raw-body HMAC signatures
plus a bounded timestamp. There is no production adapter or live credential. Retrieved reconciliation state
must carry a timezone-aware provider watermark and is normalized through the same locked projection/state
machine as a verified webhook.

Subscription projection covers `trialing`, `active`, `past_due`, `incomplete`, `unpaid` and `canceled`, with
finite entitled periods, a required trial end, a required cancellation timestamp, stale-event rejection,
full same-timestamp conflict detection and terminal cancellation. Invoice projection has independent ordering,
financial-field validation and a bounded state machine. Redirect/query state never mutates either projection.

The entitlement evaluator is server-authoritative, fails closed for malformed/expired states and inactive
accounts, keeps athlete access included, and serializes new staff/client admission against optional approved
caps. Existing memberships and athlete data are never deleted or suspended by billing.

### 10.2 API, operations and UX

Implemented endpoints cover catalog, organization workspace, checkout, portal, billing-admin delegation,
manual reconciliation and public signed webhooks under `/api/v1/billing`. Owner/delegated-admin authorization
is re-evaluated from active membership; ordinary coach, athlete-only, support and cross-tenant callers are
denied organization billing records. Error bodies include RFC 7807-compatible type/status/detail plus instance,
message key and correlation ID.

Django admin now provides protected, filtered visibility for accounts, subscriptions, invoices, checkout
attempts, webhook status/attempt/error metadata, reconciliation issues, audits and domain hooks. Provider-owned
and audit projections are read-only there. Provider retry remains deliberate redelivery of the original signed
event because raw payloads are intentionally not retained; manual reconciliation performs a fresh adapter
retrieval and records conflicts without changing verified state.

The bilingual billing workspace exists at `/[locale]/org/billing` with `fa-IR` RTL and `en-US` LTR parity.
It presents current lifecycle/period/trial/grace state, approved plans and prices, usage/caps, included-athlete
copy, bounded invoices, loading/empty/forbidden/degraded/action-error states and an explicit hosted-provider
transition warning. Native controls, semantic headings/regions, bidi isolation, live alert/status messaging,
localized modal labels, focus containment, 44 px targets, responsive grids and horizontally contained invoice
tables are used. Browser return state is explicitly described as pending verification.

### 10.3 Exact changed files

Configuration, routing and integration:

- `.env.example`
- `backend/apps/core/urls.py`
- `backend/apps/organizations/views.py`
- `backend/config/settings/base.py`
- `backend/config/settings/test.py`
- `backend/requirements-dev.txt`

Billing backend and migration:

- `backend/apps/billing/__init__.py`
- `backend/apps/billing/admin.py`
- `backend/apps/billing/apps.py`
- `backend/apps/billing/entitlements.py`
- `backend/apps/billing/migrations/0001_initial.py`
- `backend/apps/billing/migrations/__init__.py`
- `backend/apps/billing/models.py`
- `backend/apps/billing/providers/__init__.py`
- `backend/apps/billing/providers/base.py`
- `backend/apps/billing/providers/fake.py`
- `backend/apps/billing/serializers.py`
- `backend/apps/billing/services.py`
- `backend/apps/billing/urls.py`
- `backend/apps/billing/views.py`
- `backend/tests/billing/test_billing.py`
- `backend/tests/billing/test_billing_contract.py`

Frontend and dependency-security migration:

- `frontend/app/[locale]/(app)/org/billing/page.tsx`
- `frontend/app/[locale]/layout.tsx`
- `frontend/components/billing/BillingWorkspace.tsx`
- `frontend/components/layout/Header.tsx`
- `frontend/components/ui/Modal.tsx`
- `frontend/eslint.config.mjs`
- `frontend/lib/api/billing.ts`
- `frontend/lib/i18n/dictionaries/en-US.json`
- `frontend/lib/i18n/dictionaries/fa-IR.json`
- `frontend/next-env.d.ts`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/tests/billing-workspace.test.tsx`
- `frontend/tsconfig.json`
- `frontend/.eslintrc.json` (removed in the ESLint 9 flat-config migration)

Contracts and evidence:

- `docs/OPENAPI.yaml`
- `docs/reports/PHASE-10-BILLING-COACH-MONETIZATION-CONTRACTS.md`
- `docs/reports/PHASE-10-BILLING-COACH-MONETIZATION-REPORT.md`

The prohibited shared trackers remain untouched.

### 10.4 Tests added

`backend/tests/billing/test_billing.py` and `test_billing_contract.py` cover catalog non-seeding, included
athletes, owner/delegated/coach/athlete/support authorization, cross-tenant denial, suspended/archived context,
checkout/portal idempotency and hosted URL boundaries, fake-provider fail-closed behavior, raw signature and
timestamp checks, malformed/prohibited payloads, duplicate replay, event identity collision, stale and
same-time conflicts, lifecycle terminality, invoice ordering/transitions, grace non-extension, finite trials,
inactive accounts, database constraints, immutable audit/hooks, capacity admission, bounded query count,
reconciliation application/reference conflicts and redacted observability logs.

`frontend/tests/billing-workspace.test.tsx` adds nine tests covering verified lifecycle/usage/invoice rendering,
pending browser return, hosted-transition confirmation, denied/degraded recovery, Persian RTL parity, exact
minor-unit formatting, approved trial/grace disclosure, exact dictionary-key parity and axe scans of both
locales. No live provider or network call runs in either suite.

### 10.5 Validation evidence

Final clean commands and exact outcomes on 2026-08-16 UTC:

| Command | Outcome |
|---|---|
| `backend/.venv/bin/ruff check .` | Pass; all checks passed |
| `backend/.venv/bin/ruff format --check .` | Pass; 89 files already formatted |
| `backend/.venv/bin/pytest --cov=apps --cov=config` | Pass; 144/144 tests, 85% total coverage |
| `backend/.venv/bin/pytest tests/billing -q` | Pass; 30/30 focused billing tests |
| `backend/.venv/bin/python backend/manage.py check` | Pass; 0 issues |
| `backend/.venv/bin/python backend/manage.py makemigrations --check --dry-run` | Pass; no changes detected |
| clean SQLite `manage.py migrate --noinput` | Pass; `billing.0001_initial` applied with all repository migrations |
| `backend/.venv/bin/python -m openapi_spec_validator docs/OPENAPI.yaml` | Pass; OpenAPI 3.1 document valid |
| `npm ci` | Pass; 523 packages installed/audited, 0 vulnerabilities |
| `npm run lint` | Pass; ESLint 9, zero warnings/errors |
| `npm run type-check` | Pass, including from a removed `.next` cache |
| `npm test` | Pass; 15 files, 84/84 tests |
| `npm run build` | Pass; Next.js 16.3.1 production build, both billing locale routes generated |
| `npm audit --audit-level=high` | Pass; 0 vulnerabilities |
| `npm audit --omit=dev --audit-level=high` | Pass; 0 production vulnerabilities |
| `bash infra/scripts/check-secrets.sh` | Pass; all four compliance checks |
| Arabic resource/route scan | Pass; 0 resource/path names and 0 locale/route references |
| changed billing-code personal-data pattern scan | Pass; 0 public-email and 0 phone candidates |
| `git diff --check` | Pass |

The initial baseline lockfile audit exposed critical/high findings in obsolete Next.js/Vitest/Vite/PostCSS
transitives. They were not waived: Next.js was upgraded to 16.3.1, Vitest to 3.2.7, Vite to 7.3.6,
PostCSS to 8.5.26, ESLint/config to 9/16, and the required route-param/flat-config migration was completed.
The final full and production-only audits both report zero vulnerabilities.

Docker smoke was attempted with `docker version` and `docker compose config --quiet`, but this execution image
has no `docker` executable (`command not found`). It is therefore recorded as **not available**, not passed;
CI or a reviewer with Docker must run the compose smoke before deployment.

### 10.6 Performance evidence

The repeatable local benchmark migrated an in-memory SQLite database, warmed each route, then measured 40
unique full subscription webhook updates and 50 authenticated workspace reads. Setup was excluded:

- webhook: median **8.53 ms**, p95 **9.28 ms**, max **9.38 ms** (budget p95 < 250 ms);
- workspace: median **5.45 ms**, p95 **6.17 ms**, max **7.20 ms** (budget p95 < 200 ms);
- bounded workspace query regression: **9 queries** (budget <= 12), including a maximum of 20 invoices and
  10 open issues.

These figures are local regression evidence only, not production claims. PostgreSQL concurrency, remote
provider latency and representative production load remain required before launch.

### 10.7 Migration and rollback strategy

`billing.0001_initial` creates only new billing tables, indexes and constraints; it does not rewrite existing
organization, identity, program or execution rows and seeds no plan/price. The organization invitation path
calls an additive capacity service that returns immediately when no billing account/approved cap exists.
Fresh migration and drift checks pass.

Before any live financial metadata, rollback may reverse the initial migration after disabling billing routes.
After live metadata exists, destructive reversal is prohibited: disable provider/session creation, retain the
financial/audit tables under approved retention policy, restore application code compatibly, and reconcile
before any later schema rollback. Provider outage or rollback must never delete athlete/member data. Database
backup/restore and PostgreSQL rollback rehearsal remain deployment gates.

### 10.8 Specialist and independent review findings

| Review role | Candidate finding | Recommendation |
|---|---|---|
| Staff product/monetization | Organization payer and athlete-included policy are explicit; no invented price or marketplace surface | Pass for human product/financial review |
| Principal billing/domain architect | Provider-neutral DTOs, finite lifecycle invariants, deterministic grace/cancellation and server entitlements align | Pass candidate architecture |
| Payments integration/webhook | Raw-body verification, replay/order/conflict controls, typed retries and normalized reconciliation are present | Pass fake-provider candidate; block production provider |
| Principal backend/data | Constraints, transaction boundaries, immutable audit, bounded reads and migration drift are clean | Pass candidate implementation |
| Security/authz/threat | Cross-tenant/default-role denial, return-state distrust, URL allowlists, redacted logs and zero dependency findings verified | Pass candidate security gate; human security approval required |
| Privacy/compliance | No raw payment credential or raw webhook retention; invoice data remains metadata; compliance overclaims excluded | Pass candidate minimization; legal/retention review required |
| Frontend UX/i18n/a11y | Persian/English parity, semantic/focus/error states, responsive source review and two-locale axe checks pass | Pass candidate UX; formal assistive-tech certification deferred |
| QA/performance/reliability | 144 backend, 84 frontend and 30 focused billing tests pass; latency/query budgets pass; reconciliation/admin visibility present | Pass local quality gate; PostgreSQL/Docker/load gates remain |
| Independent final gate | No unresolved critical/high candidate defect found in the reviewed diff | Recommend opening PR; do not merge without named human approvals |

No automated agent can grant final financial correctness, legal, tax, accounting, PCI, production-provider or
security approval. Those approvals remain explicit PR/deployment gates.

### 10.9 Residual risks and production blockers

- There is no production provider adapter, live credential, approved commercial catalog or live-money test.
- Provider-specific retry schedules, webhook endpoint registration, dead-letter tooling and scheduled batch
  reconciliation require the production adapter; raw events cannot be replayed from CoachOS by design.
- Shared/distributed rate limiting, central metrics/alerts and PostgreSQL race/load testing remain required.
- Docker Compose smoke could not run in this environment.
- Formal screen-reader/keyboard/browser matrix and external penetration testing remain required.
- Refund/dispute handling is only a boundary; tax, statutory invoices, accounting, retention, consumer-law and
  data-subject procedures require qualified review.
- No reconciliation issue-resolution workflow or dedicated support dashboard is claimed; protected Django
  admin visibility and owner/manual reconciliation are the candidate minimum.

## 11. PR and approval evidence

**Candidate implementation commit:** `2b2d47d5d72c563128ce84ab26fa416c5f3c3ac7`

**Implementation PR:** [#20 — Phase 10: organization billing and coach monetization foundation](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/20) targeting `main` from the Arena-fixed branch

**CI on the candidate implementation commit:** all reported checks passed:

- [Backend Lint, Type & Tests (Django/DRF)](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31944431499/job/95158199240) — pass, 31 s;
- [Frontend Lint, Type & Tests (Next.js/PWA)](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31944431499/job/95158199287) — pass, 54 s;
- [Security Scan & Language Compliance](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31944431499/job/95158199333) — pass, 7 s;
- [Secret & Pattern Scanning](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31944431890/job/95158200040) — pass, 5 s.

**Merge status:** PR is open, non-draft and intentionally unmerged. Founder/product-financial, security,
backend/data, frontend UX/i18n/a11y and QA approval remain required.
