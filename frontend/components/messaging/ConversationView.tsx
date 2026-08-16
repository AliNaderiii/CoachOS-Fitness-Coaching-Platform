"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { AlertCircle, ArrowLeft, Loader2, RefreshCw, Send } from "lucide-react";
import { useTranslation } from "../layout/DirectionProvider";
import { Card } from "../ui/Card";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import { ApiError } from "@/lib/api/client";
import {
  getConversation,
  listMessages,
  markConversationRead,
  newClientMessageId,
  sendMessage,
  type ConversationDetailView,
  type MessageView,
} from "@/lib/api/messaging";
import { formatTimestamp, interpolate, messageKeyToText } from "@/lib/messaging/format";
import { useNetworkStatus } from "@/lib/athlete/useNetworkStatus";

const MESSAGE_MAX_LENGTH = 2000;
const PAGE_SIZE = 30;

export interface ConversationViewProps {
  conversationId: string;
  currentUserId?: string;
}

/**
 * Conversation detail with an accessible composer.
 *
 * Send model: no optimistic insertion. A pending message is shown as a distinct
 * "sending" row and only becomes a real message when the server confirms it,
 * so there is never a rollback of content the user believes was delivered. A
 * failed send keeps the text in the composer with an explicit retry that reuses
 * the same client_message_id, which the server deduplicates.
 *
 * There is no durable offline queue: nothing is persisted to storage and no
 * background sync is registered.
 */
