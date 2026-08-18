"use client";

export default function IntegrationStatus({ state = "connected" }: { state?: string }) {
  const label = state === "connected" ? "Connected" : state === "disconnected" ? "Disconnected" : state === "reauthorizing" ? "Reauthorizing" : state === "limited_permission" ? "Limited Permission" : "Expired";
  return (
    <div className="inline-flex items-center gap-2 rounded-full bg-slate-900 border border-slate-700 px-3 py-1 text-xs font-medium text-slate-200" aria-label={`Integration status: ${label}`}>
      <span className={`h-2 w-2 rounded-full ${state === "connected" ? "bg-emerald-400" : state === "disconnected" ? "bg-slate-500" : state === "reauthorizing" ? "bg-amber-400" : state === "limited_permission" ? "bg-orange-400" : "bg-red-400"}`} aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}
