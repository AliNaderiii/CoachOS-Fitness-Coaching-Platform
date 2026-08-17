"use client";

export default function IntegrationErrorBanner({ messageKey = "errors.sync.network_timeout" }: { messageKey?: string }) {
  const messages: Record<string, string> = {
    "errors.sync.network_timeout": "Network timeout — will retry.",
    "errors.sync.conflict": "Conflict detected — choose resolution.",
    "errors.sync.authz_denied": "Access denied — reconnect required.",
    "errors.sync.schema_mismatch": "Schema mismatch — manual retry required.",
    "errors.sync.age_limit": "Operation too old — please retry or discard.",
    "errors.sync.integrity_check_failed": "Data integrity check failed — please discard.",
    "integration.error.authentication_failed": "Authentication failed — reconnect required.",
    "integration.error.rate_limited": "Rate limit reached — retry after 60 seconds.",
    "integration.error.provider_outage": "Provider temporarily unavailable — sync will resume automatically.",
    "integration.error.scope_denied": "Required permission denied — reconnect with updated scopes.",
  };
  const text = messages[messageKey] || messageKey;
  return (
    <div role="alert" className="rounded-lg bg-rose-950/30 border border-rose-500/20 px-4 py-3 text-xs text-rose-200 flex items-center gap-2">
      <span className="inline-block h-2 w-2 rounded-full bg-rose-400" aria-hidden="true" />
      <span>{text}</span>
    </div>
  );
}
