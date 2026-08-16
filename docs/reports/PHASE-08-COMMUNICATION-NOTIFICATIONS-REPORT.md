# Phase 08 — Communication and Notifications: Implementation Report

**Phase:** 08 — Communication and Notifications (candidate implementation, parallel Phases 08–12 wave)
**Status:** Candidate — PR open for founder review. **Not merged. Do not merge automatically.**
**Report date:** 2026-08-16 (UTC)
**Companion contract:** `docs/reports/PHASE-08-COMMUNICATION-NOTIFICATIONS-CONTRACTS.md`

---

## 1. Gate 0 — Remote preflight evidence

### 1.1 Baseline verification

| Check | Expected | Actual | Result |
|---|---|---|---|
| Remote `main` SHA | `f7ccaf457cbd2e67de2708d5367f6c1386a3edce` | `f7ccaf457cbd2e67de2708d5367f6c1386a3edce` | ✅ **matches recorded baseline** |
| PR #17 (Phase 07 implementation) | merged | `MERGED` at `0949abeead5ba74a3deb0d2439a464ab6bbd99dd`, 2026-08-16T09:57:48Z | ✅ |
| PR #18 (post-merge Phase 07 sync) | merged | `MERGED` at `f7ccaf457cbd2e67de2708d5367f6c1386a3edce`, 2026-08-16T10:08:05Z | ✅ |
| `main` head is PR #18 merge commit | yes | `f7ccaf4 Merge pull request #18 from AliNaderiii/arena/01a00a05-...` | ✅ |

Commands run:

```
git fetch --all --prune
git rev-parse origin/main            # f7ccaf457cbd2e67de2708d5367f6c1386a3edce
gh pr view 17 --json state,mergedAt,mergeCommit
gh pr view 18 --json state,mergedAt,mergeCommit
```

### 1.2 Required repository inventory on actual `main`

| Required path | Present | Note |
|---|---|---|
| `.github/workflows/ci.yml` | ✅ (98 lines) | 3 jobs: backend, frontend, security/governance |
| `.github/workflows/security-scan.yml` | ✅ (25 lines) | Secret & pattern scanning |
| `docs/OPENAPI.yaml` | ✅ (2805 lines) | Contains `planned-phase-08` message/notification stubs |
| `docs/architecture/AUTHORIZATION_ARCHITECTURE.md` | ✅ (235 lines) | |
| `docs/architecture/THREAT_MODEL.md` | ⚠️ **not at that path** | Present at **`docs/THREAT_MODEL.md`** |
| `docs/architecture/SECURITY_CONTROL_MATRIX.md` | ⚠️ **not at that path** | Present at **`docs/SECURITY_CONTROL_MATRIX.md`** |
| `docs/ux/RTL_LTR_SPECIFICATION.md` | ✅ (90 lines) | |
| `docs/ux/ACCESSIBILITY_SPEC.md` | ✅ (68 lines) | |

**Finding P08-GATE0-01 (informational, not a blocker).** Two required documents exist with the required *names and content* but live directly under `docs/` rather than `docs/architecture/`. This is a pre-existing repository layout fact inherited from Phase 03, not a Phase 08 change. Both documents were read as part of preflight. Phase 08 does **not** relocate them, because moving tracked architecture documents during a parallel five-phase wave would create avoidable cross-branch conflicts. Recommendation for the founder: normalize the paths in a separate docs-only PR after the 08–12 wave lands.

### 1.3 Baseline check runs (head SHA `f7ccaf457cbd2e67de2708d5367f6c1386a3edce`)

| Check run name | Status | Conclusion |
|---|---|---|
| `Backend Lint, Type & Tests (Django/DRF)` | completed | success |
| `Frontend Lint, Type & Tests (Next.js/PWA)` | completed | success |
| `Security Scan & Language Compliance` | completed | success |
| `Secret & Pattern Scanning` | completed | success |
| `build` | completed | success |
| `deploy` | completed | success |
| `report-build-status` | completed | success |

Run IDs: `31940874618` (pages build/deploy), `31940875218` (CI Quality Gates), `31940875264` (Security & Vulnerability Scan). All seven check runs on the baseline SHA are `completed / success`.

### 1.4 Tracking-document state at Gate 0

`PROJECT_STATUS.md` states: *"Phase 07 — merged and complete for its documented scope (PR #17)"* and *"Phase 08 (messaging/notifications) is the next product phase but is **not started**"*. `PROJECT_CHECKLIST.md` and `CHANGELOG.md` agree. ✅ Scope boundary confirmed: Phase 08 was not started before this branch.

### 1.5 Prior-phase material read before design

