import React from "react";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import "@testing-library/jest-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { DirectionProvider } from "../components/layout/DirectionProvider";
import { ConversationList } from "../components/messaging/ConversationList";
import { ConversationView } from "../components/messaging/ConversationView";
import { NotificationCenter } from "../components/messaging/NotificationCenter";
import { NotificationPreferences } from "../components/messaging/NotificationPreferences";
import { ApiError } from "../lib/api/client";
import {
  formatInboxTimestamp,
  formatTimestamp,
  interpolate,
  messageKeyToText,
  resolveNotificationText,
} from "../lib/messaging/format";
import * as messagingApi from "../lib/api/messaging";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn(), back: vi.fn(), replace: vi.fn() }),
  usePathname: () => "/fa-IR/messages",
  useParams: () => ({ conversationId: "conv-1" }),
}));

vi.mock("../lib/api/messaging", () => ({
  listConversations: vi.fn(),
  createConversation: vi.fn(),
  getConversation: vi.fn(),
  listMessages: vi.fn(),
  sendMessage: vi.fn(),
  markConversationRead: vi.fn(),
  setConversationMuted: vi.fn(),
  listNotifications: vi.fn(),
  markNotificationRead: vi.fn(),
  markAllNotificationsRead: vi.fn(),
  getNotificationPreferences: vi.fn(),
  updateNotificationPreferences: vi.fn(),
  newClientMessageId: vi.fn(() => "client-id-1"),
}));

const renderWith = (locale: "fa-IR" | "en-US", ui: React.ReactNode) =>
  render(<DirectionProvider locale={locale}>{ui}</DirectionProvider>);

const conversation = {
  id: "conv-1",
  organization_id: "org-1",
  kind: "direct" as const,
  context_type: "none" as const,
  context_id: null,
  last_message_at: "2026-08-16T10:00:00Z",
  last_message_preview: "Great depth on set 3",
  is_archived: false,
  created_at: "2026-08-15T10:00:00Z",
  counterpart: {
    user_id: "coach-1",
    display_name: "Coach Reza",
    role: "coach",
    is_active: true,
  },
  unread_count: 2,
};

const detail = {
  ...conversation,
  unread_count: 0,
  can_send: true,
  send_block_key: "",
  last_read_at: null,
  is_muted: false,
};

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(messagingApi.newClientMessageId).mockReturnValue("client-id-1");
  vi.mocked(messagingApi.listConversations).mockResolvedValue({
    conversations: [conversation],
    next_cursor: null,
  });
  vi.mocked(messagingApi.getConversation).mockResolvedValue(detail);
  vi.mocked(messagingApi.listMessages).mockResolvedValue({
    messages: [
      {
        id: "m-1",
        conversation_id: "conv-1",
        sender_user_id: "coach-1",
        body: "Great depth on set 3",
        created_at: "2026-08-16T10:00:00Z",
      },
    ],
    next_cursor: null,
    has_more: false,
  });
  vi.mocked(messagingApi.markConversationRead).mockResolvedValue({
    conversation_id: "conv-1",
    last_read_at: "2026-08-16T10:05:00Z",
    unread_count: 0,
  });
});

// --- Inbox ------------------------------------------------------------------ //

