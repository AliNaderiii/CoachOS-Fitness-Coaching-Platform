import { describe, it, expect } from "vitest";
import { isolateLtr, isolateRtl, formatPrescriptionBidi } from "../lib/i18n/bidi";

describe("Bidirectional (BiDi) Text Utilities", () => {
  it("wraps LTR text in FSI/PDI directional isolate marks", () => {
    const ltrSnippet = "100 kg x 5 reps";
    const isolated = isolateLtr(ltrSnippet);
    expect(isolated.startsWith("\u2068")).toBe(true);
    expect(isolated.endsWith("\u2069")).toBe(true);
    expect(isolated).toContain(ltrSnippet);
  });

  it("wraps RTL text in RTL isolate marks", () => {
    const rtlSnippet = "پرس سینه هالتر";
    const isolated = isolateRtl(rtlSnippet);
    expect(isolated.startsWith("\u2067")).toBe(true);
    expect(isolated.endsWith("\u2069")).toBe(true);
    expect(isolated).toContain(rtlSnippet);
  });

  it("formats workout prescriptions cleanly with multiplication symbol", () => {
    const formatted = formatPrescriptionBidi(3, 10, 100, "kg");
    expect(formatted).toBe("3 × 10 (100 kg)");

    const formattedNoWeight = formatPrescriptionBidi(4, 12);
    expect(formattedNoWeight).toBe("4 × 12");
  });
});
