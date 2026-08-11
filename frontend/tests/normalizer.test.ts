import { describe, it, expect } from "vitest";
import { normalizePersianSearch } from "../lib/i18n/normalizer";

describe("Frontend Persian Search Normalizer (ADR-018)", () => {
  it("folds Arabic Yeh and Kaf to Persian equivalents", () => {
    const raw = "حركت اسكوات با هالتر يكي";
    const normalized = normalizePersianSearch(raw);

    expect(normalized).toContain("ک");
    expect(normalized).toContain("ی");
    expect(normalized).not.toContain("ك");
    expect(normalized).not.toContain("ي");
  });

  it("folds Arabic-Indic digits to Persian digits", () => {
    const raw = "تمرین ١٢٣٤٥";
    const normalized = normalizePersianSearch(raw);

    expect(normalized).toContain("۱۲۳۴۵");
    expect(normalized).not.toContain("١");
  });

  it("strips Persian and Arabic diacritics", () => {
    const raw = "حَرَکَتِ اِسْکُوات";
    const normalized = normalizePersianSearch(raw);

    expect(normalized).toBe("حرکت اسکوات");
  });

  it("handles zero-width non-joiners gracefully", () => {
    const raw = "می‌خواهم شنا\u200Cسوئدی";
    const normalized = normalizePersianSearch(raw, false);

    expect(normalized).not.toContain("\u200C");
    expect(normalized).toContain("شنا");
  });
});
