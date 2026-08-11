"use client";

import React, { useEffect, useState } from "react";
import { WifiOff, RefreshCw } from "lucide-react";
import { useTranslation } from "@/components/layout/DirectionProvider";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

export default function OfflinePage() {
  const { t } = useTranslation();
  const [isRetrying, setIsRetrying] = useState<boolean>(false);

  const handleRetry = () => {
    setIsRetrying(true);
    if (navigator.onLine) {
      window.location.reload();
    } else {
      setTimeout(() => {
        setIsRetrying(false);
      }, 1000);
    }
  };

  useEffect(() => {
    const handleOnline = () => {
      window.location.reload();
    };

    window.addEventListener("online", handleOnline);
    return () => window.removeEventListener("online", handleOnline);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] max-w-md mx-auto text-center space-y-6 px-4">
      <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
        <WifiOff className="w-8 h-8" />
      </div>

      <div className="space-y-2">
        <h1 className="text-2xl font-bold text-brand-text">{t("offline.title")}</h1>
        <p className="text-sm text-brand-text-muted leading-relaxed">
          {t("offline.description")}
        </p>
      </div>

      <Card variant="default" className="w-full text-xs text-brand-text-muted">
        {t("offline.cached_content_notice")}
      </Card>

      <Button
        onClick={handleRetry}
        isLoading={isRetrying}
        variant="primary"
        size="lg"
        className="w-full sm:w-auto"
      >
        <RefreshCw className="w-4 h-4 -ms-1 me-2" />
        {t("offline.retry_button")}
      </Button>
    </div>
  );
}
