import { describe, it, expect } from "vitest";
import { getDirection, isValidLocale, SUPPORTED_LOCALES, DEFAULT_LOCALE } from "../lib/i18n/config";
import faDict from "../lib/i18n/dictionaries/fa-IR.json";
import enDict from "../lib/i18n/dictionaries/en-US.json";

function getFlatKeys(obj: Record<string, any>, prefix = ""): string[] {
  return Object.keys(obj).reduce((res: string[], el: string) => {
    if (Array.isArray(obj[el])) {
      return res;
    } else if (typeof obj[el] === "object" && obj[el] !== null) {
      return [...res, ...getFlatKeys(obj[el], `${prefix}${el}.`)];
    }
    return [...res, prefix + el];
  }, []);
}

describe("i18n Configuration & Dictionaries", () => {
  it("only supports fa-IR and en-US", () => {
    expect(SUPPORTED_LOCALES).toEqual(["fa-IR", "en-US"]);
    expect(DEFAULT_LOCALE).toBe("fa-IR");
    expect(isValidLocale("fa-IR")).toBe(true);
    expect(isValidLocale("en-US")).toBe(true);
    expect(isValidLocale("ar-SA")).toBe(false);
    expect(isValidLocale("ar")).toBe(false);
  });

  it("assigns correct direction: RTL for fa-IR, LTR for en-US", () => {
    expect(getDirection("fa-IR")).toBe("rtl");
    expect(getDirection("en-US")).toBe("ltr");
  });

  it("maintains 100% key parity between Persian and English dictionaries", () => {
    const faKeys = getFlatKeys(faDict).sort();
    const enKeys = getFlatKeys(enDict).sort();

    expect(faKeys).toEqual(enKeys);
    expect(faKeys.length).toBeGreaterThan(20);
  });
});
