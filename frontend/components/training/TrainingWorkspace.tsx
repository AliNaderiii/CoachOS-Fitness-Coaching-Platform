"use client";

import React, { useEffect, useMemo, useState } from "react";
import { ChevronDown, ChevronUp, Dumbbell, Plus, Save } from "lucide-react";
import { useTranslation } from "@/components/layout/DirectionProvider";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { ApiError } from "@/lib/api/client";
import {
  createProgram,
  listExercises,
  listOrganizations,
  type ExerciseSummary,
  type OrganizationContext,
  type ProgramInput,
} from "@/lib/api/training";

type LoadState = "loading" | "ready" | "empty" | "error" | "unauthorized";
type SaveState = "idle" | "saving" | "success" | "error" | "unauthorized";

function errorState(error: unknown): "error" | "unauthorized" {
  return error instanceof ApiError && (error.status === 401 || error.status === 403)
    ? "unauthorized"
    : "error";
}

export function TrainingWorkspace() {
  const { locale, t } = useTranslation();
  const [organizations, setOrganizations] = useState<OrganizationContext[]>([]);
  const [activeOrgId, setActiveOrgId] = useState("");
  const [orgState, setOrgState] = useState<LoadState>("loading");
  const [catalogState, setCatalogState] = useState<LoadState>("loading");
  const [exercises, setExercises] = useState<ExerciseSummary[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [query, setQuery] = useState("");
  const [equipment, setEquipment] = useState("all");
  const [orgRetryVersion, setOrgRetryVersion] = useState(0);
  const [catalogRetryVersion, setCatalogRetryVersion] = useState(0);
  const [programTitle, setProgramTitle] = useState("");
  const [sets, setSets] = useState(4);
  const [reps, setReps] = useState("8");
  const [tempo, setTempo] = useState("3-1-1-0");
  const [rpe, setRpe] = useState("8");
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [savedProgramId, setSavedProgramId] = useState("");

  useEffect(() => {
    let active = true;
    setOrgState("loading");
    listOrganizations(locale)
      .then(({ organizations: available }) => {
        if (!active) return;
        setOrganizations(available);
        if (available.length === 0) {
          setActiveOrgId("");
          setOrgState("empty");
          return;
        }
        setActiveOrgId((current) =>
          available.some((organization) => organization.id === current)
            ? current
            : available[0].id,
        );
        setOrgState("ready");
      })
      .catch((error: unknown) => {
        if (active) setOrgState(errorState(error));
      });
    return () => {
      active = false;
    };
  }, [locale, orgRetryVersion]);

  useEffect(() => {
    if (!activeOrgId || orgState !== "ready") return;
    let active = true;
    setCatalogState("loading");
    setSaveState("idle");
    listExercises(activeOrgId, {
      q: query || undefined,
      equipment: equipment === "all" ? undefined : equipment,
      locale,
    })
      .then(({ exercises: available }) => {
        if (!active) return;
        setExercises(available);
        setSelectedId((current) =>
          available.some((exercise) => exercise.id === current)
            ? current
            : available[0]?.id || "",
        );
        setCatalogState(available.length === 0 ? "empty" : "ready");
      })
      .catch((error: unknown) => {
        if (!active) return;
        setExercises([]);
        setSelectedId("");
        setCatalogState(errorState(error));
      });
    return () => {
      active = false;
    };
  }, [activeOrgId, catalogRetryVersion, equipment, locale, orgState, query]);

  const selected = useMemo(
    () => exercises.find((exercise) => exercise.id === selectedId) || null,
    [exercises, selectedId],
  );

  const localizedName = (exercise: ExerciseSummary) =>
    exercise.translations.find((translation) => translation.locale === locale)?.name ||
    exercise.translations[0]?.name ||
    exercise.id;

  const alternateName = (exercise: ExerciseSummary) =>
    exercise.translations.find((translation) => translation.locale !== locale)?.name || "";


  const saveProgram = async () => {
    if (!activeOrgId || !selected || !programTitle.trim()) return;
    setSaveState("saving");
    setSavedProgramId("");
    const prescriptions = Array.from({ length: sets }, (_, index) => ({
      set_index: index + 1,
      target_reps: reps,
      target_rpe: Number(rpe),
      tempo,
    }));
    const input: ProgramInput = {
      org_id: activeOrgId,
      title: programTitle.trim(),
      target_goal: "strength",
      is_template: false,
      phases: [
        {
          name: t("training.phase_one"),
          sequence_order: 1,
          duration_weeks: 1,
          weeks: [
            {
              week_number: 1,
              days: [
                {
                  day_number: 1,
                  title: t("training.upper_day"),
                  workouts: [
                    {
                      title: programTitle.trim(),
                      sequence_order: 1,
                      items: [
                        {
                          exercise_id: selected.id,
                          sequence_order: 1,
                          group_key: "A1",
                          segment: "main",
                          rest_seconds_between_sets: 90,
                          prescriptions,
                        },
                      ],
                    },
                  ],
                },
              ],
            },
          ],
        },
      ],
    };
    try {
      const created = await createProgram(input, locale);
      setSavedProgramId(created.id);
      setSaveState("success");
    } catch (error: unknown) {
      setSaveState(errorState(error));
    }
  };

  return (
    <div className="space-y-6" data-testid="training-workspace">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <Badge variant="success">{t("training.phase_badge")}</Badge>
            <span className="text-xs text-brand-text-muted">{t("training.coach_owner_only")}</span>
          </div>
          <h1 className="text-2xl font-bold text-brand-text sm:text-3xl">{t("training.title")}</h1>
          <p className="mt-1 max-w-2xl text-sm text-brand-text-muted">{t("training.description")}</p>
        </div>
        <Button
          onClick={saveProgram}
          aria-label={t("training.save_program")}
          className="min-h-touch"
          isLoading={saveState === "saving"}
          disabled={!activeOrgId || !selected || !programTitle.trim()}
        >
          <Save aria-hidden="true" className="h-4 w-4" />
          {saveState === "saving" ? t("training.saving") : t("training.save_program")}
        </Button>
      </header>

      {saveState === "success" && (
        <div role="status" className="rounded-lg border border-emerald-700 bg-emerald-700/20 p-3 text-sm">
          {t("training.saved_status")} <bdi>{savedProgramId}</bdi>
        </div>
      )}
      {(saveState === "error" || saveState === "unauthorized") && (
        <div role="alert" className="rounded-lg border border-red-700 bg-red-900/20 p-3 text-sm">
          {t(saveState === "unauthorized" ? "training.unauthorized" : "training.save_error")}
        </div>
      )}

      {orgState === "loading" && <StateCard message={t("training.loading_context")} />}
      {orgState === "empty" && <StateCard message={t("training.no_organization")} />}
      {(orgState === "error" || orgState === "unauthorized") && (
        <StateCard
          message={t(orgState === "unauthorized" ? "training.unauthorized" : "training.context_error")}
          retryLabel={t("training.retry")}
          onRetry={() => setOrgRetryVersion((version) => version + 1)}
        />
      )}

      {orgState === "ready" && (
        <>
          <label className="flex max-w-sm flex-col gap-1 text-sm text-brand-text-muted">
            {t("training.active_organization")}
            <select
              value={activeOrgId}
              onChange={(event) => setActiveOrgId(event.target.value)}
              className="min-h-touch rounded-lg border border-obsidian-700 bg-obsidian-800 px-3 text-brand-text"
            >
              {organizations.map((organization) => (
                <option key={organization.id} value={organization.id}>{organization.name}</option>
              ))}
            </select>
          </label>

          <div className="grid gap-5 xl:grid-cols-12">
            <Card variant="elevated" className="space-y-4 xl:col-span-4" aria-label={t("training.outline")}>
              <div className="flex items-center justify-between">
                <h2 className="font-semibold text-brand-text">{t("training.outline")}</h2>
                <Button variant="ghost" size="sm" aria-label={t("training.add_phase")}>
                  <Plus aria-hidden="true" className="h-4 w-4" />
                  {t("training.add_phase")}
                </Button>
              </div>
              <div role="tree" aria-label={t("training.outline")} className="space-y-2 text-sm">
                <div role="treeitem" aria-expanded="true" aria-selected="false" className="rounded-lg border border-obsidian-700 bg-obsidian-800 p-3">
                  <strong>{t("training.phase_one")}</strong>
                  <div role="group" className="mt-2 border-s border-obsidian-600 ps-3">
                    <div role="treeitem" aria-expanded="true" aria-selected="false">
                      {t("training.week_one")}
                      <div role="group" className="mt-2 ps-3">
                        <button type="button" role="treeitem" aria-selected="true" className="min-h-touch w-full rounded-md bg-emerald-700/30 px-3 py-2 text-start text-emerald-300">
                          {t("training.upper_day")}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <p className="text-xs text-brand-text-muted">{t("training.keyboard_hint")}</p>
            </Card>

            <section className="space-y-5 xl:col-span-8" aria-label={t("training.editor")}>
              <Card variant="elevated" className="space-y-4">
                <div className="flex flex-col gap-3 md:flex-row md:items-end">
                  <Input label={t("training.search_label")} value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t("training.search_placeholder")} type="search" />
                  <label className="flex min-w-44 flex-col gap-1 text-sm text-brand-text-muted">
                    {t("training.equipment")}
                    <select value={equipment} onChange={(event) => setEquipment(event.target.value)} className="min-h-touch rounded-lg border border-obsidian-700 bg-obsidian-800 px-3 text-brand-text">
                      <option value="all">{t("training.all_equipment")}</option>
                      <option value="barbell">{t("training.barbell")}</option>
                      <option value="dumbbell">{t("training.dumbbell")}</option>
                      <option value="cable">{t("training.cable")}</option>
                    </select>
                  </label>
                </div>

                {catalogState === "loading" && <p role="status">{t("training.loading_catalog")}</p>}
                {catalogState === "empty" && <p role="status">{t("training.empty_catalog")}</p>}
                {(catalogState === "error" || catalogState === "unauthorized") && (
                  <StateCard
                    message={t(catalogState === "unauthorized" ? "training.unauthorized" : "training.catalog_error")}
                    retryLabel={t("training.retry")}
                    onRetry={() => setCatalogRetryVersion((version) => version + 1)}
                  />
                )}
                {catalogState === "ready" && (
                  <>
                    <p aria-live="polite" className="text-xs text-brand-text-muted">
                      {t("training.results")}: <bdi>{exercises.length}</bdi>
                    </p>
                    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                      {exercises.map((exercise) => (
                        <button
                          key={exercise.id}
                          type="button"
                          aria-pressed={selectedId === exercise.id}
                          onClick={() => { setSelectedId(exercise.id); setSaveState("idle"); }}
                          className="min-h-touch rounded-lg border border-obsidian-700 bg-obsidian-800 p-3 text-start hover:border-emerald-600 aria-pressed:border-emerald-500"
                        >
                          <Dumbbell aria-hidden="true" className="mb-2 h-5 w-5 text-emerald-400" />
                          <strong className="block text-sm text-brand-text">{localizedName(exercise)}</strong>
                          <span className="mt-1 block text-xs text-brand-text-muted" dir="auto">{alternateName(exercise)}</span>
                        </button>
                      ))}
                    </div>
                  </>
                )}
              </Card>

              <Card variant="elevated" className="space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <h2 className="font-semibold text-brand-text">{t("training.prescription")}</h2>
                    <p className="text-sm text-emerald-300">{selected ? localizedName(selected) : t("training.select_exercise")}</p>
                  </div>
                  <div className="flex gap-1" aria-label={t("training.reorder")}>
                    <Button variant="ghost" size="sm" className="min-h-touch min-w-touch" aria-label={t("training.move_up")}><ChevronUp aria-hidden="true" className="h-4 w-4" /></Button>
                    <Button variant="ghost" size="sm" className="min-h-touch min-w-touch" aria-label={t("training.move_down")}><ChevronDown aria-hidden="true" className="h-4 w-4" /></Button>
                  </div>
                </div>
                <Input label={t("training.program_title")} value={programTitle} onChange={(event) => { setProgramTitle(event.target.value); setSaveState("idle"); }} required />
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  <Input label={t("training.sets")} type="number" min={1} max={20} value={sets} onChange={(event) => setSets(Number(event.target.value))} />
                  <Input label={t("training.reps")} value={reps} onChange={(event) => setReps(event.target.value)} />
                  <Input label={t("training.tempo")} value={tempo} onChange={(event) => setTempo(event.target.value)} />
                  <Input label={t("training.rpe")} type="number" min={1} max={10} step="0.5" value={rpe} onChange={(event) => setRpe(event.target.value)} />
                </div>
                <div className="rounded-lg bg-obsidian-800 p-3 text-sm text-brand-text-muted">
                  <span>{t("training.preview")}: </span>
                  <bdi className="text-brand-text">{sets} × {reps} · {tempo} · RPE {rpe}</bdi>
                </div>
              </Card>
            </section>
          </div>
        </>
      )}
    </div>
  );
}

function StateCard({ message, retryLabel, onRetry }: { message: string; retryLabel?: string; onRetry?: () => void }) {
  return (
    <Card variant="elevated" role={onRetry ? "alert" : "status"} className="space-y-3">
      <p>{message}</p>
      {onRetry && retryLabel && <Button variant="outline" onClick={onRetry}>{retryLabel}</Button>}
    </Card>
  );
}
