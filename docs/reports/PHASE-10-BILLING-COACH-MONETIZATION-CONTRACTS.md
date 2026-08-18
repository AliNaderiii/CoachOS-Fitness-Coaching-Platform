# Phase 10 — Billing and Coach Monetization Contracts

**Status:** implementation contract fixed before payment-boundary code  
**Baseline:** `f7ccaf457cbd2e67de2708d5367f6c1386a3edce`  
**Scope:** organization SaaS billing only; deterministic fake provider; no live money movement

## 1. Domain language

- **Billing account:** one organization-owned aggregate. An athlete can never own it.
- **Plan:** feature/limit presentation. It contains no money.
- **Price:** approved immutable commercial offer in integer minor units, ISO currency, interval, optional
  trial/grace durations and provider mapping.
- **Subscription:** normalized last verified provider lifecycle, never a client assertion.
- **Entitlement:** effective server decision derived from verified subscription + plan + bounded time + usage.
- **Staff seat:** distinct active user with owner or coach membership in the organization.
- **Active client:** distinct active user with athlete membership. Included/free means the athlete never pays;
  an approved plan may still impose an organization client-cap entitlement.
- **Grace:** derived bounded access window for verified `past_due`, not a provider status and not renewable by
  browser action.

## 2. Subscription state machine

Normalized states: `trialing`, `active`, `past_due`, `incomplete`, `unpaid`, `canceled`.
There is deliberately no `is_paid` boolean.

| From | Allowed verified next states | Paid organization entitlement |
|---|---|---|
| none | trialing, active, incomplete, past_due, unpaid, canceled | based on resulting state |
| trialing | trialing, active, past_due, incomplete, canceled, unpaid | enabled until verified trial end; no browser extension |
| active | active, past_due, incomplete, canceled, unpaid | enabled; if cancel-at-period-end, only through verified period end |
| past_due | past_due, active, unpaid, canceled, incomplete | enabled only before finite `grace_period_ends_at` |
| incomplete | incomplete, active, canceled, unpaid | disabled |
| unpaid | unpaid, active, canceled | disabled |
| canceled | canceled | disabled; reactivation requires a different provider subscription identity |

A stale event whose provider creation time is older than the subscription watermark is `ignored`; it cannot
regress state. Same-time conflicting lifecycle input is a process failure/reconciliation issue. A provider
adapter may retrieve current state for reconciliation, but this candidate's fake adapter performs no network.

### Cancellation rules

- `cancel_at_period_end=true` with `active`/`trialing`: entitlement lasts no later than verified
  `current_period_end`.
- `canceled`: paid entitlements disabled immediately regardless of browser return.
- Cancellation never deletes memberships, athlete records, sessions, metrics or photos.

### Invoice state machine

Normalized states: `draft`, `open`, `paid`, `uncollectible`, `void`. Invoice metadata does not independently
grant access. Subscription lifecycle remains the entitlement source. Payment failure may create/update an open
invoice and transition subscription only when the verified event includes normalized subscription state.

### Webhook event state machine

`received -> verified -> processed | ignored | failed`.

- Unsigned/bad timestamp/bad HMAC: HTTP 400/401, no domain mutation.
- Signed malformed schema without stable identity: HTTP 400, no domain mutation.
- Verified duplicate `(provider,event_id)`: HTTP 200, existing terminal state returned, no second mutation.
- Verified unknown customer/type: `ignored`, HTTP 200.
- Transaction/process failure: `failed`, reconciliation issue, HTTP 503 so provider retries.

## 3. Effective entitlement contract

Evaluator output:

```json
{
  "access_state": "active|trial|grace|restricted|none",
  "athlete_access_included": true,
  "features": {"feature_key": true},
  "limits": {"staff_seats": null, "active_clients": null},
  "usage": {"staff_seats": 2, "active_clients": 18},
  "effective_until": "RFC3339 or null",
  "reason": "stable.message_key"
}
```

Rules:

1. `athlete_access_included` is always true and is not used to authorize sensitive athlete data; existing
   tenancy/assignment/consent rules remain authoritative.
