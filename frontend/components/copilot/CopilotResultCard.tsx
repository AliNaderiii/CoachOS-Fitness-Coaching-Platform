"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  ClipboardCopy,
  Eye,
  FileText,
  RefreshCw,
  ShieldAlert,
  Sparkles,
  XCircle,
} from "lucide-react";
import { useTranslation } from "@/components/layout/DirectionProvider";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import type { CopilotRun } from "@/lib/api/copilot";

export interface CopilotResultCardProps {
  run: CopilotRun;
  onEdit: (payload: Record<string, unknown>) => Promise<void>;
  onApprove: (note: string) => Promise<void>;
  onReject: (note: string) => Promise<void>;
  onRegenerate: () => Promise<void>;
  onReport: (reportType: string, detail: string) => Promise<void>;
  busy: boolean;
}

function asList(value: unknown): string[] {
  return Array.isArray(value) ? value.filter((v): v is string => typeof v === "string") : [];
}

function asString(value: unknown): string {
  return typeof value === "string" ? value : "";
}

/**
 * Renders one AI draft with provenance, limitations, and explicit human
 * review actions. Draft = untrusted until approved. Nothing in this component
 * can send, apply, or export anything automatically; copy-to-clipboard is an
 * explicit user gesture.
 */
export function CopilotResultCard({
  run,
  onEdit,
  onApprove,
  onReject,
  onRegenerate,
  onReport,
  busy,
}: CopilotResultCardProps) {
  const { t, locale } = useTranslation();
  const [editing, setEditing] = useState(false);
  const [editDraft, setEditDraft] = useState<Record<string, unknown>>({});
  const [rejecting, setRejecting] = useState(false);
  const [reporting, setReporting] = useState(false);
  const [note, setNote] = useState("");
  const [reportType, setReportType] = useState("unsafe");
  const [copyState, setCopyState] = useState<"idle" | "copied">("idle");
  const headingRef = useRef<HTMLHeadingElement>(null);

  const output = run.output;
  const payload = output?.payload ?? null;

  useEffect(() => {
    headingRef.current?.focus();
  }, [run.id]);

  if (run.status !== "succeeded" || !output || !payload) {
    return (
      <Card className="p-4" data-testid="copilot-result-empty">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" aria-hidden="true" />
          <div>
            <h3 className="font-semibold text-brand-text">
              {t("copilot.result.unavailable_title")}
            </h3>
            <p className="text-sm text-brand-text-muted mt-1">
              {t(`copilot.error.${run.error_code || "generic"}`, t("copilot.error.generic"))}
            </p>
            <p className="text-xs text-brand-text-muted mt-2">
              {t("copilot.result.fallback_notice")}
            </p>
          </div>
        </div>
      </Card>
    );
  }

  const canReview = Boolean(run.actions?.can_approve) && ["draft", "edited"].includes(output.status);

  const startEdit = () => {
    setEditDraft({ ...payload });
    setEditing(true);
  };

  const submitEdit = async () => {
    await onEdit(editDraft);
    setEditing(false);
  };

  const copyDraft = async () => {
    const text =
      run.capability === "draft_check_in"
        ? `${asString(payload.subject)}\n\n${asString(payload.body)}`
        : run.capability === "summarize_progress"
          ? `${asString(payload.summary)}\n${asList(payload.highlights).join("\n")}`
          : JSON.stringify(payload, null, 2);
    try {
      await navigator.clipboard.writeText(text);
      setCopyState("copied");
      setTimeout(() => setCopyState("idle"), 2000);
    } catch {
      setCopyState("idle");
    }
  };

  return (
    <Card className="p-4 sm:p-6" data-testid="copilot-result-card">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex items-center gap-2 min-w-0">
          <Sparkles className="w-5 h-5 text-emerald-400 shrink-0" aria-hidden="true" />
          <h3
            ref={headingRef}
            tabIndex={-1}
            className="font-semibold text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 rounded"
          >
            {t(`copilot.capability.${run.capability}.title`)}
          </h3>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Badge variant="info" size="sm">
            <FileText className="w-3.5 h-3.5" aria-hidden="true" />
            {t("copilot.draft_badge")}
          </Badge>
          <Badge
            variant={output.status === "approved" ? "success" : output.status === "rejected" ? "error" : "warning"}
            size="sm"
          >
            {t(`copilot.status.${output.status}`)}
          </Badge>
          <Badge variant="neutral" size="sm">
            <bdi dir="ltr">{run.generation_language}</bdi>
          </Badge>
        </div>
      </div>

      <p className="text-xs text-brand-text-muted mt-2" role="note">
        {t("copilot.human_review_notice")}
      </p>

      {/* Draft content (source facts vs. generated suggestion are separated) */}
      <div className="mt-4 space-y-4">
        {run.capability === "summarize_progress" && (
          <section aria-label={t("copilot.capability.summarize_progress.title")}>
            {editing ? (
              <label className="block">
                <span className="text-sm font-medium text-brand-text">
                  {t("copilot.field.summary")}
                </span>
                <textarea
                  className="mt-1 w-full min-h-[96px] rounded-lg bg-obsidian-900 border border-obsidian-700 p-3 text-sm text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                  value={asString(editDraft.summary)}
                  onChange={(event) => setEditDraft({ ...editDraft, summary: event.target.value })}
                  maxLength={1600}
                />
              </label>
            ) : (
              <p className="text-sm text-brand-text leading-7 whitespace-pre-wrap break-words">
                {asString(payload.summary)}
              </p>
            )}
            <dl className="mt-3 grid grid-cols-2 gap-2 text-sm">
              <div className="rounded-lg bg-obsidian-900 p-3">
                <dt className="text-brand-text-muted">{t("copilot.metric.sessions_completed")}</dt>
                <dd className="text-lg font-semibold text-emerald-400" dir="ltr">
                  {String(payload.sessions_completed ?? 0)}
                </dd>
              </div>
              <div className="rounded-lg bg-obsidian-900 p-3">
                <dt className="text-brand-text-muted">{t("copilot.metric.sessions_missed")}</dt>
                <dd className="text-lg font-semibold text-amber-400" dir="ltr">
                  {String(payload.sessions_missed ?? 0)}
                </dd>
              </div>
            </dl>
            {asList(payload.highlights).length > 0 && (
              <ul className="mt-3 space-y-1 text-sm text-brand-text list-disc ps-5">
                {asList(payload.highlights).map((item, index) => (
                  <li key={`highlight-${index}`} className="break-words">
                    {item}
                  </li>
                ))}
              </ul>
            )}
            {asList(payload.concerns).length > 0 && (
              <div className="mt-3 rounded-lg border border-amber-500/30 bg-amber-500/5 p-3">
                <p className="text-xs font-medium text-amber-400 mb-1">
                  {t("copilot.section.concerns")}
                </p>
                <ul className="space-y-1 text-sm text-brand-text list-disc ps-5">
                  {asList(payload.concerns).map((item, index) => (
                    <li key={`concern-${index}`} className="break-words">
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}

        {run.capability === "draft_check_in" && (
          <section aria-label={t("copilot.capability.draft_check_in.title")}>
            {editing ? (
              <div className="space-y-3">
                <label className="block">
                  <span className="text-sm font-medium text-brand-text">
                    {t("copilot.field.subject")}
                  </span>
                  <input
                    className="mt-1 w-full rounded-lg bg-obsidian-900 border border-obsidian-700 p-3 text-sm text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                    value={asString(editDraft.subject)}
                    onChange={(event) =>
                      setEditDraft({ ...editDraft, subject: event.target.value })
                    }
                    maxLength={140}
                  />
                </label>
                <label className="block">
                  <span className="text-sm font-medium text-brand-text">
                    {t("copilot.field.body")}
                  </span>
                  <textarea
                    className="mt-1 w-full min-h-[140px] rounded-lg bg-obsidian-900 border border-obsidian-700 p-3 text-sm text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                    value={asString(editDraft.body)}
                    onChange={(event) => setEditDraft({ ...editDraft, body: event.target.value })}
                    maxLength={1600}
                  />
                </label>
              </div>
            ) : (
              <div className="rounded-lg border border-obsidian-700 bg-obsidian-900 p-4">
                <p className="text-sm font-semibold text-brand-text break-words">
                  {asString(payload.subject)}
                </p>
                <p className="mt-2 text-sm text-brand-text leading-7 whitespace-pre-wrap break-words">
                  {asString(payload.body)}
                </p>
              </div>
            )}
            <p className="mt-2 text-xs text-brand-text-muted">{t("copilot.never_sent_notice")}</p>
          </section>
        )}

        {run.capability === "suggest_program_adjustment" && (
          <section aria-label={t("copilot.capability.suggest_program_adjustment.title")}>
            <p className="text-sm text-brand-text-muted break-words">
              {asString(payload.target_day_title)}
            </p>
            <ul className="mt-2 space-y-2">
              {(Array.isArray(payload.suggestions) ? payload.suggestions : []).map(
                (suggestion, index) => {
                  const entry = suggestion as Record<string, unknown>;
                  return (
                    <li
                      key={`suggestion-${index}`}
                      className="rounded-lg border border-obsidian-700 bg-obsidian-900 p-3 text-sm"
                    >
                      <div className="flex items-center justify-between gap-2 flex-wrap">
                        <span className="font-medium text-brand-text break-all" dir="ltr">
                          <bdi>{asString(entry.exercise_id)}</bdi>
                        </span>
                        <Badge variant="neutral" size="sm">
                          {t(`copilot.change_type.${asString(entry.change_type)}`, asString(entry.change_type))}
                        </Badge>
                      </div>
                      <p className="mt-1 text-brand-text-muted break-words">
                        {asString(entry.rationale)}
                      </p>
                    </li>
                  );
                },
              )}
            </ul>
            <p className="mt-3 text-xs text-amber-400 flex items-start gap-1.5">
              <ShieldAlert className="w-4 h-4 shrink-0 mt-0.5" aria-hidden="true" />
              {asString(payload.safety_disclaimer)}
            </p>
          </section>
        )}
      </div>

      {/* Limitations & uncertainty */}
      {asList(payload.limitations).length > 0 && (
        <details className="mt-4 rounded-lg border border-obsidian-700 p-3" open>
          <summary className="text-sm font-medium text-brand-text cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 rounded">
            {t("copilot.section.limitations")}
          </summary>
          <ul className="mt-2 space-y-1 text-sm text-brand-text-muted list-disc ps-5">
            {asList(payload.limitations).map((item, index) => (
              <li key={`limitation-${index}`} className="break-words">
                {item}
              </li>
            ))}
          </ul>
        </details>
      )}

      {/* Sources / provenance */}
      {run.sources.length > 0 && (
        <details className="mt-3 rounded-lg border border-obsidian-700 p-3">
          <summary className="text-sm font-medium text-brand-text cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 rounded">
            {t("copilot.section.sources")} (<span dir="ltr">{run.sources.length}</span>)
          </summary>
          <ul className="mt-2 space-y-1 text-xs text-brand-text-muted">
            {run.sources.map((source) => (
              <li key={source.id} className="flex items-center gap-2 break-words">
                <Eye className="w-3.5 h-3.5 shrink-0" aria-hidden="true" />
                <Badge variant="neutral" size="sm">
                  {t(`copilot.source_type.${source.source_type}`, source.source_type)}
                </Badge>
                <span>{source.descriptor}</span>
              </li>
            ))}
          </ul>
        </details>
      )}

      {/* Omissions (what the Copilot could not see) */}
      {run.context?.omissions && run.context.omissions.length > 0 && (
        <p className="mt-3 text-xs text-brand-text-muted break-words">
          {t("copilot.section.omissions")}:{" "}
          {run.context.omissions.map((o) => t(`copilot.omission.${o}`, o)).join("، ")}
        </p>
      )}

      {/* Actions */}
      <div className="mt-5 flex flex-wrap gap-2" role="group" aria-label={t("copilot.actions_group")}>
        {editing ? (
          <>
            <Button size="sm" onClick={submitEdit} disabled={busy} isLoading={busy}>
              {t("copilot.action.save_edit")}
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setEditing(false)}>
              {t("copilot.action.cancel_edit")}
            </Button>
          </>
        ) : rejecting ? (
          <>
            <input
              aria-label={t("copilot.field.review_note")}
              className="flex-1 min-w-[160px] rounded-lg bg-obsidian-900 border border-obsidian-700 px-3 py-2 text-sm text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
              placeholder={t("copilot.field.review_note_placeholder")}
              value={note}
              onChange={(event) => setNote(event.target.value)}
              maxLength={500}
            />
            <Button
              size="sm"
              variant="danger"
              disabled={busy}
              isLoading={busy}
              onClick={() => onReject(note).then(() => setRejecting(false))}
            >
              {t("copilot.action.confirm_reject")}
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setRejecting(false)}>
              {t("copilot.action.cancel_edit")}
            </Button>
          </>
        ) : reporting ? (
          <>
            <select
              aria-label={t("copilot.field.report_type")}
              className="rounded-lg bg-obsidian-900 border border-obsidian-700 px-2 py-2 text-sm text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
              value={reportType}
              onChange={(event) => setReportType(event.target.value)}
            >
              {["unsafe", "incorrect", "privacy", "hallucinated_source", "other"].map((type) => (
                <option key={type} value={type}>
                  {t(`copilot.report_type.${type}`)}
                </option>
              ))}
            </select>
            <input
              aria-label={t("copilot.field.report_detail")}
              className="flex-1 min-w-[160px] rounded-lg bg-obsidian-900 border border-obsidian-700 px-3 py-2 text-sm text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
              placeholder={t("copilot.field.report_detail_placeholder")}
              value={note}
              onChange={(event) => setNote(event.target.value)}
              maxLength={1000}
            />
            <Button
              size="sm"
              variant="secondary"
              disabled={busy}
              isLoading={busy}
              onClick={() => onReport(reportType, note).then(() => setReporting(false))}
            >
              {t("copilot.action.confirm_report")}
            </Button>
            <Button size="sm" variant="ghost" onClick={() => setReporting(false)}>
              {t("copilot.action.cancel_edit")}
            </Button>
          </>
        ) : (
          <>
            {canReview && run.actions?.can_edit && run.capability !== "suggest_program_adjustment" && (
              <Button size="sm" variant="secondary" onClick={startEdit}>
                {t("copilot.action.edit")}
              </Button>
            )}
            {canReview && (
              <Button
                size="sm"
                disabled={busy}
                isLoading={busy}
                onClick={() => {
                  if (window.confirm(t("copilot.action.approve_confirm"))) {
                    void onApprove("");
                  }
                }}
              >
                <CheckCircle2 className="w-4 h-4 me-1" aria-hidden="true" />
                {t("copilot.action.approve")}
              </Button>
            )}
            {canReview && (
              <Button size="sm" variant="outline" onClick={() => setRejecting(true)}>
                <XCircle className="w-4 h-4 me-1" aria-hidden="true" />
                {t("copilot.action.reject")}
              </Button>
            )}
            {run.actions?.can_regenerate && (
              <Button
                size="sm"
                variant="ghost"
                disabled={busy}
                isLoading={busy}
                onClick={() => onRegenerate()}
              >
                <RefreshCw className="w-4 h-4 me-1" aria-hidden="true" />
                {t("copilot.action.regenerate")}
              </Button>
            )}
            <Button size="sm" variant="ghost" onClick={copyDraft}>
              <ClipboardCopy className="w-4 h-4 me-1" aria-hidden="true" />
              {copyState === "copied" ? t("copilot.action.copied") : t("copilot.action.copy")}
            </Button>
            {run.actions?.can_report && (
              <Button size="sm" variant="ghost" onClick={() => setReporting(true)}>
                <AlertTriangle className="w-4 h-4 me-1" aria-hidden="true" />
                {t("copilot.action.report")}
              </Button>
            )}
          </>
        )}
      </div>

      <p className="mt-4 text-[11px] text-brand-text-muted break-all" dir="ltr">
        <bdi>
          run {run.id} · {run.provider_slug} · policy {run.policy_version} · v
          {output.schema_version} · {run.model_identifier}
        </bdi>
      </p>
      <span className="sr-only" role="status" aria-live="polite">
        {locale === "fa-IR" ? "پیش‌نویس آماده بازبینی است" : "Draft ready for review"}
      </span>
    </Card>
  );
}
