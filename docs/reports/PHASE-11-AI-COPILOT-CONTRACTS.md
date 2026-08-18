# Phase 11 — AI Copilot Contracts

**Baseline:** `f7ccaf457cbd2e67de2708d5367f6c1386a3edce` · **Policy:** `docs/architecture/AI_GOVERNANCE.md` (`POLICY_VERSION = 2026-08-16.v1`)
**Status:** Implemented against the deterministic fake provider; reconciled to `docs/OPENAPI.yaml` v1.1.0-phase11 (paths marked `x-implementation-status: implemented-phase-11`).

---

## 1. Capability registry (allowlist — anything else is rejected)

| Capability | Output schema | Human review | Draft semantics |
|---|---|---|---|
| `summarize_progress` | `ai_progress_summary.v1` | required | Coaching progress brief over authorized recent activity; nothing sent |
| `draft_check_in` | `ai_check_in_message.v1` | required | Coach→athlete message draft; **never sent** by Copilot |
| `suggest_program_adjustment` | `ai_program_adjustment.v1` | required | Adjustment suggestions constrained to org published library; **never applied** |

Unknown capability ids fail validation (`400`). Per-capability kill list: `COPILOT_DISABLED_CAPABILITIES`.

## 2. REST operations (all under `/api/v1`, professional roles only)

| Method & path | Purpose | Success | Denials |
|---|---|---|---|
| `GET /copilot/capabilities?org_id=` | Feature state, allowlist, provider metadata, limits | 200 | 403 |
| `POST /copilot/runs` | Create+execute governed run (idempotent via `Idempotency-Key` or body key) | 201 (200 on replay) | 400 / 403 / 404 / 429 |
| `GET /copilot/runs?org_id=` | List authorized runs (coach: own; owner: org; max 50) | 200 | 403 |
| `GET /copilot/runs/{id}?org_id=` | Run detail: draft, sources, limitations, inspectable context, actions | 200 | 403 / 404 / 410 |
| `POST /copilot/runs/{id}/cancel` | Cancel queued/running run | 200 | 403 / 409 |
| `POST /copilot/runs/{id}/regenerate` | New linked run (blocked after approval) | 201 | 403 / 409 |
| `POST /copilot/runs/{id}/report` | Structured feedback report (`unsafe`/`incorrect`/`privacy`/`hallucinated_source`/`other`) | 201 | 400 / 403 |
| `PATCH /copilot/runs/{id}/output` | Human edit; payload revalidated against schema + citations | 200 | 400 / 403 / 409 |
| `POST /copilot/runs/{id}/output/approve` | Explicit human approval (+actor/timestamp) | 200 | 403 / 409 |
| `POST /copilot/runs/{id}/output/reject` | Explicit human rejection (+note) | 200 | 403 / 409 |
| `GET /copilot/runs/{id}/sources/{ref}?org_id=` | Open one provenance record (re-authorized) | 200 | 403 / 404 |

Every error is the shared RFC 7807 envelope (`type`, `title`, `status`, `detail`, `instance`, `message_key`, `correlation_id`). Copilot `message_key` values: `error.ai_feature_disabled`, `error.ai_capability_unknown`, `error.ai_prohibited_use`, `error.ai_not_authorized`, `error.ai_quota_exceeded`, `error.rate_limit_exceeded`, `error.ai_output_invalid`, `error.ai_state_conflict`, `error.ai_expired`, `error.validation_failed`, `error.not_found`, `error.permission_denied`.

## 3. Run request contract

```json
{
  "org_id": "<org uuid> (or ?org_id= / tenant context)",
  "capability": "summarize_progress",
  "athlete_id": "<subject athlete uuid>",
  "generation_language": "en-US | fa-IR",
  "parameters": { "period_days": 14, "notes": "<≤500 chars, screened>", "variation": 0 },
  "idempotency_key": "<≤64 chars> (or Idempotency-Key header)"
}
```

Server-enforced gates, in order: feature flag → capability allowlist → prohibited-intent screening (`notes`/`target_assignment_id`) → per-actor/minute rate limit → subject authorization (before retrieval; 404 cross-tenant, 403 unassigned) → daily actor/org quota → org cost cap → idempotent create → context build → provider call (bounded attempts, measured timeout) → output validation → persist draft.

## 4. Output contracts (strict; validated server-side before persistence)