- `apps/identity/` (User, UUIDv7 PK, `preferred_locale`, `timezone`, `IsAuthenticatedAndActive`)
- `apps/organizations/` (Organization, Membership roles/status, active-owner invariant)
- `apps/programs/` (`CoachAthleteAssignment`, `ProgramAssignment` immutable snapshot)
- `apps/execution/` (Phase 07 `WorkoutSession`, `FeedbackFlag`, consent gating, `_sensitive_scope` authorization idiom)
- `apps/audit/` (immutable `AuditEvent`, action enumeration)
- `apps/core/` (RFC 7807 handler, correlation ID, security headers, redaction, tenant context)
- `docs/PRD.md` §Epic E6 (US-MSG-001, US-NTF-001), `docs/DATA_MODEL.md` §3.5, `docs/API_CONTRACT.md` §7, `docs/OPENAPI.yaml` planned stubs
- Phase 05/06/07 reports in `docs/reports/`

### 1.6 Branch discipline deviation (recorded, founder-visible)

The prompt requests a branch named `phase/08-communication-notifications`. **This Arena session is hard-bound to the branch `arena/01a00a2a-coachos-fitness-coaching-platf`**, which was created from the verified baseline `f7ccaf457cbd2e67de2708d5367f6c1386a3edce`. Work on any other branch would not be tracked by the session. All Phase 08 work therefore lives on `arena/01a00a2a-coachos-fitness-coaching-platf`, branched from the correct approved baseline, in an isolated checkout. No other agent writes to this checkout. `main` is never pushed to; no force push; no destructive reset.

### 1.7 Risk register

| ID | Risk | Likelihood | Impact | Mitigation | Evidence |
|---|---|---|---|---|---|
| R-01 | Message privacy leak to non-participants | Med | Critical | Participant-only server authorization on every route; `404` for non-participants; owner backdoor explicitly removed (AMD-08-01) | `test_authorization.py` |
| R-02 | Message bodies leaking into logs/audit/events/analytics | Med | Critical | Bodies excluded from event payloads, audit metadata, notification payloads and error strings; automated log-scan test | `test_privacy_logging.py` |
| R-03 | Data retention ambiguity for user content | Med | High | Tier-3 classification, cascade rules and purge-eligibility documented; purge job explicitly deferred | Contract §5 |
| R-04 | Notification spam / abuse | Med | High | Preferences, per-conversation mute, forced-category allowlist, dedupe on stable event identity, capped unread counts | `test_preferences.py`, `test_outbox.py` |
| R-05 | Duplicate delivery from outbox retries | High | Med | `event_id` unique + `(recipient, dedupe_key)` unique + idempotent dispatcher | `test_outbox.py` |
| R-06 | Browser push permission denied / misleading claim | High | Med | Web Push is a local fake; permission state persisted; `denied` ⇒ `suppressed` attempt; no real-time claim in UI or docs | `test_delivery.py` |
| R-07 | Cross-tenant leakage via ids | Med | Critical | Every query filtered by org + participant; cross-tenant ids resolve to `404` without existence signal | `test_authorization.py` |
| R-08 | Rate-limit bypass across endpoints/identifiers | Med | High | Server-derived user/org keys only; separate per-user, per-conversation, per-org windows; fail-closed | `test_rate_limits.py` |
| R-09 | Localization gaps / Arabic slippage | Med | Med | fa-IR ⇄ en-US key-parity test; Arabic scanners; BiDi isolation for names and bodies | `i18n.test.ts`, `no-arabic.test.ts` |
| R-10 | Stored XSS / unsafe links in message bodies | Med | Critical | Plain-text storage and rendering, no `dangerouslySetInnerHTML`, auto-linking disabled, control-char normalization | `test_message_content.py`, `conversations.test.tsx` |
| R-11 | Unbounded queries on large inboxes | Med | Med | Keyset pagination, bounded page sizes, denormalized `last_message_at`, targeted indexes, query-count assertions | `test_performance.py` |
| R-12 | Scope creep into Phases 09–12 | Med | High | Automated scope scanner test asserting absence of forbidden domains | `test_phase08_scope.py`, `offline-scope.test.ts` |

### 1.8 Acceptance-criteria matrix