2. No account/subscription, incomplete, unpaid, canceled or expired grace returns paid features false.
3. Missing limit is unlimited (`null`). Zero is a real zero cap.
4. Capacity changes lock the billing account and count distinct active role users in the same transaction.
5. Existing usage above a newly reduced cap is grandfathered for reads and existing access, but new admissions
   fail with 409 and an owner-facing recovery key. No member/data is auto-deleted.
6. Snapshots are cache/audit material only. Security-sensitive enforcement invokes the evaluator against DB
   state; stale snapshots cannot grant access.

## 4. Provider adapter contract

Provider domain DTOs contain only normalized references/URLs/states:

```python
create_customer(account_reference, idempotency_key) -> ProviderCustomer
create_checkout_session(customer_ref, price_ref, return_url, cancel_url, idempotency_key) -> HostedSession
create_portal_session(customer_ref, return_url, idempotency_key) -> HostedSession
verify_webhook(raw_body, signature_header, received_at) -> VerifiedWebhookEvent
retrieve_subscription(subscription_ref) -> ProviderSubscription
```

`ProviderSubscription` includes the provider's timezone-aware `updated_at` watermark. Reconciliation rejects
missing/future/mismatched references and applies the normalized DTO through the same locked, ordered
subscription projection used by verified webhooks; it never trusts the retrieval merely because it succeeded.

Adapter obligations:

- no raw card/bank fields in arguments or results;
- timeout/error is a typed sanitized exception;
- HTTPS hosted URL and configured host allowlist;
- signature over the exact raw bytes plus bounded timestamp;
- stable provider event/customer/subscription IDs;
- no domain authorization or entitlement decision;
- never log secret, signature or payload.

`fake` uses HMAC-SHA256 and deterministic `.invalid` hosted URLs. It is the only enabled candidate provider.
Unknown providers fail closed. A future Stripe/Shetab adapter must pass the same contract and independent
production-readiness review.

## 5. HTTP route contract

All responses use existing JSON/RFC 7807 conventions. Authentication is cookie/session based. Mutations
require CSRF under normal browser authentication. Exact schemas are in `docs/OPENAPI.yaml`.

| Method/path | Permission | Behavior |
|---|---|---|
| `GET /api/v1/billing/plans` | active owner/coach (not athlete-only/support-only) | active mapped catalog; no org records |
| `GET /api/v1/billing/organizations/{org_id}/workspace` | active owner or delegated billing admin | current verified state, effective entitlement, usage, last 20 invoices/issues |
| `POST .../{org_id}/checkout-sessions` | active owner/admin; org not archived | requires `Idempotency-Key`; server-selected Price; returns allowed hosted URL |
| `POST .../{org_id}/portal-sessions` | active owner/admin | requires provider customer; returns allowed hosted URL |
| `GET/POST .../{org_id}/admins` | owner; GET may include admin | list/delegate active-member billing admins |
| `DELETE .../{org_id}/admins/{assignment_id}` | owner | revoke delegation |
| `POST /api/v1/billing/webhooks/{provider}` | public provider endpoint | raw-body verify, dedupe, process/ignore/fail |
| `POST .../{org_id}/reconcile` | active owner/admin, rate limited | retrieve, validate and synchronously apply ordered normalized state; fake returns explicit unavailable/no-network result |

No route accepts an athlete ID, amount, currency, provider customer ID, subscription status, entitlement,
return URL or hosted URL from the browser.

### Checkout input

```json
{"price_id":"CoachOS UUID","locale":"fa-IR|en-US"}
```

`Idempotency-Key` is 16–128 visible ASCII characters. Reusing a key with another price is `409`. Same key and
same price returns the prior safe session result. Return and cancel URLs are constructed from configured
`BILLING_FRONTEND_BASE_URL`; query parameters are UX hints only.

## 6. Fake webhook envelope

This is a deterministic provider fixture, not a public generic event ingestion API:

