"use client";

import React, { useCallback, useEffect, useState } from "react";
import { Camera, Lock, Scale } from "lucide-react";
import { useTranslation } from "../layout/DirectionProvider";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { Input } from "../ui/Input";
import { ApiError } from "@/lib/api/client";
import {
  createBodyMetric,
  getMe,
  grantConsent,
  listBodyMetrics,
  listConsents,
  listProgressPhotos,
  revokeConsent,
  uploadProgressPhoto,
  type BodyMetricView,
  type ConsentView,
  type ProgressPhotoView,
} from "@/lib/api/athlete";
import { parseNumber, type Unit } from "@/lib/athlete/units";

export const ProgressManager: React.FC = () => {
  const { locale, t } = useTranslation();

  const [athleteId, setAthleteId] = useState<string | null>(null);
  const [unit, setUnit] = useState<Unit>("kg");
  const [metrics, setMetrics] = useState<BodyMetricView[]>([]);
  const [photos, setPhotos] = useState<ProgressPhotoView[]>([]);
  const [consents, setConsents] = useState<ConsentView[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [forbidden, setForbidden] = useState(false);

  // metric form
  const [value, setValue] = useState("");
  const [metricDate, setMetricDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [savingMetric, setSavingMetric] = useState(false);

  // photo form
  const [photoType, setPhotoType] = useState<"front" | "side" | "back">("front");
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  // consent form
  const [coachId, setCoachId] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    setForbidden(false);
    try {
      const me = await getMe(locale);
      setAthleteId(me.user.id);
      if (me.user.preferred_unit === "lbs") setUnit("lbs");
      const id = me.user.id;
      const [m, p, c] = await Promise.all([
        listBodyMetrics(id, locale),
        listProgressPhotos(id, locale),
        listConsents(id, locale),
      ]);
      setMetrics(m.metrics);
      setPhotos(p.photos);
      setConsents(c.consents);
    } catch (err) {
      if (err instanceof ApiError && (err.status === 403 || err.status === 404)) {
        setForbidden(true);
      } else {
        setError(err instanceof ApiError ? err.problem.title : "error");
      }
    } finally {
      setLoading(false);
    }
  }, [locale]);

  useEffect(() => {
    void load();
  }, [load]);

  const handleSaveMetric = async () => {
    if (!athleteId) return;
    const num = parseNumber(value);
    if (num === null || num < 0) return;
    setSavingMetric(true);
    try {
      await createBodyMetric(
        athleteId,
        {
          metric_type: "body_weight",
          value: String(num),
          unit: unit,
          recorded_at: metricDate,
        },
        locale,
      );
      setValue("");
      await load();
    } finally {
      setSavingMetric(false);
    }
  };

  const handleUpload = async () => {
    if (!athleteId || !photoFile) return;
    setUploading(true);
    try {
      const form = new FormData();
      form.append("file", photoFile);
      form.append("photo_type", photoType);
      form.append("captured_at", new Date().toISOString().slice(0, 10));
      await uploadProgressPhoto(athleteId, form, locale);
      setPhotoFile(null);
      await load();
    } finally {
      setUploading(false);
    }
  };

  const handleGrant = async (type: string) => {
    if (!athleteId || !coachId.trim()) return;
    await grantConsent(
      { athlete_user_id: athleteId, grantee_user_id: coachId.trim(), consent_type: type },
      locale,
    );
    setCoachId("");
    await load();
  };

  const handleRevoke = async (granteeId: string, type: string) => {
    if (!athleteId) return;
    await revokeConsent(
      { athlete_id: athleteId, grantee_id: granteeId, consent_type: type },
      locale,
    );
    await load();
  };

  const activeFor = (type: string) =>
    consents.filter((c) => c.consent_type === type && c.is_granted);

  if (loading) {
    return <div className="py-8 text-center text-brand-text-muted">{t("athlete.progress_loading")}</div>;
  }
  if (forbidden) {
    return (
      <Card variant="elevated" className="space-y-2">
        <h2 className="font-semibold text-brand-text">{t("athlete.today_forbidden_title")}</h2>
        <p className="text-sm text-brand-text-muted">{t("athlete.today_forbidden_desc")}</p>
      </Card>
    );
  }
  if (error) {
    return (
      <Card variant="elevated" className="space-y-3">
        <h2 className="font-semibold text-brand-text">{t("athlete.today_error_title")}</h2>
        <Button variant="secondary" onClick={() => void load()}>
          {t("athlete.retry")}
        </Button>
      </Card>
    );
  }

  return (
    <div className="space-y-5 max-w-3xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-brand-text">{t("athlete.progress_title")}</h1>
        <p className="text-sm text-brand-text-muted mt-1">{t("athlete.progress_subtitle")}</p>
      </div>

      {/* Body metrics */}
      <Card variant="default" className="space-y-3">
        <h2 className="font-semibold text-brand-text flex items-center gap-2">
          <Scale className="w-4 h-4 text-emerald-400" />
          {t("athlete.progress_metrics_title")}
        </h2>
        {metrics.length === 0 ? (
          <p className="text-sm text-brand-text-muted">{t("athlete.progress_empty")}</p>
        ) : (
          <ul className="text-sm space-y-1">
            {metrics.slice(0, 20).map((m) => (
              <li key={m.id} className="flex justify-between">
                <span>{m.recorded_at}</span>
                <span className="tabular-nums">
                  {m.value} {m.unit}
                </span>
              </li>
            ))}
          </ul>
        )}
        <div className="grid grid-cols-3 gap-2 items-end">
          <Input
            label={t("athlete.progress_weight_label")}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            inputMode="decimal"
            placeholder={t("athlete.progress_value_placeholder")}
          />
          <Input
            label={t("athlete.progress_recorded_at")}
            type="date"
            value={metricDate}
            onChange={(e) => setMetricDate(e.target.value)}
          />
          <Button size="md" variant="primary" isLoading={savingMetric} onClick={() => void handleSaveMetric()}>
            {t("athlete.progress_save")}
          </Button>
        </div>
      </Card>

      {/* Photos */}
      <Card variant="default" className="space-y-3">
        <h2 className="font-semibold text-brand-text flex items-center gap-2">
          <Camera className="w-4 h-4 text-emerald-400" />
          {t("athlete.progress_photos_title")}
        </h2>
        <p className="text-xs text-brand-text-muted flex items-center gap-1">
          <Lock className="w-3.5 h-3.5" />
          {t("athlete.progress_photos_private")}
        </p>
        <div className="flex gap-2 items-end">
          <div className="flex gap-1">
            {(["front", "side", "back"] as const).map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => setPhotoType(p)}
                className={`min-h-[44px] px-3 rounded-lg border text-sm ${
                  photoType === p
                    ? "border-emerald-500 text-emerald-400"
                    : "border-obsidian-700 text-brand-text-muted"
                }`}
              >
                {t(`athlete.progress_photo_${p}`)}
              </button>
            ))}
          </div>
          <input
            type="file"
            accept="image/*"
            aria-label={t("athlete.progress_upload")}
            onChange={(e) => setPhotoFile(e.target.files?.[0] ?? null)}
            className="block text-sm text-brand-text-muted file:mr-2 file:min-h-[44px] file:px-3 file:rounded-lg file:border-0 file:bg-obsidian-800 file:text-brand-text"
          />
        </div>
        <Button
          variant="secondary"
          size="md"
          isLoading={uploading}
          disabled={!photoFile}
          onClick={() => void handleUpload()}
        >
          {t("athlete.progress_upload")}
        </Button>
        {photos.length > 0 && (
          <p className="text-xs text-brand-text-muted">
            {photos.length} · {photos.map((p) => p.photo_type).join(", ")}
          </p>
        )}
      </Card>

      {/* Consent */}
      <Card variant="default" className="space-y-3">
        <h2 className="font-semibold text-brand-text">{t("athlete.progress_consent_title")}</h2>
        <p className="text-xs text-brand-text-muted">{t("athlete.progress_consent_desc")}</p>

        {consents.length > 0 && (
          <ul className="text-sm space-y-1">
            {consents.map((c) => (
              <li key={c.id} className="flex items-center justify-between gap-2">
                <span className="flex items-center gap-2">
                  <Badge variant={c.is_granted ? "success" : "neutral"}>{c.consent_type}</Badge>
                  <span className="text-xs text-brand-text-muted">{(c.grantee_user_id || "").slice(0, 8)}</span>
                </span>
                {c.is_granted ? (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => void handleRevoke(c.grantee_user_id, c.consent_type)}
                  >
                    {t("athlete.progress_revoke")}
                  </Button>
                ) : null}
              </li>
            ))}
          </ul>
        )}

        <div className="flex gap-2 items-end">
          <Input
            label="Coach ID"
            value={coachId}
            onChange={(e) => setCoachId(e.target.value)}
            placeholder="coach user id"
          />
          <div className="flex gap-1">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => void handleGrant("progress_photo")}
              disabled={!coachId.trim()}
            >
              {t("athlete.progress_grant")} · Photos
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => void handleGrant("body_metrics")}
              disabled={!coachId.trim()}
            >
              {t("athlete.progress_grant")} · Metrics
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};
