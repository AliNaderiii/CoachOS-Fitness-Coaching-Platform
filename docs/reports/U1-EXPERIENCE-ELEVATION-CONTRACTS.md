# U1 — Experience Elevation and Design System v2 — Contracts

**Status:** 📋 **PROPOSED — not implemented.** Gate 0 preflight failed; see `U1-EXPERIENCE-ELEVATION-AUDIT.md`.
**Date:** 2026-08-19 (UTC)
**Verified `main` SHA:** `6722d5fefc92262334d53200f8be2b010487eb60`
**Purpose:** Freeze the design contracts (route matrix, role model, tokens, component API, acceptance criteria) so implementation can begin immediately once the founder resolves Decision A.

**Nothing in this document has been built.** It is a specification awaiting approval.

---

## 1. Scope boundaries

**In scope:** dual-theme semantic tokens; role-aware shell/navigation; athlete core loop; coach command center; shared-surface polish; RTL/LTR parity; a11y/perf/visual QA; removal of foundation copy from customer surfaces.

**Explicitly out of scope (must not appear in any implementation PR):** nutrition (Phase 09), new billing features, new AI capabilities, marketplace, wearables, native apps, Arabic in any form, new backend domains, new API endpoints, toolchain migrations beyond the Decision A outcome.

**Contract preservation:** no existing API contract may change. The UI re-skins and re-routes around `/api/v1/**` exactly as it exists today.

---

## 2. Role model contract

The frontend has **no role primitive today** (audit §5.3). This must be built first; everything in Gates 3–5 depends on it.

```ts
// lib/auth/roles.ts  (proposed)
export type Role = "athlete" | "coach" | "owner" | "support";
export type SessionState =
  | { status: "anonymous" }
  | { status: "suspended"; user: UserRef }
  | { status: "active"; user: UserRef; role: Role; orgId: string; roles: Role[] };
```

Rules:
1. Navigation is derived from `role`, never hard-coded per screen.
2. A user holding multiple roles sees **one** workspace at a time, changed only via an explicit `ContextSwitcher`. No blended navigation, ever.
3. Route guards are declarative and colocated with the route manifest (§3), not scattered in components.
4. Unauthorized access renders `ForbiddenState` — never a redirect that leaks resource existence.
5. `suspended` and `wrong-tenant` are first-class rendered states, not crashes.

**Consent gating:** athlete sensitive data (body metrics, progress photos) stays consent-gated in the UI exactly as the backend enforces. The UI must never render a sensitive surface it cannot prove authorization for, and must show an explicit "consent required" state rather than an empty chart.

---

## 3. Route manifest and navigation contract

### 3.1 Athlete — mobile bottom nav, **5 items maximum**

Replaces today's 7-item mixed-role bar.

| Item | Route | Status |
|---|---|---|
| Today | `/[locale]/athlete/today` | exists — redesign |
| Plan | `/[locale]/athlete/plan` | **new** |
| Progress | `/[locale]/athlete/progress` | exists — redesign |
| Inbox | `/[locale]/athlete/inbox` | **new** (scoped view of messages) |
| Profile | `/[locale]/athlete/profile` | **new** (replaces the `/org/settings` leak) |

Supporting athlete routes (not in the bar): `/athlete/workout/[sessionId]`, `/athlete/workout/[sessionId]/complete` (**new**).

### 3.2 Coach — desktop rail + contextual header

| Item | Route | Status |
|---|---|---|
| Overview | `/[locale]/coach/overview` | **new** |
| Athletes | `/[locale]/coach/athletes` | **new** |
| Athlete context | `/[locale]/coach/athletes/[athleteId]` | **new** |
| Programs | `/[locale]/coach/programs` | exists — redesign |
| Calendar | `/[locale]/coach/calendar` | **new** |
| Inbox | `/[locale]/coach/inbox` | **new** |
| Reports | `/[locale]/coach/reports` | **new** |
| Copilot | `/[locale]/coach/copilot` | exists — polish only, no new AI capability |
| Settings | `/[locale]/coach/settings` | **new** |

### 3.3 Owner — administration workspace

| Item | Route | Status |
|---|---|---|
| Organization | `/[locale]/org/overview` | **new** |
| Members & Access | `/[locale]/org/members` | **new** |
| Billing | `/[locale]/org/billing` | exists — redesign |
| Settings | `/[locale]/org/settings` | exists — strip foundation copy |

### 3.4 Migration rules
- Existing routes keep their paths where possible; new routes are additive.
- Any moved route ships a redirect for one release; no dead links.
- Deep links preserve `[locale]` and role context; a deep link into an unauthorized route renders `ForbiddenState`.
- No API path changes.

### 3.5 Required states per route
Every route must implement: **loading, empty, error, offline, forbidden, suspended, wrong-tenant**. This is a checklist item per route, not a global fallback.

---

## 4. Design token contract

