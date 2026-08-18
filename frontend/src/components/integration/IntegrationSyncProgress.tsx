"use client";

export default function IntegrationSyncProgress({ eventsImported = 0, total = 0 }: { eventsImported?: number; total?: number }) {
  const progress = total > 0 ? Math.round((eventsImported / total) * 100) : 0;
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-4" aria-label="Sync progress">
      <h3 className="text-base font-semibold text-slate-100 mb-3">Sync Progress</h3>
      <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden" aria-hidden="true">
        <div className="h-full rounded-full bg-emerald-500" style={{ width: `${progress}%` }} />
      </div>
      <p className="mt-2 text-xs text-slate-300">{eventsImported} of {total} events imported ({progress}%)</p>
    </div>
  );
}
