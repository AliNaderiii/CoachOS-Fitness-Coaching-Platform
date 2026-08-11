"use client";

import React from "react";
import { Building2, Info } from "lucide-react";
import { useTranslation } from "@/components/layout/DirectionProvider";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

export default function OrgSettingsPage() {
  const { t } = useTranslation();

  return (
    <div className="space-y-6 max-w-4xl mx-auto py-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-brand-text">
            {t("placeholders.org_settings_title")}
          </h1>
          <p className="text-sm text-brand-text-muted mt-1">
            {t("placeholders.org_settings_desc")}
          </p>
        </div>
        <Badge variant="warning" size="md">
          Phase 04 Foundation Shell
        </Badge>
      </div>

      <Card variant="elevated" className="space-y-4">
        <div className="flex items-center gap-3 text-emerald-400">
          <Building2 className="w-6 h-6" />
          <h2 className="text-lg font-semibold text-brand-text">
            Single-Location Organization Profile (ADR-013)
          </h2>
        </div>

        <div className="p-4 bg-obsidian-800 rounded-xl border border-obsidian-700 space-y-2 text-xs text-brand-text-muted">
          <div className="flex items-center gap-2 text-blue-400 font-medium">
            <Info className="w-4 h-4" />
            <span>Phase 05 Tenancy Scope:</span>
          </div>
          <ul className="list-disc list-inside space-y-1 ps-2">
            <li>Single primary location gym setup.</li>
            <li>Coach & Athlete membership invitations via secure single-use tokens.</li>
            <li>Role-based access control (Owner, Coach, Athlete, Support).</li>
          </ul>
        </div>
      </Card>
    </div>
  );
}
