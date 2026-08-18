"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import { AlertTriangle, Ban, Gauge, Shield, Sparkles } from "lucide-react";
import { useTranslation } from "@/components/layout/DirectionProvider";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ApiError } from "@/lib/api/client";
import {
  createCopilotRun,
  editCopilotOutput,
  getCopilotRun,
  listAuthorizedAssignments,
  listCopilotCapabilities,
  listCopilotRuns,
  regenerateCopilotRun,
  reportCopilotRun,
  reviewCopilotOutput,
  type CopilotCapability,
  type CopilotCapabilityId,
  type CopilotRun,
  type ProgramAssignmentSummary,
} from "@/lib/api/copilot";
import { listOrganizations, type OrganizationContext } from "@/lib/api/training";
import { CopilotResultCard } from "./CopilotResultCard";

type LoadState = "loading" | "ready" | "empty" | "error" | "unauthorized" | "disabled";

function errorState(error: unknown): LoadState {
  return error instanceof ApiError && (error.status === 401 || error.status === 403)
    ? "unauthorized"
    : "error";
}

function newIdempotencyKey(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `idem-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

/**
 * Phase 11 Copilot console for professional users.
 *
 * Deliberately a capability picker, not a free-form chat box. Every run is a
 * governed request over one authorized athlete; results arrive as labeled
 * drafts with sources/limitations and no automatic side effects.
 */
export function CopilotConsole() {
  const { locale, t } = useTranslation();
  const [organizations, setOrganizations] = useState<OrganizationContext[]>([]);
  const [activeOrgId, setActiveOrgId] = useState("");
  const [orgState, setOrgState] = useState<LoadState>("loading");
  const [capabilities, setCapabilities] = useState<CopilotCapability[]>([]);
  const [capability, setCapability] = useState<CopilotCapabilityId>("summarize_progress");
  const [assignments, setAssignments] = useState<ProgramAssignmentSummary[]>([]);
  const [athleteId, setAthleteId] = useState("");
  const [periodDays, setPeriodDays] = useState(14);
  const [notes, setNotes] = useState("");
  const [runState, setRunState] = useState<"idle" | "running">("idle");
  const [currentRun, setCurrentRun] = useState<CopilotRun | null>(null);
  const [history, setHistory] = useState<CopilotRun[]>([]);
  const [announcement, setAnnouncement] = useState("");
  const [errorMessageKey, setErrorMessageKey] = useState("");

  useEffect(() => {
    let active = true;
    listOrganizations(locale)
      .then(({ organizations: available }) => {
        if (!active) return;
        setOrganizations(available);
        if (available.length === 0) {
          setOrgState("empty");
          return;
        }
        setActiveOrgId((current) =>
          available.some((org) => org.id === current) ? current : available[0].id,
        );
        setOrgState("ready");
      })
      .catch((error: unknown) => {
        if (active) setOrgState(errorState(error));
      });
    return () => {
      active = false;
    };
  }, [locale]);

  useEffect(() => {
    if (!activeOrgId || orgState !== "ready") return;
    let active = true;
    Promise.all([
      listCopilotCapabilities(activeOrgId, locale),
      listAuthorizedAssignments(activeOrgId, locale).catch(() => ({ assignments: [] })),
      listCopilotRuns(activeOrgId, locale).catch(() => ({ runs: [], count: 0, retention_days: 0 })),
    ])
      .then(([caps, assignmentList, runList]) => {
        if (!active) return;
        setCapabilities(caps.capabilities);
        setOrgState(caps.feature.enabled ? "ready" : "disabled");
        setAssignments(assignmentList.assignments);
        setHistory(runList.runs);
      })
      .catch(() => {
        if (active) setOrgState("error");
      });
    return () => {
      active = false;
    };
  }, [activeOrgId, locale, orgState]);

  const athleteOptions = useMemo(() => {
    const seen = new Map<string, ProgramAssignmentSummary>();
    for (const assignment of assignments) {
      if (assignment.status === "active" && !seen.has(assignment.athlete_user_id)) {
        seen.set(assignment.athlete_user_id, assignment);
      }
    }
    return [...seen.values()];
  }, [assignments]);

  const refreshHistory = useCallback(async () => {
    if (!activeOrgId) return;
    try {
      const list = await listCopilotRuns(activeOrgId, locale);
      setHistory(list.runs);
    } catch {
      /* history failure is non-fatal */
    }
  }, [activeOrgId, locale]);

  const handleError = useCallback(
    (error: unknown) => {
      if (error instanceof ApiError) {
        setErrorMessageKey(error.problem.message_key || "copilot.error.generic");
      } else {
        setErrorMessageKey("copilot.error.generic");
      }
      setAnnouncement(t("copilot.announce.failed"));
    },
    [t],
  );

  const requestRun = async () => {
    if (!activeOrgId || !athleteId.trim()) return;
    setRunState("running");
    setErrorMessageKey("");
    setCurrentRun(null);
    setAnnouncement(t("copilot.announce.started"));
    try {
      const run = await createCopilotRun(
        activeOrgId,
        {
          capability,
          athleteId: athleteId.trim(),
          generationLanguage: locale,
          periodDays: capability === "suggest_program_adjustment" ? undefined : periodDays,
          notes: notes.trim() || undefined,
        },
        newIdempotencyKey(),
        locale,
      );
      setCurrentRun(run);
      setAnnouncement(
        run.status === "succeeded" ? t("copilot.announce.succeeded") : t("copilot.announce.failed"),
      );
      void refreshHistory();
    } catch (error) {
      handleError(error);
    } finally {
      setRunState("idle");
    }
  };

  const openHistoryRun = async (run: CopilotRun) => {
    if (!activeOrgId) return;
    setErrorMessageKey("");
    try {
      const detail = await getCopilotRun(activeOrgId, run.id, locale);
      setCurrentRun(detail);
    } catch (error) {
      handleError(error);
    }
  };

  const replaceRun = (run: CopilotRun) => {
    setCurrentRun(run);
    void refreshHistory();
  };

  const selectedCapability = capabilities.find((item) => item.id === capability);

  if (orgState === "loading") {
    return (
      <div className="flex items-center justify-center py-16" role="status">
        <p className="text-brand-text-muted">{t("app.loading")}</p>
      </div>
    );
  }

  if (orgState === "unauthorized" || orgState === "error" || orgState === "empty") {
    return (
      <Card className="p-6 text-center" data-testid="copilot-error-state">
        <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" aria-hidden="true" />
        <p className="mt-3 text-brand-text">{t(`copilot.state.${orgState}`)}</p>
      </Card>
    );
  }

  if (orgState === "disabled") {
    return (
      <Card className="p-6" data-testid="copilot-disabled-state">
        <div className="flex items-start gap-3">
          <Ban className="w-6 h-6 text-brand-text-muted shrink-0" aria-hidden="true" />
          <div>
            <h2 className="font-semibold text-brand-text">{t("copilot.state.disabled_title")}</h2>
            <p className="mt-2 text-sm text-brand-text-muted leading-6">
              {t("copilot.state.disabled_body")}
            </p>
            <p className="mt-2 text-sm text-brand-text-muted leading-6">
              {t("copilot.prohibited_notice")}
            </p>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-5" data-testid="copilot-console">
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Sparkles className="w-5 h-5" aria-hidden="true" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-brand-text">{t("copilot.title")}</h1>
            <p className="text-xs text-brand-text-muted">{t("copilot.subtitle")}</p>
          </div>
        </div>
        <Badge variant="info" size="sm">
          <Shield className="w-3.5 h-3.5" aria-hidden="true" />
          {t("copilot.governance_badge")}
        </Badge>
      </div>

      <p className="text-xs text-brand-text-muted leading-5 rounded-lg border border-obsidian-700 bg-obsidian-900/60 p-3">
        {t("copilot.prohibited_notice")}
      </p>

      <Card className="p-4 sm:p-5 space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium text-brand-text">{t("copilot.org_label")}</span>
            <select
              className="mt-1 w-full rounded-lg bg-obsidian-900 border border-obsidian-700 p-2.5 text-sm text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 min-h-[44px]"
              value={activeOrgId}
              onChange={(event) => setActiveOrgId(event.target.value)}
            >
              {organizations.map((org) => (
                <option key={org.id} value={org.id}>
                  {org.name}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="text-sm font-medium text-brand-text">{t("copilot.athlete_label")}</span>
            {athleteOptions.length > 0 ? (
              <select
                className="mt-1 w-full rounded-lg bg-obsidian-900 border border-obsidian-700 p-2.5 text-sm text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 min-h-[44px]"
                value={athleteId}
                onChange={(event) => setAthleteId(event.target.value)}
              >
                <option value="">{t("copilot.athlete_placeholder")}</option>
                {athleteOptions.map((assignment) => (
                  <option key={assignment.id} value={assignment.athlete_user_id}>
                    <bdi dir="ltr">{assignment.athlete_user_id}</bdi>
                  </option>
                ))}
              </select>
            ) : (
              <input
                dir="ltr"
                className="mt-1 w-full rounded-lg bg-obsidian-900 border border-obsidian-700 p-2.5 text-sm text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 min-h-[44px]"
                placeholder={t("copilot.athlete_placeholder")}
                value={athleteId}
                onChange={(event) => setAthleteId(event.target.value)}
              />
            )}
          </label>
        </div>

        <fieldset>
          <legend className="text-sm font-medium text-brand-text">
            {t("copilot.capability_label")}
          </legend>
          <div className="mt-2 grid gap-2 sm:grid-cols-3" role="radiogroup">
            {capabilities.map((item) => {
              const selected = item.id === capability;
              return (
                <label
                  key={item.id}
                  className={`flex flex-col gap-1 rounded-lg border p-3 cursor-pointer min-h-[44px] transition-colors focus-within:ring-2 focus-within:ring-emerald-500 ${
                    selected
                      ? "border-emerald-500/60 bg-emerald-500/5"
                      : "border-obsidian-700 bg-obsidian-900 hover:border-obsidian-600"
                  } ${item.enabled ? "" : "opacity-50"}`}
                >
                  <input
                    type="radio"
                    name="copilot-capability"
                    className="sr-only"
                    checked={selected}
                    disabled={!item.enabled}
                    onChange={() => setCapability(item.id)}
                  />
                  <span className="text-sm font-medium text-brand-text">
                    {t(`copilot.capability.${item.id}.title`)}
                  </span>
                  <span className="text-xs text-brand-text-muted leading-5">
                    {t(`copilot.capability.${item.id}.description`)}
                  </span>
                </label>
              );
            })}
          </div>
        </fieldset>

        <div className="grid gap-4 sm:grid-cols-2">
          {capability !== "suggest_program_adjustment" && (
            <label className="block">
              <span className="text-sm font-medium text-brand-text">
                {t("copilot.period_label")}
              </span>
              <select
                className="mt-1 w-full rounded-lg bg-obsidian-900 border border-obsidian-700 p-2.5 text-sm text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 min-h-[44px]"
                value={periodDays}
                onChange={(event) => setPeriodDays(Number(event.target.value))}
              >
                {[7, 14, 21, 30].map((days) => (
                  <option key={days} value={days}>
                    {t("copilot.period_days", "").replace("{days}", String(days))}
                  </option>
                ))}
              </select>
            </label>
          )}
          <label className="block">
            <span className="text-sm font-medium text-brand-text">{t("copilot.notes_label")}</span>
            <input
              className="mt-1 w-full rounded-lg bg-obsidian-900 border border-obsidian-700 p-2.5 text-sm text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 min-h-[44px]"
              placeholder={t("copilot.notes_placeholder")}
              value={notes}
              onChange={(event) => setNotes(event.target.value)}
              maxLength={500}
            />
          </label>
        </div>

        <div className="flex items-center justify-between gap-3 flex-wrap">
          <p className="text-xs text-brand-text-muted">
            <Gauge className="w-3.5 h-3.5 inline-block me-1" aria-hidden="true" />
            {t("copilot.generation_language_notice")}: <bdi dir="ltr">{locale}</bdi>
          </p>
          <Button
            onClick={requestRun}
            disabled={runState === "running" || !athleteId.trim() || selectedCapability?.enabled === false}
            isLoading={runState === "running"}
            className="min-h-[44px]"
          >
            {runState === "running" ? t("copilot.action.running") : t("copilot.action.run")}
          </Button>
        </div>
        {errorMessageKey && (
          <p className="text-sm text-red-400" role="alert">
            {t(errorMessageKey, t("copilot.error.generic"))}
          </p>
        )}
      </Card>

      <div aria-live="polite" role="status" className="sr-only">
        {announcement}
      </div>

      {currentRun && (
        <CopilotResultCard
          run={currentRun}
          busy={runState === "running"}
          onEdit={async (payload) => {
            if (!activeOrgId) return;
            replaceRun(await editCopilotOutput(activeOrgId, currentRun.id, payload, locale));
          }}
          onApprove={async (note) => {
            if (!activeOrgId) return;
            replaceRun(await reviewCopilotOutput(activeOrgId, currentRun.id, "approve", note, locale));
          }}
          onReject={async (note) => {
            if (!activeOrgId) return;
            replaceRun(await reviewCopilotOutput(activeOrgId, currentRun.id, "reject", note, locale));
          }}
          onRegenerate={async () => {
            if (!activeOrgId) return;
            replaceRun(await regenerateCopilotRun(activeOrgId, currentRun.id, locale));
          }}
          onReport={async (reportType, detail) => {
            if (!activeOrgId) return;
            await reportCopilotRun(
              activeOrgId,
              currentRun.id,
              reportType as "unsafe" | "incorrect" | "privacy" | "hallucinated_source" | "other",
              detail,
              locale,
            );
          }}
        />
      )}

      {history.length > 0 && (
        <Card className="p-4 sm:p-5">
          <h2 className="text-sm font-semibold text-brand-text">{t("copilot.history_title")}</h2>
          <ul className="mt-3 divide-y divide-obsidian-700">
            {history.slice(0, 10).map((run) => (
              <li key={run.id}>
                <button
                  type="button"
                  className="w-full flex items-center justify-between gap-3 py-2.5 min-h-[44px] text-start rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                  onClick={() => openHistoryRun(run)}
                >
                  <span className="text-sm text-brand-text truncate">
                    {t(`copilot.capability.${run.capability}.title`)}
                  </span>
                  <span className="flex items-center gap-2 shrink-0">
                    <Badge
                      variant={
                        run.status === "succeeded"
                          ? "success"
                          : run.status === "failed"
                            ? "error"
                            : "neutral"
                      }
                      size="sm"
                    >
                      {t(`copilot.run_status.${run.status}`, run.status)}
                    </Badge>
                  </span>
                </button>
              </li>
            ))}
          </ul>
          <p className="mt-2 text-[11px] text-brand-text-muted">{t("copilot.history_notice")}</p>
        </Card>
      )}
    </div>
  );
}
