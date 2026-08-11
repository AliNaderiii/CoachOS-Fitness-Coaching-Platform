"use client";

import React from "react";
import Link from "next/link";
import { Activity, CheckCircle2, Dumbbell, ShieldCheck, Smartphone, Users, Zap } from "lucide-react";
import { useTranslation } from "@/components/layout/DirectionProvider";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { InstallPromptBanner } from "@/components/pwa/InstallPromptBanner";

export default function HomePage() {
  const { locale, t } = useTranslation();

  const statusItems = [
    {
      title: t("home.status_frontend"),
      desc: "Next.js 14 App Router • TypeScript Strict • Logical CSS",
      icon: Zap,
    },
    {
      title: t("home.status_backend"),
      desc: "Django 5 DRF • /healthz • /readyz • /api/v1/meta",
      icon: Activity,
    },
    {
      title: t("home.status_pwa"),
      desc: "Manifest v1 • Service Worker • Offline Shell Fallback",
      icon: Smartphone,
    },
    {
      title: t("home.status_i18n"),
      desc: "fa-IR (RTL) • en-US (LTR) • No Arabic • Solar Hijri",
      icon: ShieldCheck,
    },
  ];

  return (
    <div className="space-y-8 py-4">
      {/* Hero Section */}
      <section className="text-center max-w-3xl mx-auto space-y-4 pt-4">
        <Badge variant="success" size="md">
          {t("app.foundation_badge")}
        </Badge>

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-brand-text tracking-tight">
          {t("home.welcome_title")}
        </h1>

        <p className="text-base sm:text-lg text-brand-text-muted">
          {t("home.welcome_subtitle")}
        </p>

        <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
          <Link href={`/${locale}/athlete/today`}>
            <Button size="lg" variant="primary">
              <Dumbbell className="w-5 h-5 -ms-1 me-2" />
              {t("home.cta_athlete")}
            </Button>
          </Link>
          <Link href={`/${locale}/coach/programs`}>
            <Button size="lg" variant="secondary">
              <Users className="w-5 h-5 -ms-1 me-2" />
              {t("home.cta_coach")}
            </Button>
          </Link>
        </div>
      </section>

      {/* PWA Install Banner */}
      <InstallPromptBanner />

      {/* Architecture Foundation Status Grid */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold text-brand-text flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          <span>{t("home.status_title")}</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {statusItems.map((item, idx) => {
            const Icon = item.icon;
            return (
              <Card key={idx} variant="default" className="flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                    <Icon className="w-4 h-4" />
                  </div>
                  <h3 className="font-semibold text-sm text-brand-text">{item.title}</h3>
                  <p className="text-xs text-brand-text-muted">{item.desc}</p>
                </div>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Boundary & Scope Notice */}
      <Card variant="elevated" className="border-obsidian-700 bg-obsidian-900/60">
        <div className="flex items-start gap-3">
          <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 flex-shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <h4 className="text-sm font-semibold text-brand-text">
              Architecture & Security Boundaries
            </h4>
            <p className="text-xs text-brand-text-muted leading-relaxed">
              {t("home.placeholder_notice")}
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
