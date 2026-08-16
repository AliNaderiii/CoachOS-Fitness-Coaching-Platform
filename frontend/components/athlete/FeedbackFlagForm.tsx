"use client";

import React, { useState } from "react";
import { AlertTriangle } from "lucide-react";
import { useTranslation } from "../layout/DirectionProvider";
import { Button } from "../ui/Button";
import { Input } from "../ui/Input";
import type { FeedbackFlagType } from "@/lib/api/athlete";

export interface FeedbackFlagFormProps {
  onSubmit: (input: {
    flag_type: FeedbackFlagType;
    anatomical_location: string;
    severity: "mild" | "moderate" | "severe";
    details: string;
  }) => Promise<void> | void;
}

const TYPES: FeedbackFlagType[] = [
  "joint_pain",
  "muscle_strain",
  "dizziness",
  "severe_fatigue",
];
const SEVERITIES = ["mild", "moderate", "severe"] as const;

export const FeedbackFlagForm: React.FC<FeedbackFlagFormProps> = ({ onSubmit }) => {
  const { t } = useTranslation();
  const [flagType, setFlagType] = useState<FeedbackFlagType | "">("");
  const [location, setLocation] = useState("");
  const [severity, setSeverity] = useState<"mild" | "moderate" | "severe" | "">("");
  const [details, setDetails] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!flagType || !severity || location.trim() === "") {
      setError(t("athlete.reason_required_error"));
      return;
    }
    setError(null);
    setSaving(true);
    try {
      await onSubmit({
        flag_type: flagType as FeedbackFlagType,
        anatomical_location: location.trim(),
        severity: severity as "mild" | "moderate" | "severe",
        details: details.trim() || "Subjective report.",
      });
      setSubmitted(true);
      setFlagType("");
      setLocation("");
      setSeverity("");
      setDetails("");
    } finally {
      setSaving(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 p-4 rounded-xl bg-obsidian-850 border border-obsidian-700"
      aria-label={t("athlete.feedback_title")}
    >
      <div className="flex items-start gap-2 text-amber-400">
        <AlertTriangle className="w-5 h-5 mt-0.5" />
        <div className="space-y-1">
          <h3 className="font-semibold text-brand-text">{t("athlete.feedback_title")}</h3>
          <p className="text-xs text-brand-text-muted">{t("athlete.feedback_subtitle")}</p>
        </div>
      </div>

      <fieldset>
        <legend className="text-xs font-medium text-brand-text-muted mb-2">
          {t("athlete.feedback_type")}
        </legend>
        <div className="grid grid-cols-2 gap-2">
          {TYPES.map((type) => (
            <label
              key={type}
              className="flex items-center gap-2 p-3 rounded-lg border border-obsidian-700 bg-obsidian-800 cursor-pointer min-h-[44px]"
            >
              <input
                type="radio"
                name="flag_type"
                value={type}
                checked={flagType === type}
                onChange={() => setFlagType(type)}
                className="accent-amber-500"
              />
              <span className="text-sm text-brand-text">{t(`athlete.feedback_${type}`)}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <Input
        label={t("athlete.feedback_location")}
        value={location}
        onChange={(e) => setLocation(e.target.value)}
        placeholder={t("athlete.feedback_location_placeholder")}
      />

      <fieldset>
        <legend className="text-xs font-medium text-brand-text-muted mb-2">
          {t("athlete.feedback_severity")}
        </legend>
        <div className="flex gap-2">
          {SEVERITIES.map((s) => (
            <label
              key={s}
              className="flex items-center gap-2 p-3 flex-1 rounded-lg border border-obsidian-700 bg-obsidian-800 cursor-pointer min-h-[44px]"
            >
              <input
                type="radio"
                name="severity"
                value={s}
                checked={severity === s}
                onChange={() => setSeverity(s)}
                className="accent-amber-500"
              />
              <span className="text-sm text-brand-text">{t(`athlete.feedback_${s}`)}</span>
            </label>
          ))}
        </div>
      </fieldset>

      <label className="text-xs font-medium text-brand-text-muted block">
        {t("athlete.feedback_details")}
        <textarea
          value={details}
          onChange={(e) => setDetails(e.target.value)}
          placeholder={t("athlete.feedback_details_placeholder")}
          rows={3}
          className="w-full mt-1 min-h-[44px] px-3.5 py-2.5 bg-obsidian-900 border border-obsidian-700 rounded-lg text-sm text-brand-text focus:outline-none focus:ring-2 focus:ring-amber-500"
        />
      </label>

      {error && (
        <p className="text-xs text-red-400" role="alert">
          {error}
        </p>
      )}
      {submitted && (
        <p className="text-xs text-emerald-400" role="status" aria-live="polite">
          {t("athlete.feedback_submitted")}
        </p>
      )}

      <p className="text-[11px] text-brand-text-muted">{t("athlete.feedback_non_clinical")}</p>

      <Button type="submit" size="lg" isLoading={saving} variant="secondary" className="w-full">
        {t("athlete.feedback_submit")}
      </Button>
    </form>
  );
};
