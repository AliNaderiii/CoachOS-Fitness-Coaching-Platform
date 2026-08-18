"use client";

import React, { useCallback, useEffect, useState } from "react";
import { AlertCircle, Info, Loader2, Lock } from "lucide-react";
import { useTranslation } from "../layout/DirectionProvider";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { ApiError } from "@/lib/api/client";
import {
  getNotificationPreferences,
  updateNotificationPreferences,
  type NotificationChannel,
  type PreferencesResponse,
} from "@/lib/api/messaging";
import { interpolate } from "@/lib/messaging/format";

const CHANNELS: NotificationChannel[] = ["in_app", "email", "web_push"];

/**
 * Notification preference settings.
 *
 * Two honesty rules are enforced in the UI:
 * 1. Email and browser push are marked unavailable because Phase 08 has no
 *    provider — the toggles persist intent but promise no delivery.
 * 2. Safety alerts are shown as locked with an explanation rather than as a
 *    toggle that silently refuses to change.
 */
export const NotificationPreferences: React.FC = () => {
  const { locale, t } = useTranslation();

  const [data, setData] = useState<PreferencesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedMessage, setSavedMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(false);
    try {
      setData(await getNotificationPreferences(locale));
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [locale]);

  useEffect(() => {
    void load();
  }, [load]);

  const persist = async (
    payload: Parameters<typeof updateNotificationPreferences>[0],
  ) => {
    setSaving(true);
    setSavedMessage(null);
    try {
      setData(await updateNotificationPreferences(payload, locale));
      setSavedMessage(t("notification_prefs.saved"));
    } catch (err) {
      setSavedMessage(
        err instanceof ApiError && err.problem.message_key ===
          "errors.notifications.category_not_suppressible"
          ? t("notification_prefs.locked_hint")
          : t("notification_prefs.save_failed"),
      );
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div
        className="py-10 text-center text-brand-text-muted flex flex-col items-center gap-3"
        role="status"
        aria-live="polite"
      >
        <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
        <span>{t("notification_prefs.loading")}</span>
      </div>
    );
  }

  if (error || !data) {
    return (
      <Card variant="elevated" className="space-y-3" role="alert">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-400" aria-hidden="true" />
          <h2 className="font-semibold text-brand-text">
            {t("notification_prefs.error_title")}
          </h2>
        </div>
        <Button onClick={() => void load()}>{t("notifications.retry")}</Button>
      </Card>
    );
  }

  const eventTypes = Array.from(new Set(data.preferences.map((row) => row.event_type)));

  return (
    <section className="space-y-5" aria-label={t("notification_prefs.title")}>
      <header className="space-y-1">
        <h1 className="text-xl font-semibold text-brand-text">
          {t("notification_prefs.title")}
        </h1>
        <p className="text-sm text-brand-text-muted">{t("notification_prefs.subtitle")}</p>
      </header>

      <Card variant="elevated" className="flex items-start gap-2">
        <Info className="w-4 h-4 mt-0.5 text-brand-text-muted shrink-0" aria-hidden="true" />
        <p className="text-xs text-brand-text-muted">
          {t("notification_prefs.channel_unavailable_desc")}
        </p>
      </Card>

      {savedMessage && (
        <p className="text-sm text-emerald-400" role="status" aria-live="polite">
          {savedMessage}
        </p>
      )}

      <div className="space-y-3">
        {eventTypes.map((eventType) => {
          const rows = data.preferences.filter((row) => row.event_type === eventType);
          const label = t(`notification_prefs.event_${eventType.replace(/\./g, "_")}`);

          return (
            <Card key={eventType} variant="elevated" className="space-y-3">
              <h2 className="font-medium text-brand-text">{label}</h2>
              <ul className="space-y-2">
                {CHANNELS.map((channel) => {
                  const row = rows.find((item) => item.channel === channel);
                  if (!row) return null;
                  const available = data.channels_available[channel];
                  const inputId = `pref-${eventType}-${channel}`;

                  return (
                    <li key={channel} className="flex items-center justify-between gap-3">
                      <label
                        htmlFor={inputId}
                        className="flex items-center gap-2 text-sm text-brand-text min-h-[44px]"
                      >
                        <input
                          id={inputId}
                          type="checkbox"
                          checked={row.is_enabled}
                          disabled={row.is_locked || saving}
                          aria-describedby={row.is_locked ? `${inputId}-hint` : undefined}
                          onChange={(event) =>
                            void persist({
                              preferences: [
                                {
                                  event_type: eventType,
                                  channel,
                                  is_enabled: event.target.checked,
                                },
                              ],
                            })
                          }
                          className="w-5 h-5 rounded accent-emerald-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                        />
                        <span>{t(`notification_prefs.channel_${channel}`)}</span>
                        {row.is_locked && (
                          <Lock className="w-3.5 h-3.5 text-brand-text-muted" aria-hidden="true" />
                        )}
                      </label>

                      <div className="flex items-center gap-2">
                        {!available && (
                          <Badge variant="neutral" size="sm">
                            {t("notification_prefs.channel_unavailable")}
                          </Badge>
                        )}
                        {row.is_locked && (
                          <span
                            id={`${inputId}-hint`}
                            className="text-[11px] text-brand-text-muted max-w-[220px]"
                          >
                            {t("notification_prefs.locked_hint")}
                          </span>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>
            </Card>
          );
        })}
      </div>

      <Card variant="elevated" className="space-y-3">
        <h2 className="font-medium text-brand-text">
          {t("notification_prefs.quiet_hours_title")}
        </h2>
        <p className="text-xs text-brand-text-muted">
          {t("notification_prefs.quiet_hours_desc")}
        </p>

        <label
          htmlFor="quiet-hours-enabled"
          className="flex items-center gap-2 text-sm text-brand-text min-h-[44px]"
        >
          <input
            id="quiet-hours-enabled"
            type="checkbox"
            checked={data.quiet_hours_enabled}
            disabled={saving}
            onChange={(event) =>
              void persist({ quiet_hours_enabled: event.target.checked })
            }
            className="w-5 h-5 rounded accent-emerald-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
          />
          {t("notification_prefs.quiet_hours_enable")}
        </label>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label
              htmlFor="quiet-start"
              className="block text-xs text-brand-text-muted mb-1"
            >
              {t("notification_prefs.quiet_hours_start")}
            </label>
            <input
              id="quiet-start"
              type="time"
              value={data.quiet_hours_start}
              disabled={saving || !data.quiet_hours_enabled}
              onChange={(event) => void persist({ quiet_hours_start: event.target.value })}
              className="w-full min-h-[44px] rounded-lg bg-obsidian-900 border border-obsidian-700 px-3 text-sm text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
            />
          </div>
          <div>
            <label htmlFor="quiet-end" className="block text-xs text-brand-text-muted mb-1">
              {t("notification_prefs.quiet_hours_end")}
            </label>
            <input
              id="quiet-end"
              type="time"
              value={data.quiet_hours_end}
              disabled={saving || !data.quiet_hours_enabled}
              onChange={(event) => void persist({ quiet_hours_end: event.target.value })}
              className="w-full min-h-[44px] rounded-lg bg-obsidian-900 border border-obsidian-700 px-3 text-sm text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
            />
          </div>
        </div>

        <p className="text-[11px] text-brand-text-muted">
          <bdi>
            {interpolate(t("notification_prefs.timezone_note"), { timezone: data.timezone })}
          </bdi>
        </p>
      </Card>

      <Card variant="elevated" className="space-y-2">
        <h2 className="font-medium text-brand-text">
          {t("notification_prefs.push_permission_title")}
        </h2>
        <Badge
          variant={data.web_push_permission_state === "denied" ? "warning" : "neutral"}
          size="sm"
        >
          {t(`notification_prefs.push_permission_${data.web_push_permission_state}`)}
        </Badge>
        {data.web_push_permission_state === "denied" && (
          <p className="text-xs text-brand-text-muted">
            {t("notification_prefs.push_denied_hint")}
          </p>
        )}
      </Card>

      {saving && (
        <p className="text-xs text-brand-text-muted" role="status" aria-live="polite">
          {t("notification_prefs.saving")}
        </p>
      )}
    </section>
  );
};
