import type { Locale } from "./config";

const PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹";
const ENGLISH_MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
] as const;
const JALALI_MONTHS = [
  "فروردین",
  "اردیبهشت",
  "خرداد",
  "تیر",
  "مرداد",
  "شهریور",
  "مهر",
  "آبان",
  "آذر",
  "دی",
  "بهمن",
  "اسفند",
] as const;

export type WeightUnit = "kg" | "lbs";

function toPersianDigits(value: string): string {
  return value.replace(/\d/g, (digit) => PERSIAN_DIGITS[Number(digit)]);
}

export function formatNumber(value: number | string, locale: Locale): string {
  if (typeof value === "number" && !Number.isFinite(value)) {
    throw new RangeError("Number must be finite");
  }

  const normalized =
    typeof value === "number"
      ? new Intl.NumberFormat("en-US", { useGrouping: false, maximumFractionDigits: 20 }).format(value)
      : value;

  return locale === "fa-IR" ? toPersianDigits(normalized) : normalized;
}

export function formatWeight(value: number | string, unit: WeightUnit, locale: Locale): string {
  const formattedValue = formatNumber(value, locale);
  if (locale === "fa-IR") {
    return `${formattedValue} ${unit === "kg" ? "کیلوگرم" : "پوند"}`;
  }
  return `${formattedValue} ${unit}`;
}

function assertValidGregorianDate(year: number, month: number, day: number): void {
  if (![year, month, day].every(Number.isInteger)) {
    throw new RangeError("Gregorian date parts must be integers");
  }

  const date = new Date(Date.UTC(year, month - 1, day));
  if (
    date.getUTCFullYear() !== year ||
    date.getUTCMonth() !== month - 1 ||
    date.getUTCDate() !== day
  ) {
    throw new RangeError("Invalid Gregorian date");
  }
}

/**
 * Converts a Gregorian calendar date to a Solar Hijri (Jalali) date.
 * Month inputs and outputs are one-based. The conversion is display-only;
 * timestamps remain ISO 8601 UTC at the data boundary.
 */
export function gregorianToJalali(year: number, month: number, day: number): [number, number, number] {
  assertValidGregorianDate(year, month, day);

  const gregorianMonthDays = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
  let gregorianYear = year;
  let jalaliYear: number;

  if (gregorianYear > 1600) {
    jalaliYear = 979;
    gregorianYear -= 1600;
  } else {
    jalaliYear = 0;
    gregorianYear -= 621;
  }

  const leapAdjustedYear = month > 2 ? gregorianYear + 1 : gregorianYear;
  let days =
    365 * gregorianYear +
    Math.floor((leapAdjustedYear + 3) / 4) -
    Math.floor((leapAdjustedYear + 99) / 100) +
    Math.floor((leapAdjustedYear + 399) / 400) -
    80 +
    day +
    gregorianMonthDays[month - 1];

  jalaliYear += 33 * Math.floor(days / 12053);
  days %= 12053;
  jalaliYear += 4 * Math.floor(days / 1461);
  days %= 1461;

  if (days > 365) {
    jalaliYear += Math.floor((days - 1) / 365);
    days = (days - 1) % 365;
  }

  if (days < 186) {
    return [jalaliYear, 1 + Math.floor(days / 31), 1 + (days % 31)];
  }

  return [jalaliYear, 7 + Math.floor((days - 186) / 30), 1 + ((days - 186) % 30)];
}

/**
 * Formats the UTC date portion of an ISO timestamp. Invalid timestamps throw
 * RangeError rather than silently producing an incorrect localized date.
 */
export function formatDate(isoDate: string, locale: Locale): string {
  const sourceDate = /^(\d{4})-(\d{2})-(\d{2})(?:T|$)/.exec(isoDate);
  if (!sourceDate) {
    throw new RangeError("Invalid ISO date");
  }
  assertValidGregorianDate(Number(sourceDate[1]), Number(sourceDate[2]), Number(sourceDate[3]));

  const date = new Date(isoDate);
  if (Number.isNaN(date.getTime())) {
    throw new RangeError("Invalid ISO date");
  }

  const year = date.getUTCFullYear();
  const month = date.getUTCMonth() + 1;
  const day = date.getUTCDate();

  if (locale === "en-US") {
    return `${ENGLISH_MONTHS[month - 1]} ${day}, ${year}`;
  }

  const [jalaliYear, jalaliMonth, jalaliDay] = gregorianToJalali(year, month, day);
  return `${formatNumber(jalaliDay, locale)} ${JALALI_MONTHS[jalaliMonth - 1]} ${formatNumber(jalaliYear, locale)}`;
}
