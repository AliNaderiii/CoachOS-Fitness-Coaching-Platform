import { request } from "./client";
import type { Locale } from "../i18n/config";

export interface ExerciseTranslation {
  locale: Locale;
  name: string;
  instructions: string;
  coaching_cues: string[];
  common_mistakes: string[];
  safety_notes?: string | null;
}

export interface ExerciseSummary {
  id: string;
  organization_id: string | null;
  movement_pattern: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  primary_muscles: string[];
  equipment_required: string[];
  translations: ExerciseTranslation[];
}

export interface ExerciseListResponse {
  exercises: ExerciseSummary[];
  count: number;
}

export interface ExerciseFilters {
  q?: string;
  locale?: Locale;
  muscle?: string;
  equipment?: string;
  movementPattern?: string;
}

export interface SetPrescriptionInput {
  set_index: number;
  target_reps: string;
  target_load?: string;
  target_rpe?: number;
  target_rir?: number;
  tempo?: string;
}

export interface ProgramInput {
  org_id: string;
  title: string;
  description?: string;
  target_goal: "hypertrophy" | "strength" | "fat_loss" | "endurance" | "general_fitness";
  is_template: boolean;
  phases: unknown[];
}

function searchParams(orgId: string, filters: ExerciseFilters): string {
  const params = new URLSearchParams({ org_id: orgId });
  if (filters.q) params.set("q", filters.q);
  if (filters.locale) params.set("locale", filters.locale);
  if (filters.muscle) params.set("muscle", filters.muscle);
  if (filters.equipment) params.set("equipment", filters.equipment);
  if (filters.movementPattern) params.set("movement_pattern", filters.movementPattern);
  return params.toString();
}

export function listExercises(orgId: string, filters: ExerciseFilters = {}) {
  return request<ExerciseListResponse>(`exercises?${searchParams(orgId, filters)}`, {
    locale: filters.locale,
  });
}

export function createProgram(input: ProgramInput, locale: Locale) {
  return request<{ id: string; version: number }>("programs", {
    method: "POST",
    locale,
    json: input,
  });
}

export function cloneProgram(
  programId: string,
  input: { title?: string; is_template?: boolean },
  locale: Locale,
) {
  return request<{ id: string; version: number }>(`programs/${programId}/clone`, {
    method: "POST",
    locale,
    json: input,
  });
}
