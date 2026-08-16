# Phase 08 — Communication and Notifications: Contract Report

**Status:** Candidate implementation contract (Stage 1 → Stage 6)
**Baseline `main` SHA:** `f7ccaf457cbd2e67de2708d5367f6c1386a3edce`
**Working branch:** `arena/01a00a2a-coachos-fitness-coaching-platf` (Arena session-imposed; see report §2)
**Scope:** Additive `apps.communication` Django module, `/api/v1` communication + notification routes, transactional outbox, provider-neutral delivery adapters, bilingual frontend inbox/conversation/notification/preferences UI.

This document is the authoritative Stage 1 contract. Implementation must not diverge from it without an amendment recorded here.

---

## 1. Domain model contract

All identifiers are UUIDv7 strings (`apps.core.utils.id_generator.generate_uuid7`, `CharField(max_length=36)`) matching Phase 05–07 conventions. All timestamps are stored UTC (`USE_TZ = True`) and serialized ISO-8601.

### 1.1 `Conversation`

| Field | Type | Bound | Notes |
|---|---|---|---|
| `id` | CharField(36) PK | UUIDv7 | |
| `organization` | FK → `organizations.Organization` CASCADE | required | Tenant anchor. Every read is org-scoped. |
| `kind` | CharField(16) | `direct` only | Group conversations are **not P0** and are not implemented (see §6). |
| `context_type` | CharField(32) | `none` \| `workout_session` | Contextual thread linkage (PRD US-MSG-001). |
| `context_id` | CharField(36) | nullable | `WorkoutSession.id` when `context_type = workout_session`. Validated same-org. |
| `created_by_user` | FK → `identity.User` PROTECT | required | |
| `created_at` | DateTimeField | default now, indexed | |
| `last_message_at` | DateTimeField | nullable, indexed | Denormalized for stable inbox ordering. |
| `last_message_preview` | CharField(140) | truncated, sanitized | Preview only; never a full body. |
| `is_archived` | Boolean | default False | Soft lifecycle; archived conversations are read-only. |

Constraints:
- `UniqueConstraint(organization, kind, participant_key)` where `participant_key` is the sorted `"user_a:user_b"` pair plus context discriminator — guarantees exactly one direct thread per (org, participant pair, context).
- Index `(organization, last_message_at DESC)` for inbox pagination.

### 1.2 `ConversationParticipant`

| Field | Type | Notes |
|---|---|---|
| `id` | CharField(36) PK | |
| `conversation` | FK CASCADE | |
| `user` | FK → `identity.User` CASCADE | |
| `role_at_join` | CharField(20) | `coach` \| `athlete` \| `owner` — snapshot for audit, not authorization. |
| `joined_at` | DateTimeField | |
| `left_at` | DateTimeField nullable | Set on removal. Historic access ends at `left_at`. |
| `last_read_at` | DateTimeField nullable | Read-state cursor (per participant). |
| `is_muted` | Boolean | Per-conversation notification mute. |

Constraints: `UniqueConstraint(conversation, user)`; index `(user, left_at)`.

**Read-state semantics:** read state is a *monotonic per-participant cursor* (`last_read_at`), never a per-message receipt table in P0. `unread_count` = messages in the conversation with `created_at > last_read_at` and `sender_user != self`, capped at `UNREAD_COUNT_CAP = 99` in serialized output to avoid unbounded counting. `POST /read` may only move the cursor forward.

### 1.3 `Message`

| Field | Type | Bound | Notes |
|---|---|---|---|
| `id` | CharField(36) PK | | |
| `conversation` | FK CASCADE | | |
| `sender_user` | FK PROTECT | | |
| `body` | TextField | 1..`MESSAGE_MAX_LENGTH` (2000) chars after normalization | Untrusted user content. |
| `client_message_id` | CharField(64) | nullable | Idempotency key supplied by client. |
| `created_at` | DateTimeField | indexed | |

Constraints:
- `UniqueConstraint(conversation, sender_user, client_message_id)` where `client_message_id` is not null → **idempotent send**.
- Index `(conversation, created_at DESC, id DESC)` → stable keyset pagination.

**Immutability:** messages are append-only in P0. No edit, no delete, no reactions, no attachments. `Message.save()` refuses updates to `body` after insert.

