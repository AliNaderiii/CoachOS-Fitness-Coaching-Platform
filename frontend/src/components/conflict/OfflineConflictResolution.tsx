"use client";

import { useState } from "react";

export default function OfflineConflictResolution({
  queuedVersion,
  serverVersion,
  onResolve,
  label = "Conflict",
}: {
  queuedVersion?: Record<string, unknown>;
  serverVersion?: Record<string, unknown>;
  onResolve: (choice: "online" | "queued" | "manual") => void;
  label?: string;
}) {
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <div className="rounded-xl border border-amber-500/20 bg-amber-950/30 p-4" role="region" aria-label={`${label} resolution`}>
      <h3 className="text-sm font-semibold text-amber-300 mb-2">{label}</h3>
      <p className="text-xs text-amber-200/80 mb-3">A newer version exists. Choose how to resolve.</p>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => { setSelected("online"); onResolve("online"); }}
          className="min-w-[48px] min-h-[48px] rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs px-3 py-2 transition-colors"
          aria-label="Keep online version — queued version will be discarded"
        >
          Keep Online
        </button>
        <button
          onClick={() => { setSelected("queued"); onResolve("queued"); }}
          className="min-w-[48px] min-h-[48px] rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs px-3 py-2 transition-colors"
          aria-label="Keep queued version — creates new operation"
        >
          Keep Queued
        </button>
        <button
          onClick={() => { setSelected("manual"); onResolve("manual"); }}
          className="min-w-[48px] min-h-[48px] rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs px-3 py-2 transition-colors"
          aria-label="Edit manually — open edit form with queued version"
        >
          Edit Manually
        </button>
      </div>
      <div className="mt-3 text-xs text-amber-200/60">
        <span>Queued: {JSON.stringify(queuedVersion || {})}</span>
        <br />
        <span>Online: {JSON.stringify(serverVersion || {})}</span>
      </div>
    </div>
  );
}
