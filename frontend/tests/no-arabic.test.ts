import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

describe("Language Governance - Strict Arabic Exclusion (ADR-003)", () => {
  it("ensures no Arabic translation files exist in the frontend workspace", () => {
    const dictionariesDir = path.resolve(__dirname, "../lib/i18n/dictionaries");
    const files = fs.readdirSync(dictionariesDir);

    const arabicFiles = files.filter((f) => f.startsWith("ar-") || f === "ar.json");
    expect(arabicFiles).toEqual([]);

    // Check that only fa-IR.json and en-US.json exist
    expect(files.sort()).toEqual(["en-US.json", "fa-IR.json"].sort());
  });

  it("ensures public directory does not contain Arabic manifest or assets", () => {
    const publicDir = path.resolve(__dirname, "../public");
    const files = fs.readdirSync(publicDir);

    const arabicAssets = files.filter((f) => f.includes("ar-") || f.includes("-ar"));
    expect(arabicAssets).toEqual([]);
  });
});