**Content policy:** bodies are normalized (NFC), stripped of C0/C1 control characters except `\n` and `\t`, collapsed to at most `MESSAGE_MAX_NEWLINES = 30` newlines, and length-validated *after* normalization. Bodies are stored as plain text and rendered as plain text — the frontend never uses `dangerouslySetInnerHTML`. Auto-linking is **disabled** in P0 (explicit URL policy: URLs are displayed as inert text; no `<a>` is generated from message content).

### 1.4 `Notification`

| Field | Type | Notes |
|---|---|---|
| `id` | CharField(36) PK | |
| `organization` | FK CASCADE nullable | Tenant scope of the originating event. |
| `recipient_user` | FK CASCADE | |
| `event_type` | CharField(48) | See §2. |
| `category` | CharField(24) | `messaging` \| `training` \| `safety` \| `account` |
| `payload` | JSONField | **Metadata only** — ids, counts, actor display name, deep-link route. Never message bodies, emails, tokens. |
| `title_key` / `body_key` | CharField(64) | i18n message keys resolved client-side (bilingual, no server-rendered locale text in the payload). |
| `dedupe_key` | CharField(128) | Stable event identity. |
| `read_at` | DateTimeField nullable | |
| `created_at` | DateTimeField indexed | |

Constraints: `UniqueConstraint(recipient_user, dedupe_key)` → **at-most-one visible notification per (recipient, event identity)** regardless of outbox retries. Index `(recipient_user, read_at, created_at DESC)`.

### 1.5 `NotificationPreference`

One row per `(user, event_type)`. Channels: `in_app`, `email`, `web_push`. Booleans default per §3 table. Quiet hours are **user-level** (`quiet_hours_start`, `quiet_hours_end` as local `HH:MM`, evaluated in `User.timezone`), stored on a single `NotificationPreferenceProfile` row per user together with a global `web_push_permission_state` (`unknown` \| `granted` \| `denied`).

**Non-suppressible categories:** `safety` (feedback/pain flags) is `in_app`-forced. Preference updates that attempt to disable in-app safety notifications are rejected with `422` and `message_key = errors.notifications.category_not_suppressible`. This matches PRD US-NTF-001 ("training-critical assignment alerts continue to deliver").

**Quiet hours semantics:** quiet hours **never suppress in-app durable notifications** (they are pull-based and non-intrusive). They defer *push-like* channels (`email`, `web_push`) by setting `DeliveryAttempt.scheduled_for` to the end of the quiet window. Quiet hours are evaluated at dispatch time in the recipient's timezone with explicit DST-safe local-time comparison, including windows that wrap midnight.

### 1.6 `OutboxRecord` (durable domain event)

| Field | Type | Notes |
|---|---|---|
| `id` | CharField(36) PK | |
| `event_id` | CharField(36) unique | Envelope event identity. |
| `event_type` | CharField(48) | |
| `schema_version` | PositiveSmallInteger | Starts at `1`. |
| `organization` | FK nullable | |
| `actor_user` | FK nullable SET_NULL | |
| `subject_type` / `subject_id` | CharField | e.g. `Message` / message id. |
| `correlation_id` | CharField(36) | From `request.correlation_id`. |
| `occurred_at` | DateTimeField | |
| `payload` | JSONField | Minimum viable metadata; **never a message body**. |
| `status` | CharField(16) | `pending` \| `claimed` \| `processed` \| `failed` \| `dead_letter` |
| `attempts` | PositiveSmallInteger | |
| `next_attempt_at` | DateTimeField indexed | Backoff schedule. |
| `claimed_at` / `claim_token` | DateTimeField / CharField | Safe claiming. |
| `last_error_code` | CharField(64) | Code only; never provider payloads or secrets. |

Index `(status, next_attempt_at)`.

**Transactionality:** the outbox row is written **inside the same `transaction.atomic()` block** as the source domain mutation (message insert, session completion, feedback-flag insert). If the domain write rolls back, the event disappears with it. No event is emitted from a post-response hook.

### 1.7 `DeliveryAttempt`

