/**
 * Phase 12 — Durable Offline Operation Record Schema (IndexedDB `offline_queue`).
 *
 * Type definitions mirroring the offline sync contract documented in
 * docs/reports/PHASE-12-DURABLE-OFFLINE-INTEGRATIONS-CONTRACTS.md §3.1
 * (Operation Record Schema). This module is the shared client-side source of
 * truth for queued-operation shapes consumed by the offline queue, sync
 * engine, and conflict-resolution UI.
 *
 * Sibling stores (per contract §Storage): `offline_sync_receipts` keeps durable
 * receipts without raw payloads; queue records carry a SHA-256 `integrity_hash`
 * over key fields + payload to detect tampering. Records are purged on
 * sign-out, account switch, tenant change, or membership revocation.
 */

/** Schema version of the `offline_queue` object store (v2 per Phase 12 migration). */
export const OFFLINE_QUEUE_SCHEMA_VERSION = 2;

/** Client-originated operation kinds a queued record may represent. */
export type OfflineOperationType =
  | "CREATE_SET_LOG"
  | "UPDATE_SESSION"
  | "CREATE_SUBSTITUTION"
  | "CREATE_FEEDBACK_FLAG"
  | "CREATE_BODY_METRIC"
  | "TRIGGER_INTEGRATION_SYNC"
  | "DISCONNECT_INTEGRATION";

/** Domain entities an offline operation may target. */
export type OfflineEntityType =
  | "workout_session"
  | "set_log"
  | "feedback_flag"
  | "body_metric"
  | "substitution"
  | "integration_connection";

/** Lifecycle states of a queued operation (see contract §3.4 for UI rules). */
export type QueueRecordState =
  | "pending"
  | "in_flight"
  | "acknowledged"
  | "conflict"
  | "failed"
  | "dead_letter"
  | "discarded";

/** Server/client error codes safe to persist on a queue record. */
export type QueueErrorCode =
  | "NETWORK_TIMEOUT"
  | "SCHEMA_MISMATCH"
  | "AUTHZ_DENIED"
  | "RATE_LIMITED"
  | "CONFLICT";

/**
 * Durable offline operation record stored in IndexedDB `offline_queue`.
 *
 * Identity/idempotency: `idempotency_key` (not stored) is derived as
 * SHA-256(actor_user_id + ":" + organization_id + ":" + operation_type + ":"
 * + entity_type + ":" + entity_id + ":" + client_operation_id) per contract
 * §3.2; duplicate `client_operation_id` submissions are discarded server-side.
 */
export interface QueueRecord {
  /** UUIDv7 generated client-side; unique per operation submission. */
  client_operation_id: string;
  operation_type: OfflineOperationType;
  entity_type: OfflineEntityType;
  entity_id: string;
  organization_id: string;
  actor_user_id: string;
  /** Operation-specific payload; shape governed by `payload_schema_version`. */
  payload: Record<string, unknown>;
  payload_schema_version: string;
  /** Client local time at enqueue; converted to UTC on sync. */
  created_at: string;
  updated_at: string;
  last_attempt_at: string | null;
  attempt_count: number;
  state: QueueRecordState;
  server_version_or_etag: string | null;
  error_code: QueueErrorCode | null;
  /** Localization key for a user-safe error message; never raw provider text. */
  safe_error_message_key: string | null;
  /** "sha256:..." over client_operation_id, entity_type, entity_id, payload_schema_version, actor_user_id, payload. */
  integrity_hash: string;
  /** Suppress retry attempts until this timestamp (exponential backoff + jitter). */
  retry_backoff_until: string | null;
}

/** Durable receipt record stored in IndexedDB `offline_sync_receipts` (no raw payload). */
export interface SyncReceiptRecord {
  client_operation_id: string;
  entity_id: string;
  state: Extract<
    QueueRecordState,
    "acknowledged" | "conflict" | "failed" | "dead_letter" | "discarded"
  >;
  server_version_or_etag: string | null;
  error_code: QueueErrorCode | null;
  updated_at: string;
}
