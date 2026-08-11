"use client";

import React from "react";
import { FolderTree, Info } from "lucide-react";
import { useTranslation } from "@/components/layout/DirectionProvider";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

export default function CoachProgramsPage() {
  const { t } = useTranslation();

  return (
    <div className="space-y-6 max-w-5xl mx-auto py-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-brand-text">
            {t("placeholders.coach_programs_title")}
          </h1>
          <p className="text-sm text-brand-text-muted mt-1">
            {t("placeholders.coach_programs_desc")}
          </p>
        </div>
        <Badge variant="warning" size="md">
          Phase 04 Foundation Shell
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Desktop Dual-Pane Outline (ADR-024) */}
        <Card variant="elevated" className="lg:col-span-4 space-y-3">
          <div className="flex items-center gap-2 text-emerald-400 font-semibold text-sm">
            <FolderTree className="w-4 h-4" />
            <span>Program Outline Tree (Desktop 35%)</span>
          </div>
          <div className="p-3 bg-obsidian-800 rounded-lg text-xs text-brand-text-muted">
            Placeholder for periodization mesocycles, microcycles, and workout days (Phase 06).
          </div>
        </Card>

        {/* Prescription Editor */}
        <Card variant="elevated" className="lg:col-span-8 space-y-3">
          <h2 className="font-semibold text-sm text-brand-text">
            Exercise Prescription Editor (Desktop 65%)
          </h2>
          <div className="p-4 bg-obsidian-800 rounded-lg text-xs text-brand-text-muted space-y-2">
            <div className="flex items-center gap-2 text-blue-400 font-medium">
              <Info className="w-4 h-4" />
              <span>Phase 06 Scope:</span>
            </div>
            <p>
              Master-detail program builder with exercise catalog search, sets/reps prescription, and immutable assignment snapshotting.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}
