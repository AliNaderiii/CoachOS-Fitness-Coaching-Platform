"use client";

import React from "react";
import { useTranslation } from "@/components/layout/DirectionProvider";
import { ConversationList } from "@/components/messaging/ConversationList";

export default function MessagesInboxPage() {
  const { t } = useTranslation();

  return (
    <div className="py-4 space-y-4">
      <header className="space-y-1">
        <h1 className="text-xl font-semibold text-brand-text">{t("messaging.inbox_title")}</h1>
        <p className="text-sm text-brand-text-muted">{t("messaging.inbox_subtitle")}</p>
      </header>
      <ConversationList />
    </div>
  );
}
