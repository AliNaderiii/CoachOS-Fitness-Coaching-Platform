export const SUPPORTED_LOCALES = ["fa-IR", "en-US"] as const;

export type Locale = (typeof SUPPORTED_LOCALES)[number];
export type Direction = "rtl" | "ltr";

export const DEFAULT_LOCALE: Locale = "fa-IR";

export interface LocaleMeta {
  name: string;
  nativeName: string;
  direction: Direction;
}

export const LOCALES_META: Readonly<Record<Locale, LocaleMeta>> = Object.freeze({
  "fa-IR": Object.freeze({
    name: "Persian",
    nativeName: "فارسی",
    direction: "rtl",
  }),
  "en-US": Object.freeze({
    name: "English",
    nativeName: "English",
    direction: "ltr",
  }),
});

export function isValidLocale(value: unknown): value is Locale {
  return typeof value === "string" && (SUPPORTED_LOCALES as readonly string[]).includes(value);
}

export function getDirection(locale: Locale): Direction {
  return LOCALES_META[locale].direction;
}
