"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { CheckCircle2, ChevronDown, ChevronUp, Flag, RefreshCw } from "lucide-react";
import { useTranslation } from "../layout/DirectionProvider";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { Modal } from "../ui/Modal";
import { Input } from "../ui/Input";
import { ApiError } from "@/lib/api/client";
import {
  completeSession,
  getMe,
  getSession,
  logSet,
  substitute,
  type CompleteSessionInput,
  type WorkoutSessionView as SessionView,
} from "@/lib/api/athlete";
import { useNetworkStatus } from "@/lib/athlete/useNetworkStatus";
import { parseNumber, type Unit } from "@/lib/athlete/units";
import { SetLogger, type LoggedSet } from "./SetLogger";
import { RestTimer } from "./RestTimer";
import {
  SubstitutionModal,
  type AlternativeExercise,
  type SubstitutionReason,
} from "./SubstitutionModal";
import { FeedbackFlagForm } from "./FeedbackFlagForm";
import { OfflineBanner } from "./OfflineBanner";

interface PendingAction {
  label: string;
  submit: () => Promise<void>;
}

export interface WorkoutSessionViewProps {
  sessionId: string;
}

export const WorkoutSessionView: React.FC<WorkoutSessionViewProps> = ({ sessionId }) => {
  const { locale, t } = useTranslation();
  const router = useRouter();
  const { online } = useNetworkStatus();

  const [session, setSession] = useState<SessionView | null>(null);
  const [unit, setUnit] = useState<Unit>("kg");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [forbidden, setForbidden] = useState(false);

  const [restSeconds, setRestSeconds] = useState<number | null>(null);
  const [restKey, setRestKey] = useState(0);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [substituteTarget, setSubstituteTarget] = useState<{
    exercise_id: string;
    name: string;
  } | null>(null);
  const [completeOpen, setCompleteOpen] = useState(false);
  const [completeInput, setCompleteInput] = useState({
    session_rpe: "",
    fatigue_score: "",
    athlete_notes: "",
    skip_or_modify_reason: "",
  });
  const [pending, setPending] = useState<PendingAction[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    setForbidden(false);
    try {
      const [sess, me] = await Promise.all([getSession(sessionId, locale), getMe(locale)]);
      setSession(sess);
      if (me.user.preferred_unit === "lbs") setUnit("lbs");
      else setUnit("kg");
    } catch (err) {
      if (err instanceof ApiError && (err.status === 403 || err.status === 404)) {
        setForbidden(true);
      } else {
        setError(err instanceof ApiError ? err.problem.title : "error");
      }
    } finally {
      setLoading(false);
    }
  }, [sessionId, locale]);

  useEffect(() => {
    void load();
  }, [load]);

  const alternatives: AlternativeExercise[] = useMemo(() => {
    const seen = new Set<string>();
    const list: AlternativeExercise[] = [];
    for (const workout of session?.workouts ?? []) {
      for (const item of workout.items) {
        if (item.exercise_id !== substituteTarget?.exercise_id && !seen.has(item.exercise_id)) {
          seen.add(item.exercise_id);
          list.push({ exercise_id: item.exercise_id, name: item.name });
        }
      }
    }
    return list;
  }, [session, substituteTarget]);

  const enqueueOrRun = (label: string, fn: () => Promise<void>) => {
    if (!online) {
      setPending((p) => [...p, { label, submit: fn }]);
      return;
    }
    void fn().catch(() => {
      setPending((p) => [...p, { label, submit: fn }]);
    });
  };

  const handleLogSet = (exerciseId: string, restAfter?: number | null) => async (logged: LoggedSet) => {
    await new Promise<void>((resolve) => {
      enqueueOrRun(`set ${exerciseId} #${logged.set_index}`, async () => {
        await logSet(
          sessionId,
          {
            exercise_id: exerciseId,
            set_index: logged.set_index,
            actual_reps: logged.actual_reps,
            actual_load_kg: logged.actual_load_kg,
            actual_rpe: logged.actual_rpe,
          },
          locale,
        );
      });
      resolve();
    });
    if (restAfter && restAfter > 0) {
      setRestSeconds(restAfter);
      setRestKey((k) => k + 1);
    }
    if (!online) {
      await load();
    }
  };

  const handleSubstitute = async (input: {
    original_exercise_id: string;
    substituted_exercise_id: string;
    reason: SubstitutionReason;
  }) => {
    await substitute(sessionId, input, locale);
    await load();
  };

  const handleComplete = async () => {
    const payload: CompleteSessionInput = {
      athlete_notes: completeInput.athlete_notes || undefined,
      skip_or_modify_reason: completeInput.skip_or_modify_reason || undefined,
    };
    const rpe = parseNumber(completeInput.session_rpe);
    const fatigue = parseNumber(completeInput.fatigue_score);
    if (rpe !== null) payload.session_rpe = rpe;
    if (fatigue !== null) payload.fatigue_score = fatigue;
    await completeSession(sessionId, payload, locale);
    setCompleteOpen(false);
    await load();
  };

  const retryPending = async () => {
    if (!online) return;
    setRefreshing(true);
    const copy = [...pending];
    setPending([]);
    for (const action of copy) {
      try {
        await action.submit();
      } catch {
        setPending((p) => [...p, action]);
      }
    }
    setRefreshing(false);
    await load();
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
        <Button onClick={() => void load()} variant="secondary">
          {t("athlete.retry")}
        </Button>
      </Card>
    );
  }

  if (!session) return null;

  const statusVariant =
    session.status === "completed"
      ? "success"
      : session.status === "in_progress"
        ? "info"
        : "neutral";

  return (
    <div className="space-y-5 max-w-3xl mx-auto">
      <OfflineBanner online={online} pendingCount={pending.length} onRetry={() => void retryPending()} />

      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-brand-text">{t("athlete.session_title")}</h1>
          <p className="text-sm text-brand-text-muted mt-1">
            {session.scheduled_date} · {t(`athlete.${session.status}`)}
          </p>
        </div>
        <Badge variant={statusVariant}>{t(`athlete.${session.status}`)}</Badge>
      </div>

      <RestTimer
        key={restKey}
        seconds={restSeconds}
        onExpire={() => setRestSeconds(null)}
      />

      {session.workouts.map((workout, wi) => (
        <div key={workout.workout_id ?? wi} className="space-y-3">
          <h2 className="font-semibold text-brand-text">{workout.title}</h2>
          {workout.items.map((item) => {
            const isOpen = expanded[item.exercise_id];
            return (
              <Card key={item.exercise_id} variant="default" className="space-y-3">
                <button
                  type="button"
                  onClick={() => setExpanded((e) => ({ ...e, [item.exercise_id]: !isOpen }))}
                  className="w-full flex items-center justify-between gap-2 min-h-[44px] text-start"
                  aria-expanded={isOpen}
                >
                  <div>
                    <div className="font-medium text-brand-text">{item.name}</div>
                    <div className="text-xs text-brand-text-muted">
                      {item.prescriptions
                        .map(
                          (p) =>
                            `${p.target_reps} reps${p.target_load ? ` · ${p.target_load}` : ""}`,
                        )
                        .join(" — ")}
                    </div>
                  </div>
                  {isOpen ? (
                    <ChevronUp className="w-5 h-5 text-brand-text-muted" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-brand-text-muted" />
                  )}
                </button>

                {isOpen && (
                  <div className="space-y-3">
                    <SetLogger
                      exerciseName={item.name}
                      restSeconds={item.rest_seconds_between_sets}
                      preferredUnit={unit}
                      onLog={handleLogSet(item.exercise_id, item.rest_seconds_between_sets)}
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() =>
                        setSubstituteTarget({ exercise_id: item.exercise_id, name: item.name })
                      }
                    >
                      <RefreshCw className="w-4 h-4" />
                      {t("athlete.substitute")}
                    </Button>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      ))}

      <FeedbackFlagForm
        onSubmit={async (input) => {
          const { addFeedbackFlag } = await import("@/lib/api/athlete");
          await addFeedbackFlag(sessionId, input, locale);
        }}
      />

      {session.status === "in_progress" && (
        <Button size="lg" variant="primary" className="w-full" onClick={() => setCompleteOpen(true)}>
          <CheckCircle2 className="w-5 h-5" />
          {t("athlete.complete_workout")}
        </Button>
      )}

      <SubstitutionModal
        isOpen={substituteTarget !== null}
        onClose={() => setSubstituteTarget(null)}
        originalExerciseName={substituteTarget?.name ?? ""}
        originalExerciseId={substituteTarget?.exercise_id ?? ""}
        alternatives={alternatives}
        onConfirm={handleSubstitute}
      />

      <Modal
        isOpen={completeOpen}
        onClose={() => setCompleteOpen(false)}
        title={t("athlete.complete_workout_title")}
      >
        <div className="space-y-4">
          <Input
            label={t("athlete.session_rpe")}
            value={completeInput.session_rpe}
            onChange={(e) =>
              setCompleteInput((c) => ({ ...c, session_rpe: e.target.value }))
            }
            inputMode="numeric"
            placeholder="1–10"
          />
          <Input
            label={t("athlete.fatigue_score")}
            value={completeInput.fatigue_score}
            onChange={(e) =>
              setCompleteInput((c) => ({ ...c, fatigue_score: e.target.value }))
            }
            inputMode="numeric"
            placeholder="1–5"
          />
          <label className="text-xs font-medium text-brand-text-muted block">
            {t("athlete.athlete_notes")}
            <textarea
              value={completeInput.athlete_notes}
              onChange={(e) =>
                setCompleteInput((c) => ({ ...c, athlete_notes: e.target.value }))
              }
              placeholder={t("athlete.athlete_notes_placeholder")}
              rows={3}
              className="w-full mt-1 min-h-[44px] px-3.5 py-2.5 bg-obsidian-900 border border-obsidian-700 rounded-lg text-sm text-brand-text focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </label>
          <Button size="lg" className="w-full" onClick={() => void handleComplete()}>
            <Flag className="w-4 h-4" />
            {t("athlete.complete_workout")}
          </Button>
        </div>
      </Modal>
    </div>
  );
};