| # | Definition-of-Done item | Where evidenced |
|---|---|---|
| 1 | Authorized direct communication end-to-end | §4, §5 |
| 2 | Tenant-safe, privacy-classified data | Contract §1, §5; §6 |
| 3 | Validated, bounded, idempotent, CSRF-protected sends | §4.2, §5 |
| 4 | Consistent read/unread | §4.2, §5 |
| 5 | Durable in-app notifications | §4.3 |
| 6 | Transactional event→notification | §4.3, §5 |
| 7 | Retries, dedupe, failures, neutral adapters | §4.3, §5 |
| 8 | Preferences + quiet hours explicit | Contract §1.5; §5 |
| 9 | No real credentials / production data | §6, §7 |
| 10 | fa-IR RTL / en-US LTR parity | §4.4, §5 |
| 11 | Keyboard/SR/focus/touch/mobile review | §4.4, §8 |
| 12 | Cross-tenant/unassigned/suspended/revoked tests | §5, §6 |
| 13 | XSS/abuse/rate-limit/replay/log-redaction tests | §5, §6 |
| 14 | Measured performance + limitations | §7 |
| 15 | OpenAPI/migration/CI/security/language/secret checks | §5 |
| 16 | Both Phase 08 reports present | this file + contract |
| 17 | PR open for founder review | §10 |
| 18 | Post-merge sync planned only | §9 |
| 19 | No forbidden domain slippage | §6 |

**Gate 0 verdict: PASS** (with informational finding P08-GATE0-01 and the recorded branch-name deviation §1.6).

---

## 2. Branch, scope, and change inventory

**Branch:** `arena/01a00a2a-coachos-fitness-coaching-platf` (from baseline `f7ccaf4`) — see §1.6 for the recorded naming deviation.
**Commits:** `a16ecbd` (backend), `f73fff6` (frontend + contract), plus this report commit.
**Diff vs baseline:** 48 files changed, ~9,100 insertions.

Shared tracking files (`PROJECT_STATUS.md`, `PROJECT_CHECKLIST.md`, `CHANGELOG.md`, `docs/PROMPT_LOG.md`) are **deliberately untouched** to avoid conflicts across the parallel 08–12 wave. Proposed entries are in §9.

### Changed files

**New backend module `apps/communication/`** — `models.py`, `authz.py`, `events.py`, `mapping.py`, `dispatcher.py`, `adapters.py`, `ratelimit.py`, `serializers.py`, `views.py`, `urls.py`, `constants.py`, `hooks.py`, `apps.py`, `migrations/0001_initial.py`.

**New backend tests** — `tests/communication/`: `helpers.py`, `conftest.py`, `test_conversations.py`, `test_authorization.py`, `test_outbox.py`, `test_delivery_and_preferences.py`, `test_security.py`, `test_performance_and_scope.py`.

**Modified backend (additive only, 31 lines total)** — `apps/audit/models.py` (+5 audit actions), `apps/audit/migrations/0004_*` (new), `apps/core/urls.py` (route include), `apps/execution/views.py` (two event hooks), `config/settings/base.py` (app registration + provider flag), `config/settings/test.py` (fake providers on in tests).

**New frontend** — `lib/api/messaging.ts`, `lib/messaging/format.ts`, `components/messaging/{ConversationList,ConversationView,NotificationCenter,NotificationPreferences}.tsx`, four route pages, `tests/messaging.test.tsx`, `tests/messaging-scope.test.ts`.

**Modified frontend** — `components/layout/BottomNav.tsx` (notifications entry replacing a dead `/calendar` link), both dictionaries (+110 keys each).

**Contract** — `docs/OPENAPI.yaml`: Phase 08 stubs replaced with the implemented contract; legacy `MessageThread`/`ThreadListResponse` stubs removed.

---

## 3. Specialist review passes

