"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  Check,
  CreditCard,
  ExternalLink,
  ReceiptText,
  RefreshCw,
  ShieldCheck,
  Users,
} from "lucide-react";
import { useTranslation } from "@/components/layout/DirectionProvider";
import { Badge, type BadgeProps } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Modal } from "@/components/ui/Modal";
import {
  createCheckoutSession,
  createPortalSession,
  getBillingWorkspace,
  listBillingPlans,
  type BillingPlan,
  type BillingPrice,
  type BillingWorkspace as BillingWorkspaceData,
  type SubscriptionStatus,
} from "@/lib/api/billing";
import { ApiError } from "@/lib/api/client";
import { listOrganizations, type OrganizationContext } from "@/lib/api/training";
import { formatDate, formatNumber } from "@/lib/i18n/formatters";
import type { Locale } from "@/lib/i18n/config";

type LoadState = "loading" | "ready" | "empty" | "forbidden" | "error" | "unavailable";
type ActionState = "idle" | "creating" | "error" | "unavailable";
type Navigate = (url: string) => void;

const statusVariants: Record<SubscriptionStatus, BadgeProps["variant"]> = {
  trialing: "info",
  active: "success",
  past_due: "warning",
  incomplete: "warning",
  unpaid: "error",
  canceled: "neutral",
};

function newIdempotencyKey(kind: string): string {
  const random =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  return `billing-${kind}-${random}`;
}

export function formatMoneyMinor(
  amountMinor: number,
  currency: string,
  exponent: number,
  locale: Locale,
): string {
  if (!Number.isSafeInteger(amountMinor) || amountMinor < 0 || exponent < 0 || exponent > 4) {
    return "—";
  }
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    minimumFractionDigits: exponent,
    maximumFractionDigits: exponent,
  }).format(amountMinor / 10 ** exponent);
}

function safeExternalUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password;
  } catch {
    return false;
  }
}

function localizedPlan(plan: BillingPlan, locale: Locale) {
  return {
    name: locale === "fa-IR" ? plan.name_fa : plan.name_en,
    description: locale === "fa-IR" ? plan.description_fa : plan.description_en,
  };
}

function displayDate(value: string | null, locale: Locale): string {
  if (!value) return "—";
  try {
    return formatDate(value, locale);
  } catch {
    return "—";
  }
}

function StateCard({
  message,
  retry,
  retryLabel,
  role = "status",
}: {
  message: string;
  retry?: () => void;
  retryLabel: string;
  role?: "status" | "alert";
}) {
  return (
    <Card role={role} className="mx-auto max-w-2xl text-center">
      <p className="text-sm text-brand-text-muted">{message}</p>
      {retry && (
        <Button className="mt-4" variant="outline" onClick={retry}>
          <RefreshCw aria-hidden="true" className="h-4 w-4" />
          {retryLabel}
        </Button>
      )}
    </Card>
  );
}