`(id, notification FK CASCADE, channel, attempt_number, status ∈ {pending, scheduled, succeeded, failed, suppressed, dead_letter}, scheduled_for, error_code, provider_ref_hash, created_at)`.

`provider_ref_hash` is a SHA-256 of any provider reference — no raw provider identifiers, no recipient email, no push endpoint URL is stored or logged. Uniqueness: `UniqueConstraint(notification, channel, attempt_number)`.

---

## 2. Versioned event envelope contract

```json
{
  "schema_version": 1,
  "event_id": "0198...-uuidv7",
  "event_type": "message.sent",
  "occurred_at": "2026-08-16T10:42:11.402Z",
  "tenant_id": "0198...",
  "actor_user_id": "0198...",
  "subject_type": "Message",
  "subject_id": "0198...",
  "correlation_id": "0198...",
  "payload": { "conversation_id": "0198...", "recipient_user_ids": ["0198..."] }
}
```

Rules:
1. `schema_version` is mandatory and monotonic. Consumers must reject unknown major versions rather than guess.
2. `payload` carries **identifiers and counts only**. A `message.sent` event never carries `Message.body`.
3. `event_id` is the idempotency anchor: `dedupe_key = f"{event_type}:{event_id}:{recipient_user_id}"`.
4. Events are internal-only. There is **no public ingest endpoint**; `OutboxRecord` rows can only be created by server-side domain code inside a transaction. Forged external events are structurally impossible in Phase 08.

### Phase 08 event catalogue (v1)

| `event_type` | Emitted by | Recipients | Category | Default channels |
|---|---|---|---|---|
| `message.sent` | `POST /conversations/{id}/messages` | other active participants | `messaging` | in_app ✔, email ✖, web_push ✖ |
| `workout.completed` | Phase 07 session completion | assigned coach(es) | `training` | in_app ✔, email ✖, web_push ✖ |
| `feedback_flag.created` | Phase 07 feedback flag creation | assigned coach(es) | `safety` | in_app ✔ (forced), email ✖, web_push ✖ |

Email and Web Push defaults are **off** because Phase 08 ships no real provider. Turning them on exercises the fake adapters only.

---

## 3. Authorization matrix (server-enforced)

Legend: ✔ allowed · ✖ denied (safe `403`/`404`, no existence leakage).

| Actor | List conversations | Read conversation/messages | Send message | Mark read | Notifications (self) | Preferences (self) |
|---|---|---|---|---|---|---|
| Athlete, active participant | ✔ own only | ✔ | ✔ | ✔ | ✔ | ✔ |
| Athlete, not a participant | ✖ (excluded from list) | ✖ 404 | ✖ 404 | ✖ 404 | n/a | n/a |
| Coach, active `CoachAthleteAssignment` + participant | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| Coach, participant but assignment revoked | ✔ (read) | ✔ read-only | ✖ 403 `errors.authz.unassigned_athlete` | ✔ | ✔ | ✔ |
| Coach, unassigned / not participant | ✖ | ✖ 404 | ✖ 404 | ✖ 404 | n/a | n/a |
| Owner (same org), not a participant | ✖ **by default** | ✖ 404 | ✖ | ✖ | ✔ own | ✔ own |
| Support (any status) | ✖ | ✖ 404 | ✖ 404 | ✖ | ✔ own | ✔ own |
| Suspended / archived membership | ✖ | ✖ 404 | ✖ 404 | ✖ 404 | ✖ 403 | ✖ 403 |
| Cross-tenant user | ✖ | ✖ 404 | ✖ 404 | ✖ 404 | ✖ | ✖ |
| Platform admin (`is_platform_admin`) | ✖ | ✖ 404 | ✖ | ✖ | ✔ own | ✔ own |

**Owner access policy (explicit decision).** The OpenAPI stub allowed "owner escalation audited" into private threads. Phase 08 **narrows** this: an organization owner has **no read path into private coach–athlete message content** through the Phase 08 API. Rationale — the prompt forbids "an unrestricted private-message backdoor," and an audited-but-always-available backdoor is still a backdoor for a coach–athlete relationship carrying health-adjacent content. Owners retain org administration and audit-event visibility (Phase 05), which records *that* conversations exist without exposing bodies. Any future lawful-access path must be a separately gated, dual-control, founder-approved feature. This is recorded as contract amendment **AMD-08-01** and reflected in `docs/OPENAPI.yaml`.

