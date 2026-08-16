"use client";

import React, { useState } from "react";
import { Minus, Plus } from "lucide-react";
import { useTranslation } from "../layout/DirectionProvider";
import { Button } from "../ui/Button";
import { Input } from "../ui/Input";
import { parseNumber, toKg, type Unit } from "@/lib/athlete/units";

export interface LoggedSet {
  set_index: number;
  actual_reps: number;
  actual_load_kg: number;
  actual_rpe?: number | null;
}

export interface SetLoggerProps {
  exerciseName: string;
  restSeconds?: number | null;
  preferredUnit: Unit;
  onLog: (logged: LoggedSet) => Promise<void> | void;
}

/** One-handed set actual logging with a keyboard alternative (numeric inputs). */
export const SetLogger: React.FC<SetLoggerProps> = ({
  exerciseName,
  restSeconds,
  preferredUnit,
  onLog,
}) => {
  const { t } = useTranslation();
  const [setIndex, setSetIndex] = useState(1);
  const [reps, setReps] = useState("");
  const [load, setLoad] = useState("");
  const [rpe, setRpe] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [justLogged, setJustLogged] = useState(false);

  const bump = (setter: (v: string) => void, current: string, delta: number) => {
    const n = parseNumber(current) ?? 0;
    const next = Math.max(0, Math.round((n + delta) * 10) / 10);
    setter(String(next));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const repsNum = parseNumber(reps);
    const loadNum = parseNumber(load);
    if (repsNum === null || repsNum < 0) {
      setError("Reps must be a non-negative number.");
      return;
    }
    if (loadNum === null || loadNum < 0) {
      setError("Load must be a non-negative number.");
      return;
    }
    const rpeNum = parseNumber(rpe);
    if (rpeNum !== null && (rpeNum < 1 || rpeNum > 10)) {
      setError("RPE must be between 1 and 10.");
      return;
    }
    setError(null);
    setSaving(true);
    try {
      await onLog({
        set_index: setIndex,
        actual_reps: repsNum,
        actual_load_kg: toKg(loadNum, preferredUnit),
        actual_rpe: rpeNum,
      });
      setJustLogged(true);
      setReps("");
      setLoad("");
      setRpe("");
      setSetIndex((i) => i + 1);
      window.setTimeout(() => setJustLogged(false), 2000);
    } finally {
      setSaving(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 p-4 rounded-xl bg-obsidian-850 border border-obsidian-700"
      aria-label={`Log set for ${exerciseName}`}
    >
      <div className="flex items-center justify-between gap-3">
        <h3 className="font-semibold text-brand-text">
          {t("athlete.set_label")} {setIndex}
        </h3>
        {restSeconds ? (
          <span className="text-xs text-brand-text-muted">
            {t("athlete.rest_seconds")}: {restSeconds}
          </span>
        ) : null}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-2">
          <label className="text-xs font-medium text-brand-text-muted select-none">
            {t("athlete.reps_label")}
          </label>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => bump(setReps, reps, -1)}
              aria-label="Decrease reps"
              className="w-11 h-11 rounded-lg bg-obsidian-800 border border-obsidian-700 text-brand-text flex items-center justify-center hover:bg-obsidian-700"
            >
              <Minus className="w-4 h-4" />
            </button>
            <Input
              value={reps}
              onChange={(e) => setReps(e.target.value)}
              inputMode="numeric"
              placeholder="0"
              aria-label={t("athlete.reps_label")}
              className="text-center"
            />
            <button
              type="button"
              onClick={() => bump(setReps, reps, 1)}
              aria-label="Increase reps"
              className="w-11 h-11 rounded-lg bg-obsidian-800 border border-obsidian-700 text-brand-text flex items-center justify-center hover:bg-obsidian-700"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-xs font-medium text-brand-text-muted select-none">
            {t("athlete.load_label")} ({preferredUnit})
          </label>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => bump(setLoad, load, -2.5)}
              aria-label="Decrease load"
              className="w-11 h-11 rounded-lg bg-obsidian-800 border border-obsidian-700 text-brand-text flex items-center justify-center hover:bg-obsidian-700"
            >
              <Minus className="w-4 h-4" />
            </button>
            <Input
              value={load}
              onChange={(e) => setLoad(e.target.value)}
              inputMode="decimal"
              placeholder="0"
              aria-label={t("athlete.load_label")}
              className="text-center"
            />
            <button
              type="button"
              onClick={() => bump(setLoad, load, 2.5)}
              aria-label="Increase load"
              className="w-11 h-11 rounded-lg bg-obsidian-800 border border-obsidian-700 text-brand-text flex items-center justify-center hover:bg-obsidian-700"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <Input
        label={t("athlete.rpe_optional")}
        value={rpe}
        onChange={(e) => setRpe(e.target.value)}
        inputMode="decimal"
        placeholder="1–10"
        hint={t("athlete.rpe_label")}
      />

      {error && <p className="text-xs text-red-400" role="alert">{error}</p>}
      {justLogged && (
        <p className="text-xs text-emerald-400" role="status" aria-live="polite">
          {t("athlete.set_logged")}
        </p>
      )}

      <Button type="submit" size="lg" isLoading={saving} className="w-full">
        {t("athlete.log_set")}
      </Button>
    </form>
  );
};
