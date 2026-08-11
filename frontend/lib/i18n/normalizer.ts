const ARABIC_INDIC_DIGITS = "٠١٢٣٤٥٦٧٨٩";
const PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹";
const DIACRITICS = /[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]/g;
const ZWNJ = "\u200C";

/**
 * Normalizes Persian search input without translating it or enabling an Arabic
 * locale. Keyboard variants and Arabic-Indic digits are folded to their Persian
 * equivalents, combining marks are removed, and whitespace is collapsed and
 * trimmed. ZWNJ is preserved by default and removed when preserveZwnj is false.
 */
export function normalizePersianSearch(input: string, preserveZwnj = true): string {
  let normalized = input
    .normalize("NFKC")
    // Accept a serialized ZWNJ sequence from plain-text inputs as the same mark.
    .replace(/\\u200c/gi, ZWNJ)
    .replace(/[يى]/g, "ی")
    .replace(/ك/g, "ک")
    .replace(/[٠-٩]/g, (digit) => PERSIAN_DIGITS[ARABIC_INDIC_DIGITS.indexOf(digit)])
    .replace(DIACRITICS, "");

  if (!preserveZwnj) {
    normalized = normalized.replaceAll(ZWNJ, "");
  }

  return normalized.replace(/\s+/g, " ").trim();
}
