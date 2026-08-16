import React from "react";
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { DirectionProvider } from "../components/layout/DirectionProvider";
import { SetLogger } from "../components/athlete/SetLogger";
import { RestTimer } from "../components/athlete/RestTimer";
import { SubstitutionModal } from "../components/athlete/SubstitutionModal";
import { FeedbackFlagForm } from "../components/athlete/FeedbackFlagForm";
import { OfflineBanner } from "../components/athlete/OfflineBanner";
import { TodayDashboard } from "../components/athlete/TodayDashboard";
import { WorkoutSessionView } from "../components/athlete/WorkoutSessionView";
import { ApiError } from "../lib/api/client";
import { fromKg, parseNumber, toKg, type Unit } from "../lib/athlete/units";
import * as athleteApi from "../lib/api/athlete";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn(), replace: vi.fn() }),
  usePathname: () => "/fa-IR",
  useParams: () => ({ sessionId: "sess-1" }),
}));

vi.mock("../lib/api/athlete", () => ({
  getTodayWorkout: vi.fn(),
  startSession: vi.fn(),
  getSession: vi.fn(),
  getMe: vi.fn(),
  logSet: vi.fn(),
  completeSession: vi.fn(),
  substitute: vi.fn(),
  addFeedbackFlag: vi.fn(),
  listBodyMetrics: vi.fn(),
  createBodyMetric: vi.fn(),
  listProgressPhotos: vi.fn(),
  uploadProgressPhoto: vi.fn(),
  listConsents: vi.fn(),
  grantConsent: vi.fn(),
  revokeConsent: vi.fn(),
}));

const renderWith = (locale: "fa-IR" | "en-US", ui: React.ReactNode) =>
  render(<DirectionProvider locale={locale}>{ui}</DirectionProvider>);

const pushMock = vi.fn();

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(athleteApi.getMe).mockResolvedValue({
    user: { id: "athlete-1", preferred_unit: "kg", preferred_locale: "en-US" },
    memberships: [],
  });
  vi.mocked(athleteApi.getSession).mockResolvedValue({
    id: "sess-1",
    organization_id: "org-1",
    program_assignment_id: "assign-1",
    athlete_user_id: "athlete-1",
    scheduled_date: "2026-08-15",
    status: "in_progress",
    workouts: [
      {
        title: "Push and pull",
        items: [
          {
            exercise_id: "ex-1",
            name: "Bench Press",
            rest_seconds_between_sets: 90,
            prescriptions: [
              { set_index: 1, target_reps: "8", target_load: "80 kg" },
              { set_index: 2, target_reps: "8", target_load: "80 kg" },
            ],
          },
        ],
      },
    ],
    set_logs: [],
  });
});

describe("units conversion policy", () => {
  it("converts lbs to kg and back", () => {
    expect(toKg(100, "lbs")).toBeCloseTo(45.36, 1);
    expect(fromKg(45.36, "lbs")).toBeCloseTo(100, 0);
    expect(toKg(80, "kg")).toBe(80);
  });

  it("parses localized decimal input", () => {
    expect(parseNumber("82٫5")).toBe(82.5);
    expect(parseNumber("82.5")).toBe(82.5);
    expect(parseNumber("")).toBeNull();
    expect(parseNumber("abc")).toBeNull();
  });
});

describe("SetLogger", () => {
  it("logs a set converting load to kg", async () => {
    const onLog = vi.fn();
    renderWith("en-US", (
      <SetLogger exerciseName="Bench Press" preferredUnit="lbs" onLog={onLog} />
    ));
    fireEvent.change(screen.getByLabelText("Reps"), { target: { value: "8" } });
    fireEvent.change(screen.getByLabelText("Load"), { target: { value: "100" } });
    fireEvent.click(screen.getByRole("button", { name: "Log set" }));
    await waitFor(() => expect(onLog).toHaveBeenCalledTimes(1));
    const logged = onLog.mock.calls[0][0];
    expect(logged.set_index).toBe(1);
    expect(logged.actual_reps).toBe(8);
    expect(logged.actual_load_kg).toBeCloseTo(45.36, 1);
  });

  it("rejects invalid reps", async () => {
    const onLog = vi.fn();
    renderWith("en-US", <SetLogger exerciseName="X" preferredUnit="kg" onLog={onLog} />);
    fireEvent.change(screen.getByLabelText("Reps"), { target: { value: "-1" } });
    fireEvent.click(screen.getByRole("button", { name: "Log set" }));
    expect(onLog).not.toHaveBeenCalled();
  });
});

