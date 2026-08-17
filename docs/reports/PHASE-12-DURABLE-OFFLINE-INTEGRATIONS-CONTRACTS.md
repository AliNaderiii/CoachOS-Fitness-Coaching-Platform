# Phase 12 — Durable Offline and Integrations Contracts

**Document version:** 1.0.0  
**Branch:** `phase/12-durable-offline-integrations`  
**Baseline SHA:** `f7ccaf457cbd2e67de2708d5367f6c1386a3edce` (verified; note that `PROJECT_STATUS.md` references `0949abeead5ba74a3deb0d2439a464ab6bbd99dd` which does not match the actual remote `main`; discrepancy documented in Phase 12 report)  
**Status:** Contract draft — not merged; for founder review only.

---

## 1. Offline Capability Matrix

| Operation Class | Offline Read | Offline Write | Online-Only Operations | Data Sensitivity | Conflict Strategy | Queue Policy | Purge Policy |
|---|---|---|---|---|---|---|---|
| App shell / manifest | Cached (CacheFirst) | No | None | Tier0 public metadata | N/A (immutable assets) | N/A | Cache cleared on logout/account switch |
| Exercise catalog (canonical) | Cached snapshot with timestamp (StaleWhileRevalidate) | No writes to catalog | Create custom exercise requires online (auth + storage) | Tier0 public metadata + Tier2 org-private | Last server wins; no offline mutation allowed | N/A | Cache metadata cleared on purge |
| Program assignment snapshot | Read cached snapshot with `last_synced_at` timestamp | No mutation to snapshot (immutable) | Assign new program (requires server authorization) | Tier2 operational (org-scoped) | Server version wins; athlete reads frozen snapshot; updates require sync | N/A for snapshot; new assignments queued | Snapshot cache cleared on tenant/logout change |
| Workout session (start/complete) | Read previous session details (stale label shown) | **Supported:** Start session (pending), complete session (pending), log set actual (pending) | Create session from unassigned athlete; delete completed session (online only) | Tier2 operational; Tier3 health-adjacent for feedback flags; Tier4 progress media (online only) | Append-only for set logs; server-wins with conflict UI for non-appendable mutations (e.g., same set_index edited simultaneously) | Durable IndexedDB queue; bounded size (max 200 queued ops); bounded age (max 7 days); bounded retry (max 5 attempts per op) | Queue cleared on sign-out/account switch/tenant change/suspension/revocation; best-effort purge (IndexedDB may persist briefly until cleared) |
| Set actual logging | Read previous set logs (stale label shown) | **Supported:** Add/update set actual with client operation ID | Edit completed session after server acknowledgment without sync conflict resolution (online only if conflict) | Tier2 operational | Idempotent append/merge by `client_operation_id`; duplicate `client_operation_id` discarded server-side; same `set_index` edited offline vs online → server version wins with visible conflict explanation | Queue per athlete + session; ordered by `created_at`; retry with exponential backoff + jitter (2s, 5s, 15s, 60s max) | Purged on sign-out/account-switch/tenant-change; failed/dead-letter visible until resolved or discarded by user |
| Exercise substitution/skip | Read substitution list (stale) | **Supported:** Create substitution record (pending) | Modify completed session substitution after server acknowledgment (online only) | Tier2 operational | Server-wins; manual conflict resolution UI if offline substitution conflicts with server update | Queue per session; retry bounded | Same purge policy |
| Feedback flag (pain/fatigue) | Read previous flags (stale) | **Supported:** Create new flag (pending) | Resolve/update flag after acknowledgment without conflict resolution (online only) | Tier3 sensitive health-adjacent | Explicit conflict UI; never auto-merge health-adjacent authored data | Queue per athlete + session; retry bounded | Purged on sign-out/account-switch/tenant-change |
| Body metric (weight, etc.) | Read previous metrics (stale) | **Supported:** Create/update metric (pending) | Delete metric (online only) | Tier3 sensitive health-adjacent | Explicit conflict UI; versioned with ETag; last safe write only if explicitly safe per consent | Queue per athlete; retry bounded | Purged on sign-out/account-switch/tenant-change |
| Progress photo / private media | Read consent record + metadata only (no image bytes cached) | **Excluded:** Upload online only; no offline durable storage of raw photos unless separately approved encrypted design exists | Any media upload, consent change, revocation (online only) | Tier4 most sensitive | Online-only; no conflict for media uploads; consent revocation blocks future reads immediately | Not queued offline | All media references removed from IndexedDB on purge; signed URLs not cached in SW |
| Message thread / message | Read previous messages (stale) | **Excluded:** No durable message queue in Phase 12; temporary in-memory preservation only (same as Phase 07) | Send message (online-only until durable message queue is separately designed) | Tier2+ confidential | Not implemented for durable offline; online-only for new messages | Not queued durably | Memory-only state cleared on reload/sign-out |
| Auth, membership, organization settings | Read cached metadata only | **Excluded:** All auth/token/membership changes require online connection | Any role change, invitation, suspension, revocation, consent change, erasure, export request | Tier1 account / Tier6 secrets | Online-only; no blind overwrite for security settings | Not queued | Session/token purge on sign-out; no persistent auth state |
| Integration sync (wearable/mock provider) | Read last sync cursor + imported data provenance (stale) | **Supported:** Trigger sync (pending); disconnect (pending with revocation) | Real-time webhook processing requires online verification; provider token refresh (online only) | Tier2 operational (imported measurements) + Tier3 health-adjacent if provider includes health data | Incremental sync by cursor + event ID; duplicate event IDs discarded; out-of-order events accepted within bounded window; rate limit respected | Queue for sync trigger events; retry bounded; dead-letter for unrecoverable provider errors | Disconnect clears sync cursor and revokes future sync; retained imported data stays per disconnect policy; erasure request handled online |

---

## 2. Data Classification and Storage Policy

### 2.1 Client Storage Classification (IndexedDB)

