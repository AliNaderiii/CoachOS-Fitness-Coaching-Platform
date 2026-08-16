/**
 * Unit conversion policy for set actuals. The backend stores load in kilograms
 * (explicit policy). Frontends convert the athlete's preferred unit to kg before
 * sending and may convert back for display.
 */
export const KG_PER_LB = 0.45359237;

export type Unit = "kg" | "lbs";

export function toKg(value: number, unit: Unit): number {
  if (unit === "lbs") {
    return round2(value * KG_PER_LB);
  }
  return round2(value);
}

export function fromKg(kg: number, unit: Unit): number {
  if (unit === "lbs") {
    return round1(kg / KG_PER_LB);
  }
  return round1(kg);
}

export function round2(value: number): number {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

export function round1(value: number): number {
  return Math.round((value + Number.EPSILON) * 10) / 10;
}

export function parseNumber(value: string): number | null {
  if (value.trim() === "") return null;
  const normalized = value.replace(/٫|,/, ".");
  const n = Number(normalized);
  return Number.isFinite(n) ? n : null;
}
