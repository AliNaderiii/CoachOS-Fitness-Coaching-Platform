"use client";

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { AlertCircle, Inbox, Loader2, MessageSquare } from "lucide-react";
import { useTranslation } from "../layout/DirectionProvider";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { ApiError } from "@/lib/api/client";
import { listConversations, type ConversationView } from "@/lib/api/messaging";
import { formatInboxTimestamp, interpolate } from "@/lib/messaging/format";

/**
 * Inbox / conversation list.
 *
 * States: loading, empty, error, forbidden, and populated. Unread state is
 * conveyed by a text badge, a bold title, and an accessible label — never by
 * colour alone.
 */
export const ConversationList: React.FC = () => {
  const { locale, t } = useTranslation();

  const [conversations, setConversations] = useState<ConversationView[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [forbidden, setForbidden] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(false);
    setForbidden(false);
    try {
      const response = await listConversations(locale);
      setConversations(response.conversations);
    } catch (err) {
      if (err instanceof ApiError && (err.status === 403 || err.status === 404)) {
        setForbidden(true);
      } else {
        setError(true);
      }
    } finally {
      setLoading(false);
    }
  }, [locale]);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) {
    return (
      <div
        className="py-10 text-center text-brand-text-muted flex flex-col items-center gap-3"
        role="status"
        aria-live="polite"
      >
        <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
        <span>{t("messaging.inbox_loading")}</span>
      </div>
    );
  }

  if (forbidden) {
    return (
      <Card variant="elevated" className="space-y-2">
        <h2 className="font-semibold text-brand-text">{t("messaging.forbidden_title")}</h2>
        <p className="text-sm text-brand-text-muted">{t("messaging.forbidden_desc")}</p>
      </Card>
    );
  }

  if (error) {
    return (
      <Card variant="elevated" className="space-y-3" role="alert">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-400" aria-hidden="true" />
          <h2 className="font-semibold text-brand-text">{t("messaging.inbox_error_title")}</h2>
        </div>
        <p className="text-sm text-brand-text-muted">{t("messaging.inbox_error_desc")}</p>
        <Button onClick={() => void load()}>{t("messaging.retry")}</Button>
      </Card>
    );
  }

  if (conversations.length === 0) {
    return (
      <Card variant="elevated" className="space-y-2 text-center py-10">
        <Inbox className="w-8 h-8 mx-auto text-brand-text-muted" aria-hidden="true" />
        <h2 className="font-semibold text-brand-text">{t("messaging.inbox_empty_title")}</h2>
        <p className="text-sm text-brand-text-muted">{t("messaging.inbox_empty_desc")}</p>
      </Card>
    );
  }

  const totalUnread = conversations.reduce((sum, item) => sum + item.unread_count, 0);

  return (
    <div className="space-y-3">
      <p className="sr-only" role="status" aria-live="polite">
        {totalUnread > 0
          ? interpolate(t("messaging.unread_count_label"), { count: totalUnread })
          : t("messaging.no_unread")}
      </p>

      <ul className="space-y-2" aria-label={t("messaging.inbox_title")}>
        {conversations.map((conversation) => {
          const isUnread = conversation.unread_count > 0;
          const name = conversation.counterpart?.display_name || "";

          return (
            <li key={conversation.id}>
              <Link
                href={`/${locale}/messages/${conversation.id}`}
                className="block rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
              >
                <Card
                  variant="interactive"
                  className="flex items-start gap-3 min-h-[64px] py-3"
                >
                  <MessageSquare
                    className="w-5 h-5 mt-0.5 shrink-0 text-brand-text-muted"
                    aria-hidden="true"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-baseline justify-between gap-2">
                      <span
                        className={`truncate ${isUnread ? "font-bold text-brand-text" : "font-medium text-brand-text"}`}
                      >
                        {/* Isolate the name so a RTL/LTR name cannot reorder the row. */}
                        <bdi>{name}</bdi>
                      </span>
                      <span className="text-xs text-brand-text-muted shrink-0">
                        <bdi>{formatInboxTimestamp(conversation.last_message_at, locale)}</bdi>
                      </span>
                    </div>
                    <p
                      className={`text-sm truncate ${isUnread ? "text-brand-text" : "text-brand-text-muted"}`}
                    >
                      <bdi>{conversation.last_message_preview}</bdi>
                    </p>
                    {conversation.context_type === "workout_session" && (
                      <p className="text-xs text-brand-text-muted mt-1">
                        {t("messaging.context_workout")}
                      </p>
                    )}
                  </div>
                  {isUnread && (
                    <Badge variant="success" size="sm" className="shrink-0">
                      {/* Text label, not colour alone. */}
                      {t("messaging.unread_badge")}
                    </Badge>
                  )}
                </Card>
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
};