| Store Name | Schema Version | Sensitive Data? | Encryption at Rest | Shared-Device Threat | XSS Threat | Purge on Logout | Notes |
|---|---|---|---|---|---|---|---|
| `offline_queue` | v1 (migrated to v2 for Phase 12) | Contains Tier2-Tier3 operation payloads (set logs, feedback, metrics) with `entity_id`, `actor_user_id`, `payload_schema_version`, `integrity_hash`. **No raw health details beyond what operation requires.** | Not encrypted by IndexedDB automatically; relies on OS-level encryption (FileVault, BitLocker, iOS data protection). Documented trade-off: full client-side encryption requires a key derived from user credentials, which introduces key-loss and usability risk. **Decision:** rely on OS-level encryption + purge policy + no secrets in storage; document limitation explicitly. | High: device lost = IndexedDB may persist until OS wipes or purge triggered. Purge on sign-out reduces exposure window. | Medium: malicious script in same origin could read IndexedDB. Mitigated by CSP (nonce/hash), HttpOnly cookies, strict XSS sanitization, and scope-scanner enforcement. Documented. | Best-effort: `offline_queue.clear()` executed synchronously; storage may persist briefly until cleared, but no new operations queued after purge trigger. | Queue records include `integrity_hash` (SHA-256 over `client_operation_id` + `entity_type` + `entity_id` + `payload_schema_version` + `actor_user_id` + `payload`) to detect payload tampering. |
| `offline_cache_metadata` | v1 | Contains `last_synced_at`, `entity_id`, `server_version` or `etag`, `stale` flag, `timestamp`. No payload. No PII beyond `entity_id` (UUIDv7) and `actor_user_id` (UUIDv7). | Same as above. | Low: metadata only. | Low. | Cleared on purge. | Used for stale-data labeling and refresh decisions. |
| `offline_sync_receipts` | v1 | Contains `client_operation_id`, `entity_id`, `state` (acknowledged/conflict/failed/dead_letter/discarded), `server_version_or_etag`, `error_code`, `updated_at`. No raw payload. No secrets. | Same. | Low. | Low. | Cleared on purge. | Durable receipt tracking; used for conflict UI and retry logic. |
| `offline_integration_state` | v1 | `provider_account_reference` (opaque reference ID only — no token), `sync_cursor`, `last_sync_at`, `connection_state` (connected/disconnected/reauthorizing/limited_permission), `provider_rate_limit_remaining`, `provider_rate_limit_reset`. **No access/refresh token, no real provider secrets.** | Same. | Low (no secrets stored). | Low. | Cleared on disconnect/purge. | Provider-neutral; fake adapter only for Phase 12; real provider requires separate approval. |
| `offline_workout_session_state` | v1 (temporary) | In-progress session state: `session_id`, `scheduled_date`, `started_at`, `current_items`, `unsaved_set_inputs`. Not durable; survives component remount but not browser restart. **Not a durable queue.** | Memory only (React state / sessionStorage optional for preservation but not durable). Not IndexedDB. | Low (memory only). | Low (no durable storage). | Cleared on reload/sign-out. | Phase 07 behavior preserved; Phase 12 durable queue is separate (`offline_queue`). |

### 2.2 Purge Policy Details

- **Sign-out / Logout:** Trigger `signOut()` which calls `IndexedDB.clearAllStores()` synchronously; also clears `offline_workout_session_state` (memory); sends revocation signal to backend (if online) to invalidate session tokens; clears service-worker queued operations that reference the user.
- **Account Switch:** If user switches active organization or role, purge all offline operations for the previous organization to prevent cross-tenant replay; new operations only for active organization.
- **Tenant Change / Suspension / Revocation:** If organization membership is suspended or revoked, purge all queued operations for that organization; future sync blocked.
- **Storage Quota Full:** If `IndexedDB` throws `QuotaExceededError`, fail visibly: show banner "Storage full — queued operations cannot be saved. Discard oldest dead-letter operations or resolve conflicts to free space." Provide discard/cancel actions per queued operation. Never silently drop operations.
- **Schema Migration:** On startup, check `offline_queue.schema_version`. If `current_version > queued_version`, migrate queued records: if payload schema version differs significantly (e.g., new required fields), move conflicting records to `dead_letter` state with `error_code` = `SCHEMA_MISMATCH`; preserve original payload in `dead_letter` for user-visible recovery. User must manually retry/discard dead-letter records.

---

## 3. Durable Queue and Operation Protocol

### 3.1 Operation Record Schema (IndexedDB `offline_queue`)

```
{
  "client_operation_id": "0191b3f2-...",  // UUIDv7 generated client-side
  "operation_type": "CREATE_SET_LOG" | "UPDATE_SESSION" | "CREATE_SUBSTITUTION" | "CREATE_FEEDBACK_FLAG" | "CREATE_BODY_METRIC" | "TRIGGER_INTEGRATION_SYNC" | "DISCONNECT_INTEGRATION",
  "entity_type": "workout_session" | "set_log" | "feedback_flag" | "body_metric" | "substitution" | "integration_connection",
  "entity_id": "0191b3f2-...",
  "organization_id": "0191b3f2-...",
  "actor_user_id": "0191b3f2-...",
  "payload": { ... },  // operation-specific payload; schema_version embedded
  "payload_schema_version": "1.2",
  "created_at": "2026-08-16T10:30:00Z",  // client local time; converted to UTC on sync
  "updated_at": "2026-08-16T10:35:00Z",
  "last_attempt_at": "2026-08-16T10:35:00Z",
  "attempt_count": 3,
  "state": "pending" | "in_flight" | "acknowledged" | "conflict" | "failed" | "dead_letter" | "discarded",
  "server_version_or_etag": "W/\"abc123\"",
  "error_code": "NETWORK_TIMEOUT" | "SCHEMA_MISMATCH" | "AUTHZ_DENIED" | "RATE_LIMITED" | "CONFLICT" | null,
  "safe_error_message_key": "errors.sync.network_timeout" | null,
  "integrity_hash": "sha256:...",  // over key fields + payload
  "retry_backoff_until": "2026-08-16T10:40:00Z"
}
```

### 3.2 Idempotency Key Derivation

- **Derivation:** `idempotency_key = SHA-256( actor_user_id + ":" + organization_id + ":" + operation_type + ":" + entity_type + ":" + entity_id + ":" + client_operation_id )`
- **Uniqueness scope:** Per `actor_user_id` + `organization_id` + `entity_type` + `entity_id` per `operation_type`. The `client_operation_id` ensures uniqueness even for identical entity mutations (e.g., updating the same set log twice with different payloads produces different idempotency keys).
- **Server enforcement:** Backend endpoints that support offline operations (`POST /api/v1/workout-sessions/{session_id}/sets`, `POST .../substitutions`, etc.) check for `Idempotency-Key` header. If a previous request with the same key exists and returned `acknowledged`, return the same response (cached acknowledgment) without re-processing. If the previous request is `in_flight`, return `409 Conflict` with `Retry-After` header. If no previous request found, process normally and store acknowledgment keyed by `idempotency_key`.
- **Durable acknowledgment storage:** Server stores acknowledgments in a durable table `IdempotencyRecord` (not in this PR; defined as contract) with columns: `idempotency_key`, `actor_user_id`, `organization_id`, `operation_type`, `entity_type`, `entity_id`, `response_payload`, `status`, `created_at`, `expires_at` (max 24h retention for retry window). After 24h, acknowledgments may be purged (idempotency is primarily for bounded retry, not infinite replay defense).

