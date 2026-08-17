import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { DirectionProvider } from "../components/layout/DirectionProvider";
import { CopilotConsole } from "../components/copilot/CopilotConsole";
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
  type CopilotCapabilitiesResponse,
  type CopilotRun,
} from "../lib/api/copilot";
import { listOrganizations } from "../lib/api/training";

vi.mock("../lib/api/training", () => ({
  listOrganizations: vi.fn(),
  listExercises: vi.fn(),
  createProgram: vi.fn(),
  cloneProgram: vi.fn(),
}));

vi.mock("../lib/api/copilot", () => ({
  listCopilotCapabilities: vi.fn(),
  listCopilotRuns: vi.fn(),
  listAuthorizedAssignments: vi.fn(),
  createCopilotRun: vi.fn(),
  getCopilotRun: vi.fn(),
  cancelCopilotRun: vi.fn(),
  regenerateCopilotRun: vi.fn(),
  editCopilotOutput: vi.fn(),
  reviewCopilotOutput: vi.fn(),
  reportCopilotRun: vi.fn(),
}));

const capabilitiesResponse: CopilotCapabilitiesResponse = {
  feature: { enabled: true },
  policy_version: "2026-08-16.v1",
  provider: {
    provider_slug: "fake-deterministic",
    provider_enabled: true,
    model_identifier: "fake-deterministic-1",
  },
  capabilities: [
    {
      id: "summarize_progress",
      output_schema: "ai_progress_summary.v1",
      requires_human_review: true,
      enabled: true,
      label: { "en-US": "Progress summary", "fa-IR": "خلاصه پیشرفت" },
    },
    {
      id: "draft_check_in",
      output_schema: "ai_check_in_message.v1",
      requires_human_review: true,
      enabled: true,
      label: { "en-US": "Check-in", "fa-IR": "پیگیری" },
    },
    {
      id: "suggest_program_adjustment",
      output_schema: "ai_program_adjustment.v1",
      requires_human_review: true,
      enabled: true,
      label: { "en-US": "Adjustment", "fa-IR": "تعدیل" },
    },
  ],
  limits: {
    rate_limit_per_minute: 10,
    daily_run_quota_per_actor: 20,
    daily_run_quota_per_org: 100,
    retention_days: 30,
  },
  prohibited_notice_key: "copilot.prohibited_notice",
};

const succeededRun: CopilotRun = {
  id: "run-1",
  capability: "summarize_progress",
  generation_language: "en-US",
  status: "succeeded",
  athlete_id: "athlete-1",
  policy_version: "2026-08-16.v1",
  provider_slug: "fake-deterministic",
  model_identifier: "fake-deterministic-1",
  attempt_count: 1,
  duration_ms: 5,
  cost_micro_usd: 10,
  error_code: "",
  fallback_applied: false,
  created_at: "2026-08-16T10:00:00Z",
  completed_at: "2026-08-16T10:00:01Z",
  expires_at: "2026-09-15T10:00:00Z",
  context: {
    payload: { period_days: 14 },
    limitations: ["AI-generated draft — coach review is required before any use."],
    omissions: ["progress_photos", "body_metrics"],
  },
  output: {
    id: "out-1",
    schema_name: "ai_progress_summary.v1",
    schema_version: 1,
    validation_status: "valid",
    status: "draft",
    was_edited: false,
    payload: {
      schema_name: "ai_progress_summary.v1",
      schema_version: 1,
      ai_generated: true,
      requires_human_review: true,
      athlete_display_name: "Saeed",
      period_days: 14,
      sessions_completed: 3,
      sessions_missed: 1,
      summary: "In the last 14 days, 3 sessions were completed and 1 were missed.",
      highlights: ["Heaviest recorded set: Bench Press at 100 kg for 5 reps."],
      concerns: ["1 missed sessions in this period; align on the reason with the athlete."],
      limitations: ["AI-generated draft — coach review is required before any use."],
      source_ids: ["session-1"],
    },
  },
  sources: [
    {
      id: "src-1",
      source_type: "workout_session",
      source_id: "session-1",
      descriptor: "2026-08-15 · completed",
      ordinal: 1,
    },
  ],
  actions: {
    can_cancel: false,
    can_regenerate: true,
    can_edit: true,
    can_approve: true,
    can_reject: true,
    can_report: true,
  },
  ai_generated: true,
  requires_human_review: true,
};

