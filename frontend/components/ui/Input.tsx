import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, id, className, disabled, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

    return (
      <div className="flex flex-col gap-1.5 w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="text-xs font-medium text-brand-text-muted select-none"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          disabled={disabled}
          className={twMerge(
            clsx(
              "w-full min-h-[44px] px-3.5 py-2.5 bg-obsidian-900 border rounded-lg text-sm text-brand-text placeholder:text-brand-text-muted transition-colors duration-150",
              "focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent",
              error
                ? "border-red-500 focus:ring-red-500"
                : "border-obsidian-700 hover:border-obsidian-600",
              disabled && "opacity-50 cursor-not-allowed bg-obsidian-950",
              className
            )
          )}
          {...props}
        />
        {error && <span className="text-xs text-red-400">{error}</span>}
        {hint && !error && <span className="text-xs text-brand-text-muted">{hint}</span>}
      </div>
    );
  }
);

Input.displayName = "Input";