**Membership-change semantics (explicit decision).** Adding a user to a conversation does **not** grant retroactive access: message history is filtered to `Message.created_at >= ConversationParticipant.joined_at`. Removing a participant (`left_at`) revokes read and write immediately; the historic window is not re-openable by re-adding (a new `joined_at` applies). Coach reassignment revokes *send* immediately and leaves *read* of the window the coach legitimately participated in — never widened.

---

## 4. API contract (additive, `/api/v1`)

All routes: cookie session auth, `IsAuthenticatedAndActive`, CSRF-enforced on unsafe methods, RFC 7807 + `message_key` errors, `X-Request-ID` correlation.

| Method | Path | Success | Notes |
|---|---|---|---|
| `GET` | `/api/v1/conversations` | 200 | Keyset page by `last_message_at,id`; `limit` 1..50 default 20; `cursor` opaque. Returns `unread_count`, `last_message_preview`, `last_message_at`, `counterpart`. |
| `POST` | `/api/v1/conversations` | 201 / 200 | Body `{counterpart_user_id, context_type?, context_id?}`. Idempotent: returns the existing thread with 200 if one exists. Requires active assignment between the two users. |
| `GET` | `/api/v1/conversations/{conversation_id}` | 200 | Participant-only detail. |
| `GET` | `/api/v1/conversations/{conversation_id}/messages` | 200 | Keyset `before` cursor, `limit` 1..50 default 30, newest-first, stable `(created_at, id)` ordering, bounded by `joined_at`. |
| `POST` | `/api/v1/conversations/{conversation_id}/messages` | 201 / 200 | Body `{body, client_message_id?}`. 200 + original message on idempotent replay. 422 on validation, 429 on rate limit. |
| `POST` | `/api/v1/conversations/{conversation_id}/read` | 200 | Body `{read_at?}`; cursor moves forward only. Never mutates messages. |
| `GET` | `/api/v1/notifications` | 200 | Self only. Filters `unread=true`, `category`. Keyset paged, `limit` 1..50 default 20. Includes `unread_count` (capped). |
| `POST` | `/api/v1/notifications/{notification_id}/read` | 200 | Self only; 404 for other users' ids (no existence leak). Idempotent. |
| `POST` | `/api/v1/notifications/read-all` | 200 | Returns `{updated}`. Bounded single UPDATE. |
| `GET` | `/api/v1/notification-preferences` | 200 | Self only; returns full matrix + quiet hours + push permission state. |
| `PATCH` | `/api/v1/notification-preferences` | 200 | Partial; rejects suppression of forced categories (422). Audited. |

### Error contract additions

| `message_key` | Status | Meaning |
|---|---|---|
| `errors.messaging.body_too_long` | 422 | Body exceeds 2000 chars after normalization. |
| `errors.messaging.body_empty` | 422 | Body empty after normalization. |
| `errors.messaging.rate_limited` | 429 | Per-user / per-conversation / per-tenant limit hit. |
| `errors.messaging.conversation_archived` | 409 | Send to archived conversation. |
| `errors.messaging.participant_inactive` | 403 | Counterpart membership suspended/archived. |
| `errors.authz.unassigned_athlete` | 403 | Coach lost the active assignment. |
| `errors.notifications.category_not_suppressible` | 422 | Attempt to disable forced in-app safety channel. |

### Rate limits (fixed-window, cache-backed, fail-closed on cache error)

| Scope | Limit |
|---|---|
| Per user, all messages | 30 / 60 s |
| Per user, per conversation | 15 / 60 s |
| Per organization (all senders) | 600 / 60 s |
| Per user, conversation creation | 10 / 300 s |
| Per user, preference PATCH | 20 / 300 s |

Counters key on the **authenticated user id and org id from server state**, never on a client-supplied header, so multi-endpoint or multi-identifier bypass is not available.

---

## 5. Data classification and retention

