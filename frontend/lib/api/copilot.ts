import type { Locale } from "../i18n/config";
import { request } from "./client";

/**
 * Phase 11 — Governed AI Copilot client.
 *
 * The Copilot is a drafting assistant for professional users. This client
 * never contains provider credentials and never calls any model provider
 * directly; all generation happens server-side behind authorization, quota,
 * and policy gates. Draft state changes (approve/reject/edit) are explicit
 * user actions initiated from the review UI.
 */

export type CopilotCapabilityId =
  | "summarize_progress"
  | "draft_check_in"
  | "suggest_program_adjustment";

export type CopilotRunStatus =
  | "queued"
  | "running"
  | "succeeded"
  | "failed"
  | "cancelled"
  | "expired";

export type CopilotOutputStatus =
  | "draft"
  | "edited"
  | "approved"
  | "rejected"
  | "quarantined"
  | "expired";

export interface CopilotCapability {
  id: CopilotCapabilityId;
  output_schema: string;
  requires_human_review: boolean;
  enabled: boolean;
  disabled_reason?: string;
  label: Record<Locale, string>;
}

export interface CopilotCapabilitiesResponse {
  feature: { enabled: boolean; disabled_reason?: string };
  policy_version: string;
  provider: { provider_slug: string; provider_enabled: boolean; model_identifier: string };
  capabilities: CopilotCapability[];
  limits: {
    rate_limit_per_minute: number;
    daily_run_quota_per_actor: number;
    daily_run_quota_per_org: number;
    retention_days: number;
  };
  prohibited_notice_key: string;
}

export interface CopilotSourceReference {
  id: string;
  run_id?: string;
  source_type: "workout_session" | "set_log" | "feedback_flag" | "program_assignment" | "exercise";
  source_id: string;
  descriptor: string;
  ordinal: number;
  record_url?: string;
}

export interface CopilotOutput {
  id: string;
  schema_name: string;
  schema_version: number;
  validation_status: "valid" | "invalid";
  status: CopilotOutputStatus;
  payload: Record<string, unknown> | null;
  was_edited: boolean;
  reviewed_by_id?: string | null;
  reviewed_at?: string | null;
  review_note?: string;
}

export interface CopilotRun {
  id: string;
  capability: CopilotCapabilityId;
  generation_language: Locale;
  status: CopilotRunStatus;
  athlete_id: string;
  policy_version: string;
  provider_slug: string;
  model_identifier: string;
  attempt_count: number;
  duration_ms: number;
  cost_micro_usd: number;
  error_code: string;
  fallback_applied: boolean;
  created_at: string;
  completed_at?: string | null;
  expires_at?: string | null;
  regenerated_from_id?: string | null;
  output_status?: CopilotOutputStatus | null;
  context?: {
    payload: Record<string, unknown> | null;
    limitations: string[];
    omissions: string[];
  } | null;
  output: CopilotOutput | null;
  sources: CopilotSourceReference[];
  actions?: {
    can_cancel: boolean;
    can_regenerate: boolean;
    can_edit: boolean;
    can_approve: boolean;
    can_reject: boolean;
    can_report: boolean;
  };
  ai_generated: boolean;
  requires_human_review: boolean;
  replayed?: boolean;
}

export interface CopilotRunListResponse {
  runs: CopilotRun[];
  count: number;
  retention_days: number;
}

export interface CreateRunInput {
  capability: CopilotCapabilityId;
  athleteId: string;
  generationLanguage: Locale;
  periodDays?: number;
  notes?: string;
}

function qs(orgId: string): string {
  return `org_id=${encodeURIComponent(orgId)}`;
}

export function listCopilotCapabilities(orgId: string, locale: Locale) {
  return request<CopilotCapabilitiesResponse>(`copilot/capabilities?${qs(orgId)}`, { locale });
}

export function listCopilotRuns(orgId: string, locale: Locale) {
  return request<CopilotRunListResponse>(`copilot/runs?${qs(orgId)}`, { locale });
}

export function createCopilotRun(
  orgId: string,
  input: CreateRunInput,
  idempotencyKey: string,
  locale: Locale,
) {
  const parameters: Record<string, unknown> = {};
  if (input.periodDays) parameters.period_days = input.periodDays;
  if (input.notes && input.notes.trim()) parameters.notes = input.notes.trim();
  return request<CopilotRun>(`copilot/runs?${qs(orgId)}`, {
    method: "POST",
    locale,
    idempotencyKey,
    json: {
      capability: input.capability,
      athlete_id: input.athleteId,
      generation_language: input.generationLanguage,
      idempotency_key: idempotencyKey,
      ...(Object.keys(parameters).length > 0 ? { parameters } : {}),
    },
  });
}

export function getCopilotRun(orgId: string, runId: string, locale: Locale) {
  return request<CopilotRun>(`copilot/runs/${encodeURIComponent(runId)}?${qs(orgId)}`, { locale });
}

export function cancelCopilotRun(orgId: string, runId: string, locale: Locale) {
  return request<CopilotRun>(`copilot/runs/${encodeURIComponent(runId)}/cancel?${qs(orgId)}`, {
    method: "POST",
    locale,
    json: {},
  });
}

export function regenerateCopilotRun(orgId: string, runId: string, locale: Locale) {
  return request<CopilotRun>(`copilot/runs/${encodeURIComponent(runId)}/regenerate?${qs(orgId)}`, {
    method: "POST",
    locale,
    json: {},
  });
}

export function editCopilotOutput(
  orgId: string,
  runId: string,
  payload: Record<string, unknown>,
  locale: Locale,
) {
  return request<CopilotRun>(`copilot/runs/${encodeURIComponent(runId)}/output?${qs(orgId)}`, {
    method: "PATCH",
    locale,
    json: { payload },
  });
}

export function reviewCopilotOutput(
  orgId: string,
  runId: string,
  action: "approve" | "reject",
  note: string,
  locale: Locale,
) {
  return request<CopilotRun>(
    `copilot/runs/${encodeURIComponent(runId)}/output/${action}?${qs(orgId)}`,
    { method: "POST", locale, json: { note } },
  );
}

export function reportCopilotRun(
  orgId: string,
  runId: string,
  reportType: "unsafe" | "incorrect" | "privacy" | "hallucinated_source" | "other",
  detail: string,
  locale: Locale,
) {
  return request<CopilotRun>(
    `copilot/runs/${encodeURIComponent(runId)}/report?${qs(orgId)}`,
    { method: "POST", locale, json: { report_type: reportType, detail } },
  );
}

export interface ProgramAssignmentSummary {
  id: string;
  athlete_user_id: string;
  status: string;
  start_date: string;
}

interface ProgramAssignmentListResponse {
  assignments: ProgramAssignmentSummary[];
}

/**
 * Helper for the coach's context picker: lists program assignments the caller
 * is authorized to see (server-scoped to assigned athletes for coaches).
 */
export function listAuthorizedAssignments(orgId: string, locale: Locale) {
  return request<ProgramAssignmentListResponse>(`program-assignments?${qs(orgId)}`, { locale });
}
