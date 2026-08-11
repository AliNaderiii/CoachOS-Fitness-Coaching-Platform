"use client";

import React from "react";
import Link from "next/link";
import { UserPlus, ShieldAlert } from "lucide-react";
import { useTranslation } from "@/components/layout/DirectionProvider";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

export default function RegisterPage() {
  const { locale, t } = useTranslation();

  return (
    <div className="max-w-md mx-auto py-8">
      <Card variant="elevated" className="space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center">
            <UserPlus className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-brand-text">{t("auth.register_title")}</h1>
          <Badge variant="warning" size="sm">
            Phase 04 Foundation Shell
          </Badge>
        </div>

        <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs text-amber-300 flex items-start gap-2">
          <ShieldAlert className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>{t("auth.placeholder_warning")}</span>
        </div>

        <form onSubmit={(e) => e.preventDefault()} className="space-y-4">
          <Input
            label={t("auth.email_label")}
            type="email"
            placeholder="new-coach@example.com"
            disabled
          />
          <Input
            label={t("auth.password_label")}
            type="password"
            placeholder="••••••••"
            disabled
          />
          <Button type="button" variant="primary" size="lg" className="w-full" disabled>
            {t("auth.submit_register")}
          </Button>
        </form>

        <div className="text-center text-xs text-brand-text-muted">
          <Link href={`/${locale}/login`} className="hover:text-emerald-400">
            {t("auth.login_title")}
          </Link>
        </div>
      </Card>
    </div>
  );
}