Single semantic layer; both themes emitted from it. **No feature component may reference a raw color, radius, or spacing value** (395 violations to migrate — audit §5.5).

### 4.1 Structure

```css
/* styles/tokens.css (proposed) */
:root, [data-theme="dark"] {
  --surface-canvas: #0B0F17;   --surface-raised: #111827;
  --surface-overlay: #1F2937;  --surface-hover: #374151;
  --border-default: #1F2937;   --border-strong: #374151;
  --text-primary: #F9FAFB;     --text-secondary: #E5E7EB;
  --text-muted: #9CA3AF;       --text-disabled: #6B7280;
  --action-primary: #10B981;   --action-primary-hover: #059669;
  /* …status, chart, focus, elevation */
}
[data-theme="light"] {
  --surface-canvas: #F8FAFC;   --surface-raised: #FFFFFF;
  --surface-overlay: #F1F5F9;  --surface-hover: #E2E8F0;
  --border-default: #E2E8F0;   --border-strong: #CBD5E1;
  --text-primary: #0F172A;     --text-secondary: #1E293B;
  --text-muted: #475569;       --text-disabled: #94A3B8;
  --action-primary: #0D9488;   --action-primary-hover: #0F766E;
  /* teal shifted darker in light theme for contrast on white */
}
```

Token families required: color/surface, typography, spacing/density, radius, elevation, border/focus, **chart palette**, status/safety, motion, z-index.

### 4.2 Rules
- Theme applied via `data-theme` on `<html>`, resolved before first paint (inline script) to prevent flash.
- Theme preference persisted in `localStorage` only. **It is a UI preference and must never carry user, health, or tenant data.**
- Theme switching must not disturb `dir`, locale, or reduced-motion state.
- Emerald `#10B981` on dark and teal `#0D9488` on light are the primary action colors; both require measured contrast against their own canvas before sign-off.
- Chart colors come from a dedicated `--chart-*` ramp that is colorblind-safe and never encodes meaning by hue alone.

### 4.3 Typography
- Persian line-height `1.65`, English `1.5` (already correct — preserve).
- **Fonts must be self-hosted via `next/font`** with `font-display: swap` and a metric-compatible fallback. Removes the render-blocking third-party `@import`s and makes Persian type work offline (audit §5.8).

---

## 5. Component contract

~36 components to build (audit §5.6). Every one must satisfy:

1. Tokens only — no literals.
2. Keyboard operable; visible `:focus-visible`; correct roles/labels.
3. Both themes × both locales (`dir` aware, logical properties only).
4. Loading / empty / error / disabled states where applicable.
5. Reduced-motion honored.
6. Touch targets ≥44px, 48px for primary actions.
7. Rendered in a gallery route with every state visible (Gate 2 exit condition).

**Data-visualization honesty rule:** every chart must label its data as **actual**, **estimated**, or **unavailable**, and must ship a text alternative (accessible summary or data table). No invented data points, no interpolation presented as measurement, no fabricated trends in empty states.

---

## 6. Athlete core-loop acceptance criteria (first vertical slice)

`Today → Workout → Set logging → Completion → Progress → Inbox`

### Today
- [ ] Greeting + current plan context, personalized.
- [ ] Exactly **one** dominant next action.
- [ ] Duration/volume shown **only when actual logged data exists**; otherwise omitted, never zero-filled.
- [ ] Coach note preview only when authorized.
- [ ] One recent win/progress moment.
- [ ] Recovery/feedback state with **no medical claim or diagnosis language**.
- [ ] Empty state routes to a concrete next action.

### Workout
- [ ] One-handed reachable layout at 360px.
- [ ] Exercise context + target prescription visible without scrolling.
- [ ] Previous performance visible at the point of logging.
- [ ] Numeric entry ≤2 taps; keyboard alternative present.
- [ ] Rest timer with unambiguous running/paused/complete state.
- [ ] Substitution and feedback flows inline — no stacked modals.
- [ ] Offline: never claims durable sync. Wording matches actual guarantee (in-memory only, per Phase 07 boundary).

### Completion
- [ ] Respectful acknowledgment — no confetti-grade gamification of health data.
- [ ] Real session summary from logged values only.
- [ ] Clear route onward to Progress or Today.

### Progress
- [ ] Progressive disclosure: summary → trends → details.
- [ ] Every chart has a text alternative.
- [ ] Consent-gated surfaces show an explicit consent state, never a blank chart.
- [ ] Comparison window and units always labeled.
- [ ] No invented metrics.

### Inbox
- [ ] Unread triage is the primary affordance.
- [ ] Conversation context preserved.
- [ ] Explicit send / sending / failed / retry states.
- [ ] Back-links to workout/progress context **only when authorized**.

