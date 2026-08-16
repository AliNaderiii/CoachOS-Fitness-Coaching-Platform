"use client";

import React, { useState } from "react";
import { useTranslation } from "../layout/DirectionProvider";
import { Modal } from "../ui/Modal";
import { Button } from "../ui/Button";
import { Input } from "../ui/Input";

export type SubstitutionReason =
  | "equipment_unavailable"
  | "discomfort"
  | "preference"
  | "other";

export interface AlternativeExercise {
  exercise_id: string;
  name: string;
}

export interface SubstitutionModalProps {
  isOpen: boolean;
  onClose: () => void;
  originalExerciseName: string;
  originalExerciseId: string;
  alternatives: AlternativeExercise[];
  onConfirm: (input: {
    original_exercise_id: string;
    substituted_exercise_id: string;
    reason: SubstitutionReason;
  }) => Promise<void> | void;
}

const REASONS: SubstitutionReason[] = [
  "equipment_unavailable",
  "discomfort",
  "preference",
  "other",
];

export const SubstitutionModal: React.FC<SubstitutionModalProps> = ({
  isOpen,
  onClose,
  originalExerciseName,
  originalExerciseId,
  alternatives,
  onConfirm,
}) => {
  const { t } = useTranslation();
  const [selected, setSelected] = useState<string>("");
  const [reason, setReason] = useState<SubstitutionReason | "">("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const reset = () => {
    setSelected("");
    setReason("");
    setError(null);
    setSaving(false);
  };

  const handleConfirm = async () => {
    if (!selected) {
      setError(t("athlete.substitute_required"));
      return;
    }
    if (!reason) {
      setError(t("athlete.reason_required_error"));
      return;
    }
    setError(null);
    setSaving(true);
    try {
      await onConfirm({
        original_exercise_id: originalExerciseId,
        substituted_exercise_id: selected,
        reason: reason as SubstitutionReason,
      });
      reset();
      onClose();
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={t("athlete.substitute_title")}
      className="max-w-md"
    >
      <div className="space-y-4">
        <p className="text-sm text-brand-text-muted">
          {originalExerciseName} →{" "}
          <span aria-hidden="true">⇄</span>
        </p>

        {alternatives.length === 0 ? (
          <p className="text-sm text-brand-text-muted">{t("athlete.substitute_required")}</p>
        ) : (
          <div role="radiogroup" aria-label={t("athlete.substitute")}>
            {alternatives.map((alt) => (
              <label
                key={alt.exercise_id}
                className="flex items-center gap-3 p-3 mb-2 rounded-lg border border-obsidian-700 bg-obsidian-800 cursor-pointer min-h-[44px]"
              >
                <input
                  type="radio"
                  name="alternative"
                  value={alt.exercise_id}
                  checked={selected === alt.exercise_id}
                  onChange={() => setSelected(alt.exercise_id)}
                  className="accent-emerald-500"
                />
                <span className="text-sm text-brand-text">{alt.name}</span>
              </label>
            ))}
          </div>
        )}

        <div role="radiogroup" aria-label={t("athlete.reason_label")}>
          {REASONS.map((r) => (
            <label
              key={r}
              className="flex items-center gap-3 p-3 mb-2 rounded-lg border border-obsidian-700 bg-obsidian-800 cursor-pointer min-h-[44px]"
            >
              <input
                type="radio"
                name="reason"
                value={r}
                checked={reason === r}
                onChange={() => setReason(r)}
                className="accent-emerald-500"
              />
              <span className="text-sm text-brand-text">
                {t(`athlete.reason_${r}`)}
              </span>
            </label>
          ))}
        </div>

        {error && (
          <p className="text-xs text-red-400" role="alert">
            {error}
          </p>
        )}

        <div className="flex gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} className="flex-1">
            {t("athlete.cancel")}
          </Button>
          <Button
            variant="primary"
            onClick={handleConfirm}
            isLoading={saving}
            className="flex-1"
          >
            {t("athlete.confirm_substitute")}
          </Button>
        </div>
      </div>
    </Modal>
  );
};