function renderConsole(locale: "fa-IR" | "en-US" = "en-US") {
  return render(
    <DirectionProvider locale={locale}>
      <CopilotConsole />
    </DirectionProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(listOrganizations).mockResolvedValue({
    organizations: [{ id: "org-1", name: "Alborz Fitness", slug: "alborz" }],
  });
  vi.mocked(listCopilotCapabilities).mockResolvedValue(capabilitiesResponse);
  vi.mocked(listAuthorizedAssignments).mockResolvedValue({
    assignments: [
      { id: "assign-1", athlete_user_id: "athlete-1", status: "active", start_date: "2026-08-01" },
    ],
  });
  vi.mocked(listCopilotRuns).mockResolvedValue({ runs: [], count: 0, retention_days: 30 });
  vi.mocked(createCopilotRun).mockResolvedValue(succeededRun);
  vi.mocked(getCopilotRun).mockResolvedValue(succeededRun);
  vi.mocked(reviewCopilotOutput).mockResolvedValue({
    ...succeededRun,
    output: { ...succeededRun.output!, status: "approved" },
  });
  vi.mocked(regenerateCopilotRun).mockResolvedValue({ ...succeededRun, id: "run-2" });
  vi.mocked(reportCopilotRun).mockResolvedValue(succeededRun);
  vi.mocked(editCopilotOutput).mockResolvedValue({
    ...succeededRun,
    output: { ...succeededRun.output!, status: "edited", was_edited: true },
  });
});

async function runSummaryFlow() {
  renderConsole();
  const athleteSelect = await screen.findByRole("combobox", { name: "Athlete context" });
  fireEvent.change(athleteSelect, { target: { value: "athlete-1" } });
  const runButton = screen.getByRole("button", { name: "Generate draft" });
  fireEvent.click(runButton);
  await screen.findByTestId("copilot-result-card");
}

