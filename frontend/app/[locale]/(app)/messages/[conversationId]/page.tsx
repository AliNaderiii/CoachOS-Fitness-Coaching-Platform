"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ConversationView } from "@/components/messaging/ConversationView";
import { useTranslation } from "@/components/layout/DirectionProvider";
import { getMe } from "@/lib/api/athlete";

export default function ConversationPage() {
  const params = useParams<{ conversationId: string }>();
  const conversationId = params?.conversationId ?? "";
  const { locale } = useTranslation();
  const [currentUserId, setCurrentUserId] = useState<string | undefined>(undefined);

  useEffect(() => {
    let cancelled = false;
    // Identity comes from the authenticated session; it is only used to align
    // message bubbles and is never trusted for authorization.
    getMe(locale)
      .then((me) => {
        if (!cancelled) setCurrentUserId(me.user.id);
      })
      .catch(() => {
        if (!cancelled) setCurrentUserId(undefined);
      });
    return () => {
      cancelled = true;
    };
  }, [locale]);

  return (
    <div className="py-4">
      <ConversationView conversationId={conversationId} currentUserId={currentUserId} />
    </div>
  );
}
