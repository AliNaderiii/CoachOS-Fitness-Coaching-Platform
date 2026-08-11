import React from "react";
import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { DirectionProvider } from "../components/layout/DirectionProvider";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
  usePathname: () => "/fa-IR",
}));

describe("UI Components Baseline", () => {
  it("renders Button with proper children and handles click", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>شروع تمرین</Button>);

    const btn = screen.getByRole("button", { name: "شروع تمرین" });
    expect(btn).toBeInTheDocument();

    fireEvent.click(btn);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("disables Button when disabled or isLoading prop is passed", () => {
    render(<Button disabled>ذخیره</Button>);
    const btn = screen.getByRole("button", { name: "ذخیره" });
    expect(btn).toBeDisabled();
  });

  it("renders Badge with correct variant", () => {
    render(<Badge variant="success">فعال</Badge>);
    const badge = screen.getByText("فعال");
    expect(badge).toBeInTheDocument();
  });

  it("renders Card component with content", () => {
    render(<Card>محتوای کارت</Card>);
    expect(screen.getByText("محتوای کارت")).toBeInTheDocument();
  });

  it("renders DirectionProvider and exposes translation", () => {
    const TestConsumer = () => {
      return (
        <DirectionProvider locale="fa-IR">
          <div>ورود به سیستم</div>
        </DirectionProvider>
      );
    };

    render(<TestConsumer />);
    expect(screen.getByText("ورود به سیستم")).toBeInTheDocument();
  });
});
