"use client";

import React from "react";
import { useRouter, usePathname } from "next/navigation";
import { Globe } from "lucide-react";
import { Locale, SUPPORTED_LOCALES, LOCALES_META } from "@/lib/i18n/config";

export interface LanguageSwitcherProps {
  currentLocale: Locale;
}

export const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ currentLocale }) => {
  const router = useRouter();
  const pathname = usePathname();

  const handleLocaleChange = (newLocale: Locale) => {
    if (newLocale === currentLocale) return;

    // Set cookie for persistence (ADR-047)
    document.cookie = `NEXT_LOCALE=${newLocale}; path=/; max-age=31536000; SameSite=Lax`;

    // Replace the locale segment in pathname or redirect
    let newPath = pathname;
    for (const loc of SUPPORTED_LOCALES) {
      if (newPath.startsWith(`/${loc}`)) {
        newPath = newPath.replace(`/${loc}`, `/${newLocale}`);
        break;
      }
    }

    if (!newPath.startsWith(`/${newLocale}`)) {
      newPath = `/${newLocale}`;
    }

    router.push(newPath);
  };

  const targetLocale: Locale = currentLocale === "fa-IR" ? "en-US" : "fa-IR";
  const targetMeta = LOCALES_META[targetLocale];

  return (
    <button
      type="button"
      onClick={() => handleLocaleChange(targetLocale)}
      className="inline-flex items-center gap-1.5 min-h-[44px] px-3 py-1.5 rounded-lg bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-xs font-medium text-brand-text transition-colors"
      aria-label={`Switch language to ${targetMeta.nativeName}`}
    >
      <Globe className="w-4 h-4 text-emerald-400" />
      <span>{targetMeta.nativeName}</span>
    </button>
  );
};
