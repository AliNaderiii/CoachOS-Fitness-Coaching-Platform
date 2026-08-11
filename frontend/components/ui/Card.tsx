import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "elevated" | "interactive";
}

export const Card: React.FC<CardProps> = ({
  children,
  className,
  variant = "default",
  ...props
}) => {
  const variantStyles = {
    default: "bg-obsidian-900 border border-obsidian-800",
    elevated: "bg-obsidian-850 border border-obsidian-700 shadow-md",
    interactive: "bg-obsidian-900 border border-obsidian-800 hover:border-emerald-500/50 hover:bg-obsidian-800/80 transition-all cursor-pointer",
  };

  return (
    <div
      className={twMerge(
        clsx("rounded-xl p-5 text-brand-text", variantStyles[variant], className)
      )}
      {...props}
    >
      {children}
    </div>
  );
};
