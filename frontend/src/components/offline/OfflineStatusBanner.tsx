"use client";

export default function OfflineStatusBanner() {
  return (
    <div role="status" aria-live="polite" aria-atomic="true" className="rounded-lg bg-amber-950/40 border border-amber-500/20 px-4 py-3 text-xs text-amber-200 flex items-center gap-2">
      <span className="inline-block h-2 w-2 rounded-full bg-amber-400 animate-pulse" aria-hidden="true" />
      <span>Offline — Changes saved temporarily. Reconnection required to save permanently.</span>
    </div>
  );
}
