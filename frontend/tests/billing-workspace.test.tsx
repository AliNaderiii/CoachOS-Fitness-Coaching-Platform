import React from "react";
import axe from "axe-core";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { BillingWorkspace, formatMoneyMinor } from "../components/billing/BillingWorkspace";
import { DirectionProvider } from "../components/layout/DirectionProvider";
import {
  createCheckoutSession,
  createPortalSession,
  getBillingWorkspace,
  listBillingPlans,
  type BillingPlan,
  type BillingWorkspace as WorkspaceData,
} from "../lib/api/billing";
import { ApiError } from "../lib/api/client";
import { listOrganizations } from "../lib/api/training";

vi.mock("../lib/api/billing", async () => {
  const actual = await vi.importActual<typeof import("../lib/api/billing")>("../lib/api/billing");
  return {
    ...actual,
    listBillingPlans: vi.fn(),
    getBillingWorkspace: vi.fn(),
    createCheckoutSession: vi.fn(),
    createPortalSession: vi.fn(),
  };
});

vi.mock("../lib/api/training", async () => {
  const actual = await vi.importActual<typeof import("../lib/api/training")>("../lib/api/training");
  return { ...actual, listOrganizations: vi.fn() };
});

const plan: BillingPlan = {
  id: "plan-1",
  code: "approved-plan",
  name_en: "Approved Studio",
  name_fa: "طرح تاییدشده",
  description_en: "For an approved organization catalog.",
  description_fa: "برای کاتالوگ تاییدشده مجموعه.",
  included_athletes: true,
  entitlements: [
    {
      key: "program_builder",
      kind: "boolean",
      enabled: true,
      integer_limit: null,
      label_en: "Program builder",
      label_fa: "برنامه‌ساز",
    },
  ],
  prices: [
    {
      id: "price-1",
      code: "approved-monthly",
      currency: "USD",
      currency_exponent: 2,
      unit_amount_minor: 12345,
      interval: "month",
      trial_days: 0,
      grace_period_days: 0,
    },
  ],
};

const workspace: WorkspaceData = {
  organization_id: "org-1",
  billing_account: { id: "account-1", status: "active" },
  subscription: {
    id: "subscription-1",
    plan_code: "approved-plan",
    price_id: "price-1",
    status: "active",
    quantity: 1,
    current_period_end: "2026-09-16T00:00:00Z",
    trial_end: null,
    grace_period_ends_at: null,
    cancel_at_period_end: false,
    canceled_at: null,
  },
  entitlement: {
    access_state: "active",
    athlete_access_included: true,
    features: { program_builder: true },
    limits: { staff_seats: 5, active_clients: null },
    usage: { staff_seats: 2, active_clients: 18 },
    effective_until: null,
    reason: "billing.entitlement.active",
  },
  invoices: [
    {
      id: "invoice-1",
      number: "INV-001",
      status: "paid",
      currency: "USD",
      currency_exponent: 2,
      amount_due_minor: 12345,
      amount_paid_minor: 12345,
      hosted_invoice_url: "https://invoices.test.coachos.invalid/i/1",
      receipt_url: null,
      issued_at: "2026-08-16T00:00:00Z",
      due_at: null,
      paid_at: "2026-08-16T00:00:00Z",
    },
  ],
  reconciliation_issues: [],
};

function renderWorkspace(
  locale: "fa-IR" | "en-US" = "en-US",
  navigate: (url: string) => void = vi.fn(),
) {
  return render(
    <DirectionProvider locale={locale}>
      <BillingWorkspace navigate={navigate} />
    </DirectionProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  window.history.replaceState({}, "", "/en-US/org/billing");
  vi.mocked(listOrganizations).mockResolvedValue({
    organizations: [{ id: "org-1", name: "Alborz Fitness", slug: "alborz" }],
  });
  vi.mocked(listBillingPlans).mockResolvedValue({ plans: [plan] });
  vi.mocked(getBillingWorkspace).mockResolvedValue(workspace);
  vi.mocked(createCheckoutSession).mockResolvedValue({
    session_id: "session-1",
    url: "https://payments.test.coachos.invalid/checkout/session-1",
    status: "created",
    message_key: "billing.redirect.provider_hosted",
  });
  vi.mocked(createPortalSession).mockResolvedValue({
    session_id: "portal-1",
    url: "https://payments.test.coachos.invalid/portal/portal-1",
    status: "created",
    message_key: "billing.redirect.provider_hosted",
  });
});

