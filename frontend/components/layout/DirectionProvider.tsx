"use client";

import React, { createContext, useContext, useEffect } from "react";
import { Locale, Direction, getDirection, DEFAULT_LOCALE } from "@/lib/i18n/config";
import faDict from "@/lib/i18n/dictionaries/fa-IR.json";
import enDict from "@/lib/i18n/dictionaries/en-US.json";

interface DirectionContextValue {
  locale: Locale;
  direction: Direction;
  t: (key: string, fallback?: string) => string;
}

const dictionaries: Record<Locale, Record<string, any>> = {
  "fa-IR": faDict,
  "en-US": enDict,
};

const DirectionContext = createContext<DirectionContextValue>({
  locale: DEFAULT_LOCALE,
  direction: "rtl",
  t: (key, fallback) => fallback || key,
});

export const useTranslation = () => useContext(DirectionContext);

export interface DirectionProviderProps {
  locale: Locale;
  children: React.ReactNode;
}

export const DirectionProvider: React.FC<DirectionProviderProps> = ({ locale, children }) => {
  const direction = getDirection(locale);

  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = direction;
  }, [locale, direction]);

  const dict = dictionaries[locale] || dictionaries[DEFAULT_LOCALE];

  const t = (key: string, fallback?: string): string => {
    const keys = key.split(".");
    let current: any = dict;
    for (const k of keys) {
      if (current && typeof current === "object" && k in current) {
        current = current[k];
      } else {
        return fallback || key;
      }
    }
    return typeof current === "string" ? current : fallback || key;
  };

  return (
    <DirectionContext.Provider value={{ locale, direction, t }}>
      {children}
    </DirectionContext.Provider>
  );
};
