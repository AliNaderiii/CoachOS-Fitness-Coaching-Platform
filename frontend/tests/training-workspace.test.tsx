import React from "react";
import { fireEvent, render, screen, within } from "@testing-library/react";
import "@testing-library/jest-dom";
import { describe, expect, it } from "vitest";
import { DirectionProvider } from "../components/layout/DirectionProvider";
import { TrainingWorkspace } from "../components/training/TrainingWorkspace";

function renderWorkspace(locale: "fa-IR" | "en-US" = "en-US") {
  return render(
    <DirectionProvider locale={locale}>
      <TrainingWorkspace />
    </DirectionProvider>,
  );
}

describe("Phase 06 training workspace", () => {
  it("renders a keyboard-operable coach/owner program hierarchy", () => {
    renderWorkspace();
    expect(screen.getByRole("heading", { name: "Exercise library and program builder" })).toBeVisible();
    expect(screen.getByRole("tree", { name: "Program outline" })).toBeVisible();
    expect(screen.getByRole("button", { name: "Move exercise up" })).toHaveClass("min-h-touch");
    expect(screen.getByRole("button", { name: "Move exercise down" })).toBeEnabled();
  });

  it("folds Persian keyboard variants while searching the bilingual catalog", () => {
    renderWorkspace("fa-IR");
    const search = screen.getByRole("searchbox", { name: "جست‌وجوی حرکت" });
    fireEvent.change(search, { target: { value: "پرس سينه" } });
    const workspace = screen.getByTestId("training-workspace");
    expect(within(workspace).getAllByText("پرس سینه دمبل").length).toBeGreaterThan(0);
    expect(within(workspace).queryByText("اسکوات پشت با هالتر")).not.toBeInTheDocument();
    expect(document.documentElement).toHaveAttribute("dir", "rtl");
    expect(document.documentElement).toHaveAttribute("lang", "fa-IR");
  });

  it("filters equipment, edits a prescription, and announces save status", () => {
    renderWorkspace();
    fireEvent.change(screen.getByRole("combobox", { name: "Equipment" }), {
      target: { value: "barbell" },
    });
    expect(screen.getByRole("button", { name: /Barbell Back Squat/ })).toBeVisible();
    expect(screen.queryByRole("button", { name: /Dumbbell Chest Press/ })).not.toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("Sets"), { target: { value: "5" } });
    expect(screen.getByText(/5 × 8/)).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: "Save program" }));
    expect(screen.getByRole("status")).toHaveTextContent(
      "Program draft is ready to save to the active organization.",
    );
  });

  it("keeps English and Persian dictionary labels at parity", async () => {
    const en = await import("../lib/i18n/dictionaries/en-US.json");
    const fa = await import("../lib/i18n/dictionaries/fa-IR.json");
    expect(Object.keys(en.default.training).sort()).toEqual(Object.keys(fa.default.training).sort());
  });
});
