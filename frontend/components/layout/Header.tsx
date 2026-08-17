"use client";

import React from "react";
import Link from "next/link";
import { Activity, Dumbbell } from "lucide-react";
import { useTranslation } from "./DirectionProvider";
import { LanguageSwitcher } from "../ui/LanguageSwitcher";
import { Badge } from "../ui/Badge";

export const Header: React.FC = () => {
  const { locale, t } = useTranslation();

  return (
    <header className="sticky top-0 z-40 w-full bg-obsidian-950/80 backdrop-blur-md border-b border-obsidian-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo and Brand */}
        <Link
          href={`/${locale}`}
          className="flex items-center gap-2.5 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 rounded-lg p-1"
        >
          <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 group-hover:bg-emerald-500/20 transition-colors">
            <Dumbbell className="w-5 h-5" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-brand-text tracking-tight">CoachOS</span>
              <Badge variant="success" size="sm">
                v0.4
              </Badge>
            </div>
            <span className="text-[10px] text-brand-text-muted hidden sm:inline">
              {t("app.tagline")}
            </span>
          </div>
        </Link>

        {/* Desktop Nav Links */}
        <nav className="hidden md:flex items-center gap-6 text-sm">
          <Link
            href={`/${locale}/athlete/today`}
            className="text-brand-text-muted hover:text-brand-text transition-colors"
          >
            {t("nav.athlete_view")}
          </Link>
          <Link
            href={`/${locale}/coach/programs`}
            className="text-brand-text-muted hover:text-brand-text transition-colors"
          >
            {t("nav.coach_view")}
          </Link>
          <Link
            href={`/${locale}/coach/copilot`}
            className="text-brand-text-muted hover:text-brand-text transition-colors"
          >
            {t("nav.copilot")}
          </Link>
          <Link
            href={`/${locale}/org/settings`}
            className="text-brand-text-muted hover:text-brand-text transition-colors"
          >
            {t("nav.org_view")}
          </Link>
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <LanguageSwitcher currentLocale={locale} />
          <Link
            href={`/${locale}/login`}
            className="hidden sm:inline-flex min-h-[44px] items-center justify-center px-4 rounded-lg bg-obsidian-800 hover:bg-obsidian-700 border border-obsidian-700 text-xs font-semibold text-brand-text transition-colors"
          >
            {t("nav.login")}
          </Link>
        </div>
      </div>
    </header>
  );
};
