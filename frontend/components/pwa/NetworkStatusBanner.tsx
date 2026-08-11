"use client";

import React, { useState, useEffect } from "react";
import { WifiOff } from "lucide-react";
import { useTranslation } from "@/components/layout/DirectionProvider";

export const NetworkStatusBanner: React.FC = () => {
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const { t } = useTranslation();

  useEffect(() => {
    if (typeof window === "undefined") return;

    setIsOnline(navigator.onLine);

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  if (isOnline) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className="bg-amber-500/15 border-b border-amber-500/30 text-amber-300 px-4 py-2 text-xs md:text-sm flex items-center justify-center gap-2 select-none z-50 sticky top-0 backdrop-blur-sm"
    >
      <WifiOff className="w-4 h-4 flex-shrink-0 text-amber-400" />
      <span>{t("pwa.offline_notice")}</span>
    </div>
  );
};
