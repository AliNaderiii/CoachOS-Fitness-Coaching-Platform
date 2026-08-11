const FIRST_STRONG_ISOLATE = "\u2068";
const RIGHT_TO_LEFT_ISOLATE = "\u2067";
const POP_DIRECTIONAL_ISOLATE = "\u2069";

/** Isolates an LTR snippet using first-strong isolation for mixed-direction text. */
export function isolateLtr(text: string): string {
  return `${FIRST_STRONG_ISOLATE}${text}${POP_DIRECTIONAL_ISOLATE}`;
}

/** Isolates an explicitly RTL snippet from surrounding text. */
export function isolateRtl(text: string): string {
  return `${RIGHT_TO_LEFT_ISOLATE}${text}${POP_DIRECTIONAL_ISOLATE}`;
}

/**
 * Formats the minimal Phase 04 prescription display contract. Domain-specific
 * validation and localized workout presentation remain outside this foundation.
 */
export function formatPrescriptionBidi(
  sets: number,
  reps: number,
  weight?: number,
  unit?: string
): string {
  const prescription = `${sets} × ${reps}`;
  if (weight === undefined) {
    return prescription;
  }

  const weightDisplay = unit ? `${weight} ${unit}` : `${weight}`;
  return `${prescription} (${weightDisplay})`;
}