### 3.3 Conflict Classification and Resolution Strategy

| Entity Class | Conflict Type | Auto-Merge Safe? | Resolution Strategy | UI Behavior |
|---|---|---|---|---|
| Set log (`set_log`) | Same `entity_id` (workout session + set_index) edited offline and online simultaneously | Partial: append-only by `client_operation_id` is safe; same `client_operation_id` = discard; different `client_operation_id` with same `set_index` but different payload = server-wins with visible explanation | Server version wins; user sees conflict card: "A newer version was saved online. Your queued version: [load/reps]. Online version: [load/reps]. Choose: [Keep Online] [Keep Queued] [Edit Manually]." | Conflict card in sync status UI; user must choose resolution before queued operation is resolved; manual edit creates a new operation |
| Feedback flag (`feedback_flag`) | Same `entity_id` edited offline and online | Not safe for health-adjacent authored content | Explicit conflict UI; never blind overwrite | User must choose which version to keep or merge details manually; conflict does not block other queued operations |
| Body metric (`body_metric`) | Same metric date edited offline and online | Not safe (versioned health data) | Explicit conflict UI; versioned with `ETag`; server-wins unless user selects queued version | Conflict card showing server version vs queued version; user selects |
| Substitution (`substitution`) | Same session/substitution edited offline and online | Not safe (structured substitution record) | Explicit conflict UI; server-wins with explanation | Conflict card; user chooses |
| Integration sync trigger (`integration_connection`) | Duplicate trigger events (same provider + same cursor) | Safe by event deduplication | Idempotent append/merge by event ID; duplicate event IDs discarded server-side | User sees "Already synced" status; no conflict |
| Integration disconnect (`integration_connection`) | Disconnect triggered multiple times | Safe by idempotency | Idempotent disconnect; future sync revoked; retained data per disconnect policy | User sees "Disconnected" status |

### 3.4 Conflict Resolution UI Requirements

- **Visible status:** For each queued operation, show `pending` / `in_flight` / `acknowledged` / `conflict` / `failed` / `dead_letter` with a localized icon and label.
- **Pending count:** Footer/status bar shows "Pending: 3" or "Failed: 1" or "Conflict: 1".
- **Conflict card:** Shows server version (read from server on reconnect) vs queued version. Provides three actions: "Keep Server Version", "Keep Queued Version" (which creates a new update operation with the queued payload), "Edit Manually" (opens edit form with queued payload pre-filled). After resolution, the queued operation is moved to `acknowledged` (if server version kept) or a new operation is queued (if queued version kept or edited).
- **Failed/dead-letter visibility:** Show error message key (localized) and retry/cancel/discard actions. "Retry" resets `attempt_count` to 0 and sets `state` to `pending`. "Discard" sets `state` to `discarded` and removes from active sync queue (retained in `offline_sync_receipts` for audit). "Cancel" sets `state` to `discarded` and removes.
- **Access rules:** Conflict resolution and retry/discard actions are only available to the `actor_user_id` of the queued operation. Cross-user operations must be blocked server-side.

---

## 4. Sync Protocol (Client ↔ Server)

### 4.1 Foreground Synchronization (Always Active)

- **Trigger conditions:** App becomes foreground (`visibilitychange` event); `navigator.onLine` changes to `true`; user taps "Retry"; user taps "Sync"; periodic foreground sync timer (every 30 seconds when online and queue non-empty) — but not excessively frequent to preserve battery.
- **Sync process:**
  1. Read all queued operations with `state` = `pending` or `failed` (not `dead_letter` or `discarded`) from `offline_queue`, ordered by `created_at` ascending.
  2. For each operation, compute `idempotency_key` and attempt `POST` (or appropriate method) with `Idempotency-Key` header.
  3. On `200`/`201` with acknowledgment: update `offline_sync_receipts` with `state` = `acknowledged`, `server_version_or_etag`, `updated_at`; remove from active queue or mark as acknowledged (retain receipt for 24h).
  4. On `409 Conflict` with conflict response: update `offline_sync_receipts` with `state` = `conflict`, `server_version_or_etag`, `updated_at`; present conflict UI.
  5. On `429 Too Many Requests`: respect `Retry-After`; set `retry_backoff_until`; do not retry immediately.
  6. On `500`/`503`/timeout/network error: increment `attempt_count`; set `last_attempt_at`; compute next `retry_backoff_until` (exponential backoff with jitter: `backoff = min(2^attempt_count * base_delay, max_delay) + random(0, jitter)` where `base_delay` = 2s, `max_delay` = 60s, `jitter` = 2s); set `state` = `pending` or `failed` based on `attempt_count` (if `attempt_count >= max_retry` = 5, set `state` = `dead_letter`).
  7. If any operation reaches `dead_letter`: show user-visible notification: "Some operations could not be synced. Review sync status."
- **Bounded retry:** Maximum 5 attempts per operation. After 5 attempts, state = `dead_letter`. User must manually retry (resets attempt count) or discard.
- **Max queue size:** 200 queued operations. If queue exceeds 200, reject new queued operations with visible error: "Queue full — resolve conflicts or discard failed operations before adding new ones."
- **Payload size limit:** Maximum queued payload size = 500KB per operation (to prevent IndexedDB bloat from large payloads). Operations exceeding this are rejected before queuing.
- **Age limit:** Operations older than 7 days in `pending` or `failed` state are moved to `dead_letter` automatically (with `error_code` = `AGE_LIMIT_EXCEEDED`). User can still manually retry from `dead_letter` if desired (resets age).

### 4.2 Background Synchronization (Optional, Feature-Detected)

- **Browser support:** Chrome/Edge on desktop and Android support `Background Sync API` (`self.registration.sync.register`). Firefox desktop does not support it. Safari iOS does not support it (as of 2026).
- **Registration:** On startup, if `navigator.serviceWorker` exists and `'sync' in self.registration` (or equivalent feature detection), register a `'sync-sets'` sync tag.
- **Fallback:** If background sync is unsupported or denied (`sync` permission not granted), rely entirely on foreground retry and the periodic timer.
- **Behavior:** When the browser triggers `'sync'` event, the service worker attempts to flush the queue by fetching `/api/v1/sync/flush` (or equivalent endpoint) with the queued operations included in the request body. The service worker updates queue state based on the response.
- **Security:** The service worker does not store user credentials or long-lived tokens. It uses the same session cookie or bearer token as the foreground app (retrieved from `IndexedDB` only if necessary and cleared after sync). The service worker does not log sensitive payloads.

