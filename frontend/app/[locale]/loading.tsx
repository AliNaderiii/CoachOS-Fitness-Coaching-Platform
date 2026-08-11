"use client";

import React from "react";
import { useTranslation } from "@/components/layout/DirectionProvider";

export default function Loading() {
  const { t } = useTranslation();

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
      <div className="w-10 h-10 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin" />
      <span className="text-sm font-medium text-brand-text-muted">{t("app.loading")}</span>
    </div>
  );
}