export const ConversationView: React.FC<ConversationViewProps> = ({
  conversationId,
  currentUserId,
}) => {
  const { locale, t } = useTranslation();
  const { online: isOnline } = useNetworkStatus();

  const [conversation, setConversation] = useState<ConversationDetailView | null>(null);
  const [messages, setMessages] = useState<MessageView[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);

  const [loading, setLoading] = useState(true);
  const [loadingOlder, setLoadingOlder] = useState(false);
  const [error, setError] = useState(false);
  const [notFound, setNotFound] = useState(false);

  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const pendingIdRef = useRef<string | null>(null);
  const composerRef = useRef<HTMLTextAreaElement>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(false);
    setNotFound(false);
    try {
      const [detail, history] = await Promise.all([
        getConversation(conversationId, locale),
        listMessages(conversationId, locale, null, PAGE_SIZE),
      ]);
      setConversation(detail);
      // The API returns newest-first; render oldest-first for reading order.
      setMessages([...history.messages].reverse());
      setCursor(history.next_cursor);
      setHasMore(history.has_more);

      if (detail.unread_count > 0) {
        try {
          await markConversationRead(conversationId, locale);
        } catch {
          // A failed read receipt must never break the reading experience.
        }
      }
    } catch (err) {
      if (err instanceof ApiError && (err.status === 404 || err.status === 403)) {
        setNotFound(true);
      } else {
        setError(true);
      }
    } finally {
      setLoading(false);
    }
  }, [conversationId, locale]);

  useEffect(() => {
    void load();
  }, [load]);

  const loadOlder = async () => {
    if (!cursor || loadingOlder) return;
    setLoadingOlder(true);
    try {
      const older = await listMessages(conversationId, locale, cursor, PAGE_SIZE);
      setMessages((current) => [...[...older.messages].reverse(), ...current]);
      setCursor(older.next_cursor);
      setHasMore(older.has_more);
    } catch {
      setSendError(t("messaging.inbox_error_desc"));
    } finally {
      setLoadingOlder(false);
    }
  };

  const performSend = async (body: string, clientMessageId: string) => {
    setSending(true);
    setSendError(null);
    try {
      const created = await sendMessage(
        conversationId,
        { body, client_message_id: clientMessageId },
        locale,
      );
      setMessages((current) =>
        current.some((message) => message.id === created.id)
          ? current
          : [...current, created],
      );
      setDraft("");
      pendingIdRef.current = null;
    } catch (err) {
      if (err instanceof ApiError) {
        setSendError(
          messageKeyToText(err.problem.message_key, t) || t("messaging.send_failed_desc"),
        );
      } else {
        setSendError(t("messaging.send_failed_desc"));
      }
    } finally {
      setSending(false);
      composerRef.current?.focus();
    }
  };

  const handleSend = async () => {
    const body = draft.trim();
    if (!body) {
      setSendError(t("messaging.empty_body"));
      return;
    }
    if (body.length > MESSAGE_MAX_LENGTH) {
      setSendError(t("messaging.too_long"));
      return;
    }
    // Reuse the same id on retry so the server deduplicates rather than
    // creating a second message.
    const clientMessageId = pendingIdRef.current ?? newClientMessageId();
    pendingIdRef.current = clientMessageId;
    await performSend(body, clientMessageId);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter sends; Shift+Enter inserts a newline. Both are keyboard-only paths.
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSend();
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
        <span>{t("messaging.conversation_loading")}</span>
      </div>
    );
  }

  if (notFound) {
    return (
      <Card variant="elevated" className="space-y-3">
        <h2 className="font-semibold text-brand-text">{t("messaging.not_found_title")}</h2>
        <p className="text-sm text-brand-text-muted">{t("messaging.not_found_desc")}</p>
        <Link
          href={`/${locale}/messages`}
          className="inline-flex items-center gap-2 text-emerald-400 min-h-[44px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 rounded-lg"
        >
          <ArrowLeft className="w-4 h-4" aria-hidden="true" />
          {t("messaging.back_to_inbox")}
        </Link>
      </Card>
    );
  }

  if (error || !conversation) {
    return (
      <Card variant="elevated" className="space-y-3" role="alert">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-400" aria-hidden="true" />
          <h2 className="font-semibold text-brand-text">{t("messaging.inbox_error_title")}</h2>
        </div>
        <Button onClick={() => void load()}>{t("messaging.retry")}</Button>
      </Card>
    );
  }

  const counterpartName = conversation.counterpart?.display_name || "";
  const blockedReason = conversation.can_send
    ? null
    : messageKeyToText(conversation.send_block_key, t) || t("messaging.read_only_notice");
  const remaining = MESSAGE_MAX_LENGTH - draft.length;

  return (
    <section className="flex flex-col gap-4" aria-label={t("messaging.message_list_label")}>
      <header className="flex items-center gap-3">
        <Link
          href={`/${locale}/messages`}
          aria-label={t("messaging.back_to_inbox")}
          className="inline-flex items-center justify-center min-h-[44px] min-w-[44px] rounded-lg text-brand-text-muted hover:text-brand-text focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500"
        >
          {/* Logical property: the icon mirrors automatically in RTL. */}
          <ArrowLeft className="w-5 h-5 rtl:rotate-180" aria-hidden="true" />
        </Link>
        <div className="min-w-0">
          <h1 className="text-lg font-semibold text-brand-text truncate">
            <bdi>{counterpartName}</bdi>
          </h1>
          {conversation.context_type === "workout_session" && (
            <p className="text-xs text-brand-text-muted">{t("messaging.context_workout")}</p>
          )}
        </div>
      </header>

      {!isOnline && (
        <Card variant="elevated" className="border-amber-500/30" role="status">
          <p className="font-medium text-amber-400">{t("messaging.offline_title")}</p>
          <p className="text-sm text-brand-text-muted">{t("messaging.offline_desc")}</p>
        </Card>
      )}

      {conversation.is_muted && (
        <p className="text-xs text-brand-text-muted">{t("messaging.muted_notice")}</p>
      )}

      {hasMore && (
        <Button
          variant="secondary"
          onClick={() => void loadOlder()}
          disabled={loadingOlder}
          className="self-center"
        >
          {loadingOlder ? t("messaging.loading_older") : t("messaging.load_older")}
        </Button>
      )}

      {messages.length === 0 ? (
        <Card variant="elevated" className="text-center space-y-2 py-8">
          <h2 className="font-semibold text-brand-text">
            {t("messaging.conversation_empty_title")}
          </h2>
          <p className="text-sm text-brand-text-muted">
            {t("messaging.conversation_empty_desc")}
          </p>
        </Card>
      ) : (
        <ol className="space-y-3" aria-label={t("messaging.message_list_label")}>
          {messages.map((message) => {
            const isOwn = currentUserId ? message.sender_user_id === currentUserId : false;
            return (
              <li
                key={message.id}
                className={`flex ${isOwn ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${
                    isOwn
                      ? "bg-emerald-500/15 border border-emerald-500/30"
                      : "bg-obsidian-900 border border-obsidian-800"
                  }`}
                >
                  <span className="sr-only">
                    {isOwn ? t("messaging.sent_by_you") : t("messaging.sent_by_them")}
                  </span>
                  {/*
                    Message bodies are rendered as plain React text nodes. React
                    escapes them, and dangerouslySetInnerHTML is never used, so
                    a stored script payload cannot execute. URLs are shown as
                    inert text: no auto-linking in Phase 08.
                  */}
                  <p className="text-sm text-brand-text whitespace-pre-wrap break-words">
                    <bdi>{message.body}</bdi>
                  </p>
                  <time
                    dateTime={message.created_at}
                    className="block text-[11px] text-brand-text-muted mt-1"
                  >
                    <bdi>{formatTimestamp(message.created_at, locale)}</bdi>
                  </time>
                </div>
              </li>
            );
          })}
        </ol>
      )}

      {sending && (
        <p className="text-xs text-brand-text-muted text-center" role="status" aria-live="polite">
          {t("messaging.sending")}
        </p>
      )}

      {blockedReason ? (
        <Card variant="elevated" className="border-amber-500/30">
          <p className="text-sm text-amber-300">{blockedReason}</p>
        </Card>
      ) : (
        <div className="sticky bottom-16 md:bottom-0 bg-obsidian-950/95 backdrop-blur-sm pt-2">
          {sendError && (
            <div className="mb-2 flex items-start gap-2" role="alert">
              <AlertCircle className="w-4 h-4 mt-0.5 text-red-400 shrink-0" aria-hidden="true" />
              <div className="flex-1">
                <p className="text-sm text-red-300">{sendError}</p>
                <Button
                  variant="secondary"
                  size="sm"
                  className="mt-2"
                  onClick={() => void handleSend()}
                  disabled={sending}
                >
                  <RefreshCw className="w-4 h-4" aria-hidden="true" />
                  {t("messaging.retry_send")}
                </Button>
              </div>
            </div>
          )}

          <label htmlFor="message-composer" className="sr-only">
            {t("messaging.composer_label")}
          </label>
          <div className="flex items-end gap-2">
            <textarea
              id="message-composer"
              ref={composerRef}
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={handleKeyDown}
              rows={2}
              maxLength={MESSAGE_MAX_LENGTH}
              placeholder={t("messaging.composer_placeholder")}
              aria-describedby="composer-counter"
              className="flex-1 min-h-[44px] rounded-lg bg-obsidian-900 border border-obsidian-700 px-3 py-2 text-sm text-brand-text placeholder:text-brand-text-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 resize-none"
            />
            <Button
              onClick={() => void handleSend()}
              disabled={sending || draft.trim().length === 0}
              isLoading={sending}
              aria-label={t("messaging.send")}
              className="min-w-[44px]"
            >
              <Send className="w-4 h-4 rtl:rotate-180" aria-hidden="true" />
              <span className="hidden sm:inline">{t("messaging.send")}</span>
            </Button>
          </div>
          <p id="composer-counter" className="text-[11px] text-brand-text-muted mt-1">
            {interpolate(t("messaging.characters_remaining"), { count: remaining })}
          </p>
          {remaining < 0 && (
            <Badge variant="error" size="sm" className="mt-1">
              {t("messaging.too_long")}
            </Badge>
          )}
        </div>
      )}
    </section>
  );
};
