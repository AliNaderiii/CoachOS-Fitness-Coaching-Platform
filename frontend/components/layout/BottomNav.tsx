"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Calendar, Dumbbell, Flame, MessageSquare, User } from "lucide-react";
import { useTranslation } from "./DirectionProvider";

export const BottomNav: React.FC = () => {
  const { locale, t } = useTranslation();
  const pathname = usePathname();

  const navItems = [
    {
      label: t("nav.today"),
      href: `/${locale}/athlete/today`,
      icon: Flame,
    },
    {
      label: t("nav.calendar"),
      href: `/${locale}/calendar`,
      icon: Calendar,
    },
    {
      label: t("nav.programs"),
      href: `/${locale}/coach/programs`,
      icon: Dumbbell,
    },
    {
      label: t("nav.messages"),
      href: `/${locale}/messages`,
      icon: MessageSquare,
    },
    {
      label: t("nav.profile"),
      href: `/${locale}/org/settings`,
      icon: User,
    },
  ];

  return (
    <nav
      role="navigation"
      aria-label="Mobile Navigation"
      className="md:hidden fixed bottom-0 inset-x-0 z-40 bg-obsidian-950/95 backdrop-blur-md border-t border-obsidian-800 px-2 py-1 flex items-center justify-around shadow-2xl"
    >
      {navItems.map((item) => {
        const isActive = pathname === item.href || pathname.startsWith(item.href);
        const Icon = item.icon;

        return (
          <Link
            key={item.href}
            href={item.href}
            className={`flex flex-col items-center justify-center min-h-[48px] min-w-[48px] px-2 rounded-lg transition-colors select-none ${
              isActive
                ? "text-emerald-400 font-semibold"
                : "text-brand-text-muted hover:text-brand-text"
            }`}
          >
            <Icon className="w-5 h-5 mb-1" />
            <span className="text-[10px] leading-tight">{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
};