| Role | Verdict | Key finding / action |
|---|---|---|
| **Conversation & Messaging Domain Architect** | ✅ | Direct-only `kind`, participant-pair uniqueness including context discriminator, append-only messages, monotonic read cursor. Group messaging deliberately excluded (not P0). |
| **Django/DRF Backend Engineer** | ✅ | Additive app following Phase 05–07 conventions (UUIDv7 `CharField(36)` PKs, `IsAuthenticatedAndActive`, RFC 7807). No Phase 07 semantics rewritten — hooks are two additive calls inside existing transactions. |
| **Outbox & Eventing Engineer** | ✅ | Outbox row written in the source transaction (proved by rollback test). Versioned envelope; `event_id` unique; stale-claim recovery; unsupported version dead-letters immediately rather than looping. |
| **Notification Delivery & Preference Engineer** | ✅ | Three channels, defaults honest (email/push off, no provider). Quiet hours defer push-like channels only. Forced safety category enforced in both the API and the dispatcher (defence in depth). |
| **Authorization & Tenant-Isolation Specialist** | ✅ | 48 authorization tests. **Raised AMD-08-01**: removed the OpenAPI-stubbed "owner escalation into private threads" path — an always-available audited backdoor is still a backdoor. Owner oversight remains via audit events. |
| **Privacy & Data-Minimization Specialist** | ✅ | Message bodies classified Tier-3. `FORBIDDEN_PAYLOAD_KEYS` blocks body/email/token keys at emit time. Counterpart payloads carry display names only. Model `__str__` excludes bodies. |
| **Abuse / Rate-Limit Engineer** | ✅ | Five fixed-window scopes keyed on server-derived identity; verified unbypassable with spoofed `X-Forwarded-For` / `X-Organization-ID` / `X-Request-ID`; fails closed on cache error. |
| **Frontend Conversation UX Engineer** | ✅ | Full state matrix. **Chose non-optimistic send**: a failed send keeps the draft and never shows unsent content as delivered, so there is no rollback of apparently-delivered text. |
| **Mobile PWA / Offline-Boundary Engineer** | ✅ | No IndexedDB, localStorage, background sync, or push subscription. Offline banner states plainly that nothing is queued. Enforced by scanner tests on both Phase 07 and Phase 08 directories. |
| **fa-IR / en-US Localization Engineer** | ✅ | 312 keys, 100% parity. `<bdi>` isolation on every user-controlled string; BiDi override characters stripped server-side; icons mirrored with `rtl:rotate-180`. No Arabic. |
| **Accessibility Specialist** | ✅ | Semantic landmarks/lists, labelled composer, polite (never assertive) live regions, keyboard send/retry, 44px targets, visible focus rings, unread conveyed by text + weight not colour alone. No certification claimed. |
| **OpenAPI / Client Contract Engineer** | ✅ | 9 paths reconciled **exactly** to Django routes (automated diff, zero drift); 220 local refs resolve; examples synthetic. |
| **QA / Test Automation Lead** | ✅ | 172 new backend + 60 new frontend tests; 286 and 135 totals; all green. |
| **Performance & Reliability Engineer** | ⚠️→✅ | **Found and fixed an N+1**: inbox counterpart/unread lookups ran per row (46 queries at limit=20, 106 at limit=50). Batched into grouped queries — now a constant 8. Regression test asserts constancy. |
| **Observability Engineer** | ✅ | Structured identifier-only logs at enqueue/process/dead-letter; correlation IDs propagate into the envelope; error **codes** persisted, never provider or exception text. |
| **Adversarial Security Reviewer** (independent pass) | ✅ | See §6. No unresolved critical/high findings. |
| **Documentation & Traceability Owner** | ✅ | Contract report + this report; traceability table maps PRD stories → contract → code → tests. |
| **Independent Final Reviewer** | ✅ **recommend founder review** | Scope respected; no unsupported claims; two accepted limitations documented in §7. |

---

## 4. Implementation summary

### 4.1 Domain and authorization

Eight models (§1 of the contract report), all UUIDv7-keyed and organization-scoped. Authorization is centralized in `authz.py` and enforced on every route:

- `resolve_conversation_for_read` returns a bare `404` for unknown ids, cross-tenant ids, non-participants, removed participants, and suspended memberships — one uniform denial with no existence signal.
- `can_send_message` is a **separate** decision from read: a coach whose assignment is revoked keeps the history they legitimately participated in but loses send (`errors.authz.unassigned_athlete`).
- History is bounded by `joined_at`, so adding a participant never grants retroactive access.
- **AMD-08-01**: organization owners have no private-message read path.

### 4.2 Messaging APIs

Message bodies are NFC-normalized, stripped of control characters and BiDi overrides, CR-normalized, newline-collapsed, and length-checked **after** normalization (so control-character padding cannot smuggle content past the 2000-character bound). `client_message_id` provides idempotency via a partial unique constraint; a replay returns the original message with `200`. Keyset pagination on `(created_at, id)` gives stable ordering; malformed cursors are ignored rather than erroring. Unread counts are capped at 99.

### 4.3 Outbox and delivery

`emit_event` inserts the outbox row inside the caller's transaction (proved by a rollback test) and rejects payloads containing forbidden keys. The dispatcher claims with `SELECT ... FOR UPDATE SKIP LOCKED` where available and a conditional UPDATE on SQLite, recovers stale claims, maps via a `(event_type, schema_version)` registry, and creates notifications idempotently on `(recipient_user, dedupe_key)`. Retries use 30s→1h bounded backoff with dead-lettering after 5 attempts. **Mappers re-verify recipient entitlement at delivery time**, so an event queued before a revocation does not notify after it.

### 4.4 Frontend

