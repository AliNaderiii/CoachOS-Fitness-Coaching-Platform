# AI Governance — CoachOS Copilot (Phase 11)

**Version:** 1.0.0 Phase 11
**Status:** Approved for Phase 11 implementation scope — policy-bound, not a legal compliance claim
**Baseline:** `f7ccaf457cbd2e67de2708d5367f6c1386a3edce` (verified remote `main`, PR #17 + PR #18 merged)
**Implements:** ADR-007 (Constrained AI Assistance), PRD P2-AI-01, Threat T17 (Prompt Injection), Privacy Tier 8 (AI Inference Logs)
**Languages:** `fa-IR` RTL + `en-US` LTR only. Arabic resources are strictly out of scope (ADR-003); the Copilot must never generate, infer, or route Arabic.

---

## 1. Position

The CoachOS AI Copilot is a **narrow, provider-neutral drafting assistant for authorized professional users (`owner`, `coach`)**. Every generated artifact is an **untrusted draft**: it is schema-validated, source-referenced, labeled as AI-generated, and inert until a human professional explicitly approves it. The Copilot is not an autonomous coach, not a medical advisor, not a decision-maker, and not a data-export channel.

Non-negotiables:

1. **No silent side effects.** The Copilot never sends a message, mutates a program, changes billing, alters consent, or grants access. Export/commit/copy of any draft is a discrete human action.
2. **Server-authoritative authorization.** The API layer (never the UI) decides which actor may request which capability over which athlete, and re-verifies it on every read.
3. **Minimum necessary context.** Only the smallest authorized dataset required for the selected capability is assembled, redacted, and sent to the provider adapter.
4. **Untrusted content is data.** Any text originating from users or imported records (exercise names, athlete notes, reasons, display names) is delimited data inside the prompt. It can never become system policy.
5. **Fail closed.** Provider outage, timeouts, malformed output, schema violations, quota/cost exhaustion, or revoked access produce a safe explicit fallback — never a guess, never a silent degradation, never an unapproved provider.

## 2. Allowed use (P0 capability scope)

| Capability ID | Actor | Subject | What it does | Human approval point |
|---|---|---|---|---|
| `summarize_progress` | owner, assigned coach | one authorized athlete | Summarizes recent authorized workout/progress activity (adherence, loads, subjective flag counts) with cited source records and explicit limitations. | Review before any copy/export. Copy is a human click. |
| `draft_check_in` | owner, assigned coach | one authorized athlete | Drafts a coach check-in/follow-up message referencing recent adherence. **Never sends.** | Approve / edit / reject before the text may be copied out. |
| `suggest_program_adjustment` | owner, assigned coach | one authorized athlete with an active assignment | Suggests a draft adjustment constrained to the organization's published exercise library with rationale and sources. **Never applies.** | Approve / edit / reject; applying any change is a separate manual coaching action. |

Anything outside this table is out of scope for Phase 11, including free-form chat ("ask anything about all organization data"), nutrition drafting (Phase 09 sibling, not on baseline), and message sending (Phase 08 sibling, not on baseline). Where a sibling capability is absent from the verified baseline, Phase 11 exposes only a **typed adapter seam** (`apps.copilot.providers.base.ModelProvider`, capability registry) — it does not duplicate that domain.

## 3. Prohibited use (enforced by tests)

The following are prohibited and are blocked by dedicated tests (`backend/tests/copilot/`):

- medical diagnosis, treatment, injury prediction, rehabilitation prescription, medication/supplement advice, eating-disorder advice, emergency triage, clinical risk scoring;
- autonomous workout-plan mutation, autonomous message/notification sending, billing action, consent change, access-control change, or any external side effect;
- athlete-facing medical/psychological chatbot;
- unbounded retrieval across organization data;
- provider lock-in as the only domain interface;
- training models on CoachOS data (no provider call may be used for that purpose by contract; no such code path exists);
- sending raw databases, credentials, secrets, or unrestricted tenant data to a provider;
- production provider credentials or real personal/health data in tests (synthetic fixtures only);
- durable offline AI queue, wearable integration, Arabic resources/routes;
- claims of provider zero-retention, HIPAA, GDPR, or safety certification without signed/verified evidence.

## 4. Data classes and flow

### 4.1 Data classes admitted to the Copilot

| Tier | Content | In context? | Controls |
|---|---|---|---|
| Tier 0 | Published exercise catalog names/metadata | Yes (allowlist for adjustments) | Org-visible published exercises only |
| Tier 1 | Athlete `display_name`, role/membership status | Minimal (subject identification) | Redacted elsewhere; no email/phone in provider context |
| Tier 2 | Sessions, set-log aggregates, assignment snapshot excerpts, adherence | Yes (minimum necessary) | Truncated, aggregated where possible |
| Tier 3 | Subjective feedback flags | **Counts + type/severity only** | Free-text `details` and `anatomical_location` never leave the DB; non-clinical disclaimer attached |
| Tier 4 | Progress photos | **Never** | Excluded by context builder + tests |
| Tier 3 | Body metrics (weight etc.) | **Never** | Consent-gated domain; excluded + tests |
| Tier 6 | Secrets, credentials, session data | **Never** | Provider payloads scanned in tests |
| Tier 8 | AI run records (this phase) | n/a | Tier 8 lifecycle below |

### 4.2 Data flow (enforced pipeline)

```
Authorized Coach Request (authenticated session, tenant context)
  -> Feature flag / kill switch (COPILOT_ENABLED, org override)
  -> Policy gate: capability allowlist + prohibited-intent screening
  -> Authorization gate: org scope -> role check -> assignment check (before retrieval)
  -> Rate limit + daily quota + org cost-cap check (before provider call)
  -> Minimum-necessary context builder (redaction, truncation, caps)
  -> Provider-neutral model adapter (configured provider; default deterministic fake)
  -> Structured output schema validation + anti-hallucination source check
  -> Safety/policy rule checks (non-clinical scope, label, disclaimer)
  -> Persisted draft + provenance (AISourceReference) + audit events
  -> Human review: view / edit / regenerate / reject / report / approve
  -> Expiry & purge per retention policy
```

### 4.3 Storage posture (Tier 8 lifecycle)

- **Not stored by default:** raw provider request strings and raw completions. The persisted `AIOutput.payload` is the *validated structured draft* only; `AIRun.context_snapshot` is the *redacted, truncated* context actually used (needed for the coach's "inspect input" right and for audit).
- **Retention:** `AIRun.expires_at = created_at + COPILOT_CONTEXT_RETENTION_DAYS` (default 30). `purge_expired_runs()` clears `context_snapshot` and unapproved output payloads and marks runs `expired`. Approved/rejected drafts keep the final structured payload as the decision record; context snapshots are still cleared.
- **Logs:** request-scoped logs record IDs, counts, hashes, and reason codes only. Free-text athlete content is never written to application logs (tested).
- **Audit:** `AIAuditEvent` (append-only, immutable at ORM level) records request/complete/fail/view/edit/approve/reject/report/source-open/purge. Access to run history is org- and role-scoped.
- **Deletion/erasure:** AI records reference `athlete_user`/`actor_user` IDs. A future privacy-erasure pipeline (Phase roadmap) must disassociate these references; documented as deferred integration — no GDPR/HIPAA claim is made.

## 5. Provider assumptions

- **Provider-neutral contract:** `apps.copilot.providers.base.ModelProvider`. The only fully implemented provider is the **deterministic fake** (`fake-deterministic`) used for local development, CI, and evaluation.
- **Selection is configuration:** `COPILOT_PROVIDER` (env) + `AIProviderAdapterConfig` rows (non-secret metadata only). There is **no silent fallback**: if the configured provider is unknown or disabled, runs fail closed with `provider_unavailable`.
- **Credentials:** real provider API keys, if ever configured, arrive only via server-side environment injection (never in DB, never in frontend config, never in tests). No claim is made about any provider's retention behavior until a signed DPA/contract exists — the report records this assumption as unverified.
- **Budgets enforced pre-call:** per-actor per-minute rate limit, per-actor and per-org daily run quotas, per-org daily cost cap (estimated tokens × configured micro-USD rates). Timeout is measured around the provider call and bounded; retry is bounded (max 1 retry, transient errors only) and idempotent at the API layer via `Idempotency-Key`.

## 6. Human-in-the-loop

- Draft lifecycle: `draft -> edited? -> approved | rejected`; runs can also be `cancelled`, `failed`, `expired`.
- Approval records `reviewed_by`, `reviewed_at`, and the final payload version (edited payload supersedes generated payload).
- `report` lets any authorized reviewer flag unsafe/incorrect/privacy/hallucinated-citation output; reports persist as `AIFeedback` with audit events.
- Every draft response carries `ai_generated: true`, `requires_human_review: true`, explicit `limitations`, and `sources` the UI must render.

## 7. Incident response (Copilot-specific)

| Scenario | Detection | Immediate action | Follow-up |
|---|---|---|---|
| Unsafe/medical output observed | `AIFeedback` report, eval regression | Kill switch: `COPILOT_ENABLED=False` (global) or org `settings.copilot_disabled=true` | Triage report, extend screening lexicon + eval case, postmortem note in phase report |
| Cross-tenant source leak | Eval/red-team case, support report | Kill switch; revoke nothing else (read-only design) | Root-cause authorization gate; add regression test; assess exposure window from `AIAuditEvent` |
| Provider outage/timeout spike | `provider_unavailable`/`provider_timeout` error codes in run metrics | None (fails closed automatically); optional disable provider row | Verify no partial outputs persisted (status `failed`) |
| Cost/quota anomaly | `AIUsageMeter` daily rows vs caps | Caps already block; alert review | Adjust caps after investigation |
| Suspected prompt-injection abuse | Report type, output quarantine (`validation_failed`) | Quarantine stays human-invisible until reviewed | Add injection pattern to eval fixtures |

## 8. Cost limits (development assumptions, not production SLOs)

| Control | Default (dev/test) | Source |
|---|---|---|
| Rate limit | 10 runs/min/actor | `COPILOT_RATE_LIMIT_PER_MINUTE` |
| Daily run quota | 20/actor, 100/org | `COPILOT_DAILY_RUN_QUOTA_*` |
| Org daily cost cap | 5.00 USD equiv (micro-USD) | `COPILOT_DAILY_COST_CAP_MICRO_USD` |
| Provider timeout | 8000 ms | `AIProviderAdapterConfig.timeout_ms` |
| Context cap | 12000 chars pre-redaction ceiling | `AIProviderAdapterConfig.max_context_chars` |
| Output cap | 1200 tokens est. | `AIProviderAdapterConfig.max_output_tokens` |
| Context retention | 30 days | `COPILOT_CONTEXT_RETENTION_DAYS` |

The deterministic fake provider reports synthetic token estimates so quota/cost code paths are always exercised in CI. These numbers are local policy defaults only; production budgets require a separate capacity plan.

## 9. Authorization matrix (capability → source → permission → output → approval)

| Capability | Sources read | Server-side permission required | Output shape | Approval |
|---|---|---|---|---|
| `summarize_progress` | `WorkoutSession` (org+athlete+window), `SetLog` aggregates, `FeedbackFlag` type/severity counts, active `ProgramAssignment` title | active `owner` OR active `coach` with active `CoachAthleteAssignment` in same org; athlete active member | `ai_progress_summary.v1` JSON draft + sources + limitations | Human review before copy/export |
| `draft_check_in` | Same session/flag scope as above (adherence facts only) | same | `ai_check_in_message.v1` JSON draft (subject+body) | Approve/edit/reject; never auto-sent |
| `suggest_program_adjustment` | Active `ProgramAssignment.snapshot_payload` excerpt + org published `Exercise` allowlist (id/name) | same | `ai_program_adjustment.v1` JSON draft; every `exercise_id` re-validated against allowlist | Approve/edit/reject; never auto-applied |

Denied populations (tested): athletes, support, suspended members, unassigned coaches, cross-tenant actors, archived orgs, and any request after assignment revocation (stale runs re-authorize on every read).

## 10. Red-team scenario suite (synthetic fixtures only)

The evaluation harness (`apps/copilot/eval/`, executed in `tests/copilot/test_copilot_evaluation.py`) covers: correct citation; cross-tenant exclusion; missing/contradictory data; prompt injection inside athlete fields; system-prompt/secret fishing; prohibited medical requests; unsafe training advice refusal; hallucinated citation rejection; schema violation quarantine; fa-IR/en-US language behavior; duplicate/idempotency; cancellation; provider outage + kill switch; quota/cost exhaustion; stale-after-revocation reads. Results and residual risks are recorded in the Phase 11 report with limitations — tiny synthetic suites demonstrate control wiring, **not** model accuracy.

## 11. Evaluation and review gates

- Gate 1 (this document + contracts): governance policy, threat model delta, data flow, authz matrix, schemas, eval plan — approved before provider code paths beyond the fake exist.
- Gate 2: backend/API/authorization/fake-provider suite green; prohibited capabilities blocked by tests.
- Gate 3: independent responsible-AI/privacy/adversarial review (simulated role review recorded in the report; the implementer does not self-approve).
- Gate 4: frontend lint/type/test/build + locale parity + accessibility review + keyboard-only approval journey.
- Gate 5: no unresolved critical/high privacy/security/safety/authorization finding.
- Gate 6: clean-checkout validation, docs, PR evidence, post-merge sync plan.