| Entity | Classification | Logged? | Retention / deletion |
|---|---|---|---|
| `Conversation` | Tier 2 — confidential relationship metadata | ids only | Cascade on organization delete. |
| `ConversationParticipant` | Tier 2 | ids only | Cascade with conversation/user. |
| `Message.body` | **Tier 3 — personal user content** | **never** | Cascade with conversation; erasure request (Phase 05 privacy path) removes user's messages. No body in logs/audit/analytics/test fixtures beyond synthetic strings. |
| `Message` metadata | Tier 2 | ids only | as above |
| `Notification.payload` | Tier 2 (ids, counts, display name) | ids only | Cascade with recipient; read notifications older than the documented window are purge-eligible (purge job deferred, documented). |
| `NotificationPreference*` | Tier 1 | change events audited (keys only) | Cascade with user. |
| `OutboxRecord.payload` | Tier 2 (ids only) | error codes only | Processed rows purge-eligible; purge job deferred. |
| `DeliveryAttempt` | Tier 1 + hashed refs | error codes only | Cascade with notification. |

Audit actions added (`apps.audit.AuditEvent.ACTION_CHOICES`): `conversation.created`, `message.sent`, `conversation.read`, `notification.preferences_updated`, `notification.read_all`. Audit metadata contains ids, counts and keys only — never bodies.

---

## 6. Explicit scope boundary

**In scope (P0, derived from PRD US-MSG-001 and US-NTF-001):** 1:1 coach–athlete conversations, optional workout-session context link, message history, read/unread, in-app notification centre, preferences, transactional outbox, provider-neutral adapters, bilingual UI.

**Gated out of Phase 08 (not P0 in the authoritative PRD; not implemented):** group conversations, broadcast/automated messages, attachments/multimedia, reactions, message edit/delete, message search, typing indicators, presence, read receipts per message.

**Hard exclusions (verified absent by the scope scanner test):** nutrition, billing/payments, AI drafting or summarization, durable offline queues / IndexedDB / background sync, SMS/WhatsApp, real email or Web Push credentials, public profiles/marketplace, clinical/crisis messaging, native apps, Arabic resources, real personal or production data.

---

## 7. Delivery reliability contract

- **Claiming:** `SELECT ... FOR UPDATE SKIP_LOCKED` where supported; on SQLite (test/dev) an atomic compare-and-set on `(status, claim_token)` provides the same at-most-one-claimer guarantee. Both paths are tested.
- **Backoff:** attempt *n* retries at `min(BASE * 2^(n-1), MAX)` seconds with `BASE = 30`, `MAX = 3600`, `MAX_ATTEMPTS = 5`; after exhaustion the record moves to `dead_letter` and is never retried automatically.
- **Deduplication:** enforced at two levels — `OutboxRecord.event_id` unique (no duplicate events) and `Notification (recipient_user, dedupe_key)` unique (no duplicate visible notifications even if the same event is processed twice).
- **Failure isolation:** an email/web-push adapter failure marks only that `DeliveryAttempt` failed. The durable in-app `Notification` is already committed and is **never deleted** because of a downstream channel failure.
- **Real-time claim boundary:** Phase 08 delivers in-app notifications via **client polling / manual refresh only**. There is no WebSocket, no SSE, no service-worker push subscription, and no real Web Push. The `web_push` adapter is a deterministic local fake that records suppression when browser permission is `denied` or `unknown`. No real-time or push-reliability claim is made anywhere in the UI or docs.

---

## 8. Traceability

| Requirement | Contract section | Implementation | Test |
|---|---|---|---|
| PRD US-MSG-001 contextual 1:1 threads | §1.1, §4 | `apps/communication/{models,views}.py` | `tests/communication/test_conversations.py` |
| PRD US-MSG-001 notification with deep link | §1.4, §2 | `apps/communication/events.py`, `mapping.py` | `tests/communication/test_outbox.py` |
| PRD US-NTF-001 preferences, non-suppressible critical | §1.5, §4 | `apps/communication/views.py` | `tests/communication/test_preferences.py` |
| NFR-AUTHZ-03 object-level authorization | §3 | `apps/communication/authz.py` | `tests/communication/test_authorization.py` |
| ADR-003 Arabic exclusion | §6 | dictionaries | `test_no_arabic.py`, `no-arabic.test.ts` |
| ADR-036 no durable offline | §6 | — | `tests/offline-scope.test.ts` (extended to Phase 08 dirs) |