Four routes under both locales. Message bodies render as plain React text nodes — no `dangerouslySetInnerHTML`, no `innerHTML`, no auto-linking (URLs display as inert text). Send is non-optimistic with idempotent retry. Notification copy is produced client-side from i18n keys plus metadata, so the server never returns locale-rendered prose.

---

## 5. Validation evidence

All commands run from a clean checkout of the final branch.

| Command | Result |
|---|---|
| `ruff check .` | **All checks passed!** |
| `ruff format --check .` | **97 files already formatted** |
| `pytest --cov=apps --cov=config` | **286 passed** — 86% total coverage; `apps/communication` 84–100% per module (views 92%, dispatcher 92%, models 90%) |
| `python manage.py check` | **System check identified no issues (0 silenced)** |
| `python manage.py makemigrations --check --dry-run` | **No changes detected** (no drift) |
| `python manage.py migrate` | All migrations apply cleanly, including `communication.0001_initial` |
| `npm ci` | clean install |
| `npm run lint` | **✔ No ESLint warnings or errors** |
| `npm run type-check` | **clean** (TypeScript strict) |
| `npm test` | **135 passed (16 files)** |
| `npm run build` | **Success** — Phase 08 routes prerendered for `fa-IR` and `en-US` |
| `bash infra/scripts/check-secrets.sh` | **🎉 ALL COMPLIANCE CHECKS PASSED** (Arabic exclusion, secret patterns, env safety, manifest) |
| OpenAPI 3.1 validation | parses as `3.1.0`; **220 local refs, 0 unresolved** |
| Route ↔ contract reconciliation | **9/9 Phase 08 routes match exactly**; zero drift in either direction |

### Live smoke test

Backend on `0.0.0.0:8000`, frontend dev server on `0.0.0.0:3000`:

```
GET  /api/v1/conversations            -> 403   (fail-closed, unauthenticated)
GET  /api/v1/notifications            -> 403
GET  /api/v1/notification-preferences -> 403
POST /api/v1/conversations            -> 403
GET  /healthz                         -> 200
```

The 403 body is a clean RFC 7807 envelope with `message_key` and `correlation_id` and no stack trace or internal detail. Frontend routes `/fa-IR/messages`, `/en-US/messages`, `/fa-IR/notifications`, `/en-US/settings/notifications` all return `200` with correct `<html lang="fa-IR" dir="rtl">` / `<html lang="en-US" dir="ltr">`.

### Test distribution (172 new backend tests)

| Suite | Tests | Focus |
|---|---|---|
| `test_conversations.py` | 25 | creation idempotency, pagination boundaries, validation bounds, read-state semantics |
| `test_authorization.py` | 48 | cross-tenant, non-participant, support, owner, suspension, revocation, notification scoping |
| `test_outbox.py` | 21 | transactionality, envelope, dedupe, claiming, retry/dead-letter, Phase 07 hooks |
| `test_delivery_and_preferences.py` | 29 | adapters, permission states, failure isolation, quiet hours, preference API |
| `test_security.py` | 34 | XSS/normalization, CSRF, rate limits, privacy logging |
| `test_performance_and_scope.py` | 15 | query counts, index presence, scope-boundary scanners |

---

## 6. Adversarial security, privacy, and abuse review

Independent pass; every case has an executable test.

