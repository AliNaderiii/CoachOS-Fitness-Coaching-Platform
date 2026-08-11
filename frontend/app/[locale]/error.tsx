"use client";

import React, { useEffect } from "react";
import { AlertTriangle, RotateCcw } from "lucide-react";
import { useTranslation } from "@/components/layout/DirectionProvider";
import { Button } from "@/components/ui/Button";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const { t } = useTranslation();

  useEffect(() => {
    console.error("[App Error Boundary]:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center max-w-md mx-auto space-y-4 px-4">
      <div className="w-14 h-14 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400">
        <AlertTriangle className="w-7 h-7" />
      </div>

      <h2 className="text-xl font-bold text-brand-text">{t("errors.server_error_title")}</h2>
      <p className="text-sm text-brand-text-muted">{t("errors.server_error_description")}</p>

      <Button onClick={reset} variant="primary" size="md">
        <RotateCcw className="w-4 h-4 -ms-1 me-2" />
        {t("offline.retry_button")}
      </Button>
    </div>
  );
}