### Cross-cutting exit criteria
- [ ] fa-IR RTL and en-US LTR parity at 528+ keys, zero asymmetry.
- [ ] Viewports 360 / 390 / 768 / 1024 / 1280 / 1440.
- [ ] Keyboard-only completion of the full loop.
- [ ] Screen-reader smoke pass: landmarks, live regions, focus order.
- [ ] Both themes.
- [ ] Visual regression baselines captured.

---

## 7. Coach command-center acceptance criteria (second slice)

Overview must answer, above the fold: **who needs attention today; who missed or completed a workout; which feedback flags are unresolved; which messages are unread; what is the next coach action.**

- [ ] Athlete profile gives a coherent longitudinal timeline without bypassing authorization or consent.
- [ ] High-frequency coaching actions are separated from administrative settings.
- [ ] Role authorization verified per route.
- [ ] Desktop and tablet responsive review recorded.
- [ ] No N+1 / unbounded query regressions introduced by new list views.

---

## 8. Benchmark principles — and what CoachOS will **not** copy

| Product | Principle adopted | **Not copied** |
|---|---|---|
| ABC Trainerize | Always give the client a clear next action; connect delivery → progress → communication into one loop | Nutrition/macro tracking; habit gamification; its dense multi-tab IA |
| TrueCoach | Focused coach dashboard: clients, due dates, alerts, compliance, messaging in one view | Its compliance-percentage scoring as a headline judgment of the athlete |
| Everfit | Progressive disclosure; clear client task flows; workout/exercise history depth | Nutrition module; leaderboards and social competition features |
| Practice Better | One authenticated portal unifying messaging, scheduling, forms, programs, resources | Payments/invoicing expansion; forms/journal builder; scheduling engine |
| Healthie | Longitudinal relationship context; provider feedback embedded with client data | Clinical/EHR framing; insurance workflows; any medical-record positioning |

**Blanket rule:** these are *pattern* references. No visual cloning, no copied copy, no lifted iconography or layout. CoachOS keeps its own Teal/Emerald identity and calm-command-center tone.

**Health-adjacent restraint:** CoachOS will not gamify pain, fatigue, injury, or body-composition data; will not present subjective athlete feedback as clinical assessment; and will not imply diagnosis anywhere in the UI.

---

## 9. Verification contract (Gate 8)

To be run from a clean checkout and recorded with actual output:

```bash
cd backend
ruff check . && ruff format --check . && pytest --cov=apps --cov=config
cd ../frontend
npm ci && npm run lint && npm run type-check && npm test && npm run build
cd ..
bash infra/scripts/check-secrets.sh
git diff --check
docker compose config
```

**Baseline measured at audit time (`6722d5f`):** backend 369 tests / 87% coverage / ruff clean; frontend 153 tests / lint / type-check / build all pass; secrets scan pass; `git diff --check` clean. `docker compose config` was **not** verifiable (docker unavailable in this sandbox) and must be run by CI or the founder.

**Prohibited claims:** no WCAG certification, no GDPR or HIPAA compliance, no PWA certification, no production SLOs. Findings are reported as measured evidence with stated methodology and limits.

---

## 10. Execution plan once Decision A is resolved

| Step | Work | Exit |
|---|---|---|
| 1 | Resolve toolchain (Decision A); record ADR | Baseline is unambiguous and recorded |
| 2 | Token layer v2 + theme switching + `next/font` | Gallery renders both themes, no flash |
| 3 | Migrate 395 color literals to tokens | Zero literals in `app/`, `components/` |
| 4 | Build ~36 primitives with full states | Gate 2 gallery passes both themes/locales |
| 5 | Role model + guards + role-aware shell | Gate 3 role×route matrix passes |
| 6 | Athlete core loop | Gate 4 criteria (§6) |
| 7 | Coach command center | Gate 5 criteria (§7) |
| 8 | Shared-surface polish; strip foundation copy | Zero Phase-04 strings on customer surfaces |
| 9 | A11y / i18n / perf / visual regression | Gate 7 evidence recorded |
| 10 | Report + PR (not merged) | Founder review |

Estimated surface: ~36 new components, ~14 new routes, 395 literal migrations, 2 theme definitions, 1 role/auth primitive, plus visual-regression tooling that does not exist yet.

---

## 11. Open questions for the founder

1. **Decision A (blocking)** — ratify Next 16, or revert to Next 14.2.35 and accept the reintroduced advisories? (audit §8)
2. **Phase 12 orphaned UI** — wire into routes, or formally defer as dead code? (recommend defer)
3. **Phase 08 "runtime correction"** — no artifact by that name exists; what does it refer to?
4. **Visual regression tooling** — none exists. Playwright screenshots are the natural fit but add a dev dependency; approve?
5. **Auth reality** — login/register are non-functional placeholders with no session backend wiring. Should the role model run on real authentication, or on a documented mock session provider for this track?
6. **Default theme** — dark for athletes and light for coach/owner administration, or a single global default with user override?