| # | Attack / risk | Result | Evidence |
|---|---|---|---|
| 1 | Cross-tenant conversation enumeration | **Blocked.** A real foreign id and a fabricated id produce byte-identical 404 bodies. | `test_cross_tenant_enumeration_is_indistinguishable` |
| 2 | Same-tenant non-participant access | **Blocked** on all 5 conversation endpoints. | parametrized `test_unassigned_coach_same_org_gets_404` |
| 3 | Owner private-message backdoor | **Removed** (AMD-08-01). | `test_owner_has_no_private_message_backdoor` |
| 4 | Support role access | **Blocked** for read, write, and creation. | `test_support_role_gets_404` |
| 5 | Participant removal → historic access | **Revoked immediately**; thread also disappears from the inbox. | `test_removed_participant_loses_access_immediately` |
| 6 | Retroactive access by adding a participant | **Blocked** — history bounded by `joined_at`. | `test_history_bounded_by_join_time` |
| 7 | Coach reassignment | Send revoked, legitimate history retained, never widened. | `test_reassignment_revokes_send_but_preserves_legitimate_history` |
| 8 | Suspended / archived / deactivated account | **All denied.** | 3 tests |
| 9 | Stored XSS (6 payload shapes) | **Inert.** Stored as text, returned as JSON, rendered as React text nodes; no `<script>`/`<img>` element created. | `XSS_PAYLOADS` parametrized + `renders message bodies as inert text` |
| 10 | Unsafe link handling | **No auto-linking**; URLs render as inert text with no anchor. | `does not auto-link URLs` |
| 11 | Control-character / CR header-injection shapes | **Stripped** before storage. | `test_control_characters_are_stripped`, `test_carriage_returns_are_normalized` |
| 12 | BiDi override display spoofing | RLO/LRO/PDF removed; legitimate isolates preserved. | `test_bidi_override_characters_are_removed` |
| 13 | Length bypass via control-character padding | **Blocked** — length validated after normalization. | `test_length_is_validated_after_normalization` |
| 14 | CSRF on all five mutation families | **403** without a token. | parametrized `test_mutations_require_csrf` |
| 15 | Duplicate send / idempotency collision | Replay returns the original; exactly one message and one event. | `test_message_send_is_idempotent_by_client_message_id` |
| 16 | Rate-limit bypass via rotating headers | **Blocked** — counters key on server-derived identity. | `test_rate_limit_cannot_be_bypassed_with_spoofed_headers` |
| 17 | Rate-limit bypass via cache failure | **Fails closed** (429), not open. | `test_rate_limit_fails_closed_when_the_cache_errors` |
| 18 | Forged/poisoned internal events | **Structurally impossible** — no ingest endpoint; outbox rows are server-only. Unknown types and unknown schema versions are rejected/dead-lettered. | `test_unknown_event_type_is_rejected`, `test_unsupported_schema_version_dead_letters_immediately` |
| 19 | Outbox retry duplication | **No duplicate visible notification** across reprocessing. | `test_reprocessing_the_same_event_creates_no_duplicate` |
| 20 | Concurrent claim race | Second claimer gets nothing; stale claims recovered. | `test_claim_is_exclusive`, `test_stale_claim_is_recovered` |
| 21 | Provider failure deleting a notification | **Never** — in-app row survives; event still `processed`. | `test_provider_failure_never_deletes_the_in_app_notification` |
| 22 | Adapter exception escaping | Contained; recorded as `adapter_exception`. | `test_adapter_exception_is_contained` |
| 23 | Preference bypass of safety alerts | **Blocked** at the API (422) *and* in the dispatcher even if a DB row says otherwise. | `test_cannot_disable_safety_in_app_notifications`, `test_safety_notification_delivers_even_if_a_preference_row_says_otherwise` |
| 24 | Quiet-hours mistakes (midnight wrap, timezone, bad tz) | Correct in all three; invalid tz falls back to UTC, not server-local. | 4 quiet-hours tests |
| 25 | Notification enumeration oracle | Another user's id returns a 404 identical to a fabricated id. | `test_notifications_are_self_scoped` |
| 26 | Message body in logs / audit / events / notifications / errors / repr | **Absent from all six surfaces.** | 6 privacy tests using a unique marker string |
| 27 | Email addresses in API responses | **Absent** from all four response families. | `test_email_addresses_are_never_returned_by_the_api` |
| 28 | Provider secret / endpoint exposure | Only SHA-256 hashes stored; no URL or address. | `test_no_provider_secret_is_present_in_delivery_records` |
| 29 | Unbounded responses | Page sizes hard-capped at 50; unread capped at 99. | 3 bounding tests |
| 30 | Out-of-scope domain slippage | 7 domain scanners + credential scanner + Arabic scanner, backend and frontend. | `test_performance_and_scope.py`, `messaging-scope.test.ts` |

**Findings raised and resolved during review**

| ID | Severity | Finding | Resolution |
|---|---|---|---|
| P08-SEC-01 | **High** | OpenAPI stub granted owners audited read access to private threads. | Removed. Contract amendment AMD-08-01; test asserts 404 for non-participant owners. |
| P08-PERF-01 | **Medium** | Inbox counterpart/unread lookups were per-row (46 queries at `limit=20`, 106 at `limit=50`). | Batched into grouped queries — constant 8. Regression test asserts constancy across page size and dataset size. |
| P08-SEC-02 | **Medium** | Rate limiter returned "allow" if the cache backend raised. | Changed to fail closed; test added. |
| P08-SEC-03 | **Low** | Length validated before normalization would allow padded oversize bodies. | Validation moved after normalization; test added. |
| P08-GATE0-01 | Informational | Two required docs live at `docs/` not `docs/architecture/`. | Pre-existing; not relocated during the parallel wave. Recommend a separate docs-only PR. |

**No unresolved critical or high findings.**

---

## 7. Measured performance and honest limitations

### Environment

Sandbox container, Python 3.11.2, Django 5.2.17, **SQLite in-memory**, `DEBUG=True` for query capture, single process, no network. Synthetic dataset: 200 conversations × 50 messages = **10,000 messages**, 20 runs per endpoint after a warm-up.

