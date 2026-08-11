import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      className,
      variant = "primary",
      size = "md",
      isLoading = false,
      disabled,
      type = "button",
      ...props
    },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center font-medium transition-colors duration-150 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed select-none";

    const variantStyles = {
      primary: "bg-emerald-500 hover:bg-emerald-600 active:bg-emerald-700 text-obsidian-950 font-semibold shadow-sm",
      secondary: "bg-obsidian-800 hover:bg-obsidian-700 text-brand-text border border-obsidian-700",
      outline: "border border-obsidian-700 hover:border-emerald-500 text-brand-text hover:bg-obsidian-800",
      ghost: "hover:bg-obsidian-800 text-brand-text hover:text-emerald-500",
      danger: "bg-red-600 hover:bg-red-700 text-white",
    };

    const sizeStyles = {
      sm: "min-h-[36px] px-3 text-xs gap-1.5",
      md: "min-h-[44px] px-4 text-sm gap-2", // 44px WCAG 2.5.5 minimum
      lg: "min-h-[48px] px-6 text-base gap-2.5", // 48px preferred touch target
    };

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || isLoading}
        className={twMerge(
          clsx(baseStyles, variantStyles[variant], sizeStyles[size], className)
        )}
        {...props}
      >
        {isLoading && (
          <svg
            className="animate-spin -ms-1 me-2 h-4 w-4 text-current"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