describe("Phase 11 Copilot console", () => {
  it("renders the capability picker with three governed capabilities (not a chat box)", async () => {
    renderConsole();
    expect(await screen.findByText("Choose one capability (no free-form chat)")).toBeVisible();
    expect(await screen.findByText("Progress summary")).toBeVisible();
    expect(screen.getByText("Check-in message draft")).toBeVisible();
    expect(screen.getByText("Program adjustment suggestion")).toBeVisible();
    expect(screen.getByText(/never provides medical advice/)).toBeVisible();
    expect(screen.queryByRole("textbox", { name: /message/i })).not.toBeInTheDocument();
  });

  it("shows the disabled empty state when the feature flag is off", async () => {
    vi.mocked(listCopilotCapabilities).mockResolvedValue({
      ...capabilitiesResponse,
      feature: { enabled: false, disabled_reason: "feature_disabled" },
    });
    renderConsole();
    expect(await screen.findByTestId("copilot-disabled-state")).toBeVisible();
    expect(screen.getByText("The Copilot is currently disabled")).toBeVisible();
  });

  it("requests a run and renders the labeled draft with sources, limitations and omissions", async () => {
    await runSummaryFlow();
    expect(createCopilotRun).toHaveBeenCalledOnce();
    const call = vi.mocked(createCopilotRun).mock.calls[0];
    expect(call[0]).toBe("org-1");
    expect(call[1]).toMatchObject({
      capability: "summarize_progress",
      athleteId: "athlete-1",
      generationLanguage: "en-US",
    });
    expect(typeof call[2]).toBe("string"); // idempotency key generated per request
    expect(await screen.findByText("AI draft — review required")).toBeVisible();
    expect(screen.getByText(/3 sessions were completed/)).toBeVisible();
    expect(screen.getByText("Limitations & uncertainty")).toBeVisible();
    expect(screen.getByText(/Sources the Copilot used/)).toBeInTheDocument();
    // Source descriptors live behind an expandable disclosure widget.
    expect(screen.getByText(/2026-08-15 · completed/)).toBeInTheDocument();
    expect(screen.getByText(/Deliberately not seen/)).toBeVisible();
    expect(screen.getByText(/progress photos/)).toBeVisible();
  });

  it("approve is an explicit confirming human action", async () => {
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValue(true);
    await runSummaryFlow();
    fireEvent.click(screen.getByRole("button", { name: /^Approve$/ }));
    await waitFor(() => expect(reviewCopilotOutput).toHaveBeenCalledOnce());
    expect(vi.mocked(reviewCopilotOutput).mock.calls[0][2]).toBe("approve");
    expect(confirmSpy).toHaveBeenCalled();
    confirmSpy.mockRestore();
  });

  it("reject requires an explicit confirm step and sends the note", async () => {
    await runSummaryFlow();
    fireEvent.click(screen.getByRole("button", { name: /^Reject$/ }));
    const noteField = screen.getByLabelText("Review note");
    fireEvent.change(noteField, { target: { value: "Too vague" } });
    fireEvent.click(screen.getByRole("button", { name: "Confirm reject" }));
    await waitFor(() => expect(reviewCopilotOutput).toHaveBeenCalledOnce());
    expect(vi.mocked(reviewCopilotOutput).mock.calls[0][3]).toBe("Too vague");
  });

  it("regenerate calls the linked-regeneration endpoint", async () => {
    await runSummaryFlow();
    fireEvent.click(screen.getByRole("button", { name: "Regenerate" }));
    await waitFor(() => expect(regenerateCopilotRun).toHaveBeenCalledOnce());
    expect(vi.mocked(regenerateCopilotRun).mock.calls[0][1]).toBe("run-1");
  });

  it("report flow submits a structured report", async () => {
    await runSummaryFlow();
    fireEvent.click(screen.getByRole("button", { name: "Report" }));
    fireEvent.change(screen.getByLabelText("Report details"), {
      target: { value: "Wrong athlete data" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Submit report" }));
    await waitFor(() => expect(reportCopilotRun).toHaveBeenCalledOnce());
    expect(vi.mocked(reportCopilotRun).mock.calls[0][2]).toBe("unsafe");
    expect(vi.mocked(reportCopilotRun).mock.calls[0][3]).toBe("Wrong athlete data");
  });

  it("edit mode submits only a full edited payload (revalidated server-side)", async () => {
    await runSummaryFlow();
    fireEvent.click(screen.getByRole("button", { name: "Edit draft" }));
    const summaryField = screen.getByLabelText("Summary");
    fireEvent.change(summaryField, { target: { value: "Coach-edited summary." } });
    fireEvent.click(screen.getByRole("button", { name: "Save edits" }));
    await waitFor(() => expect(editCopilotOutput).toHaveBeenCalledOnce());
    const payload = vi.mocked(editCopilotOutput).mock.calls[0][2];
    expect(payload.summary).toBe("Coach-edited summary.");
    expect(payload.schema_name).toBe("ai_progress_summary.v1");
    expect(payload.source_ids).toEqual(["session-1"]);
  });

  it("renders Persian RTL copy for fa-IR", async () => {
    render(
      <DirectionProvider locale="fa-IR">
        <CopilotConsole />
      </DirectionProvider>,
    );
    expect(await screen.findByText("کوپایلوت مربی")).toBeVisible();
    expect(screen.getByText("انسان در حلقه تصمیم")).toBeVisible();
    expect(document.documentElement.dir).toBe("rtl");
    expect(document.documentElement.lang).toBe("fa-IR");
  });
});