| Endpoint | p50 | p95 | Queries |
|---|---|---|---|
| `GET /conversations?limit=20` | 13.67 ms | 15.12 ms | **8** |
| `GET /conversations?limit=50` | 23.30 ms | 24.85 ms | **8** |
| `GET /conversations/{id}/messages?limit=30` | 6.18 ms | 7.46 ms | **6** |
| `GET /conversations/{id}/messages?limit=50` | 6.77 ms | 7.97 ms | **6** |
| `GET /notifications?limit=20` | 2.43 ms | 2.70 ms | **4** |

Query counts are **constant** with respect to both page size and dataset size — the property that matters. Indexes: `(organization, -last_message_at)`, `(conversation, -created_at, -id)`, `(recipient_user, read_at, -created_at)`.

**These numbers are not SLOs.** They were measured on SQLite in a shared sandbox and will not match PostgreSQL 16 production behaviour under concurrency. No production latency target is claimed or implied.

### Explicit limitations (nothing here is claimed as production-ready)

1. **No real-time delivery.** No WebSocket, SSE, or Web Push. In-app notifications are pull-based; the UI says so ("Notifications update when you refresh this page").
2. **No production email or Web Push.** Both adapters are deterministic local fakes gated behind `COMMUNICATION_FAKE_PROVIDERS_ENABLED` (default **false**). No credentials exist in the repository. The preferences API reports `channels_available: {email: false, web_push: false}`.
3. **No dispatcher runtime is scheduled.** `run_dispatcher()` is implemented and tested but is not yet wired to a Celery beat schedule or worker deployment. In this branch it runs only when invoked.
4. **No compliance certification.** No GDPR, HIPAA, or WCAG certification is claimed. Accessibility was reviewed against the repository's own targets by inspection and automated test, not audited.
5. **Retention purge jobs are deferred.** Retention and purge-eligibility are classified and documented; the scheduled purge job is not implemented.
6. **Group messaging, attachments, reactions, edit/delete, and search are not implemented** — not P0 in the PRD.
7. **Docker Compose smoke test not run** — no Docker daemon in this sandbox. Dev-server smoke tests were run instead and are recorded in §5.
8. **No device-matrix testing.** Mobile behaviour was verified by responsive markup review and the production build, not on physical devices.

---

## 8. Benchmark lessons

Patterns studied (Trainerize, TrueCoach, Practice Better, Healthie) — principles only, no layouts, assets, wording, or code copied.

| Learned | Applied as |
|---|---|
| Unread triage is the primary inbox job | Unread count, bold title, text badge, and a polite aggregate announcement |
| Context beats a generic chat box | Optional `workout_session` thread context with a distinct thread and a deep link |
| Notification fatigue kills adoption | Defaults off for optional channels, per-conversation mute, quiet hours, dedupe on stable identity |
| Secure client portal expectations | Participant-only access, no owner backdoor, no email exposure, Tier-3 body classification |
| Configurable per-event preferences | Full (event × channel) matrix with explicit locked safety category |

**Deliberately not copied:** automated/broadcast coach messaging (spam risk without governance), group rooms (not P0; an org-wide room would be an authorization shortcut), multimedia attachments (needs the deferred production media pipeline), read receipts per message (privacy cost outweighs value at this stage), and any "instant/real-time" marketing language we cannot substantiate.

---

## 9. Proposed post-merge tracker entries

To be applied in a **separate docs-only synchronization PR after** the implementation PR merges. Not applied here, to avoid conflicts with the parallel 08–12 wave.

**`PROJECT_STATUS.md`** — set current phase to "Phase 08 — Communication and Notifications, merged and complete for its documented scope"; record the merge SHA, both post-merge check-run URLs, and a Phase 08 evidence table mirroring §5; note Phase 09+ not started.

**`PROJECT_CHECKLIST.md`** — tick Phase 08 items: conversations, messages, read state, notification centre, preferences, transactional outbox, provider-neutral adapters, bilingual UI, authorization matrix, security review. Leave unchecked and annotated: production email/Web Push provider, dispatcher scheduling, retention purge job, device-matrix validation, accessibility certification.

