import type { Locale } from "../i18n/config";
import { request } from "./client";

/**
 * Phase 07 athlete API — typed client for the athlete execution and progress
 * endpoints. Authentication is cookie-managed; this client stores no tokens and
 * performs no durable offline queueing (Phase 12).
 */

export type SessionStatus =
  | "scheduled"
  | "in_progress"
  | "completed"
  | "skipped"
  | "modified";

export interface SetPrescriptionView {
  set_index: number;
  target_reps: string;
  target_load?: string | null;
  target_rpe?: string | null;
}

export interface WorkoutItemView {
  exercise_id: string;
  name: string;
  group_key?: string | null;
  segment?: string | null;
  rest_seconds_between_sets?: number | null;
  coach_notes?: string | null;
  prescriptions: SetPrescriptionView[];
}

export interface WorkoutView {
  workout_id?: string | null;
  title: string;
  estimated_minutes?: number | null;
  sequence_order?: number | null;
  items: WorkoutItemView[];
}

export interface SetLogView {
  id: string;
  exercise_id: string;
  set_index: number;
  actual_reps: number;
  actual_load_kg: string;
  actual_rpe?: string | null;
  is_completed: boolean;
  created_at: string;
}

export interface WorkoutSessionView {
  id: string;
  organization_id: string;
  program_assignment_id: string;
  athlete_user_id: string;
  scheduled_date: string;
  status: SessionStatus;
  started_at?: string | null;
  completed_at?: string | null;
  session_rpe?: number | null;
  fatigue_score?: number | null;
  athlete_notes?: string | null;
  skip_or_modify_reason?: string | null;
  workouts: WorkoutView[];
  set_logs: SetLogView[];
}

export interface TodayWorkout {
  session_id?: string | null;
  assignment_id: string;
  title?: string | null;
  status: SessionStatus;
  workout: WorkoutView;
}

export interface TodayResponse {
  date: string;
  scheduled_workouts: TodayWorkout[];
}

export interface StartSessionInput {
  program_assignment_id: string;
  scheduled_date: string;
}

export interface CompleteSessionInput {
  session_rpe?: number;
  fatigue_score?: number;
  athlete_notes?: string;
  skip_or_modify_reason?: string;
}

export interface CreateSetLogInput {
  exercise_id: string;
  set_index: number;
  actual_reps: number;
  actual_load_kg: number;
  actual_rpe?: number | null;
  is_completed?: boolean;
  note?: string;
}

export interface SubstitutionInput {
  original_exercise_id: string;
  substituted_exercise_id: string;
  reason: "equipment_unavailable" | "discomfort" | "preference" | "other";
  note?: string;
}

export type FeedbackFlagType =
  | "joint_pain"
  | "muscle_strain"
  | "dizziness"
  | "severe_fatigue";

export interface FeedbackFlagInput {
  flag_type: FeedbackFlagType;
  anatomical_location: string;
  severity: "mild" | "moderate" | "severe";
  details: string;
}

export interface BodyMetricView {
  id: string;
  metric_type: string;
  value: string;
  unit: string;
  recorded_at: string;
  created_at: string;
}

export interface ProgressPhotoView {
  id: string;
  athlete_user_id: string;
  photo_type: string;
  captured_at?: string | null;
  signed_url?: string | null;
  thumbnail_signed_url?: string | null;
  created_at: string;
}

export interface ConsentView {
  id: string;
  athlete_user_id: string;
  grantee_user_id: string;
  consent_type: string;
  is_granted: boolean;
  granted_at?: string | null;
  revoked_at?: string | null;
}

export interface MeResponse {
  user: {
    id: string;
    email?: string;
    display_name?: string;
    preferred_locale?: string;
    preferred_unit?: "kg" | "lbs";
  };
  memberships: Array<{ id: string; organization_id: string; role: string; status: string }>;
}

export function getMe(locale: Locale) {
  return request<MeResponse>("auth/me", { locale });
}

// --- Athlete Today + Session Lifecycle ------------------------------------ //
export function getTodayWorkout(locale: Locale) {
  return request<TodayResponse>("athlete/today", { locale });
}

export function startSession(input: StartSessionInput, locale: Locale) {
  return request<WorkoutSessionView>("workout-sessions", {
    method: "POST",
    locale,
    json: input,
  });
}

export function getSession(sessionId: string, locale: Locale) {
  return request<WorkoutSessionView>(`workout-sessions/${sessionId}`, { locale });
}

export function completeSession(
  sessionId: string,
  input: CompleteSessionInput,
  locale: Locale,
) {
  return request<WorkoutSessionView>(`workout-sessions/${sessionId}`, {
    method: "POST",
    locale,
    json: input,
  });
}

export function logSet(sessionId: string, input: CreateSetLogInput, locale: Locale) {
  return request<SetLogView>(`workout-sessions/${sessionId}/set-logs`, {
    method: "POST",
    locale,
    json: input,
  });
}

export function substitute(sessionId: string, input: SubstitutionInput, locale: Locale) {
  return request<{ id: string; reason: string }>(
    `workout-sessions/${sessionId}/substitutions`,
    { method: "POST", locale, json: input },
  );
}

export function addFeedbackFlag(
  sessionId: string,
  input: FeedbackFlagInput,
  locale: Locale,
) {
  return request<{ id: string; flag_type: string; severity: string; is_resolved: boolean }>(
    `workout-sessions/${sessionId}/feedback-flags`,
    { method: "POST", locale, json: input },
  );
}

// --- Progress metrics ------------------------------------------------------ //
export function listBodyMetrics(athleteId: string, locale: Locale) {
  return request<{ metrics: BodyMetricView[] }>(`athletes/${athleteId}/body-metrics`, {
    locale,
  });
}

export function createBodyMetric(
  athleteId: string,
  input: { metric_type: string; value: string; unit: string; recorded_at: string },
  locale: Locale,
) {
  return request<BodyMetricView>(`athletes/${athleteId}/body-metrics`, {
    method: "POST",
    locale,
    json: input,
  });
}

// --- Progress photos ------------------------------------------------------- //
export function listProgressPhotos(athleteId: string, locale: Locale) {
  return request<{ photos: ProgressPhotoView[] }>(`athletes/${athleteId}/progress/photos`, {
    locale,
  });
}

export function uploadProgressPhoto(
  athleteId: string,
  form: FormData,
  locale: Locale,
) {
  return request<ProgressPhotoView>(`athletes/${athleteId}/progress/photos`, {
    method: "POST",
    locale,
    body: form,
  });
}

// --- Consents -------------------------------------------------------------- //
export function listConsents(athleteId: string, locale: Locale) {
  return request<{ consents: ConsentView[] }>(`consents?athlete_id=${athleteId}`, {
    locale,
  });
}

export function grantConsent(
  input: {
    athlete_user_id: string;
    grantee_user_id: string;
    consent_type: string;
    is_granted?: boolean;
  },
  locale: Locale,
) {
  return request<ConsentView>("consents", { method: "POST", locale, json: input });
}

export function revokeConsent(
  params: { athlete_id: string; grantee_id: string; consent_type: string },
  locale: Locale,
) {
  const qs = new URLSearchParams(params).toString();
  return request<void>(`consents?${qs}`, { method: "DELETE", locale });
}
