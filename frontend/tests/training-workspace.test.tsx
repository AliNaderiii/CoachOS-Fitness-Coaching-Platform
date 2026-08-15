import React from "react";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { DirectionProvider } from "../components/layout/DirectionProvider";
import { TrainingWorkspace } from "../components/training/TrainingWorkspace";
import { ApiError } from "../lib/api/client";
import {
  createProgram,
  listExercises,
  listOrganizations,
  type ExerciseSummary,
} from "../lib/api/training";

vi.mock("../lib/api/training", () => ({
  listOrganizations: vi.fn(),
  listExercises: vi.fn(),
  createProgram: vi.fn(),
  cloneProgram: vi.fn(),
}));

const exercise: ExerciseSummary = {
  id: "exercise-1",
  organization_id: null,
  movement_pattern: "horizontal_push",
  difficulty: "beginner",
  primary_muscles: ["chest"],
  equipment_required: ["dumbbell"],
  translations: [
    {
      locale: "fa-IR",
      name: "پرس سینه دمبل",
      instructions: "کنترل حرکت",
      coaching_cues: [],
      common_mistakes: [],
    },
    {
      locale: "en-US",
      name: "Dumbbell Chest Press",
      instructions: "Control the movement",
      coaching_cues: [],
      common_mistakes: [],
    },
  ],
};

function renderWorkspace(locale: "fa-IR" | "en-US" = "en-US") {
  return render(
    <DirectionProvider locale={locale}>
      <TrainingWorkspace />
    </DirectionProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(listOrganizations).mockResolvedValue({
    organizations: [{ id: "org-1", name: "Alborz Fitness", slug: "alborz" }],
  });
  vi.mocked(listExercises).mockResolvedValue({ exercises: [exercise], count: 1 });
  vi.mocked(createProgram).mockResolvedValue({ id: "program-1", version: 1 });
});

describe("Phase 06 integrated training workspace", () => {
  it("loads the authenticated organization context and API catalog", async () => {
    renderWorkspace();
    expect(screen.getByText("Loading organization context…")).toBeVisible();
    expect(await screen.findByRole("combobox", { name: "Active organization" })).toHaveValue(
      "org-1",
    );
    expect(await screen.findByRole("button", { name: /Dumbbell Chest Press/ })).toBeVisible();
    expect(listOrganizations).toHaveBeenCalledWith("en-US");
    expect(listExercises).toHaveBeenCalledWith("org-1", {
      q: undefined,
      equipment: undefined,
      locale: "en-US",
    });
  });

  it("sends search and equipment filters to listExercises without fake fallback data", async () => {
    renderWorkspace("fa-IR");
    expect((await screen.findAllByText("پرس سینه دمبل")).length).toBeGreaterThan(0);
    fireEvent.change(screen.getByRole("searchbox", { name: "جست‌وجوی حرکت" }), {
      target: { value: "پرس سينه" },
    });
    fireEvent.change(screen.getByRole("combobox", { name: "تجهیزات" }), {
      target: { value: "dumbbell" },
    });
    await waitFor(() =>
      expect(listExercises).toHaveBeenLastCalledWith("org-1", {
        q: "پرس سينه",
        equipment: "dumbbell",
        locale: "fa-IR",
      }),
    );
    expect(document.documentElement).toHaveAttribute("dir", "rtl");
  });

  it("renders empty, error, retry, and unauthorized states", async () => {
    vi.mocked(listExercises).mockResolvedValueOnce({ exercises: [], count: 0 });
    const view = renderWorkspace();
    expect(await screen.findByText("No exercises match these filters.")).toBeVisible();

    view.unmount();
    vi.mocked(listOrganizations).mockRejectedValueOnce(
      new ApiError({ title: "Permission denied", status: 403 }),
    );
    renderWorkspace();
    expect(
      await screen.findByText("You are not authorized to use this coach or owner workspace."),
    ).toBeVisible();
  });

  it("shows catalog failure and retries the API request", async () => {
    vi.mocked(listExercises)
      .mockRejectedValueOnce(new Error("network"))
      .mockResolvedValueOnce({ exercises: [exercise], count: 1 });
    renderWorkspace();
    expect(await screen.findByText("Exercise catalog could not be loaded.")).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    expect(await screen.findByRole("button", { name: /Dumbbell Chest Press/ })).toBeVisible();
    expect(listExercises).toHaveBeenCalledTimes(2);
  });

  it("persists the constructed program through createProgram and reports success", async () => {
    renderWorkspace();
    await screen.findByRole("button", { name: /Dumbbell Chest Press/ });
    fireEvent.change(screen.getByLabelText("Program title"), {
      target: { value: "Strength Base" },
    });
    fireEvent.change(screen.getByLabelText("Sets"), { target: { value: "3" } });
    fireEvent.click(screen.getByRole("button", { name: "Save program" }));

    await waitFor(() => expect(createProgram).toHaveBeenCalledTimes(1));
    const [payload, locale] = vi.mocked(createProgram).mock.calls[0];
    expect(locale).toBe("en-US");
    expect(payload.org_id).toBe("org-1");
    expect(payload.title).toBe("Strength Base");
    expect(payload.phases[0].weeks[0].days[0].workouts[0].items[0].exercise_id).toBe(
      "exercise-1",
    );
    expect(
      payload.phases[0].weeks[0].days[0].workouts[0].items[0].prescriptions,
    ).toHaveLength(3);
    expect(await screen.findByRole("status")).toHaveTextContent("program-1");
  });

  it("shows save failure without claiming local persistence", async () => {
    let rejectSave: (reason?: unknown) => void = () => undefined;
    vi.mocked(createProgram).mockReturnValueOnce(
      new Promise((_, reject) => {
        rejectSave = reject;
      }),
    );
    renderWorkspace();
    await screen.findByRole("button", { name: /Dumbbell Chest Press/ });
    fireEvent.change(screen.getByLabelText("Program title"), { target: { value: "Plan" } });
    fireEvent.click(screen.getByRole("button", { name: "Save program" }));
    expect(screen.getByRole("button", { name: "Save program" })).toBeDisabled();
    await act(async () => rejectSave(new Error("save failed")));
    expect(await screen.findByRole("alert")).toHaveTextContent("Program could not be saved");
  });

  it("keeps English and Persian dictionary labels at parity", async () => {
    const en = await import("../lib/i18n/dictionaries/en-US.json");
    const fa = await import("../lib/i18n/dictionaries/fa-IR.json");
    expect(Object.keys(en.default.training).sort()).toEqual(Object.keys(fa.default.training).sort());
  });
});