**`CHANGELOG.md`** — under a new Phase 08 heading:
- Added: `apps.communication` (conversations, messages, notifications, preferences, transactional outbox, delivery attempts); 9 additive `/api/v1` routes; messaging and notification UI in fa-IR/en-US; provider-neutral adapters with local fakes.
- Changed: `docs/OPENAPI.yaml` Phase 08 stubs replaced with the implemented contract; bottom navigation now links notifications; 5 new audit actions.
- Security: participant-only authorization with uniform 404 denial; owner private-message backdoor removed (AMD-08-01); five rate-limit scopes failing closed; message bodies excluded from logs, audit, events, and notification payloads.
- Not included: real-time delivery, production email/Web Push, group messaging, attachments, durable offline.

**`docs/PROMPT_LOG.md`** — append the Phase 08 coordinator prompt, the Gate 0 baseline verification, AMD-08-01, and the P08-* finding IDs from §6.

---

## 10. PR evidence and Definition-of-Done status

| # | DoD item | Status | Evidence |
|---|---|---|---|
| 1 | Authorized direct communication end-to-end | ✅ | §4, §5; 25 conversation tests; live smoke |
| 2 | Tenant-safe, privacy-classified data | ✅ | Contract §1/§5; 48 authz tests |
| 3 | Validated, bounded, idempotent, CSRF-protected send | ✅ | §4.2; idempotency + CSRF tests |
| 4 | Consistent read/unread | ✅ | cursor monotonicity, clamping, cap tests |
| 5 | Durable in-app notifications | ✅ | `test_dispatcher_creates_durable_notification` |
| 6 | Transactional event→notification | ✅ | `test_event_rolls_back_with_the_domain_write` |
| 7 | Retries, dedupe, failures, neutral adapters | ✅ | 21 outbox + 29 delivery tests |
| 8 | Preferences and quiet hours explicit | ✅ | forced-category + 4 quiet-hours tests |
| 9 | No real credentials or production data | ✅ | credential scanner; fakes default off; synthetic fixtures |
| 10 | fa-IR RTL / en-US LTR parity | ✅ | 312/312 keys; `dir`/`lang` verified live |
| 11 | Keyboard, SR, focus, touch, mobile reviewed | ✅ | §3; a11y scanner tests; keyboard send/retry tests |
| 12 | Cross-tenant/unassigned/suspended/revoked | ✅ | §6 rows 1–8 |
| 13 | XSS, abuse, rate-limit, replay, log redaction | ✅ | §6 rows 9–28 |
| 14 | Measured performance and limitations | ✅ | §7 |
| 15 | OpenAPI, migration, CI, security, language, secret checks | ✅ | §5 |
| 16 | Both Phase 08 reports present | ✅ | this file + contract report |
| 17 | Implementation PR open for founder review | ✅ | §10 (URL below) |
| 18 | Post-merge sync planned only | ✅ | §9; four tracked files untouched |
| 19 | No forbidden domain slippage | ✅ | scanners in both stacks |

**Status: all 19 Definition-of-Done items evidenced.**

### PR and CI evidence

| Item | Value |
|---|---|
| **Pull request** | [#19 — feat(phase-08): communication and notifications (candidate — do not merge)](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/19) |
| **Base → head** | `main` ← `arena/01a00a2a-coachos-fitness-coaching-platf` |
| **Head commit SHA** | `6ba656e057e3e7006d0b071d4b8c83e36f65de65` |
| **Baseline SHA** | `f7ccaf457cbd2e67de2708d5367f6c1386a3edce` |
| **State** | **Open — awaiting founder review. Not merged.** |

PR check runs (all **pass**):

| Check | Result | URL |
|---|---|---|
| Backend Lint, Type & Tests (Django/DRF) | pass (36s) | [job 95157315780](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31944055381/job/95157315780) |
| Frontend Lint, Type & Tests (Next.js/PWA) | pass (1m6s) | [job 95157315757](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31944055381/job/95157315757) |
| Security Scan & Language Compliance | pass (6s) | [job 95157315821](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31944055381/job/95157315821) |
| Secret & Pattern Scanning | pass (5s) | [job 95157315582](https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/actions/runs/31944055382/job/95157315582) |

### Founder decisions requested

1. **Ratify AMD-08-01** — owners have no read path into private coach–athlete message content. This narrows the previously documented OpenAPI contract. If lawful-access is required later it should be a separate, dual-control, explicitly gated feature.
2. **Confirm the deferral list in §7** — particularly dispatcher scheduling, production email/Web Push providers, and retention purge jobs.
3. **Note the Gate 0 path finding (P08-GATE0-01)** — `THREAT_MODEL.md` and `SECURITY_CONTROL_MATRIX.md` live under `docs/` rather than `docs/architecture/`; recommend normalizing in a separate docs-only PR after the 08–12 wave.

### Stop condition

Per the prompt, work stops here. The PR is **open for founder review and must not be merged automatically**. Phases 09–12 have not been started in this branch.
