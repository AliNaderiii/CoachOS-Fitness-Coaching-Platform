"use client";

import React from "react";
import Link from "next/link";
import { HelpCircle, Home } from "lucide-react";
import { useTranslation } from "@/components/layout/DirectionProvider";
import { Button } from "@/components/ui/Button";

export default function NotFound() {
  const { locale, t } = useTranslation();

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center max-w-md mx-auto space-y-4 px-4">
      <div className="w-14 h-14 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
        <HelpCircle className="w-7 h-7" />
      </div>

      <h2 className="text-xl font-bold text-brand-text">{t("errors.not_found_title")}</h2>
      <p className="text-sm text-brand-text-muted">{t("errors.not_found_description")}</p>

      <Link href={`/${locale}`}>
        <Button variant="primary" size="md">
          <Home className="w-4 h-4 -ms-1 me-2" />
          {t("errors.not_found_button")}
        </Button>
      </Link>
    </div>
  );
}
