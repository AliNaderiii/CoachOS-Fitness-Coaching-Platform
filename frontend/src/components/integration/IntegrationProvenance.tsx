"use client";

export default function IntegrationProvenance() {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-4" aria-label="Data provenance">
      <h3 className="text-base font-semibold text-slate-100 mb-2">Data Provenance</h3>
      <table className="w-full text-xs text-slate-300">
        <tbody>
          <tr className="border-b border-slate-800">
            <th className="text-left py-1 text-slate-500">Source</th>
            <td className="py-1">Mock Fitness Provider</td>
          </tr>
          <tr className="border-b border-slate-800">
            <th className="text-left py-1 text-slate-500">Imported At</th>
            <td className="py-1">2026-08-16 10:30:00 (UTC)</td>
          </tr>
          <tr className="border-b border-slate-800">
            <th className="text-left py-1 text-slate-500">Event ID</th>
            <td className="py-1" dir="ltr"><bdi>mock_event_001</bdi></td>
          </tr>
          <tr>
            <th className="text-left py-1 text-slate-500">Provider Timestamp</th>
            <td className="py-1">2026-08-09 00:00:00 (UTC)</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