describe("Phase 10 billing workspace", () => {
  it("renders verified plan, usage, invoice, included-athlete and renewal disclosures", async () => {
    renderWorkspace();
    expect(screen.getByText("Loading billing workspace…")).toBeVisible();
    expect(await screen.findByRole("heading", { name: "Current plan" })).toBeVisible();
    expect(screen.getAllByText("Approved Studio").length).toBeGreaterThan(0);
    expect(screen.getByText("Active")).toBeVisible();
    expect(screen.getByText(/Renews automatically/)).toBeVisible();
    expect(screen.getByText("Athlete access is included")).toBeVisible();
    expect(screen.getByText("INV-001")).toBeVisible();
    expect(screen.getAllByText("$123.45").length).toBeGreaterThan(0);
    expect(screen.getByRole("link", { name: /View hosted invoice/ })).toHaveAttribute(
      "rel",
      "noopener noreferrer",
    );
  });

  it("treats checkout return as pending instead of client-side success", async () => {
    window.history.replaceState({}, "", "/en-US/org/billing?checkout=return&paid=true");
    renderWorkspace();
    expect(await screen.findByText("We are verifying the provider update")).toBeVisible();
    expect(screen.getByText(/Returning here does not confirm payment/)).toBeVisible();
    expect(await screen.findByText("Active")).toBeVisible();
  });

  it("warns before leaving and redirects only to the server-created hosted URL", async () => {
    const navigate = vi.fn();
    renderWorkspace("en-US", navigate);
    await screen.findAllByText("Approved Studio");
    fireEvent.click(screen.getByRole("button", { name: /Continue with this plan/ }));
    expect(
      screen.getByRole("dialog", { name: "Continue to the hosted billing provider?" }),
    ).toBeVisible();
    expect(screen.getByText(/Returning alone will not grant access/)).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: /Continue to provider/ }));
    await waitFor(() => expect(createCheckoutSession).toHaveBeenCalledTimes(1));
    expect(createCheckoutSession).toHaveBeenCalledWith(
      "org-1",
      "price-1",
      "en-US",
      expect.stringMatching(/^billing-checkout-/),
    );
    expect(navigate).toHaveBeenCalledWith(
      "https://payments.test.coachos.invalid/checkout/session-1",
    );
  });

  it("shows forbidden and provider-unavailable recovery states without billing claims", async () => {
    vi.mocked(getBillingWorkspace).mockRejectedValueOnce(
      new ApiError({ title: "Forbidden", status: 403 }),
    );
    const first = renderWorkspace();
    expect(
      await screen.findByText("You do not have permission to view or manage organization billing."),
    ).toBeVisible();
    first.unmount();

    vi.mocked(getBillingWorkspace).mockRejectedValueOnce(
      new ApiError({ title: "Unavailable", status: 503 }),
    );
    renderWorkspace();
    expect(
      await screen.findByText(/Your last verified access state has not changed/),
    ).toBeVisible();
  });

  it("renders Persian RTL parity and canonical minor money accurately", async () => {
    renderWorkspace("fa-IR");
    expect(await screen.findByRole("heading", { name: "طرح فعلی" })).toBeVisible();
    expect(screen.getByText("دسترسی ورزشکاران در طرح گنجانده شده است")).toBeVisible();
    expect(document.documentElement).toHaveAttribute("dir", "rtl");
    expect(formatMoneyMinor(12345, "USD", 2, "en-US")).toBe("$123.45");
    expect(formatMoneyMinor(5, "USD", 2, "en-US")).toBe("$0.05");
    expect(formatMoneyMinor(5, "USD", 9, "en-US")).toBe("—");
  });

  it("discloses approved trial and grace durations without inventing defaults", async () => {
    vi.mocked(listBillingPlans).mockResolvedValueOnce({
      plans: [
        {
          ...plan,
          prices: [{ ...plan.prices[0], trial_days: 14, grace_period_days: 3 }],
        },
      ],
    });
    renderWorkspace();
    expect(await screen.findByLabelText("14 day trial")).toBeVisible();
    expect(screen.getByLabelText("3 day payment grace")).toBeVisible();
  });

  it.each(["en-US", "fa-IR"] as const)(
    "has no automated axe violations in the %s workspace",
    async (locale) => {
      const { container } = renderWorkspace(locale);
      await screen.findByTestId("billing-workspace");
      await screen.findByText("INV-001");
      const results = await axe.run(container, {
        rules: { "color-contrast": { enabled: false } },
      });
      expect(results.violations.map(({ id }) => id)).toEqual([]);
    },
  );

  it("keeps the English and Persian billing dictionaries at exact key parity", async () => {
    const en = await import("../lib/i18n/dictionaries/en-US.json");
    const fa = await import("../lib/i18n/dictionaries/fa-IR.json");
    expect(Object.keys(en.default.billing).sort()).toEqual(Object.keys(fa.default.billing).sort());
  });
});
