"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { AlertCircle, Bell, BellOff, CheckCheck, Loader2, RefreshCw } from "lucide-react";
import { useTranslation } from "../layout/DirectionProvider";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { ApiError } from "@/lib/api/client";
import {
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  type NotificationView,
} from "@/lib/api/messaging";
import { formatTimestamp, interpolate, resolveNotificationText } from "@/lib/messaging/format";

/**
 * In-app notification centre.
 *
 * Delivery model: notifications are fetched when the page loads and when the
 * user refreshes. Phase 08 has no WebSocket, no SSE, and no Web Push, so the
 * UI states plainly that updates arrive on refresh rather than implying
 * real-time delivery.
 */
export const NotificationCenter: React.FC = () => {
  const { locale, t } = useTranslation();

  const [notifications, setNotifications] = useState<NotificationView[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [updating, setUpdating] = useState(false);

  const load = useCallback(
    async (filterUnread: boolean) => {
      setLoading(true);
      setError(false);
      try {
        const response = await listNotifications(locale, { unreadOnly: filterUnread });
        setNotifications(response.notifications);
        setUnreadCount(response.unread_count);
      } catch (err) {
        if (!(err instanceof ApiError) || err.status >= 400) {
          setError(true);
        }
      } finally {
        setLoading(false);
      }
    },
    [locale],
  );

  useEffect(() => {
    void load(unreadOnly);
  }, [load, unreadOnly]);

  const handleMarkRead = async (notificationId: string) => {
    setUpdating(true);
    try {
      const updated = await markNotificationRead(notificationId, locale);
      setNotifications((current) =>
        unreadOnly
          ? current.filter((item) => item.id !== notificationId)
          : current.map((item) => (item.id === notificationId ? updated : item)),
      );
      setUnreadCount((count) => Math.max(0, count - 1));
    } catch {
      setError(true);
    } finally {
      setUpdating(false);
    }
  };

  const handleMarkAll = async () => {
    setUpdating(true);
    try {
      await markAllNotificationsRead(locale);
      await load(unreadOnly);
    } catch {
      setError(true);
    } finally {
      setUpdating(false);
    }
  };

  return (
    <section className="space-y-4" aria-label={t("notifications.center_title")}>
      <header className="space-y-1">
        <h1 className="text-xl font-semibold text-brand-text">
          {t("notifications.center_title")}
        </h1>
        <p className="text-sm text-brand-text-muted">{t("notifications.center_subtitle")}</p>
        {/* Honest capability statement: no real-time or push claim. */}
        <p className="text-xs text-brand-text-muted">{t("notifications.refresh_hint")}</p>
      </header>

      {/* Polite live region: announces the count, not each arriving item. */}
      <p className="sr-only" role="status" aria-live="polite">
        {unreadCount > 0
          ? interpolate(t("notifications.unread_count_label"), { count: unreadCount })
          : t("notifications.empty_title")}
      </p>

      <div className="flex flex-wrap items-center gap-2">
        <div role="group" aria-label={t("notifications.filter_all")} className="flex gap-2">
          <Button
            variant={unreadOnly ? "secondary" : "primary"}
            size="sm"
            aria-pressed={!unreadOnly}
            onClick={() => setUnreadOnly(false)}
          >
            {t("notifications.filter_all")}
          </Button>
          <Button
            variant={unreadOnly ? "primary" : "secondary"}
            size="sm"
            aria-pressed={unreadOnly}
            onClick={() => setUnreadOnly(true)}
          >
            {t("notifications.filter_unread")}
          </Button>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => void load(unreadOnly)}
          aria-label={t("notifications.refresh")}
        >
          <RefreshCw className="w-4 h-4" aria-hidden="true" />
          {t("notifications.refresh")}
        </Button>
        {unreadCount > 0 && (
          <Button
            variant="secondary"
            size="sm"
            onClick={() => void handleMarkAll()}
            disabled={updating}
          >
            <CheckCheck className="w-4 h-4" aria-hidden="true" />
            {updating ? t("notifications.marking") : t("notifications.mark_all_read")}
          </Button>
        )}
      </div>

      {loading ? (
        <div
          className="py-10 text-center text-brand-text-muted flex flex-col items-center gap-3"
          role="status"
          aria-live="polite"
        >
          <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
          <span>{t("notifications.loading")}</span>
        </div>
      ) : error ? (
        <Card variant="elevated" className="space-y-3" role="alert">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-400" aria-hidden="true" />
            <h2 className="font-semibold text-brand-text">{t("notifications.error_title")}</h2>
          </div>
          <Button onClick={() => void load(unreadOnly)}>{t("notifications.retry")}</Button>
        </Card>
      ) : notifications.length === 0 ? (
        <Card variant="elevated" className="text-center space-y-2 py-10">
          <BellOff className="w-8 h-8 mx-auto text-brand-text-muted" aria-hidden="true" />
          <h2 className="font-semibold text-brand-text">{t("notifications.empty_title")}</h2>
          <p className="text-sm text-brand-text-muted">{t("notifications.empty_desc")}</p>
        </Card>
      ) : (
        <ul className="space-y-2">
          {notifications.map((notification) => {
            const { title, body } = resolveNotificationText(notification, t);
            const isUnread = !notification.read_at;
            const route =
              typeof notification.payload.route === "string" ? notification.payload.route : null;

            return (
              <li key={notification.id}>
                <Card
                  variant="elevated"
                  className={`space-y-2 ${isUnread ? "border-emerald-500/30" : ""}`}
                >
                  <div className="flex items-start gap-3">
                    <Bell
                      className="w-5 h-5 mt-0.5 shrink-0 text-brand-text-muted"
                      aria-hidden="true"
                    />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <h3
                          className={`text-sm ${isUnread ? "font-bold" : "font-medium"} text-brand-text`}
                        >
                          <bdi>{title}</bdi>
                        </h3>
                        {/* Status conveyed by text, not colour alone. */}
                        <Badge variant={isUnread ? "success" : "neutral"} size="sm">
                          {isUnread
                            ? t("notifications.unread_label")
                            : t("notifications.read_label")}
                        </Badge>
                      </div>
                      <p className="text-sm text-brand-text-muted mt-1">
                        <bdi>{body}</bdi>
                      </p>
                      <p className="text-[11px] text-brand-text-muted mt-1">
                        <bdi>
                          {t(`notifications.category_${notification.category}`)} ·{" "}
                          {formatTimestamp(notification.created_at, locale)}
                        </bdi>
                      </p>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {route && (
                      <Link
                        href={`/${locale}${route}`}
                        className="inline-flex items-center min-h-[44px] px-3 rounded-lg text-sm text-emerald-400 hover:bg-obsidian-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
                      >
                        {t("notifications.open_link")}
                      </Link>
                    )}
                    {isUnread && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => void handleMarkRead(notification.id)}
                        disabled={updating}
                      >
                        {t("notifications.mark_read")}
                      </Button>
                    )}
                  </div>
                </Card>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
};
