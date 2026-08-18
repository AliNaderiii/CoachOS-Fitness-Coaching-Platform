"use client";

export default function IntegrationWorkspace() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950/40 p-6" aria-label="Integration workspace">
      <h2 className="text-xl font-bold text-slate-100 mb-4">Integration Workspace</h2>
      <div className="space-y-4">
        <div className="rounded-lg border border-slate-800 bg-slate-900/20 p-4">
          <h3 className="text-sm font-semibold text-slate-200 mb-1">Mock Fitness Provider</h3>
          <p className="text-xs text-slate-400 mb-2">Provider-neutral adapter — deterministic mock/sandbox vertical slice.</p>
          <div className="flex gap-2">
            <a href="#" className="min-w-[48px] min-h-[48px] rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white text-xs px-3 py-2 transition-colors" aria-label="Connect mock fitness provider">
              Connect
            </a>
            <a href="#" className="min-w-[48px] min-h-[48px] rounded-lg bg-rose-700 hover:bg-rose-600 text-white text-xs px-3 py-2 transition-colors" aria-label="Disconnect integration">
              Disconnect
            </a>
          </div>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/20 p-4">
          <h3 className="text-sm font-semibold text-slate-200 mb-2">Sync Status</h3>
          <p className="text-xs text-slate-400">Connected. Last sync: 10:30 AM. Rate limit: 95 remaining.</p>
        </div>
      </div>
    </div>
  );
}
