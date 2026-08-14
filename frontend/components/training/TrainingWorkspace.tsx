"use client";

import React, { useMemo, useState } from "react";
import { ChevronDown, ChevronUp, Dumbbell, Plus, Save } from "lucide-react";
import { useTranslation } from "@/components/layout/DirectionProvider";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { normalizePersianSearch } from "@/lib/i18n/normalizer";

interface CatalogExercise {
  id: string;
  en: string;
  fa: string;
  pattern: "squat" | "horizontal_push" | "horizontal_pull";
  equipment: "barbell" | "dumbbell" | "cable";
  muscle: "quadriceps" | "chest" | "back";
  difficulty: "beginner" | "intermediate";
}

const CATALOG: CatalogExercise[] = [
  {
    id: "exercise-back-squat",
    en: "Barbell Back Squat",
    fa: "اسکوات پشت با هالتر",
    pattern: "squat",
    equipment: "barbell",
    muscle: "quadriceps",
    difficulty: "intermediate",
  },
  {
    id: "exercise-chest-press",
    en: "Dumbbell Chest Press",
    fa: "پرس سینه دمبل",
    pattern: "horizontal_push",
    equipment: "dumbbell",
    muscle: "chest",
    difficulty: "beginner",
  },
  {
    id: "exercise-row",
    en: "Seated Cable Row",
    fa: "قایقی سیم‌کش",
    pattern: "horizontal_pull",
    equipment: "cable",
    muscle: "back",
    difficulty: "beginner",
  },
];

export function TrainingWorkspace() {
  const { locale, t } = useTranslation();
  const [query, setQuery] = useState("");
  const [equipment, setEquipment] = useState("all");
  const [selected, setSelected] = useState<CatalogExercise>(CATALOG[1]);
  const [sets, setSets] = useState(4);
  const [reps, setReps] = useState("8");
  const [tempo, setTempo] = useState("3-1-1-0");
  const [rpe, setRpe] = useState("8");
  const [saved, setSaved] = useState(false);

  const results = useMemo(() => {
    const normalized = normalizePersianSearch(query, false).toLocaleLowerCase();
    return CATALOG.filter((exercise) => {
      const searchable = normalizePersianSearch(`${exercise.fa} ${exercise.en}`, false).toLocaleLowerCase();
      return (
        (!normalized || searchable.includes(normalized)) &&
        (equipment === "all" || exercise.equipment === equipment)
      );
    });
  }, [equipment, query]);

  const name = (exercise: CatalogExercise) => (locale === "fa-IR" ? exercise.fa : exercise.en);

  return (
    <div className="space-y-6" data-testid="training-workspace">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <Badge variant="success">{t("training.phase_badge")}</Badge>
            <span className="text-xs text-brand-text-muted">{t("training.coach_owner_only")}</span>
          </div>
          <h1 className="text-2xl font-bold text-brand-text sm:text-3xl">
            {t("training.title")}
          </h1>
          <p className="mt-1 max-w-2xl text-sm text-brand-text-muted">
            {t("training.description")}
          </p>
        </div>
        <Button
          onClick={() => setSaved(true)}
          aria-label={t("training.save_program")}
          className="min-h-touch"
        >
          <Save aria-hidden="true" className="h-4 w-4" />
          {t("training.save_program")}
        </Button>
      </header>

      {saved && (
        <div role="status" className="rounded-lg border border-emerald-700 bg-emerald-700/20 p-3 text-sm">
          {t("training.saved_status")}
        </div>
      )}

      <div className="grid gap-5 xl:grid-cols-12">
        <Card variant="elevated" className="space-y-4 xl:col-span-4" aria-label={t("training.outline") }>
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
                    <button
                      type="button"
                      role="treeitem"
                      aria-selected="true"
                      className="min-h-touch w-full rounded-md bg-emerald-700/30 px-3 py-2 text-start text-emerald-300"
                    >
                      {t("training.upper_day")}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <p className="text-xs text-brand-text-muted">{t("training.keyboard_hint")}</p>
        </Card>

        <section className="space-y-5 xl:col-span-8" aria-label={t("training.editor") }>
          <Card variant="elevated" className="space-y-4">
            <div className="flex flex-col gap-3 md:flex-row md:items-end">
              <Input
                label={t("training.search_label")}
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder={t("training.search_placeholder")}
                type="search"
              />
              <label className="flex min-w-44 flex-col gap-1 text-sm text-brand-text-muted">
                {t("training.equipment")}
                <select
                  value={equipment}
                  onChange={(event) => setEquipment(event.target.value)}
                  className="min-h-touch rounded-lg border border-obsidian-700 bg-obsidian-800 px-3 text-brand-text"
                >
                  <option value="all">{t("training.all_equipment")}</option>
                  <option value="barbell">{t("training.barbell")}</option>
                  <option value="dumbbell">{t("training.dumbbell")}</option>
                  <option value="cable">{t("training.cable")}</option>
                </select>
              </label>
            </div>
            <p aria-live="polite" className="text-xs text-brand-text-muted">
              {t("training.results")}: <bdi>{results.length}</bdi>
            </p>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {results.map((exercise) => (
                <button
                  key={exercise.id}
                  type="button"
                  aria-pressed={selected.id === exercise.id}
                  onClick={() => {
                    setSelected(exercise);
                    setSaved(false);
                  }}
                  className="min-h-touch rounded-lg border border-obsidian-700 bg-obsidian-800 p-3 text-start hover:border-emerald-600 aria-pressed:border-emerald-500"
                >
                  <Dumbbell aria-hidden="true" className="mb-2 h-5 w-5 text-emerald-400" />
                  <strong className="block text-sm text-brand-text">{name(exercise)}</strong>
                  <span className="mt-1 block text-xs text-brand-text-muted" dir="auto">
                    {locale === "fa-IR" ? exercise.en : exercise.fa}
                  </span>
                </button>
              ))}
            </div>
          </Card>

          <Card variant="elevated" className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <h2 className="font-semibold text-brand-text">{t("training.prescription")}</h2>
                <p className="text-sm text-emerald-300">{name(selected)}</p>
              </div>
              <div className="flex gap-1" aria-label={t("training.reorder") }>
                <Button variant="ghost" size="sm" className="min-h-touch min-w-touch" aria-label={t("training.move_up")}>
                  <ChevronUp aria-hidden="true" className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="min-h-touch min-w-touch" aria-label={t("training.move_down")}>
                  <ChevronDown aria-hidden="true" className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <Input
                label={t("training.sets")}
                type="number"
                min={1}
                max={20}
                value={sets}
                onChange={(event) => setSets(Number(event.target.value))}
              />
              <Input label={t("training.reps")} value={reps} onChange={(event) => setReps(event.target.value)} />
              <Input label={t("training.tempo")} value={tempo} onChange={(event) => setTempo(event.target.value)} />
              <Input label={t("training.rpe")} value={rpe} onChange={(event) => setRpe(event.target.value)} />
            </div>
            <div className="rounded-lg bg-obsidian-800 p-3 text-sm text-brand-text-muted">
              <span>{t("training.preview")}: </span>
              <bdi className="text-brand-text">{sets} × {reps} · {tempo} · RPE {rpe}</bdi>
            </div>
          </Card>
        </section>
      </div>
    </div>
  );
}
