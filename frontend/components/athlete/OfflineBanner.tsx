"use client";

import React from "react";
import { WifiOff } from "lucide-react";
import { useTranslation } from "../layout/DirectionProvider";
import { Button } from "../ui/Button";

export interface OfflineBannerProps {
  online: boolean;
  pendingCount?: number;
  onRetry?: () => void;
}

/**
 * Phase 07 temporary offline boundary. Surfaces an accurate network status banner
 * and, when there are in-memory pending items, offers retry. No durable queue.
 */
export const OfflineBanner: React.FC<OfflineBannerProps> = ({
  online,
  pendingCount = 0,
  onRetry,
}) => {
  const { t } = useTranslation();

  if (online && pendingCount === 0) return null;

  const message = online
    ? t("athlete.pending_count").replace("{count}", String(pendingCount))
    : t("athlete.offline_notice");

  return (
    <div
      role="status"
      aria-live="polite"
      className="flex items-center justify-between gap-3 px-4 py-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 mb-4"
    >
      <div className="flex items-center gap-2 text-sm">
        <WifiOff className="w-4 h-4" aria-hidden="true" />
        <span>{message}</span>
      </div>
      {!online && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          {t("athlete.offline_retry")}
        </Button>
      )}
    </div>
  );
};
