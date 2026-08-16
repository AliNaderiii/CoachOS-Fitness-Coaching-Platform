"use client";

import { useEffect, useState } from "react";

/**
 * Tracks browser connectivity for the Phase 07 temporary offline boundary.
 * Only used to show an accurate banner and gate in-memory retry — there is no
 * durable client-side database queue or background sync (deferred to Phase 12).
 */
export function getBrowserOnline(): boolean {
  if (typeof navigator === "undefined") return true;
  return navigator.onLine;
}

export function useNetworkStatus(): { online: boolean } {
  const [online, setOnline] = useState<boolean>(() => getBrowserOnline());

  useEffect(() => {
    if (typeof window === "undefined") return undefined;
    const goOnline = () => setOnline(true);
    const goOffline = () => setOnline(false);
    window.addEventListener("online", goOnline);
    window.addEventListener("offline", goOffline);
    return () => {
      window.removeEventListener("online", goOnline);
      window.removeEventListener("offline", goOffline);
    };
  }, []);

  return { online };
}
