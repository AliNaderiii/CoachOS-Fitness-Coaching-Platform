"use client";

import { QueueRecord } from "../../lib/indexeddb/offlineQueueSchema";

export default function OfflineQueueDetails({ records }: { records: QueueRecord[] }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-4" aria-label="Queued operations details">
      <h2 className="text-base font-semibold text-slate-100 mb-3">Queued Operations</h2>
      {records.length === 0 ? (
        <p className="text-xs text-slate-400">No queued operations.</p>
      ) : (
        <ul className="space-y-2">
          {records.map((r) => (
            <li key={r.client_operation_id} className="rounded-lg border border-slate-800 bg-slate-900/30 px-3 py-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-medium text-slate-200" aria-label={`Operation ${r.operation_type} for entity ${r.entity_type}`}>
                  {r.operation_type} — {r.entity_type}
                </span>
                <span className={`text-[10px] uppercase tracking-wide font-semibold px-2 py-0.5 rounded-full ${
                  r.state === "acknowledged" ? "bg-emerald-900/40 text-emerald-300" :
                  r.state === "pending" ? "bg-amber-900/40 text-amber-300" :
                  r.state === "conflict" ? "bg-rose-900/40 text-rose-300" :
                  r.state === "failed" ? "bg-red-900/40 text-red-300" :
                  r.state === "dead_letter" ? "bg-slate-800 text-slate-300" :
                  r.state === "discarded" ? "bg-slate-800 text-slate-300" : "bg-slate-900/40 text-slate-300"
                }`} aria-label={`Status ${r.state}`}>
                  {r.state}
                </span>
              </div>
              <div className="mt-1 text-[10px] text-slate-500">
                ID: {r.entity_id} | Attempts: {r.attempt_count}
              </div>
              {r.safe_error_message_key && (
                <div className="mt-1 text-[10px] text-rose-300">Error: {r.safe_error_message_key}</div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