describe("ConversationList", () => {
  it("shows a loading state before data arrives", () => {
    vi.mocked(messagingApi.listConversations).mockReturnValue(new Promise(() => {}));
    renderWith("en-US", <ConversationList />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading conversations");
  });

  it("renders the counterpart, preview, timestamp and unread badge", async () => {
    renderWith("en-US", <ConversationList />);
    expect(await screen.findByText("Coach Reza")).toBeInTheDocument();
    expect(screen.getByText("Great depth on set 3")).toBeInTheDocument();
    expect(screen.getByText("Unread")).toBeInTheDocument();
  });

  it("announces the unread total in a polite live region", async () => {
    renderWith("en-US", <ConversationList />);
    await screen.findByText("Coach Reza");
    const live = document.querySelector('[aria-live="polite"]');
    expect(live).toHaveTextContent("2 unread messages");
  });

  it("does not rely on colour alone for unread state", async () => {
    renderWith("en-US", <ConversationList />);
    // A textual badge plus a bold title carry the state, not just a hue.
    expect(await screen.findByText("Unread")).toBeInTheDocument();
  });

  it("renders the empty state", async () => {
    vi.mocked(messagingApi.listConversations).mockResolvedValue({
      conversations: [],
      next_cursor: null,
    });
    renderWith("en-US", <ConversationList />);
    expect(await screen.findByText("No conversations yet")).toBeInTheDocument();
  });

  it("renders a forbidden state without leaking detail", async () => {
    vi.mocked(messagingApi.listConversations).mockRejectedValue(
      new ApiError({ title: "Forbidden", status: 403 }),
    );
    renderWith("en-US", <ConversationList />);
    expect(await screen.findByText("Not available")).toBeInTheDocument();
  });

  it("renders an error state with a retry action", async () => {
    vi.mocked(messagingApi.listConversations).mockRejectedValue(new Error("network"));
    renderWith("en-US", <ConversationList />);
    const retry = await screen.findByRole("button", { name: "Try again" });

    vi.mocked(messagingApi.listConversations).mockResolvedValue({
      conversations: [conversation],
      next_cursor: null,
    });
    fireEvent.click(retry);
    expect(await screen.findByText("Coach Reza")).toBeInTheDocument();
  });

  it("renders Persian strings under fa-IR", async () => {
    renderWith("fa-IR", <ConversationList />);
    expect(await screen.findByText("خوانده‌نشده")).toBeInTheDocument();
  });
});

// --- Conversation ------------------------------------------------------------- //

describe("ConversationView", () => {
  it("renders history and marks the thread read when unread", async () => {
    vi.mocked(messagingApi.getConversation).mockResolvedValue({
      ...detail,
      unread_count: 3,
    });
    renderWith("en-US", <ConversationView conversationId="conv-1" currentUserId="ath-1" />);

    expect(await screen.findByText("Great depth on set 3")).toBeInTheDocument();
    await waitFor(() =>
      expect(messagingApi.markConversationRead).toHaveBeenCalledWith("conv-1", "en-US"),
    );
  });

  it("renders message bodies as inert text, never as HTML", async () => {
    vi.mocked(messagingApi.listMessages).mockResolvedValue({
      messages: [
        {
          id: "m-x",
          conversation_id: "conv-1",
          sender_user_id: "coach-1",
          body: "<script>alert('xss')</script><img src=x onerror=alert(1)>",
          created_at: "2026-08-16T10:00:00Z",
        },
      ],
      next_cursor: null,
      has_more: false,
    });
    const { container } = renderWith(
      "en-US",
      <ConversationView conversationId="conv-1" currentUserId="ath-1" />,
    );

    // The payload is visible as literal text and no element was created.
    expect(
      await screen.findByText("<script>alert('xss')</script><img src=x onerror=alert(1)>"),
    ).toBeInTheDocument();
    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("img")).toBeNull();
  });

  it("does not auto-link URLs in message bodies", async () => {
    vi.mocked(messagingApi.listMessages).mockResolvedValue({
      messages: [
        {
          id: "m-url",
          conversation_id: "conv-1",
          sender_user_id: "coach-1",
          body: "see https://evil.test/steal",
          created_at: "2026-08-16T10:00:00Z",
        },
      ],
      next_cursor: null,
      has_more: false,
    });
    renderWith("en-US", <ConversationView conversationId="conv-1" currentUserId="ath-1" />);

    const bubble = await screen.findByText("see https://evil.test/steal");
    expect(within(bubble.closest("li") as HTMLElement).queryByRole("link")).toBeNull();
  });

  it("sends a message with an idempotent client id", async () => {
    vi.mocked(messagingApi.sendMessage).mockResolvedValue({
      id: "m-2",
      conversation_id: "conv-1",
      sender_user_id: "ath-1",
      body: "Thanks coach",
      created_at: "2026-08-16T11:00:00Z",
    });
    renderWith("en-US", <ConversationView conversationId="conv-1" currentUserId="ath-1" />);

    const composer = await screen.findByLabelText("Write a message");
    fireEvent.change(composer, { target: { value: "Thanks coach" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() =>
      expect(messagingApi.sendMessage).toHaveBeenCalledWith(
        "conv-1",
        { body: "Thanks coach", client_message_id: "client-id-1" },
        "en-US",
      ),
    );
    expect(await screen.findByText("Thanks coach")).toBeInTheDocument();
  });

  it("sends on Enter and inserts a newline on Shift+Enter", async () => {
    vi.mocked(messagingApi.sendMessage).mockResolvedValue({
      id: "m-3",
      conversation_id: "conv-1",
      sender_user_id: "ath-1",
      body: "keyboard send",
      created_at: "2026-08-16T11:00:00Z",
    });
    renderWith("en-US", <ConversationView conversationId="conv-1" currentUserId="ath-1" />);

    const composer = await screen.findByLabelText("Write a message");
    fireEvent.change(composer, { target: { value: "keyboard send" } });
    fireEvent.keyDown(composer, { key: "Enter", shiftKey: true });
    expect(messagingApi.sendMessage).not.toHaveBeenCalled();

    fireEvent.keyDown(composer, { key: "Enter" });
    await waitFor(() => expect(messagingApi.sendMessage).toHaveBeenCalledTimes(1));
  });

  it("keeps the draft and offers retry when a send fails", async () => {
    vi.mocked(messagingApi.sendMessage).mockRejectedValue(
      new ApiError({ title: "Server error", status: 500 }),
    );
    renderWith("en-US", <ConversationView conversationId="conv-1" currentUserId="ath-1" />);

    const composer = await screen.findByLabelText("Write a message");
    fireEvent.change(composer, { target: { value: "will fail" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    expect(await screen.findByRole("alert")).toBeInTheDocument();
    // Content is preserved: nothing was optimistically shown as delivered.
    expect(composer).toHaveValue("will fail");
    expect(screen.queryByText("will fail", { selector: "p" })).toBeNull();
  });

  it("reuses the same client id on retry so the server can deduplicate", async () => {
    vi.mocked(messagingApi.sendMessage).mockRejectedValueOnce(new Error("boom"));
    renderWith("en-US", <ConversationView conversationId="conv-1" currentUserId="ath-1" />);

    const composer = await screen.findByLabelText("Write a message");
    fireEvent.change(composer, { target: { value: "retry me" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    const retry = await screen.findByRole("button", { name: /Retry sending/ });
    vi.mocked(messagingApi.sendMessage).mockResolvedValue({
      id: "m-4",
      conversation_id: "conv-1",
      sender_user_id: "ath-1",
      body: "retry me",
      created_at: "2026-08-16T11:05:00Z",
    });
    fireEvent.click(retry);

    await waitFor(() => expect(messagingApi.sendMessage).toHaveBeenCalledTimes(2));
    const [, secondCall] = vi.mocked(messagingApi.sendMessage).mock.calls;
    expect(secondCall[1].client_message_id).toBe("client-id-1");
  });

  it("surfaces a localized rate-limit message", async () => {
    vi.mocked(messagingApi.sendMessage).mockRejectedValue(
      new ApiError({
        title: "Rate limited",
        status: 429,
        message_key: "errors.messaging.rate_limited",
      }),
    );
    renderWith("en-US", <ConversationView conversationId="conv-1" currentUserId="ath-1" />);

    const composer = await screen.findByLabelText("Write a message");
    fireEvent.change(composer, { target: { value: "spam" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    expect(
      await screen.findByText(/sending messages too quickly/i),
    ).toBeInTheDocument();
  });

  it("hides the composer and explains why when sending is blocked", async () => {
    vi.mocked(messagingApi.getConversation).mockResolvedValue({
      ...detail,
      can_send: false,
      send_block_key: "errors.authz.unassigned_athlete",
    });
    renderWith("en-US", <ConversationView conversationId="conv-1" currentUserId="ath-1" />);

    expect(await screen.findByText(/no longer assigned/i)).toBeInTheDocument();
    expect(screen.queryByLabelText("Write a message")).toBeNull();
  });

  it("explains an archived read-only conversation", async () => {
    vi.mocked(messagingApi.getConversation).mockResolvedValue({
      ...detail,
      is_archived: true,
      can_send: false,
      send_block_key: "errors.messaging.conversation_archived",
    });
    renderWith("en-US", <ConversationView conversationId="conv-1" currentUserId="ath-1" />);
    expect(await screen.findByText(/archived and is read-only/i)).toBeInTheDocument();
  });

  it("renders a safe not-found state for an inaccessible conversation", async () => {
    vi.mocked(messagingApi.getConversation).mockRejectedValue(
      new ApiError({ title: "Not found", status: 404 }),
    );
    renderWith("en-US", <ConversationView conversationId="conv-1" />);
    expect(await screen.findByText("Conversation unavailable")).toBeInTheDocument();
  });

  it("renders the empty conversation state", async () => {
    vi.mocked(messagingApi.listMessages).mockResolvedValue({
      messages: [],
      next_cursor: null,
      has_more: false,
    });
    renderWith("en-US", <ConversationView conversationId="conv-1" />);
    expect(await screen.findByText("No messages yet")).toBeInTheDocument();
  });

  it("loads older messages when more history exists", async () => {
    vi.mocked(messagingApi.listMessages).mockResolvedValueOnce({
      messages: [
        {
          id: "m-new",
          conversation_id: "conv-1",
          sender_user_id: "coach-1",
          body: "newest",
          created_at: "2026-08-16T10:00:00Z",
        },
      ],
      next_cursor: "cursor-1",
      has_more: true,
    });
    renderWith("en-US", <ConversationView conversationId="conv-1" />);

    const button = await screen.findByRole("button", { name: "Load older messages" });
    vi.mocked(messagingApi.listMessages).mockResolvedValueOnce({
      messages: [
        {
          id: "m-old",
          conversation_id: "conv-1",
          sender_user_id: "coach-1",
          body: "older",
          created_at: "2026-08-15T10:00:00Z",
        },
      ],
      next_cursor: null,
      has_more: false,
    });
    fireEvent.click(button);
    expect(await screen.findByText("older")).toBeInTheDocument();
  });

  it("preserves mixed BiDi content and renders Persian UI", async () => {
    vi.mocked(messagingApi.listMessages).mockResolvedValue({
      messages: [
        {
          id: "m-bidi",
          conversation_id: "conv-1",
          sender_user_id: "coach-1",
          body: "امروز Bench Press با ۸۰ kg",
          created_at: "2026-08-16T10:00:00Z",
        },
      ],
      next_cursor: null,
      has_more: false,
    });
    renderWith("fa-IR", <ConversationView conversationId="conv-1" />);

    const bubble = await screen.findByText("امروز Bench Press با ۸۰ kg");
    // Mixed-direction content is isolated so it cannot reorder the layout.
    expect(bubble.querySelector("bdi") ?? bubble.closest("bdi")).toBeTruthy();
    expect(screen.getByLabelText("نوشتن پیام")).toBeInTheDocument();
  });
});

// --- Notification centre --------------------------------------------------------- //

const notification = {
  id: "n-1",
  organization_id: "org-1",
  event_type: "message.sent",
  category: "messaging" as const,
  title_key: "notifications.message_sent.title",
  body_key: "notifications.message_sent.body",
  payload: { actor_display_name: "Coach Reza", route: "/messages/conv-1" },
  read_at: null,
  created_at: "2026-08-16T10:00:00Z",
};

describe("NotificationCenter", () => {
  beforeEach(() => {
    vi.mocked(messagingApi.listNotifications).mockResolvedValue({
      notifications: [notification],
      unread_count: 1,
      next_cursor: null,
    });
  });

  it("renders localized notification text from keys and metadata", async () => {
    renderWith("en-US", <NotificationCenter />);
    expect(await screen.findByText("New message")).toBeInTheDocument();
    expect(screen.getByText("Coach Reza sent you a message.")).toBeInTheDocument();
  });

  it("states that updates arrive on refresh rather than in real time", async () => {
    renderWith("en-US", <NotificationCenter />);
    expect(
      await screen.findByText("Notifications update when you refresh this page."),
    ).toBeInTheDocument();
  });

  it("announces the unread count politely", async () => {
    renderWith("en-US", <NotificationCenter />);
    await screen.findByText("New message");
    const live = document.querySelector('[aria-live="polite"]');
    expect(live).toHaveTextContent("1 unread notifications");
  });

  it("marks a single notification read", async () => {
    vi.mocked(messagingApi.markNotificationRead).mockResolvedValue({
      ...notification,
      read_at: "2026-08-16T11:00:00Z",
    });
    renderWith("en-US", <NotificationCenter />);

    fireEvent.click(await screen.findByRole("button", { name: "Mark as read" }));
    await waitFor(() =>
      expect(messagingApi.markNotificationRead).toHaveBeenCalledWith("n-1", "en-US"),
    );
  });

  it("marks all notifications read", async () => {
    vi.mocked(messagingApi.markAllNotificationsRead).mockResolvedValue({
      updated: 1,
      read_at: "2026-08-16T11:00:00Z",
    });
    renderWith("en-US", <NotificationCenter />);

    fireEvent.click(await screen.findByRole("button", { name: /Mark all as read/ }));
    await waitFor(() => expect(messagingApi.markAllNotificationsRead).toHaveBeenCalled());
  });

  it("filters to unread only", async () => {
    renderWith("en-US", <NotificationCenter />);
    fireEvent.click(await screen.findByRole("button", { name: "Unread only" }));
    await waitFor(() =>
      expect(messagingApi.listNotifications).toHaveBeenLastCalledWith("en-US", {
        unreadOnly: true,
      }),
    );
  });

  it("renders the empty and error states", async () => {
    vi.mocked(messagingApi.listNotifications).mockResolvedValue({
      notifications: [],
      unread_count: 0,
      next_cursor: null,
    });
    const { unmount } = renderWith("en-US", <NotificationCenter />);
    expect(await screen.findByText("You are all caught up")).toBeInTheDocument();
    unmount();

    vi.mocked(messagingApi.listNotifications).mockRejectedValue(new Error("down"));
    renderWith("en-US", <NotificationCenter />);
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });

  it("renders a safety notification with its non-clinical disclaimer", async () => {
    vi.mocked(messagingApi.listNotifications).mockResolvedValue({
      notifications: [
        {
          ...notification,
          id: "n-2",
          event_type: "feedback_flag.created",
          category: "safety" as const,
          title_key: "notifications.feedback_flag.title",
          body_key: "notifications.feedback_flag.body",
          payload: {
            actor_display_name: "Athlete Neda",
            severity: "moderate",
            flag_type: "joint_pain",
            route: "/coach/sessions/s-1",
          },
        },
      ],
      unread_count: 1,
      next_cursor: null,
    });
    renderWith("en-US", <NotificationCenter />);

    expect(await screen.findByText("Athlete reported discomfort")).toBeInTheDocument();
    expect(screen.getByText(/not a medical assessment/i)).toBeInTheDocument();
  });

  it("renders Persian notification text", async () => {
    renderWith("fa-IR", <NotificationCenter />);
    expect(await screen.findByText("پیام تازه")).toBeInTheDocument();
  });
});

// --- Preferences ------------------------------------------------------------------- //

const preferences = {
  preferences: [
    {
      event_type: "message.sent",
      category: "messaging" as const,
      channel: "in_app" as const,
      is_enabled: true,
      is_locked: false,
    },
    {
      event_type: "message.sent",
      category: "messaging" as const,
      channel: "email" as const,
      is_enabled: false,
      is_locked: false,
    },
    {
      event_type: "message.sent",
      category: "messaging" as const,
      channel: "web_push" as const,
      is_enabled: false,
      is_locked: false,
    },
    {
      event_type: "feedback_flag.created",
      category: "safety" as const,
      channel: "in_app" as const,
      is_enabled: true,
      is_locked: true,
    },
    {
      event_type: "feedback_flag.created",
      category: "safety" as const,
      channel: "email" as const,
      is_enabled: false,
      is_locked: false,
    },
    {
      event_type: "feedback_flag.created",
      category: "safety" as const,
      channel: "web_push" as const,
      is_enabled: false,
      is_locked: false,
    },
  ],
  quiet_hours_enabled: false,
  quiet_hours_start: "22:00",
  quiet_hours_end: "07:00",
  web_push_permission_state: "unknown" as const,
  timezone: "Asia/Tehran",
  channels_available: { in_app: true, email: false, web_push: false },
};

describe("NotificationPreferences", () => {
  beforeEach(() => {
    vi.mocked(messagingApi.getNotificationPreferences).mockResolvedValue(preferences);
    vi.mocked(messagingApi.updateNotificationPreferences).mockResolvedValue(preferences);
  });

  it("marks email and browser push as unavailable in this release", async () => {
    renderWith("en-US", <NotificationPreferences />);
    await screen.findByText("Notification preferences");
    expect(screen.getAllByText("Not available yet").length).toBeGreaterThan(0);
    expect(
      screen.getByText(/not connected to a provider in this release/i),
    ).toBeInTheDocument();
  });

  it("locks the safety in-app channel and explains why", async () => {
    renderWith("en-US", <NotificationPreferences />);
    const checkbox = await screen.findByLabelText(/In-app/, { selector: "#pref-feedback_flag\\.created-in_app" });
    expect(checkbox).toBeDisabled();
    expect(checkbox).toBeChecked();
    expect(
      screen.getAllByText(/Safety alerts always appear in the app/i).length,
    ).toBeGreaterThan(0);
  });

  it("persists a channel toggle", async () => {
    renderWith("en-US", <NotificationPreferences />);
    const emailToggle = await screen.findByLabelText(/Email/, {
      selector: "#pref-message\\.sent-email",
    });
    fireEvent.click(emailToggle);

    await waitFor(() =>
      expect(messagingApi.updateNotificationPreferences).toHaveBeenCalledWith(
        {
          preferences: [
            { event_type: "message.sent", channel: "email", is_enabled: true },
          ],
        },
        "en-US",
      ),
    );
  });

  it("explains that quiet hours never delay in-app notifications", async () => {
    renderWith("en-US", <NotificationPreferences />);
    expect(
      await screen.findByText(/In-app notifications are never delayed/i),
    ).toBeInTheDocument();
  });

  it("shows the profile timezone used for quiet hours", async () => {
    renderWith("en-US", <NotificationPreferences />);
    expect(await screen.findByText(/Asia\/Tehran/)).toBeInTheDocument();
  });

  it("surfaces a denied browser permission without breaking in-app delivery", async () => {
    vi.mocked(messagingApi.getNotificationPreferences).mockResolvedValue({
      ...preferences,
      web_push_permission_state: "denied",
    });
    renderWith("en-US", <NotificationPreferences />);
    expect(await screen.findByText("Blocked in your browser")).toBeInTheDocument();
    expect(screen.getByText(/In-app notifications still work/i)).toBeInTheDocument();
  });

  it("renders Persian preference labels", async () => {
    renderWith("fa-IR", <NotificationPreferences />);
    expect(await screen.findByText("تنظیمات اعلان")).toBeInTheDocument();
  });
});

// --- Formatting helpers ----------------------------------------------------------- //

describe("messaging formatters", () => {
  it("formats a timestamp for both locales", () => {
    expect(formatTimestamp("2026-08-16T10:00:00Z", "en-US")).toContain("August 16, 2026");
    expect(formatTimestamp("2026-08-16T10:00:00Z", "fa-IR")).toContain("مرداد");
  });

  it("returns an empty string for a missing inbox timestamp", () => {
    expect(formatInboxTimestamp(null, "en-US")).toBe("");
    expect(formatInboxTimestamp(undefined, "en-US")).toBe("");
  });

  it("interpolates placeholders and leaves unknown ones intact", () => {
    expect(interpolate("{count} unread", { count: 3 })).toBe("3 unread");
    expect(interpolate("{missing} value", {})).toBe("{missing} value");
  });

  it("never interprets interpolated values as markup", () => {
    const result = interpolate("Hello {name}", { name: "<b>x</b>" });
    // The helper returns a plain string; React escapes it at render time.
    expect(result).toBe("Hello <b>x</b>");
  });

  it("maps message keys to localized text", () => {
    const t = (key: string) => key;
    expect(messageKeyToText("errors.messaging.rate_limited", t)).toBe("messaging.rate_limited");
    expect(messageKeyToText("errors.unknown.key", t)).toBeNull();
    expect(messageKeyToText(undefined, t)).toBeNull();
  });

  it("resolves notification text from keys without server-rendered copy", () => {
    const t = (key: string) =>
      key === "notifications.message_sent.title" ? "New message" : "{name} sent you a message.";
    const resolved = resolveNotificationText(
      {
        title_key: "notifications.message_sent.title",
        body_key: "notifications.message_sent.body",
        payload: { actor_display_name: "Coach Reza" },
      },
      t,
    );
    expect(resolved.title).toBe("New message");
    expect(resolved.body).toBe("Coach Reza sent you a message.");
  });
});