```json
{
  "id": "evt_fixture_001",
  "type": "subscription.updated",
  "created": 1786896000,
  "data": {
    "customer_id": "cus_fixture_001",
    "subscription": {
      "id": "sub_fixture_001",
      "status": "active",
      "price_id": "price_fixture_001",
      "quantity": 1,
      "current_period_start": 1786896000,
      "current_period_end": 1789574400,
      "trial_end": null,
      "cancel_at_period_end": false,
      "canceled_at": null
    }
  }
}
```

Invoice events use `invoice` with ID/status/currency/amount integer fields and optional provider-hosted HTTPS
URLs. Unknown fields are ignored at the adapter boundary; prohibited raw instrument-shaped fields fail schema
validation. Signature header: `t=<unix>,v1=<hex HMAC-SHA256 of "<t>.<raw-body>">`; default tolerance 300s.

## 7. Authorization matrix

| Actor | Catalog | Workspace/invoices | Checkout/portal | Delegate admin | Webhook |
|---|---:|---:|---:|---:|---:|
| Active owner | yes | yes, own org | yes, own org | yes | no special access |
| Active delegated billing admin | yes | yes, own org | yes, own org | list only | no special access |
| Active regular coach | yes | no by default | no | no | no |
| Athlete (including multi-role absent owner/admin) | no billing records | no | no | no | no |
| Support membership | no | no | no | no | no |
| Suspended/archived member | no | no | no | no | no |
| Platform admin | no implicit bypass in this candidate | no | no | no | no |
| Provider | n/a | n/a | n/a | n/a | signed endpoint only |

Multi-role evaluation is a union: an athlete who is also active owner is acting as owner and may manage the
organization account. Athlete-only users are never payment-gated.

## 8. Data constraints

- one BillingAccount per organization;
- `(provider, external_customer_id)` globally unique and one reference per account/provider;
- `(provider, external_subscription_id)` unique;
- `(provider, external_invoice_id)` unique;
- `(provider, provider_event_id)` unique;
- `(billing_account, idempotency_key)` unique;
- positive subscription quantity; nonnegative money and plan limits; uppercase 3-character currency;
- one active admin assignment per account/user;
- bounded status and interval choices.

External IDs are never used alone for authorization; all owner requests start from server membership and org.

## 9. Observability and reconciliation

Safe structured dimensions: request/correlation ID, organization UUID, provider name, provider event ID,
normalized event type, processing state, latency bucket and sanitized error code. Prohibited: signature,
secret, raw body, billing email, hosted URL query, payment instrument details.

Material transitions append immutable `BillingAuditEvent` and a `BillingDomainEvent` outbox-style hook. The
hook is deliberately not a notification engine. `ReconciliationIssue` gives owners/operators bounded status
without secrets. Automated scheduling, support dashboard and provider-specific dead-letter replay are deferred.

## 10. UX contract

`/[locale]/org/billing` provides: plan comparison; included-athlete statement; canonical localized amount;
current status and renewal/cancellation; usage/limits; one clear checkout or portal action; bounded invoice
summary; pending return; action-required, forbidden, provider-unavailable, loading, empty and retry states.
It warns before leaving for a hosted provider. It never says payment succeeded based on URL query state.

`fa-IR` RTL and `en-US` LTR keys must be exactly paired. Currency/date/number display uses `Intl` while API
money remains integer minor units. Semantic headings, native buttons, visible focus, 44px targets,
`role=status/alert`, non-color labels and no horizontal overflow are required. No Arabic resource is created.

## 11. Explicit exclusions and production gates

Excluded: live payment calls/credentials, raw card/bank data, athlete billing, marketplace, payouts,
commissions, transfers, tax calculation/advice, legal invoice certification, accounting certification,
chargeback automation, notification engine, AI, nutrition, durable offline, wearables, native apps, Arabic.

Before production: approved price/catalog and commercial durations; production adapter and provider account
configuration; key rotation/secrets management; independent webhook penetration/replay test; tax/legal/
consumer/accounting/retention review; refund/dispute procedures; support access model; reconciliation worker
and alerts; capacity/load test on PostgreSQL; deployment allowlists; formal accessibility/device review.
