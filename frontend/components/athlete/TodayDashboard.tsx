"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { CalendarDays, Dumbbell } from "lucide-react";
import { useTranslation } from "../layout/DirectionProvider";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { ApiError } from "@/lib/api/client";
import {
  getTodayWorkout,
  startSession,
  type TodayWorkout,
} from "@/lib/api/athlete";
import { useNetworkStatus } from "@/lib/athlete/useNetworkStatus";
import { OfflineBanner } from "./OfflineBanner";

export const TodayDashboard: React.FC = () => {
  const { locale, t } = useTranslation();
  const router = useRouter();
  const { online } = useNetworkStatus();

  const [today, setToday] = useState<TodayWorkout[]>([]);
  const [date, setDate] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [forbidden, setForbidden] = useState(false);
  const [starting, setStarting] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    setForbidden(false);
    try {
      const resp = await getTodayWorkout(locale);
      setToday(resp.scheduled_workouts);
      setDate(resp.date);
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

  const handleStart = async (assignmentId: string) => {
    if (!date) return;
    setStarting(assignmentId);
    try {
      const session = await startSession(
        { program_assignment_id: assignmentId, scheduled_date: date },
        locale,
      );
      router.push(`/${locale}/athlete/workout/${session.id}`);
    } catch {
      await load();
    } finally {
      setStarting(null);
    }
  };

  if (loading) {
    return <div className="py-8 text-center text-brand-text-muted">{t("athlete.today_loading")}</div>;
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
        <p className="text-sm text-brand-text-muted">{error}</p>
        <Button variant="secondary" onClick={() => void load()}>
          {t("athlete.retry")}
        </Button>
      </Card>
    );
  }

  if (today.length === 0) {
    return (
      <Card variant="elevated" className="text-center space-y-3">
        <CalendarDays className="w-8 h-8 mx-auto text-brand-text-muted" />
        <h2 className="font-semibold text-brand-text">{t("athlete.today_empty_title")}</h2>
        <p className="text-sm text-brand-text-muted">{t("athlete.today_empty_desc")}</p>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <OfflineBanner online={online} pendingCount={0} />
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-brand-text">{t("athlete.today_title")}</h1>
          <p className="text-sm text-brand-text-muted mt-1">{date}</p>
        </div>
        <Badge variant="success" size="md">
          <Dumbbell className="w-3.5 h-3.5" />
          {t("athlete.today_title")}
        </Badge>
      </div>

      {today.map((w, i) => (
        <Card key={`${w.assignment_id}-${i}`} variant="default" className="space-y-3">
          <div className="flex items-center justify-between gap-3">
            <h2 className="font-semibold text-brand-text">{w.title || w.workout.title}</h2>
            <Badge variant={w.status === "completed" ? "success" : "info"}>
              {t(`athlete.${w.status}`)}
            </Badge>
          </div>
          <div className="text-xs text-brand-text-muted space-y-1">
            {w.workout.items.map((item) => (
              <div key={item.exercise_id} className="flex justify-between">
                <span>{item.name}</span>
                <span>
                  {item.prescriptions.map((p) => p.target_reps).join(" / ")} reps
                </span>
              </div>
            ))}
          </div>
          {w.status === "scheduled" && (
            <Button
              size="lg"
              variant="primary"
              className="w-full"
              isLoading={starting === w.assignment_id}
              onClick={() => void handleStart(w.assignment_id)}
            >
              <Dumbbell className="w-5 h-5" />
              {t("athlete.start_workout")}
            </Button>
          )}
        </Card>
      ))}
    </div>
  );
};