export function BillingWorkspace({
  navigate = (url) => window.location.assign(url),
}: {
  navigate?: Navigate;
}) {
  const { locale, t } = useTranslation();
  const [organizations, setOrganizations] = useState<OrganizationContext[]>([]);
  const [activeOrgId, setActiveOrgId] = useState("");
  const [plans, setPlans] = useState<BillingPlan[]>([]);
  const [workspace, setWorkspace] = useState<BillingWorkspaceData | null>(null);
  const [selectedPriceId, setSelectedPriceId] = useState("");
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [actionState, setActionState] = useState<ActionState>("idle");
  const [confirmation, setConfirmation] = useState<"portal" | string | null>(null);
  const [retryVersion, setRetryVersion] = useState(0);

  const checkoutReturn = useMemo(() => {
    if (typeof window === "undefined") return null;
    return new URLSearchParams(window.location.search).get("checkout");
  }, []);

  const load = useCallback(async () => {
    setLoadState("loading");
    setActionState("idle");
    try {
      const [organizationResponse, planResponse] = await Promise.all([
        listOrganizations(locale),
        listBillingPlans(locale),
      ]);
      setOrganizations(organizationResponse.organizations);
      setPlans(planResponse.plans);
      if (organizationResponse.organizations.length === 0) {
        setWorkspace(null);
        setActiveOrgId("");
        setLoadState("empty");
        return;
      }
      const nextOrg = organizationResponse.organizations.some((org) => org.id === activeOrgId)
        ? activeOrgId
        : organizationResponse.organizations[0].id;
      setActiveOrgId(nextOrg);
      const nextWorkspace = await getBillingWorkspace(nextOrg, locale);
      setWorkspace(nextWorkspace);
      const currentPrice = nextWorkspace.subscription?.price_id;
      const fallbackPrice = planResponse.plans.flatMap((plan) => plan.prices)[0]?.id || "";
      setSelectedPriceId(currentPrice || fallbackPrice);
      setLoadState("ready");
    } catch (error: unknown) {
      setWorkspace(null);
      if (error instanceof ApiError && error.status === 403) setLoadState("forbidden");
      else if (error instanceof ApiError && error.status === 503) setLoadState("unavailable");
      else setLoadState("error");
    }
  }, [activeOrgId, locale]);

  useEffect(() => {
    void load();
    // retryVersion deliberately retriggers a complete server-authoritative refresh.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [locale, retryVersion]);

  const switchOrganization = async (orgId: string) => {
    setActiveOrgId(orgId);
    setLoadState("loading");
    try {
      const nextWorkspace = await getBillingWorkspace(orgId, locale);
      setWorkspace(nextWorkspace);
      setSelectedPriceId(
        nextWorkspace.subscription?.price_id || plans.flatMap((plan) => plan.prices)[0]?.id || "",
      );
      setLoadState("ready");
    } catch (error: unknown) {
      if (error instanceof ApiError && error.status === 403) setLoadState("forbidden");
      else if (error instanceof ApiError && error.status === 503) setLoadState("unavailable");
      else setLoadState("error");
    }
  };

  const redirectToHosted = async (kind: "checkout" | "portal", priceId?: string) => {
    if (!activeOrgId) return;
    setActionState("creating");
    try {
      const session =
        kind === "checkout" && priceId
          ? await createCheckoutSession(
              activeOrgId,
              priceId,
              locale,
              newIdempotencyKey("checkout"),
            )
          : await createPortalSession(activeOrgId, locale, newIdempotencyKey("portal"));
      if (!safeExternalUrl(session.url)) throw new Error("Unsafe hosted URL");
      setConfirmation(null);
      navigate(session.url);
    } catch (error: unknown) {
      setConfirmation(null);
      setActionState(
        error instanceof ApiError && error.status === 503 ? "unavailable" : "error",
      );
    }
  };

  const selectedPrice = plans
    .flatMap((plan) => plan.prices)
    .find((price) => price.id === selectedPriceId);

  return (
    <main className="mx-auto max-w-6xl space-y-6 py-4" data-testid="billing-workspace">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="mb-2 flex items-center gap-2">
            <Badge variant="info">{t("billing.phase_badge")}</Badge>
            <span className="text-xs text-brand-text-muted">{t("billing.owner_admin_only")}</span>
          </div>
          <h1 className="text-2xl font-bold text-brand-text sm:text-3xl">{t("billing.title")}</h1>
          <p className="mt-1 max-w-3xl text-sm text-brand-text-muted">{t("billing.subtitle")}</p>
        </div>
        {loadState === "ready" && organizations.length > 0 && (
          <label className="flex min-w-56 flex-col gap-1 text-sm text-brand-text-muted">
            {t("billing.organization")}
            <select
              value={activeOrgId}
              onChange={(event) => void switchOrganization(event.target.value)}
              className="min-h-touch rounded-lg border border-obsidian-700 bg-obsidian-800 px-3 text-brand-text"
            >
              {organizations.map((organization) => (
                <option key={organization.id} value={organization.id}>
                  {organization.name}
                </option>
              ))}
            </select>
          </label>
        )}
      </header>

      {checkoutReturn === "return" || checkoutReturn === "portal-return" ? (
        <div role="status" className="rounded-xl border border-blue-700 bg-blue-900/20 p-4">
          <strong>{t("billing.return_pending_title")}</strong>
          <p className="mt-1 text-sm text-brand-text-muted">{t("billing.return_pending_desc")}</p>
        </div>
      ) : null}
      {checkoutReturn === "cancelled" ? (
        <div role="status" className="rounded-xl border border-obsidian-700 bg-obsidian-900 p-4">
          <strong>{t("billing.checkout_cancelled_title")}</strong>
          <p className="mt-1 text-sm text-brand-text-muted">{t("billing.checkout_cancelled_desc")}</p>
        </div>
      ) : null}

      {loadState === "loading" && (
        <StateCard message={t("billing.loading")} retryLabel={t("billing.retry")} />
      )}
      {loadState === "empty" && (
        <StateCard message={t("billing.no_organization")} retryLabel={t("billing.retry")} />
      )}
      {loadState === "forbidden" && (
        <StateCard
          role="alert"
          message={t("billing.forbidden")}
          retryLabel={t("billing.retry")}
        />
      )}
      {loadState === "unavailable" && (
        <StateCard
          role="alert"
          message={t("billing.provider_unavailable")}
          retry={() => setRetryVersion((version) => version + 1)}
          retryLabel={t("billing.retry")}
        />
      )}
      {loadState === "error" && (
        <StateCard
          role="alert"
          message={t("billing.load_error")}
          retry={() => setRetryVersion((version) => version + 1)}
          retryLabel={t("billing.retry")}
        />
      )}

      {loadState === "ready" && workspace && (
        <>
          <section aria-labelledby="current-plan-title" className="grid gap-4 lg:grid-cols-3">
            <Card variant="elevated" className="space-y-4 lg:col-span-2">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 id="current-plan-title" className="text-lg font-semibold">
                    {t("billing.current_plan")}
                  </h2>
                  <p className="mt-1 text-sm text-brand-text-muted">
                    {workspace.subscription
                      ? plans.find((plan) => plan.code === workspace.subscription?.plan_code)
                        ? localizedPlan(
                            plans.find(
                              (plan) => plan.code === workspace.subscription?.plan_code,
                            ) as BillingPlan,
                            locale,
                          ).name
                        : workspace.subscription.plan_code
                      : t("billing.no_subscription")}
                  </p>
                </div>
                {workspace.subscription ? (
                  <Badge variant={statusVariants[workspace.subscription.status]}>
                    {t(`billing.status_${workspace.subscription.status}`)}
                  </Badge>
                ) : (
                  <Badge variant="neutral">{t("billing.status_none")}</Badge>
                )}
              </div>

              {workspace.subscription && (
                <dl className="grid gap-3 text-sm sm:grid-cols-2">
                  <div>
                    <dt className="text-brand-text-muted">{t("billing.period_end")}</dt>
                    <dd>{displayDate(workspace.subscription.current_period_end, locale)}</dd>
                  </div>
                  <div>
                    <dt className="text-brand-text-muted">{t("billing.cancellation")}</dt>
                    <dd>
                      {workspace.subscription.cancel_at_period_end
                        ? t("billing.cancels_at_period_end")
                        : t("billing.renews_automatically")}
                    </dd>
                  </div>
                  {workspace.subscription.trial_end && (
                    <div>
                      <dt className="text-brand-text-muted">{t("billing.trial_ends")}</dt>
                      <dd>{displayDate(workspace.subscription.trial_end, locale)}</dd>
                    </div>
                  )}
                  {workspace.subscription.grace_period_ends_at && (
                    <div>
                      <dt className="text-brand-text-muted">{t("billing.grace_ends")}</dt>
                      <dd>{displayDate(workspace.subscription.grace_period_ends_at, locale)}</dd>
                    </div>
                  )}
                </dl>
              )}

              <div className="rounded-lg border border-emerald-700/50 bg-emerald-900/10 p-3 text-sm">
                <div className="flex items-start gap-2">
                  <ShieldCheck aria-hidden="true" className="mt-0.5 h-5 w-5 shrink-0 text-emerald-400" />
                  <div>
                    <strong>{t("billing.athletes_included_title")}</strong>
                    <p className="mt-1 text-brand-text-muted">{t("billing.athletes_included_desc")}</p>
                  </div>
                </div>
              </div>

              {workspace.subscription && (
                <Button variant="outline" onClick={() => setConfirmation("portal")}>
                  <CreditCard aria-hidden="true" className="h-4 w-4" />
                  {t("billing.manage_billing")}
                  <ExternalLink aria-hidden="true" className="h-4 w-4" />
                </Button>
              )}
            </Card>

            <Card className="space-y-4">
              <div className="flex items-center gap-2">
                <Users aria-hidden="true" className="h-5 w-5 text-blue-400" />
                <h2 className="font-semibold">{t("billing.usage_title")}</h2>
              </div>
              {(["staff_seats", "active_clients"] as const).map((key) => (
                <div key={key}>
                  <div className="flex justify-between gap-3 text-sm">
                    <span>{t(`billing.${key}`)}</span>
                    <bdi>
                      {formatNumber(workspace.entitlement.usage[key], locale)} / {workspace.entitlement.limits[key] === null
                        ? t("billing.unlimited")
                        : formatNumber(workspace.entitlement.limits[key] as number, locale)}
                    </bdi>
                  </div>
                </div>
              ))}
              <p className="text-xs text-brand-text-muted">
                {t(`billing.access_${workspace.entitlement.access_state}`)}
              </p>
            </Card>
          </section>

          {workspace.reconciliation_issues.length > 0 && (
            <section aria-labelledby="billing-attention-title">
              <Card className="border-amber-700/70 bg-amber-900/10">
                <div className="flex items-start gap-3">
                  <AlertTriangle aria-hidden="true" className="mt-0.5 h-5 w-5 shrink-0 text-amber-400" />
                  <div>
                    <h2 id="billing-attention-title" className="font-semibold">
                      {t("billing.attention_title")}
                    </h2>
                    <p className="mt-1 text-sm text-brand-text-muted">
                      {t("billing.attention_desc")}
                    </p>
                  </div>
                </div>
              </Card>
            </section>
          )}

          <section aria-labelledby="plans-title" className="space-y-4">
            <div>
              <h2 id="plans-title" className="text-xl font-semibold">
                {t("billing.plans_title")}
              </h2>
              <p className="text-sm text-brand-text-muted">{t("billing.plans_desc")}</p>
            </div>
            {plans.length === 0 ? (
              <StateCard message={t("billing.no_plans")} retryLabel={t("billing.retry")} />
            ) : (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {plans.map((plan) => {
                  const text = localizedPlan(plan, locale);
                  return (
                    <Card key={plan.id} variant="elevated" className="flex flex-col gap-4">
                      <div>
                        <h3 className="text-lg font-semibold">{text.name}</h3>
                        <p className="mt-1 text-sm text-brand-text-muted">{text.description}</p>
                      </div>
                      <ul className="space-y-2 text-sm">
                        <li className="flex items-start gap-2">
                          <Check aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                          {t("billing.included_athletes_feature")}
                        </li>
                        {plan.entitlements.map((entitlement) => (
                          <li key={entitlement.key} className="flex items-start gap-2">
                            <Check aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                            {locale === "fa-IR" ? entitlement.label_fa : entitlement.label_en}
                            {entitlement.kind === "integer" && entitlement.integer_limit !== null
                              ? ` · ${formatNumber(entitlement.integer_limit, locale)}`
                              : null}
                          </li>
                        ))}
                      </ul>
                      <div className="mt-auto space-y-2">
                        {plan.prices.map((price: BillingPrice) => (
                          <label
                            key={price.id}
                            className="flex min-h-touch cursor-pointer items-center justify-between gap-3 rounded-lg border border-obsidian-700 p-3"
                          >
                            <span className="space-y-1">
                              <span className="block">
                                <bdi>
                                  {formatMoneyMinor(
                                    price.unit_amount_minor,
                                    price.currency,
                                    price.currency_exponent,
                                    locale,
                                  )}
                                </bdi>
                                <span className="text-brand-text-muted">
                                  {price.interval === "month"
                                    ? ` / ${t("billing.month")}`
                                    : ` / ${t("billing.year")}`}
                                </span>
                              </span>
                              {price.trial_days > 0 && (
                                <span
                                  className="block text-xs text-blue-300"
                                  aria-label={`${formatNumber(price.trial_days, locale)} ${t("billing.trial_days_suffix")}`}
                                >
                                  <bdi>{formatNumber(price.trial_days, locale)}</bdi>{" "}
                                  {t("billing.trial_days_suffix")}
                                </span>
                              )}
                              {price.grace_period_days > 0 && (
                                <span
                                  className="block text-xs text-brand-text-muted"
                                  aria-label={`${formatNumber(price.grace_period_days, locale)} ${t("billing.grace_days_suffix")}`}
                                >
                                  <bdi>{formatNumber(price.grace_period_days, locale)}</bdi>{" "}
                                  {t("billing.grace_days_suffix")}
                                </span>
                              )}
                            </span>
                            <input
                              type="radio"
                              name="billing-price"
                              value={price.id}
                              checked={selectedPriceId === price.id}
                              onChange={() => setSelectedPriceId(price.id)}
                              aria-label={`${text.name} ${price.interval}`}
                              className="h-5 w-5 accent-emerald-500"
                            />
                          </label>
                        ))}
                        <Button
                          className="w-full"
                          disabled={!plan.prices.some((price) => price.id === selectedPriceId)}
                          onClick={() => setConfirmation(selectedPriceId)}
                        >
                          {t("billing.choose_plan")}
                          <ExternalLink aria-hidden="true" className="h-4 w-4" />
                        </Button>
                      </div>
                    </Card>
                  );
                })}
              </div>
            )}
          </section>

          <section aria-labelledby="invoices-title" className="space-y-3">
            <div className="flex items-center gap-2">
              <ReceiptText aria-hidden="true" className="h-5 w-5 text-blue-400" />
              <h2 id="invoices-title" className="text-xl font-semibold">
                {t("billing.invoices_title")}
              </h2>
            </div>
            {workspace.invoices.length === 0 ? (
              <Card className="text-sm text-brand-text-muted">{t("billing.no_invoices")}</Card>
            ) : (
              <div className="overflow-x-auto rounded-xl border border-obsidian-700">
                <table className="w-full min-w-[36rem] text-sm">
                  <thead className="bg-obsidian-800 text-brand-text-muted">
                    <tr>
                      <th className="p-3 text-start">{t("billing.invoice_number")}</th>
                      <th className="p-3 text-start">{t("billing.invoice_date")}</th>
                      <th className="p-3 text-start">{t("billing.invoice_amount")}</th>
                      <th className="p-3 text-start">{t("billing.invoice_status")}</th>
                      <th className="p-3 text-start">{t("billing.invoice_action")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {workspace.invoices.map((invoice) => (
                      <tr key={invoice.id} className="border-t border-obsidian-700">
                        <td className="p-3"><bdi>{invoice.number || "—"}</bdi></td>
                        <td className="p-3">{displayDate(invoice.issued_at, locale)}</td>
                        <td className="p-3"><bdi>{formatMoneyMinor(invoice.amount_due_minor, invoice.currency, invoice.currency_exponent, locale)}</bdi></td>
                        <td className="p-3">{t(`billing.invoice_${invoice.status}`)}</td>
                        <td className="p-3">
                          {invoice.hosted_invoice_url && safeExternalUrl(invoice.hosted_invoice_url) ? (
                            <a
                              href={invoice.hosted_invoice_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex min-h-touch items-center gap-1 text-emerald-400 underline underline-offset-4"
                            >
                              {t("billing.view_invoice")}
                              <ExternalLink aria-hidden="true" className="h-4 w-4" />
                            </a>
                          ) : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}

      <Modal
        isOpen={confirmation !== null}
        onClose={() => setConfirmation(null)}
        title={t("billing.external_title")}
        closeLabel={t("billing.close_dialog")}
        className="max-w-lg"
      >
        <div className="space-y-4">
          <p className="text-sm text-brand-text-muted">{t("billing.external_desc")}</p>
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button variant="ghost" onClick={() => setConfirmation(null)}>
              {t("billing.stay_here")}
            </Button>
            <Button
              isLoading={actionState === "creating"}
              onClick={() =>
                void redirectToHosted(
                  confirmation === "portal" ? "portal" : "checkout",
                  confirmation === "portal" ? undefined : confirmation || undefined,
                )
              }
            >
              {t("billing.continue_provider")}
              <ExternalLink aria-hidden="true" className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Modal>

      {(actionState === "error" || actionState === "unavailable") && (
        <div role="alert" className="rounded-xl border border-red-700 bg-red-900/20 p-4 text-sm">
          {t(
            actionState === "unavailable"
              ? "billing.provider_unavailable"
              : "billing.action_error",
          )}
        </div>
      )}

      <p className="text-xs text-brand-text-muted">{t("billing.compliance_boundary")}</p>
    </main>
  );
}
