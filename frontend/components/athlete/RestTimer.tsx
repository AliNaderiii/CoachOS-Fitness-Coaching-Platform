"use client";

import React, { useEffect, useState } from "react";
import { Timer } from "lucide-react";
import { useTranslation } from "../layout/DirectionProvider";
import { Button } from "../ui/Button";

export interface RestTimerProps {
  /** Duration in seconds. 0/undefined disables the timer. */
  seconds?: number | null;
  onExpire?: () => void;
  /** Live region announcement key (localized). */
}

export const RestTimer: React.FC<RestTimerProps> = ({ seconds, onExpire }) => {
  const { t } = useTranslation();
  const [remaining, setRemaining] = useState<number | null>(null);
  const [active, setActive] = useState(false);

  useEffect(() => {
    if (!seconds || seconds <= 0) {
      setActive(false);
      setRemaining(null);
      return;
    }
    setRemaining(seconds);
    setActive(true);
  }, [seconds]);

  useEffect(() => {
    if (!active || remaining === null) return;
    if (remaining <= 0) {
      setActive(false);
      onExpire?.();
      return;
    }
    const id = window.setTimeout(() => setRemaining((r) => (r === null ? r : r - 1)), 1000);
    return () => window.clearTimeout(id);
  }, [active, remaining, onExpire]);

  if (!active || remaining === null) {
    return null;
  }

  const minutes = Math.floor(remaining / 60);
  const secs = remaining % 60;
  const label = `${minutes}:${String(secs).padStart(2, "0")}`;

  return (
    <div
      className="flex items-center justify-between gap-4 p-4 rounded-xl bg-obsidian-800 border border-obsidian-700"
      role="timer"
      aria-label={`${t("athlete.rest_title")} ${label}`}
    >
      <div className="flex items-center gap-3" aria-live="polite">
        <Timer className="w-5 h-5 text-emerald-400" aria-hidden="true" />
        <div>
          <div className="text-xs text-brand-text-muted">{t("athlete.rest_title")}</div>
          <div className="text-xl font-bold tabular-nums text-brand-text">{label}</div>
        </div>
      </div>
      <Button variant="secondary" size="sm" onClick={() => setActive(false)}>
        {t("athlete.rest_skip")}
      </Button>
    </div>
  );
};
