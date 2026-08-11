"use client";

import React from "react";
import { useTranslation } from "./DirectionProvider";

export const Footer: React.FC = () => {
  const { t } = useTranslation();

  return (
    <footer className="w-full bg-obsidian-950 border-t border-obsidian-800 py-8 px-4 sm:px-6 lg:px-8 text-xs text-brand-text-muted mt-auto mb-16 md:mb-0">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-4 text-center sm:text-start">
          <span className="font-medium text-brand-text">CoachOS Platform</span>
          <span>•</span>
          <span>{t("footer.rights")}</span>
        </div>
        <div className="flex items-center gap-4 text-center">
          <span>{t("footer.version")}</span>
          <span>•</span>
          <span className="text-[11px] text-brand-text-disabled">{t("footer.legal_notice")}</span>
        </div>
      </div>
    </footer>
  );
};
