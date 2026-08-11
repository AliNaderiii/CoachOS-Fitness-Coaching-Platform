import { describe, it, expect } from "vitest";
import {
  formatNumber,
  formatWeight,
  gregorianToJalali,
  formatDate,
} from "../lib/i18n/formatters";

describe("Locale Formatters (ADR-009)", () => {
  it("formats numbers into Persian digits in fa-IR locale", () => {
    expect(formatNumber(12345, "fa-IR")).toBe("۱۲۳۴۵");
    expect(formatNumber("100", "fa-IR")).toBe("۱۰۰");
    expect(formatNumber(12345, "en-US")).toBe("12345");
  });

  it("formats weights with localized units", () => {
    expect(formatWeight(100, "kg", "fa-IR")).toBe("۱۰۰ کیلوگرم");
    expect(formatWeight(225, "lbs", "fa-IR")).toBe("۲۲۵ پوند");
    expect(formatWeight(100, "kg", "en-US")).toBe("100 kg");
  });

  it("converts Gregorian date to Jalali accurately", () => {
    // 2026-08-11 UTC -> 1405-05-20 (20 Mordad 1405)
    const [jy, jm, jd] = gregorianToJalali(2026, 8, 11);
    expect(jy).toBe(1405);
    expect(jm).toBe(5);
    expect(jd).toBe(20);
  });

  it("formats date strings in Jalali for fa-IR and Gregorian for en-US", () => {
    const isoDate = "2026-08-11T12:00:00Z";
    const faFormatted = formatDate(isoDate, "fa-IR");
    expect(faFormatted).toContain("مرداد");
    expect(faFormatted).toContain("۱۴۰۵");

    const enFormatted = formatDate(isoDate, "en-US");
    expect(enFormatted).toBe("August 11, 2026");
  });

  it("uses UTC date parts near a timezone boundary and rejects invalid dates", () => {
    expect(formatDate("2026-08-11T23:59:59-10:00", "en-US")).toBe("August 12, 2026");
    expect(() => formatDate("not-an-iso-date", "fa-IR")).toThrowError(RangeError);
    expect(() => formatDate("2026-02-30T12:00:00Z", "en-US")).toThrowError(RangeError);
    expect(() => gregorianToJalali(2026, 2, 30)).toThrowError(RangeError);
  });
});
