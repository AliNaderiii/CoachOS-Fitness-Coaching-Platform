import type { Locale } from "../i18n/config";
import { request } from "./client";

export interface BillingPrice {
  id: string;
  code: string;
  currency: string;
  currency_exponent: number;
  unit_amount_minor: number;
  interval: "month" | "year";
  trial_days: number;
  grace_period_days: number;
}

export interface BillingPlanEntitlement {
  key: string;
  kind: "boolean" | "integer";
  enabled: boolean;
  integer_limit: number | null;
  label_en: string;
  label_fa: string;
}

export interface BillingPlan {
  id: string;
  code: string;
  name_en: string;
  name_fa: string;
  description_en: string;
  description_fa: string;
  included_athletes: true;
  entitlements: BillingPlanEntitlement[];
  prices: BillingPrice[];
}

export type BillingAccessState = "active" | "trial" | "grace" | "restricted" | "none";
export type SubscriptionStatus =
  | "trialing"
  | "active"
  | "past_due"
  | "incomplete"
  | "unpaid"
  | "canceled";

export interface BillingWorkspace {
  organization_id: string;
  billing_account: { id: string; status: string } | null;
  subscription: {
    id: string;
    plan_code: string;
    price_id: string;
    status: SubscriptionStatus;
    quantity: number;
    current_period_end: string | null;
    trial_end: string | null;
    grace_period_ends_at: string | null;
    cancel_at_period_end: boolean;
    canceled_at: string | null;
  } | null;
  entitlement: {
    access_state: BillingAccessState;
    athlete_access_included: true;
    features: Record<string, boolean>;
    limits: { staff_seats: number | null; active_clients: number | null };
    usage: { staff_seats: number; active_clients: number };
    effective_until: string | null;
    reason: string;
  };
  invoices: Array<{
    id: string;
    number: string;
    status: string;
    currency: string;
    currency_exponent: number;
    amount_due_minor: number;
    amount_paid_minor: number;
    hosted_invoice_url: string | null;
    receipt_url: string | null;
    issued_at: string | null;
    due_at: string | null;
    paid_at: string | null;
  }>;
  reconciliation_issues: Array<{
    id: string;
    issue_code: string;
    message_key: string;
    first_seen_at: string;
    last_seen_at: string;
  }>;
}

export interface HostedBillingSession {
  session_id: string;
  url: string;
  status: "created";
  message_key: string;
}

export function listBillingPlans(locale: Locale) {
  return request<{ plans: BillingPlan[] }>("billing/plans", { locale });
}

export function getBillingWorkspace(orgId: string, locale: Locale) {
  return request<BillingWorkspace>(`billing/organizations/${orgId}/workspace`, { locale });
}

export function createCheckoutSession(
  orgId: string,
  priceId: string,
  locale: Locale,
  idempotencyKey: string,
) {
  return request<HostedBillingSession>(`billing/organizations/${orgId}/checkout-sessions`, {
    method: "POST",
    locale,
    idempotencyKey,
    json: { price_id: priceId, locale },
  });
}

export function createPortalSession(orgId: string, locale: Locale, idempotencyKey: string) {
  return request<HostedBillingSession>(`billing/organizations/${orgId}/portal-sessions`, {
    method: "POST",
    locale,
    idempotencyKey,
    json: { locale },
  });
}
