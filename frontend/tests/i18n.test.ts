import { describe, it, expect } from "vitest";
import {
  getDirection,
  isValidLocale,
  SUPPORTED_LOCALES,
  DEFAULT_LOCALE,
  LOCALES_META,
} from "../lib/i18n/config";
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

const TRACKED_UI_KEYS = [
  "app.foundation_badge",
  "app.loading",
  "app.tagline",
  "auth.email_label",
  "auth.login_title",
  "auth.password_label",
  "auth.placeholder_warning",
  "auth.register_title",
  "auth.submit_login",
  "auth.submit_register",
  "errors.not_found_button",
  "errors.not_found_description",
  "errors.not_found_title",
  "errors.server_error_description",
  "errors.server_error_title",
  "footer.legal_notice",
  "footer.rights",
  "footer.version",
  "home.cta_athlete",
  "home.cta_coach",
  "home.placeholder_notice",
  "home.status_backend",
  "home.status_frontend",
  "home.status_i18n",
  "home.status_pwa",
  "home.status_title",
  "home.welcome_subtitle",
  "home.welcome_title",
  "nav.athlete_view",
  "nav.calendar",
  "nav.coach_view",
  "nav.login",
  "nav.messages",
  "nav.org_view",
  "nav.profile",
  "nav.programs",
  "nav.today",
  "offline.cached_content_notice",
  "offline.description",
  "offline.retry_button",
  "offline.title",
  "placeholders.athlete_today_desc",
  "placeholders.athlete_today_title",
  "placeholders.coach_programs_desc",
  "placeholders.coach_programs_title",
  "placeholders.org_settings_desc",
  "placeholders.org_settings_title",
  "pwa.install_button",
  "pwa.install_description",
  "pwa.install_title",
  "pwa.ios_instruction_step1",
  "pwa.ios_instruction_step2",
  "pwa.ios_instructions_title",
  "pwa.offline_notice",
] as const;

describe("i18n Configuration & Dictionaries", () => {
  it("only supports fa-IR and en-US", () => {
    expect(SUPPORTED_LOCALES).toEqual(["fa-IR", "en-US"]);
    expect(DEFAULT_LOCALE).toBe("fa-IR");
    expect(isValidLocale("fa-IR")).toBe(true);
    expect(isValidLocale("en-US")).toBe(true);
    expect(isValidLocale("ar-SA")).toBe(false);
    expect(isValidLocale("ar")).toBe(false);
  });

  it("assigns correct direction and switcher metadata without Arabic metadata", () => {
    expect(getDirection("fa-IR")).toBe("rtl");
    expect(getDirection("en-US")).toBe("ltr");
    expect(LOCALES_META["fa-IR"]).toEqual({
      name: "Persian",
      nativeName: "فارسی",
      direction: "rtl",
    });
    expect(LOCALES_META["en-US"]).toEqual({
      name: "English",
      nativeName: "English",
      direction: "ltr",
    });
    expect(Object.keys(LOCALES_META)).toEqual(["fa-IR", "en-US"]);
  });

  it("maintains 100% key parity between Persian and English dictionaries", () => {
    const faKeys = getFlatKeys(faDict).sort();
    const enKeys = getFlatKeys(enDict).sort();

    expect(faKeys).toEqual(enKeys);
    expect(faKeys.length).toBeGreaterThan(20);
  });

  it("provides a non-empty Persian and English string for every tracked UI key", () => {
    const faKeys = getFlatKeys(faDict);
    const enKeys = getFlatKeys(enDict);

    for (const key of TRACKED_UI_KEYS) {
      expect(faKeys, `missing fa-IR key: ${key}`).toContain(key);
      expect(enKeys, `missing en-US key: ${key}`).toContain(key);

      const readValue = (dictionary: Record<string, any>) =>
        key.split(".").reduce<any>((current, segment) => current?.[segment], dictionary);
      expect(readValue(faDict), `empty fa-IR value: ${key}`).toBeTypeOf("string");
      expect(readValue(faDict).trim(), `empty fa-IR value: ${key}`).not.toBe("");
      expect(readValue(enDict), `empty en-US value: ${key}`).toBeTypeOf("string");
      expect(readValue(enDict).trim(), `empty en-US value: ${key}`).not.toBe("");
    }
  });
});