describe("RestTimer", () => {
  it("renders countdown and skips", () => {
    vi.useFakeTimers();
    renderWith("en-US", <RestTimer seconds={2} />);
    expect(screen.getByText("Rest")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Skip rest" }));
    vi.useRealTimers();
  });
});

describe("SubstitutionModal", () => {
  it("requires a reason and confirms", async () => {
    const onConfirm = vi.fn().mockResolvedValue(undefined);
    renderWith("en-US", (
      <SubstitutionModal
        isOpen
        onClose={() => {}}
        originalExerciseName="Bench Press"
        originalExerciseId="ex-1"
        alternatives={[{ exercise_id: "ex-2", name: "Dumbbell Row" }]}
        onConfirm={onConfirm}
      />
    ));
    fireEvent.click(screen.getByText("Dumbbell Row"));
    // no reason selected -> error
    fireEvent.click(screen.getByRole("button", { name: "Confirm substitution" }));
    expect(onConfirm).not.toHaveBeenCalled();
    fireEvent.click(screen.getByText("Preference"));
    fireEvent.click(screen.getByRole("button", { name: "Confirm substitution" }));
    await waitFor(() => expect(onConfirm).toHaveBeenCalled());
    const input = onConfirm.mock.calls[0][0];
    expect(input.reason).toBe("preference");
    expect(input.substituted_exercise_id).toBe("ex-2");
  });
});

describe("FeedbackFlagForm", () => {
  it("submits a non-clinical flag", async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    renderWith("en-US", <FeedbackFlagForm onSubmit={onSubmit} />);
    fireEvent.click(screen.getByText("Joint pain"));
    fireEvent.change(screen.getByLabelText("Anatomical location"), { target: { value: "left knee" } });
    fireEvent.click(screen.getByText("Moderate"));
    fireEvent.change(screen.getByLabelText("Details"), { target: { value: "slight discomfort" } });
    fireEvent.click(screen.getByRole("button", { name: "Submit report" }));
    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1));
    const input = onSubmit.mock.calls[0][0];
    expect(input.flag_type).toBe("joint_pain");
    expect(input.severity).toBe("moderate");
    expect(input.anatomical_location).toBe("left knee");
  });
});

describe("OfflineBanner", () => {
  it("shows offline notice when offline and nothing when online", () => {
    const { unmount } = renderWith("en-US", <OfflineBanner online={false} pendingCount={2} />);
    expect(screen.getByText(/unsaved input is kept in memory/i)).toBeInTheDocument();
    unmount();
    renderWith("en-US", <OfflineBanner online />);
    expect(screen.queryByRole("status")).toBeNull();
  });
});

describe("TodayDashboard", () => {
  it("shows empty state when no workout scheduled", async () => {
    vi.mocked(athleteApi.getTodayWorkout).mockResolvedValue({ date: "2026-08-15", scheduled_workouts: [] });
    renderWith("en-US", <TodayDashboard />);
    expect(await screen.findByText("No workout scheduled today")).toBeInTheDocument();
  });

  it("shows error state and retry", async () => {
    vi.mocked(athleteApi.getTodayWorkout).mockRejectedValueOnce(new ApiError({ title: "boom", status: 500 }, "req-1"));
    renderWith("en-US", <TodayDashboard />);
    expect(await screen.findByText("Could not load today's workout")).toBeInTheDocument();
    vi.mocked(athleteApi.getTodayWorkout).mockResolvedValue({ date: "2026-08-15", scheduled_workouts: [] });
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    await screen.findByText("No workout scheduled today");
  });

  it("starts a workout and navigates", async () => {
    vi.mocked(athleteApi.getTodayWorkout).mockResolvedValue({
      date: "2026-08-15",
      scheduled_workouts: [
        {
          session_id: null,
          assignment_id: "assign-1",
          title: "Push and pull",
          status: "scheduled",
          workout: {
            title: "Push and pull",
            items: [
              { exercise_id: "ex-1", name: "Bench Press", prescriptions: [{ set_index: 1, target_reps: "8" }] },
            ],
          },
        },
      ],
    });
    vi.mocked(athleteApi.startSession).mockResolvedValue({
      id: "sess-1",
      organization_id: "org-1",
      program_assignment_id: "assign-1",
      athlete_user_id: "athlete-1",
      scheduled_date: "2026-08-15",
      status: "in_progress",
      workouts: [],
      set_logs: [],
    });
    renderWith("en-US", <TodayDashboard />);
    fireEvent.click(await screen.findByRole("button", { name: "Start workout" }));
    await waitFor(() => expect(athleteApi.startSession).toHaveBeenCalled());
  });
});

describe("WorkoutSessionView", () => {
  it("shows forbidden when not authorized", async () => {
    vi.mocked(athleteApi.getSession).mockRejectedValueOnce(new ApiError({ title: "Forbidden", status: 403 }, "req-1"));
    renderWith("en-US", <WorkoutSessionView sessionId="sess-1" />);
    expect(await screen.findByText("Not authorized")).toBeInTheDocument();
  });

  it("renders session workout and complete button", async () => {
    renderWith("en-US", <WorkoutSessionView sessionId="sess-1" />);
    expect(await screen.findByText("Push and pull")).toBeInTheDocument();
    expect(await screen.findByText("Bench Press")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Complete workout/i })).toBeInTheDocument();
  });

  it("renders in Persian RTL locale", async () => {
    vi.mocked(athleteApi.getSession).mockResolvedValue({
      id: "sess-1",
      organization_id: "org-1",
      program_assignment_id: "assign-1",
      athlete_user_id: "athlete-1",
      scheduled_date: "2026-08-15",
      status: "in_progress",
      workouts: [
        { title: "تمرین فشاری و کششی", items: [{ exercise_id: "ex-1", name: "پرس سینه", prescriptions: [{ set_index: 1, target_reps: "۸" }] }] },
      ],
      set_logs: [],
    });
    renderWith("fa-IR", <WorkoutSessionView sessionId="sess-1" />);
    expect(await screen.findByText("جلسه تمرین")).toBeInTheDocument();
  });
});
