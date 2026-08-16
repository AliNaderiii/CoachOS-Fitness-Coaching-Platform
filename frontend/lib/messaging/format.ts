import { formatDate, formatNumber } from "../i18n/formatters";
import type { Locale } from "../i18n/config";

/**
 * Phase 08 presentation helpers.
 *
 * Timestamp policy: the API returns UTC ISO-8601. The UI renders the date part
 * with the existing locale-aware formatter (Jalali for fa-IR) and the time part
 * in the viewer's own browser timezone. Nothing is silently reinterpreted as
 * server-local time.
 */

/** Formats the clock portion of an ISO timestamp in the viewer's timezone. */
export function formatTime(iso: string, locale: Locale): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    throw new RangeError("Invalid ISO timestamp");
  }
  const hours = date.getHours();
  const minutes = date.getMinutes();
  const padded = `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
  return locale === "fa-IR" ? formatNumber(padded, locale) : padded;
}

/** Full "date · time" label used by message bubbles and notification rows. */
export function formatTimestamp(iso: string, locale: Locale): string {
  return `${formatDate(iso, locale)} · ${formatTime(iso, locale)}`;
}

/**
 * Compact inbox timestamp: time for today, date otherwise. Comparison uses the
 * viewer's local calendar day so "today" means what the reader expects.
 */
export function formatInboxTimestamp(iso: string | null | undefined, locale: Locale): string {
  if (!iso) return "";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";

  const now = new Date();
  const sameDay =
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate();

  return sameDay ? formatTime(iso, locale) : formatDate(iso, locale);
}

/** Substitutes {name}-style placeholders without ever interpreting markup. */
export function interpolate(template: string, values: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (match, key: string) =>
    key in values ? String(values[key]) : match,
  );
}

/**
 * Resolves a notification into localized title and body strings.
 *
 * Server payloads carry i18n keys and metadata only, so all user-visible text
 * is produced on the client from the local dictionary. Unknown keys degrade to
 * the key itself rather than throwing.
 */
export function resolveNotificationText(
  notification: { title_key: string; body_key: string; payload: Record<string, unknown> },
  t: (key: string, fallback?: string) => string,
): { title: string; body: string } {
  const payload = notification.payload || {};
  const rawName = typeof payload.actor_display_name === "string" ? payload.actor_display_name : "";
  const severityKey = typeof payload.severity === "string" ? payload.severity : "";
  const flagKey = typeof payload.flag_type === "string" ? payload.flag_type : "";

  const values: Record<string, string> = {
    name: rawName,
    severity: severityKey ? t(`notifications.severity_${severityKey}`, severityKey) : "",
    flag_type: flagKey ? t(`notifications.flag_${flagKey}`, flagKey) : "",
  };

  return {
    title: interpolate(t(notification.title_key, notification.title_key), values),
    body: interpolate(t(notification.body_key, notification.body_key), values),
  };
}

/** Maps an API problem message_key to a localized, user-safe string. */
export function messageKeyToText(
  messageKey: string | undefined,
  t: (key: string, fallback?: string) => string,
): string | null {
  switch (messageKey) {
    case "errors.messaging.body_too_long":
      return t("messaging.too_long");
    case "errors.messaging.body_empty":
      return t("messaging.empty_body");
    case "errors.messaging.rate_limited":
      return t("messaging.rate_limited");
    case "errors.messaging.conversation_archived":
      return t("messaging.archived");
    case "errors.messaging.participant_inactive":
      return t("messaging.participant_inactive");
    case "errors.authz.unassigned_athlete":
      return t("messaging.unassigned");
    default:
      return null;
  }
}