Common envelope (exact key set enforced): `schema_name`, `schema_version: 1`, `ai_generated: true`, `requires_human_review: true`, `limitations: string[1..10]`, `source_ids: string[]` (each must exist in the run's authorized sources — hallucinated citations fail validation), plus per-schema fields:

- **`ai_progress_summary.v1`**: `athlete_display_name(≤160)`, `period_days(1..31)`, `sessions_completed`, `sessions_missed`, `summary(≤1600)`, `highlights(≤12×240)`, `concerns(≤12×240)`.
- **`ai_check_in_message.v1`**: `subject(≤140)`, `body(≤1600)`, `tone(≤40)`.
- **`ai_program_adjustment.v1`**: `target_day_title(≤160)`, `suggestions[1..8]` of `{exercise_id ∈ org published allowlist, change_type ∈ substitute|reduce_load|adjust_sets|coach_note, rationale(≤280)}`, `safety_disclaimer(≤400)`.

Invalid output is quarantined (`AIOutput.status=quarantined`, payload never persisted); the run ends `failed` with `error_code=output_invalid` and a safe fallback presentation.

## 5. Persisted records (no raw prompts/completions)

| Record | Key fields | Notes |
|---|---|---|
| `AIRun` | org/actor/athlete FKs, capability, status, idempotency key (unique per org+actor), policy_version, prompt_template FK, provider/model ids, context hash, tokens+cost estimates, attempts, duration, error_code, fallback flag, expires_at | `context_snapshot` = redacted truncated context actually used; cleared on expiry |
| `AIOutput` | run 1:1, schema+version, validation status/errors, payload, edited_payload, status, reviewed_by/at | `effective_payload` = edited ?? generated |
| `AISourceReference` | run FK, source_type/id, descriptor, ordinal | re-authorized on open |
| `AIProviderAdapterConfig` | slug, kind, model id, limits, micro-USD rates, retention note | **no secrets** (enforced by test) |
| `PromptTemplateVersion` | capability+version+locale unique, sha256, directive, schema id, active flag | seeded v1 for both locales × 3 capabilities |
| `AIFeedback` | run FK, reporter, type, ≤1000-char detail, status | reports never screened (needs fidelity) |
| `AIPolicyDecision` | org/actor/run, stage, allow/deny, reason_code | durable incl. outside transactions |
| `AIAuditEvent` | immutable; `ai.run.*`, `ai.output.*`, `ai.source.opened`, `ai.purge.executed` | mirrors Phase 05 immutability contract |
| `AIUsageMeter` | org+actor+date unique; runs, tokens, cost | atomic F-expression increments |

## 6. Provider adapter contract

```python
class ModelProvider(Protocol):
    slug: str
    def generate(self, request: ProviderRequest) -> ProviderResponse: ...

ProviderRequest: capability, generation_language, system_directive, context_payload, output_schema, max_output_tokens
ProviderResponse: payload(dict), model_identifier, provider_request_id, input/output tokens est, cost_micro_usd
Errors: ProviderUnavailable / ProviderTimeout (transient, 1 bounded retry) / ProviderOutputMalformed / ProviderError
```

- Implemented: `fake-deterministic` (deterministic composition; never interpolates user free text; fa-IR/en-US templates only; synthetic token/cost estimates).
- Registry: `settings.COPILOT_PROVIDER` + enabled `AIProviderAdapterConfig` row; unknown/disabled/unimplemented kinds fail closed with `provider_unavailable` — **no silent fallback**.
- Future HTTP providers must implement timeout, budget, and error mapping and pass the same schema validation; Phase 11 ships no live provider integration.

## 7. Safety envelope summary

| Layer | Mechanism |
|---|---|
| Scope | Capability allowlist (3 ids); prohibited-intent screening (defense in depth, not sole control) |
| Data | Tier-2 max in context; Tier-3 counts only; Tier-4/6 never; redaction of emails/phones/URLs; truncation caps |
| Model | Structured schemas + citation allowlist check + exercise allowlist check |
| Operations | Rate limit, daily quotas, org cost cap (pre-call), measured timeout, ≤1 transient retry, idempotency keys, cancel, kill switches (global/org/capability/provider row) |
| Human | draft→edited→approved/rejected lifecycle; view/edit/regenerate/reject/report; audit trail; retention purge (30d default) |
