import type { Locale } from "../i18n/config";
import { request } from "./client";

/**
 * Phase 08 communication and notification API — typed client.
 *
 * Authentication is cookie-managed; this module stores no tokens. There is no
 * durable offline queue, no client-side database, and no background sync:
 * message sends are online-only with an in-memory retry affordance. Durable
 * offline behaviour is owned by Phase 12.
 */

export type ConversationKind = "direct";
export type ConversationContextType = "none" | "workout_session";
export type NotificationCategory = "messaging" | "training" | "safety" | "account";
export type NotificationChannel = "in_app" | "email" | "web_push";
export type PushPermissionState = "unknown" | "granted" | "denied";

export interface CounterpartView {
  user_id: string;
  display_name: string;
  role: string;
  is_active: boolean;
}

export interface ConversationView {
  id: string;
  organization_id: string;
  kind: ConversationKind;
  context_type: ConversationContextType;
  context_id?: string | null;
  last_message_at?: string | null;
  last_message_preview: string;
  is_archived: boolean;
  created_at: string;
  counterpart: CounterpartView | null;
  unread_count: number;
}

export interface ConversationDetailView extends ConversationView {
  can_send: boolean;
  send_block_key: string;
  last_read_at?: string | null;
  is_muted: boolean;
}

export interface MessageView {
  id: string;
  conversation_id: string;
  sender_user_id: string;
  body: string;
  created_at: string;
}

export interface ConversationListResponse {
  conversations: ConversationView[];
  next_cursor: string | null;
}

export interface MessageListResponse {
  messages: MessageView[];
  next_cursor: string | null;
  has_more: boolean;
}

export interface NotificationView {
  id: string;
  organization_id?: string | null;
  event_type: string;
  category: NotificationCategory;
  title_key: string;
  body_key: string;
  payload: Record<string, unknown>;
  read_at?: string | null;
  created_at: string;
}

export interface NotificationListResponse {
  notifications: NotificationView[];
  unread_count: number;
  next_cursor: string | null;
}

export interface PreferenceRow {
  event_type: string;
  category: NotificationCategory;
  channel: NotificationChannel;
  is_enabled: boolean;
  is_locked: boolean;
}

export interface PreferencesResponse {
  preferences: PreferenceRow[];
  quiet_hours_enabled: boolean;
  quiet_hours_start: string;
  quiet_hours_end: string;
  web_push_permission_state: PushPermissionState;
  timezone: string;
  channels_available: Record<NotificationChannel, boolean>;
}

export interface ReadReceiptResponse {
  conversation_id: string;
  last_read_at: string;
  unread_count: number;
}

// --- Conversations ---------------------------------------------------------- //

export function listConversations(locale: Locale, cursor?: string | null, limit = 20) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (cursor) params.set("cursor", cursor);
  return request<ConversationListResponse>(`conversations?${params.toString()}`, { locale });
}

export function createConversation(
  input: {
    counterpart_user_id: string;
    context_type?: ConversationContextType;
    context_id?: string | null;
  },
  locale: Locale,
) {
  return request<ConversationView>("conversations", {
    method: "POST",
    locale,
    json: input,
  });
}

export function getConversation(conversationId: string, locale: Locale) {
  return request<ConversationDetailView>(`conversations/${conversationId}`, { locale });
}

export function listMessages(
  conversationId: string,
  locale: Locale,
  before?: string | null,
  limit = 30,
) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (before) params.set("before", before);
  return request<MessageListResponse>(
    `conversations/${conversationId}/messages?${params.toString()}`,
    { locale },
  );
}

export function sendMessage(
  conversationId: string,
  input: { body: string; client_message_id?: string },
  locale: Locale,
) {
  return request<MessageView>(`conversations/${conversationId}/messages`, {
    method: "POST",
    locale,
    json: input,
    // The server deduplicates on client_message_id, so a retry after a network
    // failure can never create a second message.
    idempotencyKey: input.client_message_id,
  });
}

export function markConversationRead(conversationId: string, locale: Locale) {
  return request<ReadReceiptResponse>(`conversations/${conversationId}/read`, {
    method: "POST",
    locale,
    json: {},
  });
}

export function setConversationMuted(
  conversationId: string,
  isMuted: boolean,
  locale: Locale,
) {
  return request<{ conversation_id: string; is_muted: boolean }>(
    `conversations/${conversationId}/mute`,
    { method: "POST", locale, json: { is_muted: isMuted } },
  );
}

// --- Notifications ---------------------------------------------------------- //

export function listNotifications(
  locale: Locale,
  options: { unreadOnly?: boolean; category?: NotificationCategory; cursor?: string | null } = {},
) {
  const params = new URLSearchParams({ limit: "20" });
  if (options.unreadOnly) params.set("unread", "true");
  if (options.category) params.set("category", options.category);
  if (options.cursor) params.set("cursor", options.cursor);
  return request<NotificationListResponse>(`notifications?${params.toString()}`, { locale });
}

export function markNotificationRead(notificationId: string, locale: Locale) {
  return request<NotificationView>(`notifications/${notificationId}/read`, {
    method: "POST",
    locale,
    json: {},
  });
}

export function markAllNotificationsRead(locale: Locale) {
  return request<{ updated: number; read_at: string }>("notifications/read-all", {
    method: "POST",
    locale,
    json: {},
  });
}

export function getNotificationPreferences(locale: Locale) {
  return request<PreferencesResponse>("notification-preferences", { locale });
}

export function updateNotificationPreferences(
  input: {
    preferences?: Array<{
      event_type: string;
      channel: NotificationChannel;
      is_enabled: boolean;
    }>;
    quiet_hours_enabled?: boolean;
    quiet_hours_start?: string;
    quiet_hours_end?: string;
    web_push_permission_state?: PushPermissionState;
  },
  locale: Locale,
) {
  return request<PreferencesResponse>("notification-preferences", {
    method: "PATCH",
    locale,
    json: input,
  });
}

/**
 * Generates a client message id for idempotent sends.
 *
 * Uses crypto.randomUUID when available and falls back to a timestamped random
 * string. The value is a correlation token only — it is never a security token
 * and carries no user data.
 */
export function newClientMessageId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `cmid-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}