### 4.3 Online-Only Operations (Explicit List)

The following operations are **online-only** and must return `403` or `400` if attempted offline (with a visible error message):

- User registration (`POST /auth/register`)
- User login (`POST /auth/login`)
- Password reset (`POST /auth/forgot-password`)
- Organization creation/update (`POST /PATCH /organizations/{id}`) — except updates to non-critical settings? Actually all org settings require auth + online.
- Invitation creation/revocation (`POST /PATCH /organizations/{org_id}/members/{id}`)
- Program assignment (`POST /programs/{id}/assign`)
- Exercise catalog moderation (`POST /admin/moderation/exercises/{id}/approve`)
- Progress photo upload (`POST /athletes/{id}/progress/photos`) — excluded from durable offline
- Consent change (`POST /consents`) — consent changes require immediate server enforcement; offline consent grant/revoke is not durable (temporary in-memory only, same as Phase 07)
- Integration connect (`POST /integrations/connect`) — OAuth redirect requires network
- Integration sync trigger (`POST /integrations/{id}/sync`) — can be queued; but initial authorization requires online
- Integration disconnect (`POST /integrations/{id}/disconnect`) — can be queued; revocation requires server; queued disconnect is allowed but revocation is best-effort until server acknowledgment
- Data export request (`POST /privacy/export-request`)
- Data erasure (`POST /privacy/forget-me`)
- Any role change, suspension, revocation (`PATCH /memberships/{id}`)
- Any message send (`POST /messages`) — excluded from durable queue in Phase 12

---

## 5. Integration Security and Data Requirements (Provider-Neutral Boundary)

### 5.1 Integration Adapter Contracts

The integration adapter is provider-neutral. A deterministic mock/sandbox adapter (`MockFitnessProviderAdapter`) is implemented in Phase 12. Real provider adapters (e.g., Strava-style webhook, Garmin, Apple HealthKit backend) may be added only with separate founder approval covering provider scopes, legal terms, data residency, credential handling, and test environment.

| Entity / Record | Fields (Server-Side Only) | Client-Side Visibility | Security / Privacy Notes |
|---|---|---|---|
| `IntegrationConnection` | `id` (UUIDv7), `organization_id`, `athlete_user_id`, `provider_type` (`mock_fitness`, `strava`, etc. — future only with approval), `provider_account_reference` (opaque reference ID — no real account number or email), `connection_state` (`connected` / `disconnected` / `reauthorizing` / `limited_permission` / `expired`), `scopes_granted` (array of scope strings, e.g., `read_activity`, `read_heart_rate` — only approved scopes), `token_vault_reference` (reference to server-side encrypted vault — **never the actual token**; no token bytes in DB, logs, or frontend), `connected_at`, `disconnected_at`, `last_sync_at`, `sync_cursor` (cursor value for incremental sync — opaque to client), `revocation_status` (`none` / `pending` / `completed`) | Shows `provider_type` (localized label: "Mock Fitness Provider"), `connection_state` (localized label), `scopes_granted` (localized list of approved scopes with explanation), `connected_at`, `last_sync_at` (localized timestamp). **No token vault reference visible. No real provider account reference visible.** | Server-side vault reference only. Client receives connection state and sync status, not credential material. Disconnect triggers revocation request to provider (if supported) and clears server-side token. No access/refresh token in URL, logs, frontend bundle, IndexedDB, localStorage, or screenshots. |
| `OAuthState` / `PKCE` (Server-Side Transaction) | `state` (crypto random nonce, 32+ bytes URL-safe base64), `code_challenge` (PKCE SHA-256 of verifier), `code_verifier` (stored server-side only — never in URL, never in client), `redirect_url` (allowlist-verified), `provider_type`, `created_at`, `expires_at` (10 min max) | Client receives only `authorization_url` (provider redirect URL) and `state` parameter embedded in the redirect URL (required for OAuth CSRF defense). Client does not receive `code_verifier`. | `state` validated server-side on callback; `redirect_url` allowlisted; `code_verifier` never exposed; PKCE `code_challenge` sent to provider, `code_verifier` kept server-side. No real provider secrets in repository. |
| `ProviderAccountReference` (Opaque) | `provider_account_id` (opaque provider-side identifier — not the athlete's real provider account number or email; derived from provider response after authorization), `provider_email` (not stored unless required and approved separately) | Not visible to user directly; used for provider event mapping. If provider event includes athlete identifier, server maps it to `IntegrationConnection.athlete_user_id` via `provider_account_reference`. | No real athlete health data or provider account details exposed to client; server-side mapping ensures tenant-safe isolation. |
| `SyncCursor` | `cursor_type` (`timestamp` / `event_id` / `page_token`), `cursor_value`, `updated_at` | Visible as "Last sync: [timestamp]" and "Sync cursor updated" status. | Cursor is opaque; no sensitive data embedded. Corruption detection: if cursor format is invalid or out of expected range, reset to safe default (e.g., 7 days ago) and log `integration.cursor_reset`. |
| `ImportedActivity` / `Measurement` (Mock) | `id` (UUIDv7), `organization_id`, `athlete_user_id`, `provider_account_reference`, `provider_type`, `provider_event_id` (unique event/object ID from provider — used for deduplication), `provider_timestamp` (original event timestamp — preserved for provenance), `imported_at` (server import time — UTC), `data_type` (`workout` / `run` / `ride` / `measurement` / `body_metric`), `payload` (normalized measurement payload — only approved fields; no raw provider response stored unless approved), `unit_normalized` (normalized to metric or imperial per athlete preference), `duplicate_check` (`provider_event_id` + `provider_account_reference` unique), `data_provenance` (`source_timestamp`, `provider_type`, `import_timestamp`, `cursor_at_import`) | Shows `provider_timestamp` (localized), `data_type` (localized), `unit_normalized`, `data_provenance` (localized explanation: "Imported from Mock Fitness Provider at 10:30 AM"), `provider_event_id` (not shown to user; used for deduplication). **No raw provider response payload visible.** | Data provenance visible: athlete can see when data was imported, from which provider, and which event it came from. Duplicate detection: if same `provider_event_id` + `provider_account_reference` is received again, discard silently (idempotent import). No full provider event payload stored unless separately approved. |
| `WebhookReceipt` (Future — Contract Only) | `provider_type`, `provider_event_id`, `event_type`, `payload_hash` (hash of verified payload — not full payload unless needed), `signature_verified` (boolean), `verified_at`, `deduplication_result` (`new` / `duplicate` / `replay`), `cursor_updated` | Not visible directly; results in `ImportedActivity` records visible to user. | Webhook verification interface defined but not implemented with real provider in Phase 12. Mock adapter uses deterministic event generation, not webhooks. Real webhook verification requires separate provider approval. Replay defense: store `provider_event_id` + `signature_verified` + `verified_at`; reject events with same `provider_event_id` that are older than the latest verified event (within bounded replay window: max 24h). Rate limit: max 100 webhook events/min per provider per athlete. |
| `IntegrationError` | `provider_type`, `provider_account_reference`, `error_type` (`authentication_failed` / `rate_limited` / `provider_outage` / `scope_denied` / `webhook_verification_failed` / `cursor_corruption` / `duplicate_event` / `invalid_payload`), `error_message_key` (localized safe message), `provider_error_code` (opaque provider error code — not exposed to user unless safe), `created_at`, `resolved_at` | Shows `connection_state` = `limited_permission` or `expired` or `reauthorizing`; shows safe localized message (e.g., "Connection requires reauthorization — tap to reconnect."). **No raw provider error details exposed.** | Provider-specific error codes are mapped to safe message keys; raw provider responses are never logged or exposed to client. Rate limit state: `provider_rate_limit_remaining` and `provider_rate_limit_reset` tracked server-side; if rate limit reached, disable sync triggers temporarily and show user message. |
| `Disconnect` / `ErasureRecord` | `provider_account_reference`, `disconnected_at`, `revocation_request_sent` (boolean — whether server sent revocation request to provider), `revocation_ack_received` (boolean — whether provider acknowledged), `retained_imported_data_policy` (`retain_for_history` / `delete_all` — user-selectable at disconnect; default: `retain_for_history` for operational data like workout logs; `delete_all` for sensitive health-adjacent data), `erasure_request_reference` (if user also triggers account erasure, link to erasure request) | Shows "Disconnected" status; shows retained data explanation: "Your imported workout data is retained for historical reference. To delete it, submit an erasure request." | Disconnect revokes future sync: server clears `token_vault_reference` (if any) and sends revocation request (if provider supports it). No new sync triggers accepted after disconnect acknowledgment. Retained imported data stays per disconnect policy; user can change policy before disconnect. Erasure request overrides retention. No raw token or provider account details exposed. |

### 5.2 OAuth / PKCE Boundary (Mock Adapter — Deterministic Vertical Slice)

The mock adapter provides a deterministic vertical slice for integration UX: authorization start, redirect callback, consent explanation, sync trigger, sync progress, disconnect, and error/provenance states.

**Mock adapter flow (deterministic):**

1. **Connect authorization start (`POST /api/v1/integrations/connect`):**
   - User selects "Mock Fitness Provider".
   - Server creates `OAuthState` with `state`, `code_challenge`, `code_verifier` (stored server-side).
   - Server generates a mock authorization URL: `/mock/oauth/authorize?state=<state>&provider=mock_fitness&scope=read_activity`.
   - Client redirects to mock authorization page (`/mock/oauth/authorize` in frontend mock page — not a real external URL).

2. **Mock authorization page (`GET /mock/oauth/authorize` — frontend mock):**
   - Shows localized consent explanation: "Mock Fitness Provider will share: workout activities, basic measurements. [Approve] [Deny]".
   - No real provider credentials involved.

3. **Mock authorization callback (`GET /api/v1/integrations/callback?state=<state>&code=<mock_code>`):**
   - Server validates `state` against stored `OAuthState`.
   - Server exchanges mock `code` for a mock access token (server-side only; no real token).
   - Server creates `IntegrationConnection` with `provider_account_reference` = `mock_user_001`, `connection_state` = `connected`, `token_vault_reference` = `mock_vault_ref_001` (fake vault reference for demonstration — no real token stored in DB).
   - Client redirected to integration workspace.

4. **Initial sync (`POST /api/v1/integrations/{id}/sync`):**
   - Server simulates incremental sync: generates 3 mock imported activities with `provider_event_id` values `mock_event_001`, `mock_event_002`, `mock_event_003`.
   - Each event has `provider_timestamp` = 7 days ago, 3 days ago, 1 day ago (to test incremental cursor).
   - Server updates `SyncCursor` with `cursor_value` = `2026-08-09T00:00:00Z` (last event timestamp).
   - Client shows progress: "Syncing... 3 of 3 imported." Then "Synced at 10:30 AM."

5. **Incremental sync progress (`GET /api/v1/integrations/{id}/status` or via sync trigger):**
   - Client shows `last_sync_at`, `connection_state`, `sync_cursor`, `provider_rate_limit_remaining`, `provider_rate_limit_reset`.
   - If sync is triggered again within 7 days, server returns same events (duplicate detection: `provider_event_id` already exists → discard silently; no new `ImportedActivity` records created).
   - If sync is triggered after 7 days (simulated by server logic or manual trigger with new events), server generates new mock events with newer timestamps.

6. **Provider rate limit state (`GET /api/v1/integrations/{id}/status`):**
   - Mock adapter simulates rate limit: after 5 sync triggers within 1 minute, `provider_rate_limit_remaining` = 0, `provider_rate_limit_reset` = 60s from now.
   - Client shows message: "Rate limit reached — retry after [time]."

7. **Provider outage state (`GET /api/v1/integrations/{id}/status` or simulated error):**
   - Mock adapter can be configured (via admin endpoint or environment variable `MOCK_PROVIDER_OUTAGE=true`) to return `provider_outage` error.
   - Client shows `connection_state` = `limited_permission` or `expired` (depending on error mapping) and safe message: "Mock Fitness Provider is temporarily unavailable. Sync will resume automatically when the service is restored."

8. **Disconnect (`POST /api/v1/integrations/{id}/disconnect`):**
   - Client sends disconnect request.
   - Server updates `IntegrationConnection` state to `disconnected`; sends mock revocation request (`revocation_request_sent` = `true`); clears `token_vault_reference`.
   - If `retained_imported_data_policy` = `retain_for_history` (default), existing `ImportedActivity` records remain visible with `connection_state` = `disconnected` label; new sync blocked.
   - Client shows "Disconnected" status and explanation of retained data.

9. **Erasure (`POST /api/v1/privacy/forget-me` or disconnect with `delete_all` policy):**
   - If user selects `delete_all` at disconnect or triggers erasure, server deletes `ImportedActivity` records linked to the connection (or anonymizes them per erasure policy).
   - `Disconnect/ErasureRecord` created with `revocation_request_sent`, `retained_imported_data_policy` = `delete_all`, `erasure_request_reference` = linked erasure request.

### 5.3 Webhook Contract (Future — Deterministic Mock Interface Only)

Real webhooks are deferred. The webhook verification interface is defined for future use:

- **Endpoint:** `POST /api/v1/webhooks/{provider_type}` (e.g., `/api/v1/webhooks/strava` — future only with approval).
- **Verification:** Provider-specific HMAC signature verification using server-side secret (not in repo; injected via environment/secrets manager). Webhook payload verified before processing.
- **Deduplication:** `provider_event_id` + `provider_type` + `provider_account_reference` used for duplicate detection. Same event received within 24h = duplicate; same event after 24h but before latest event = replay (rejected if replay defense enabled); same event after 24h and newer than latest = new event (accepted).
- **Replay defense:** Store `provider_event_id` + `verified_at`. Reject events with `verified_at` older than the latest verified event for the same `provider_account_reference` (bounded replay window: max 24h). Events with same `provider_event_id` but newer timestamp than latest = replay attack; reject.
- **Rate limit:** Max 100 webhook events/min per provider per athlete. If exceeded, return `429` to provider (if provider supports backoff) and log `integration.rate_limit_exceeded`.
- **Cursor update:** After processing webhook events, update `SyncCursor` to the latest event timestamp or event ID.
- **Mock adapter webhook:** Not implemented in Phase 12 (no real webhooks); mock adapter uses deterministic event generation and polling-based incremental sync (`GET /api/v1/integrations/{id}/events`) instead of webhooks. The webhook verification interface is defined but not activated.

---

## 6. Localization, Accessibility, and UX Requirements

### 6.1 Bilingual Mobile-First UX for Offline States

- **Status indicators:**
  - Online: Green dot icon + text "Online" (`fa-IR`: «آنلاین» / `en-US`: "Online")
  - Offline: Yellow dot icon + text "Offline — Changes saved temporarily" (`fa-IR`: «آفلاین — تغییرات به صورت موقت ذخیره می‌شوند» / `en-US`: "Offline — Changes saved temporarily")
  - Syncing: Blue spinner + text "Syncing..." (`fa-IR`: «در حال همگام‌سازی...» / `en-US`: "Syncing...")
  - Pending count: Badge with number of pending queued operations.
  - Failed count: Badge with number of failed/dead-letter operations.
  - Conflict count: Badge with number of conflicts requiring resolution.
  - Acknowledged: Green check + text "Synced" (`fa-IR`: «همگام‌سازی شده» / `en-US`: "Synced")

- **Stale-data labeling:** Every cached read that is older than 1 hour (or has no recent server acknowledgment) shows a label: "Stale — Last updated: [timestamp]" (localized). When user reconnects, refresh updates the label.

- **Conflict resolution UI (accessibility):**
  - Focus management: When conflict card appears, focus moves to the first interactive element (`Keep Online` button) with `aria-live="polite"` announcement: "Conflict detected — choose how to resolve."
  - Keyboard navigation: `Tab` cycles through `Keep Online`, `Keep Queued`, `Edit Manually`, and `Cancel` actions.
  - Touch target: All action buttons ≥ 48×48px (design target; implementation must be tested).
  - Screen reader: `aria-label` on each action explains the consequence (e.g., "Keep online version — your queued version will be discarded.").

- **No false "saved" claim:** The UI never displays "Saved" or "Saved to server" for queued operations. It always shows "Pending" or "Queued" until the server acknowledgment (`acknowledged`) is received.

- **Queue details accessibility:** The sync status screen lists each queued operation with:
  - Operation type (localized label)
  - Entity reference (e.g., "Workout session — Aug 16")
  - Status (localized label + color-coded icon)
  - Created time (localized timestamp)
  - Retry count / attempt count
  - Error message (if failed/dead-letter) — localized safe message key (not raw server error)
  - Actions: Retry, Discard, Resolve Conflict (if applicable)

### 6.2 RTL / LTR Parity

- **Status badges and icons:** Icons must adapt to `dir` attribute; arrow icons should point in the correct direction for RTL (`←` in RTL points to the right; use logical CSS properties `margin-inline-start` etc.).
- **Mixed BiDi:** Provider names (`Strava`, `Garmin`, `Apple HealthKit`) and UUIDv7 identifiers must be isolated with `<bdi>` tags or `unicode-bidi: isolate` CSS to prevent BiDi corruption.
- **Localized timestamps:** All timestamps in sync status, queue details, and provenance labels must be formatted according to the user's `preferred_locale` and `timezone` (Jalali for `fa-IR`, Gregorian for `en-US`).
- **Localized retry states:** All retry states and error message keys must have complete `fa-IR` and `en-US` translations; no fallback to English in Persian locale.

---

## 7. Browser / Device Support Matrix (Measured, Not Generalized)

| Feature / Browser | Chrome 120+ (Desktop) | Chrome 120+ (Android) | Safari 17+ (iOS) | Firefox 120+ (Desktop) | Notes / Limitations |
|---|---|---|---|---|---|
| IndexedDB durable queue | ✅ Supported | ✅ Supported | ✅ Supported (with storage limits) | ✅ Supported | Storage quota ~50MB per origin typical; persistent storage requires user permission request (`navigator.storage.persist()`); iOS may evict after 7 days of inactivity for non-installed apps |
| Service Worker (CacheFirst static, NetworkFirst dynamic) | ✅ Supported | ✅ Supported | ✅ Supported (with some limitations) | ✅ Supported (with service worker support) | iOS Safari requires user to add to Home Screen for full PWA behavior; desktop Firefox opens PWA as tab, not standalone |
| Background Sync API | ✅ Supported | ✅ Supported | ❌ Not supported (as of 2026) | ❌ Not supported | Phase 12 must have foreground retry fallback; no universal background sync claim |
| Web Push (optional) | ✅ Supported | ✅ Supported (with VAPID) | ⚠️ Limited (iOS 16.4+ standalone installed only) | ✅ Supported | Push not reliable on iOS until added to Home Screen; deferred to P2 |
| Offline banner / network status | ✅ Tested | ✅ Tested | ✅ Tested | ✅ Tested | Manual review required; no universal claim |
| Conflict resolution UI | ✅ Implemented | ✅ Implemented | ✅ Implemented | ✅ Implemented | Accessibility tested on Chrome and Safari mobile; not certified |
| Integration adapter (mock) | ✅ Implemented | ✅ Implemented | ✅ Implemented | ✅ Implemented | Mock adapter deterministic; no real provider integration |

**Explicit exclusions:**
- No claim of universal PWA/background-sync support.
- No claim of iOS Safari background sync support.
- No claim of universal IndexedDB persistence (storage may be cleared under pressure; persistent storage request is best-effort).
- No native iOS/Android background services.
- No production wearable credentials or unapproved integrations.

---

## 8. Performance, Battery, and Storage-Quota Budget (Hypotheses to Measure)

| Dimension | Budget / Target | Measurement Method | Residual Risk |
|---|---|---|---|
| Queue memory footprint | < 5MB for 200 queued operations (average payload ~25KB) | Measure `IndexedDB` size via `navigator.storage.estimate()`; measure payload sizes | Large payloads (e.g., rich notes) may exceed budget; reject payloads > 500KB |
| Sync latency (online, small queue) | < 2s for 10 queued operations (foreground sync) | Measure time from `visibilitychange` or retry trigger to acknowledgment receipt; measure per operation latency | Network latency dominates; budget is for processing overhead only |
| Sync battery impact | < 1% battery per 30 min of active sync (with background sync disabled) | Measure battery usage via Chrome DevTools Performance Monitor; compare with and without sync active | Background sync not supported on iOS; foreground sync more battery-intensive but necessary |
| Storage quota exhaustion handling | Visible failure message; no silent data loss | Manually test quota exhaustion by filling IndexedDB with synthetic data; verify error banner and discard actions visible | Storage may be cleared by browser under pressure; persistent storage request reduces risk but does not eliminate it |
| Service worker update rollback | Queue operations survive SW update; no stranded operations | Manually test SW update during queued state; verify queue preserved and sync resumes | If SW update changes queue schema without migration, records may become unreadable; migration path required |
| Conflict resolution time | User completes resolution within 10 seconds for simple conflicts | Manual UX review; measure click counts and time to resolve | Complex conflicts (e.g., multiple edits) may take longer; design must support quick actions |

---

## 9. Integration Threat Model Updates (Phase 12 Addition)

### 9.1 Integration Threats Addressed in Phase 12 Contract

| Threat | Control | Status |
|---|---|---|
| OAuth CSRF (state/nonsense) | `state` nonce validated server-side; `redirect_url` allowlisted; `PKCE` code_challenge/code_verifier | Contract defined; mock adapter implemented |
| Token custody (no client storage) | `token_vault_reference` only; no access/refresh token in IndexedDB, localStorage, logs, URLs, or frontend | Contract enforced; mock adapter uses fake vault reference |
| Token leakage in logs/errors | Redaction middleware logs only `token_vault_reference`; no token bytes in error responses or debug logs | Contract enforced |
| Provider event duplication (replay) | Deduplication by `provider_event_id` + `provider_account_reference`; replay defense within 24h window | Contract defined; mock adapter uses deterministic event IDs |
| Provider rate limit exhaustion | `provider_rate_limit_remaining` and `provider_rate_limit_reset` tracked server-side; sync disabled temporarily when limit reached | Contract enforced; mock adapter simulates limit |
| Provider outage | `connection_state` = `expired` / `limited_permission`; safe localized message shown; queued sync triggers fail safely | Contract enforced; mock adapter can simulate outage |
| Cross-tenant provider account mix-up | `provider_account_reference` mapped to `athlete_user_id` + `organization_id` server-side; unassigned provider account access denied 403 | Contract enforced |
| Data provenance falsification | `provider_timestamp` preserved; `provider_event_id` preserved; `imported_at` preserved; `data_provenance` visible to user | Contract enforced; mock adapter provides provenance metadata |
| Webhook forgery (future) | Signature verification interface defined; HMAC verification with server-side secret; replay defense; rate limit | Contract defined; real webhook implementation deferred |
| Integration disconnect/revocation abuse | Disconnect triggers revocation request; `revocation_request_sent` tracked; `retained_imported_data_policy` user-selectable; erasure overrides retention | Contract enforced |

---

## 10. Cross-Phase Contract Reconciliation

### 10.1 Phase 07 Contracts (Baseline for Phase 12)

- **Offline boundary:** Phase 07 uses temporary in-memory preservation only (no IndexedDB). Phase 12 introduces durable IndexedDB queue (`offline_queue`, `offline_sync_receipts`, `offline_cache_metadata`, `offline_integration_state`) with explicit schema versions and migration paths.
- **Service worker:** Phase 04 defines Cache-First static, Network-First navigation, NetworkOnly for `/api/*/*`. Phase 12 updates service worker to handle queue flush (`POST /api/v1/sync/flush` or equivalent) and background sync (`'sync-sets'` tag) with feature detection and fallback.
- **PWA offline wording:** Phase 04/07 use precise wording: "Unsaved input is retained temporarily in memory. Reconnection is required to save changes." Phase 12 updates to: "Offline — queued operations will sync when reconnected. Pending: [count]. Conflicts: [count]."
- **Conflict resolution:** Phase 07 does not implement durable queue or conflict resolution. Phase 12 introduces conflict resolution UI for queued operations that cannot be auto-merged.

### 10.2 Phase 08 (Messaging) — Not Modified

Phase 12 does not implement messaging/notifications (Phase 08 deferred). The durable message queue is excluded from Phase 12 scope. Message sending remains online-only (temporary in-memory preservation only, same as Phase 07).

### 10.3 Phase 09 (Nutrition) — Not Modified

Phase 12 does not implement nutrition (Phase 09 deferred). No nutrition-related operations are added to the durable queue contract.

### 10.4 Phase 10 (Billing/Payments) — Not Modified

Phase 12 does not implement billing or payments. Integration adapter is provider-neutral and does not include payment gateway integrations. Webhook contract for future payments is defined but not implemented.

### 10.5 Phase 11 (AI) — Not Modified

Phase 12 does not implement AI. Prompt injection defense is deferred; no AI endpoints added to durable queue or integration adapter.

---

## 11. Test Strategy (Explicit)

### 11.1 Backend Tests

- **Idempotency tests:** Duplicate write with same `Idempotency-Key` returns acknowledgment; concurrent writes with same key return `409 Conflict`; replay after acknowledgment returns acknowledgment; replay after expiration (>24h) returns `404` or new acknowledgment (depending on retention policy).
- **Conflicts:** Concurrent update to same `workout_session` with different payloads produces `409 Conflict` response with server version; server version preserved; conflict response schema validated.
- **Retry and backoff:** Maximum 5 attempts; after 5 attempts, state = `dead_letter`; retry timer respects exponential backoff with jitter; `Retry-After` header present on `429`.
- **Migration:** Queue schema version mismatch handled; records with `payload_schema_version` that cannot be migrated automatically moved to `dead_letter` with `SCHEMA_MISMATCH`.
- **Integration adapter:** Mock adapter produces deterministic events; duplicate events discarded; out-of-order events within 24h window accepted; replay events (>24h and older than latest) rejected; rate limit simulated correctly.
- **Security:** Cross-tenant queued operation IDs return `403`; queued operations for suspended/revoked membership return `403` on sync; no raw health data in error responses; token/log/URL redaction verified.

### 11.2 Frontend Tests

- **IndexedDB:** Queue survives browser refresh (only if persistent storage granted); queue survives service worker update; queue does not survive process termination unless persistent; queue cleared correctly on sign-out/account-switch; storage quota error handled visibly.
- **Service worker:** Cache first for static; network first for navigation; network only for API; background sync registered with feature detection; foreground retry remains fallback; service worker update does not strand queued operations.
- **Offline/network:** Network flapping handled; online/offline/syncing status accurate; stale data label visible; no false "saved" claim before acknowledgment; retry/cancel/discard actions work; conflict resolution UI accessible.
- **Integration UX:** Connect/sync/disconnect/provenance/error states visible; no token visibility; tenant-safe mapping; duplicate events handled; rate limit message shown; disconnect clears sync and revokes future sync.
- **Localization/accessibility:** `fa-IR` RTL / `en-US` LTR parity for all new UI elements; no Arabic resources; keyboard/screen-reader operation for conflict resolution and queue details; touch targets ≥44px; no horizontal overflow.

### 11.3 Manual Review Matrix

- Browser/device combinations tested: Chrome desktop (Windows/macOS/Linux), Chrome Android (mobile), Safari iOS 17+ (mobile), Firefox desktop (Windows/macOS/Linux).
- Manual tests: Offline/online flapping, browser refresh, tab duplication, service worker update, quota error simulation, partial acknowledgment, conflict resolution, disconnect/revocation, integration sync progress.
- Performance measurements: Queue size, payload size, sync latency, battery usage (approximate via DevTools Performance Monitor).
- Security review: XSS in queued payload (sanitization), IndexedDB access via malicious script (scope isolation), stale queue replay after logout (purge verification), cross-tenant operation IDs (server-side blocking), service worker cache poisoning (SW scope same-origin, HTTPS only), webhook forgery (signature verification interface defined but not activated for mock), token leakage (redaction verification).

---

## 12. Deferred Work (Explicit)

The following items are explicitly deferred and not implemented in Phase 12:

- **Durable message queue:** Messaging remains temporary in-memory only (Phase 07 behavior). Full durable message queue requires separate design for conflict resolution, encryption, and notification integration (Phase 08+).
- **Real wearable/provider integrations:** Only mock adapter implemented. Real provider adapters (Strava, Garmin, Apple HealthKit, etc.) require separate founder approval covering provider scopes, legal terms, data residency, credential handling, and test environment.
- **Web Push notifications:** Not implemented in Phase 12. Push requires VAPID keys, server-side subscription management, and separate privacy/design review.
- **Production media storage, upload, signing, transcoding:** Mock adapter only. Real media storage requires separate security review (bucket policies, encryption at rest, signed URL TTL, ClamAV, rights verification).
- **Native iOS/Android background services:** Not implemented. Phase 12 relies on PWA service worker and foreground retry; native background services require separate architecture decision.
- **Formal accessibility certification:** Accessibility is tested at the component level for both locales; no WCAG 2.2 AA certification is claimed.
- **Device-matrix validation beyond recorded combinations:** Only Chrome desktop, Chrome Android, Safari iOS, Firefox desktop tested manually. No universal PWA/background-sync claim made.
- **Penetration testing:** Not performed in Phase 12; deferred to Phase 13 or separate security audit.
- **Production backup restore testing:** Backup and disaster recovery design remains proposed; restore testing deferred to Phase 13.

---

## 13. OpenAPI 3.1 Updates (Contract Changes)

The following new or updated endpoints are proposed for Phase 12 (not all implemented in this PR; contracts defined for future integration):

- `POST /api/v1/workout-sessions/{session_id}/sets` — updated to support `Idempotency-Key` header; response includes acknowledgment or conflict.
- `POST /api/v1/workout-sessions/{session_id}/substitutions` — updated similarly.
- `POST /api/v1/workout-sessions/{session_id}/feedback-flags` — updated similarly.
- `POST /api/v1/athletes/{id}/body-metrics` — updated similarly.
- `GET /api/v1/sync/status` — new: returns queued operation counts, sync state per operation, last sync time, conflict count, failed count, dead-letter count.
- `POST /api/v1/sync/flush` — new: triggers foreground sync; accepts queued operations; returns acknowledgment results.
- `GET /api/v1/sync/receipt/{client_operation_id}` — new: returns durable receipt (`acknowledged`, `conflict`, `failed`, `dead_letter`, `discarded`).
- `POST /api/v1/integrations/connect` — new: starts OAuth/PKCE authorization (mock adapter only).
- `GET /api/v1/integrations/callback` — new: OAuth callback endpoint (mock adapter only).
- `POST /api/v1/integrations/{id}/sync` — new: triggers incremental sync (mock adapter only).
- `GET /api/v1/integrations/{id}/status` — new: returns connection state, sync cursor, last sync time, rate limit state, provenance information.
- `GET /api/v1/integrations/{id}/events` — new: returns imported events (poll-based incremental sync for mock adapter; webhook interface deferred).
- `POST /api/v1/integrations/{id}/disconnect` — new: disconnects integration; triggers revocation; updates retention policy.
- `GET /api/v1/integrations/{id}/provenance` — new: returns data provenance for imported measurements.
- `POST /api/v1/webhooks/{provider_type}` — new: webhook verification endpoint (contract only; not activated for mock adapter).

**Note:** The actual OpenAPI file (`docs/OPENAPI.yaml`) is updated with selected endpoint contracts (not all proposed endpoints fully implemented in code for Phase 12). The contract document (`PHASE-12-DURABLE-OFFLINE-INTEGRATIONS-CONTRACTS.md`) defines the full contract for future phases.
