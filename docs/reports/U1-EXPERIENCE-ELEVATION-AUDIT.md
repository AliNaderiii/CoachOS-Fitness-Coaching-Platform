# U1 — Experience Elevation and Design System v2 — Gate 0 Audit

**Status:** ⛔ **BLOCKED AT PREFLIGHT — EXPERIENCE TRACK NOT STARTED**
**Audit date:** 2026-08-19 (UTC)
**Auditor:** Experience Elevation track, Gate 0 (repository and product audit)
**Verified remote `main` SHA:** `6722d5fefc92262334d53200f8be2b010487eb60`
**Working branch:** `arena/01a0193c-coachos-fitness-coaching-platf`
**Scope of this document:** Read-only audit. **No application source code was modified.**

---

## 0. Executive summary

The mandatory preflight gate defined by the U1/U2 prompt **fails**. The prompt states:

> Verify whether the approved frontend baseline has been restored. The historical approved baseline is: Next.js 14.2.35 / Vitest 1.6.0 / ESLint 8 / `frontend/.eslintrc.json`.
> **If the unapproved Next.js 16/Vitest 3/ESLint 9 migration is still present, stop the experience track and report it.**

The unapproved migration **is still present on `main`**. Per the founder's own instruction, the experience track is stopped at Gate 0 and reported rather than started. No visual, token, shell, or component work has been performed.

A second, independent finding: `PROJECT_STATUS.md` is materially inaccurate and must not be used as a design contract without reconciliation (the prompt anticipated this).

| Preflight requirement | Result |
|---|---|
| Record actual current remote `main` SHA | ✅ `6722d5fefc92262334d53200f8be2b010487eb60` |
| Verify post-parallel-wave stabilization and merge commits | ⚠️ Merged, but **stabilization was silently reverted** (§2) |
| Reconcile `PROJECT_STATUS.md` against reality | ❌ **Inaccurate** (§3) |
| Approved frontend baseline restored (Next 14.2.35 / Vitest 1.6 / ESLint 8 / `.eslintrc.json`) | ❌ **NO — blocker** (§1) |
| Phase 08 runtime correction verified | ⚠️ **No such artifact exists** (§3.3) |
| Phase 12 OpenAPI/test discovery verified | ❌ **Phase 12 UI is 100% orphaned; tests undiscoverable** (§4) |
| Work in isolated clone/worktree, never write to `main` | ✅ Working branch only; `main` untouched |

---

## 1. BLOCKER — unapproved frontend toolchain migration is present

### 1.1 Observed state on `main` (`6722d5f`)

`frontend/package.json` at the verified remote `main` SHA:

| Dependency | Approved baseline | **Actual on `main`** | Verdict |
|---|---|---|---|
| `next` | `14.2.35` | **`16.3.1`** | ❌ Unapproved major migration |
| `vitest` | `^1.6.0` | **`^3.2.7`** | ❌ Unapproved major migration |
| `eslint` | `^8.57.0` | **`^9.39.5`** | ❌ Unapproved major migration |
| `eslint-config-next` | `14.x` | **`^16.3.1`** | ❌ |
| `vite` | (not a direct dep) | **`^7.3.6`** | ❌ Added |
| ESLint config file | `frontend/.eslintrc.json` | **`frontend/eslint.config.mjs`** (flat config) | ❌ Replaced |
| `lint` script | `next lint` | **`eslint . --max-warnings=0`** | ❌ Replaced |

Verification commands:

```
$ git rev-parse origin/main
6722d5fefc92262334d53200f8be2b010487eb60

$ ls frontend/.eslintrc.json
ls: cannot access 'frontend/.eslintrc.json': No such file or directory
```

`frontend/eslint.config.mjs` (present on `main`) additionally **disables a React correctness rule** to make the new toolchain pass:

```js
// Existing async loaders and timers intentionally initialize state in effects.
rules: { "react-hooks/set-state-in-effect": "off" },
```

### 1.2 This is a *regression of an already-completed correction*

This is the aggravating finding. The same migration was previously caught and reverted under an explicit standing policy. `CHANGELOG.md` line 66 records:

> **Review correction:** removed the unapproved Next.js/ESLint/Vitest/Vite/TypeScript/jsdom migration and lockfile rewrite. Restored the Phase 05 frontend package manifest, lockfile, `.eslintrc.json`, `next lint`, TypeScript config […]; removed the ESLint 9 flat config and all rule overrides. […] **Any toolchain migration requires a separate proposal and PR.**

The migration then **returned** during the parallel 08–12 wave. Commit-level bisect of `main`:

| Commit (chronological) | PR | `next` version |
|---|---|---|
| `13c70a3622` docs(phase-08) | #19 lineage | `14.2.35` |
| **`2b2d47d5d7` feat: add Phase 10 organization billing foundation** | **#20** | **`16.3.1` ← migration reintroduced here** |
| `52f8f4bdaf` docs: record Phase 10 PR validation evidence | #20 | `16.3.1` |
| `8c1106a57b` Merge PR #20 | #20 | `16.3.1` |
| `6005936ab5` Merge PR #21 (Phases 11+12) | #21 | `14.2.35` (baseline still intact on this line) |
| `74c671a614` merge: integrate main (Phases 11-12) into Phase 08 branch | #19 | `14.2.35` |
| `706d83ce00` merge: integrate main (Phase 10 via PR #20) into Phase 08 branch | #19 | **`16.3.1` ← re-applied by merge** |
| `326babce7b` Merge PR #19 | #19 | `16.3.1` |
| `6722d5fefc` Merge PR #22 (**current `main`**) | #22 | **`16.3.1`** |

**Origin: PR #20 (Phase 10 billing).** It was not hidden — PR #20's own description declares it:

> "Dependency-security remediation to zero npm audit findings (Next 16.3.1, Vitest 3.2.7, Vite 7.3.6, ESLint 9 migration)."

A billing-scoped PR performed a frontend major-version migration, contrary to the standing "separate proposal and PR" policy. The concurrent merge topology then propagated it into `main` through PR #19's back-merge, past the Phase 11/12 line that had correctly preserved the baseline.

### 1.3 The genuine trade-off the founder must decide

This is **not** a simple "revert it" call. PR #20's stated motivation is real and verified. Measured in this sandbox:

**Current `main` (Next 16 / Vitest 3 / ESLint 9):**
```
$ npm audit --audit-level=low
found 0 vulnerabilities
```

**Approved baseline (Next 14.2.35 / Vitest 1.6 / ESLint 8), restored from `6005936` and audited:**
```
10 vulnerabilities (3 moderate, 6 high, 1 critical)
```

| Severity | Package | Advisory summary |
|---|---|---|
| **CRITICAL** | `vitest` <=3.2.5 | RCE when a malicious website is visited while the Vitest API server is listening; arbitrary file read/execute via UI server |
| HIGH | `next` 9.3.4-canary.0 – 16.3.0-preview.10 | DoS via Image Optimizer `remotePatterns`; HTTP request smuggling in rewrites; RSC deserialization DoS |
| HIGH | `vite` <=6.4.2 | Path traversal in optimized-deps `.map` handling; `server.fs.deny` bypass |
| HIGH | `postcss` <=8.5.22 | XSS via unescaped `</style>`; arbitrary `.map` file read via `sourceMappingURL` |
| HIGH | `glob` 10.2.0–10.4.5 | Command injection via `-c/--cmd` |
| HIGH | `eslint-config-next`, `@next/eslint-plugin-next` | transitive via `glob` |
| MODERATE | `esbuild`, `vite-node`, `@vitejs/plugin-react` | dev-server request forgery; transitive |

Most are **development-time** exposures (Vitest/Vite/esbuild/glob), not production runtime. The `next` and `postcss` entries are the ones with production-adjacent surface. A blind revert to the approved baseline **reintroduces a critical-severity dev-toolchain advisory**. That is exactly why this needs a founder decision rather than an autonomous fix in either direction.

### 1.4 Current toolchain gate status (measured, this sandbox)

The unapproved toolchain is *not* visibly broken — it passes every gate:

```
frontend: npm ci        → 523 packages, 0 vulnerabilities
frontend: npm run lint  → pass (eslint . --max-warnings=0)
frontend: npm run type-check → pass (tsc --noEmit, strict)
frontend: npm test      → 18 files, 153 tests passed
frontend: npm run build → pass (all fa-IR/en-US routes prerendered)
backend:  ruff check .        → All checks passed!
backend:  ruff format --check → 150 files already formatted
backend:  pytest --cov        → 369 passed, 87% coverage
infra:    check-secrets.sh    → ALL COMPLIANCE CHECKS PASSED
git diff --check              → clean
docker compose config         → not verifiable (docker unavailable in sandbox)
```

So the risk is **governance and stability-of-record**, not a red build. The prompt's concern stands regardless: a large design-system track must not be built on a toolchain whose approval status is contested and which was reverted once already. If the founder authorizes Next 16, the authorization should be explicit and recorded so this cannot silently flip a third time.

---

## 2. Stabilization state verification

All parallel-wave PRs are merged; post-merge checks on current `main` are green.

| PR | Title | Merge SHA | State |
|---|---|---|---|
| #19 | Phase 08 — communication and notifications | `326babce7b` | MERGED |
| #20 | Phase 10 — organization billing | `8c1106a57b` | MERGED (**introduced the migration**) |
| #21 | Phase 11 + Phase 12 | `6005936ab5` | MERGED |
| #22 | docs: post-merge Phase 11 status sync | `6722d5fefc` | MERGED — **current `main`** |

Check runs on `6722d5fefc` — all `success`:
`Backend Lint, Type & Tests`, `Frontend Lint, Type & Tests`, `Security Scan & Language Compliance`, `Secret & Pattern Scanning`, `build`, `deploy`, `report-build-status`.

**Conclusion:** the wave is merged and CI-green, but "stabilized" is not accurate — the accepted stabilization (baseline restoration) was reverted in transit and nobody noticed, because the replacement toolchain also passes CI.

---

## 3. `PROJECT_STATUS.md` reconciliation — inaccurate

The prompt instructed: *"Do not assume that `PROJECT_STATUS.md` is accurate."* Confirmed inaccurate.

### 3.1 Wrong base commit
States **Base commit (main):** `326babce7bcfaae9e1c7d5f04e7d059e2e00af93`. Actual `main` is `6722d5fefc…`. The document describes `326babce` as "verified current remote `main`", which was true only momentarily during the concurrent wave.

### 3.2 Wrong test counts (under-reported by >2x)

| Metric | `PROJECT_STATUS.md` claim | Measured actual | Delta |
|---|---|---|---|
| Backend tests | 167 | **369** | +202 |
| Backend coverage | 86% | **87%** | +1pt |
| Frontend tests | 84 | **153** | +69 |

The status file reports only the Phase 11 session's view; Phases 08/10/12 test contributions were never aggregated (the file itself admits per-phase syncs "may still be pending").

### 3.3 Stale/absent toolchain and correction records
- Line 84 still describes the frontend as **"Next.js 14.2 App Router"** — contradicting the shipped `next@16.3.1`. The status file therefore *documents the approved baseline while the repository ships the unapproved one.*
- **Phase 08 "runtime correction":** the prompt asks to verify this before treating it as a design contract. A repository-wide search for `runtime correction` / `runtime-correction` across `docs/`, `PROJECT_STATUS.md`, and `CHANGELOG.md` returns **zero matches**. No such artifact exists under that name. It cannot be used as a design contract; it must be located, renamed, or declared nonexistent by the founder.

---

## 4. Phase 12 UI is entirely orphaned

The prompt requires: *"all Phase 12 UI that is not wired to active routes must be connected or explicitly deferred."* Current state: **none of it is wired**.

Phase 12 shipped a parallel `frontend/src/` tree that no active route imports.

| File | Imported by active app? |
|---|---|
| `src/components/conflict/OfflineConflictResolution.tsx` | ❌ 0 references |
| `src/components/integration/IntegrationWorkspace.tsx` | ❌ 0 references |
| `src/components/integration/IntegrationStatus.tsx` | ❌ 0 references |
| `src/components/integration/IntegrationErrorBanner.tsx` | ❌ 0 references |
| `src/components/integration/IntegrationProvenance.tsx` | ❌ 0 references |
| `src/components/integration/IntegrationSyncProgress.tsx` | ❌ 0 references |
| `src/components/offline/OfflineQueueDetails.tsx` | ❌ 0 references |
| `src/components/offline/OfflineStatusBanner.tsx` | ❌ 0 references |
| `src/lib/indexeddb/offlineQueueSchema.ts` | ❌ 0 references |

Verified: `grep -rn "@/src|src/components|src/lib" app components lib tests` → **no matches**.

**Test discovery gap:** `vitest.config.ts` uses `include: ["tests/**/*.test.{ts,tsx}"]`, and `find frontend/src -name "*.test.*"` returns **0** files. The entire `src/` tree is both unreachable at runtime and untested — it is dead code that nonetheless passes lint, type-check, and build. Phase 12's own report concedes its automated suite "relies on manual review."

This directly contradicts treating Phase 12 as a usable design contract for offline/PWA states in Gate 6.

---

## 5. Product-surface audit (confirms every issue the prompt listed)

Read-only inspection of the live frontend. Every problem named in the prompt is reproduced and located.

### 5.1 Route inventory (21 route files, all under `app/[locale]/`)

| Route | Role intent | Notes |
|---|---|---|
| `/[locale]` | public | Architecture status page, not a product entry (§5.2) |
| `/[locale]/login`, `/register` | anonymous | Inputs **disabled**; "Phase 04 Foundation Shell" badge |
| `/[locale]/athlete/today` | athlete | Core loop start |
| `/[locale]/athlete/workout/[sessionId]` | athlete | Dynamic (ƒ) |
| `/[locale]/athlete/progress` | athlete | |
| `/[locale]/coach/programs` | coach | |
| `/[locale]/coach/copilot` | coach | |
| `/[locale]/messages`, `/messages/[conversationId]` | athlete+coach | Shared, no role separation |
| `/[locale]/notifications` | all | |
| `/[locale]/settings/notifications` | all | |
| `/[locale]/org/settings` | owner | "Phase 04 Foundation Shell" badge |
| `/[locale]/org/billing` | owner | |
| `/[locale]/offline`, `error`, `loading`, `not-found` | system | |

**Missing vs. target journeys:** no coach `Overview`, no `Roster`/athlete-context route, no `Calendar`, no `Reports`, no athlete `Plan`, no athlete `Profile`, no workout `Completion` screen, no owner `Members/Access`. The coach command center (Gate 5) has essentially no route surface today.

### 5.2 Stale foundation copy on customer-facing surfaces — confirmed

| Location | Content |
|---|---|
| `app/[locale]/page.tsx:43` | `t("app.foundation_badge")` → "Phase 04 Foundation" / "زیرساخت فاز ۰۴" |
| `app/[locale]/page.tsx:73` | "Architecture Foundation Status Grid" section |
| `app/[locale]/page.tsx` | Status cards reading "Next.js 14 App Router • TypeScript Strict • Logical CSS", "Django 5 DRF • /healthz • /readyz", etc. — **also factually wrong now** (ships Next 16) |
| `app/[locale]/(auth)/login/page.tsx:24` | Badge "Phase 04 Foundation Shell" |
| `app/[locale]/(auth)/register/page.tsx:24` | Badge "Phase 04 Foundation Shell" |
| `app/[locale]/(app)/org/settings/page.tsx:24` | Badge "Phase 04 Foundation Shell" |
| `en-US.json` / `fa-IR.json` | `app.foundation_badge`, `home.welcome_title` ("CoachOS foundation is ready"), `home.status_*`, `home.placeholder_notice`, `auth.placeholder_warning`, `nav.*_desc` ("Foundation shell for the future…"), `errors.not_found_description` ("…in this foundation shell") |

The homepage is an engineering status board presented to customers, and the login form is non-functional by design.

### 5.3 Navigation is not role-aware — confirmed

`components/layout/BottomNav.tsx` renders **7 mobile items** mixing three roles:

`Today` (athlete) · `Progress` (athlete) · `Notifications` (all) · `Programs` (**coach**) · `Copilot` (**coach**) · `Messages` (all) · `Profile → /org/settings` (**owner**)

This violates the prompt's constraint (max 4–5 athlete items) three ways: too many items, mixed-role leakage, and "Profile" deep-linking an athlete into **organization settings**. `components/layout/Header.tsx` has the same problem on desktop — it renders coach, Copilot, org, and billing links unconditionally.

There is **no role/session model in the frontend at all**: `grep -rn "role|session|auth" lib/ components/layout/` returns nothing, and `lib/api/client.ts` carries no role concept. Role-aware navigation (Gate 3) requires building this primitive from scratch.

### 5.4 Theming is dark-only — confirmed

`app/[locale]/layout.tsx` hard-codes `<html className="dark">` and `<body className="bg-obsidian-950 …">`. `styles/tokens.css` defines a **single** `:root` block of dark values with **no light theme and no `[data-theme]`/`.light` scope**, despite `docs/ux/DESIGN_TOKENS.md` §1.2 specifying full light-theme values. Tailwind is set to `darkMode: "class"` but nothing ever toggles it. No theme persistence, no `prefers-color-scheme` handling.

### 5.5 Hard-coded colors bypass tokens — confirmed

**395 raw color literals** across `app/`, `components/`, `src/` (`obsidian-950`, `emerald-500`, `#0B0F17`, etc.):

| File | Count |
|---|---|
| `components/copilot/CopilotResultCard.tsx` | 37 |
| `components/copilot/CopilotConsole.tsx` | 30 |
| `components/billing/BillingWorkspace.tsx` | 25 |
| `src/components/offline/OfflineQueueDetails.tsx` | 20 |
| `components/training/TrainingWorkspace.tsx` | 20 |
| `components/messaging/ConversationView.tsx` | 18 |
| `components/athlete/SetLogger.tsx` | 16 |
| …plus 18 more files | remainder |

A light theme is **impossible** until these are migrated to semantic tokens. This is the single largest mechanical work item in Gate 2.

### 5.6 Component library gaps — confirmed

Implemented primitives: `Badge`, `Button`, `Card`, `Input`, `Modal`, `LanguageSwitcher` (**6 total**).

Required by Gate 2 but **absent**: `AppShell`, `RoleShell`, `NavigationRail`, `MobileNav` (role-aware), `PageHeader`, `Breadcrumbs`, `ContextSwitcher`, `IconButton`, `LinkButton`, `Surface`, `StatCard`, `Tabs`, `SegmentedControl`, `Select`, `Combobox`, `Textarea`, `NumberInput`, `DateRange`, `Drawer`, `BottomSheet`, `ConfirmDialog`, `Toast`, `Alert`, `InlineError`, `Skeleton`, `EmptyState`, `ErrorState`, `ForbiddenState`, `DataTable`, `Timeline`, `ActivityFeed`, `ProgressRing`, `ProgressBar`, `LineChart`/`BarChart`, `Avatar`, `StatusDot`, `AttentionIndicator`. **~36 components to build.**

### 5.7 Invalid DOM nesting: `<bdi>` inside `<option>` — confirmed, exactly one instance

`components/copilot/CopilotConsole.tsx:278`

```jsx
<option key={assignment.id} value={assignment.athlete_user_id}>
  <bdi dir="ltr">{assignment.athlete_user_id}</bdi>
</option>
```

`<option>` accepts text only; browsers strip the element and BiDi isolation is silently lost. All other 30 `<bdi>` usages in the codebase are correctly placed. Fix is to drop the wrapper and isolate via Unicode control characters (U+2068/U+2069) or `dir` on the `<select>`.

### 5.8 Font loading policy — confirmed risk

`styles/globals.css` imports both webfonts over the network at CSS parse time:

```css
@import url("https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css");
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");
```

Render-blocking, third-party dependent, **offline-hostile in a PWA**, no `next/font`, no self-hosting, no explicit `font-display` for Vazirmatn, and a layout-shift source. The CSP does permit `https:` font/style sources, so it functions online — but a PWA whose Persian typeface fails offline is a direct contradiction of the product's offline posture.

### 5.9 Positives worth preserving

- **Locale dictionaries are at exact parity: 528 keys in each of `en-US.json` and `fa-IR.json`, zero asymmetry** (verified by flattened key-set diff). Excellent foundation for Gate 7.
- No Arabic resources; `check-secrets.sh` language compliance passes.
- Logical CSS properties (`-ms-`/`-me-`) already used in layout code.
- `--touch-target-min: 44px` / `48px` tokens already defined.
- `:focus-visible` outline defined globally.
- Backend is genuinely healthy: 369 tests, 87% coverage, clean ruff.

---

## 6. Role × route access matrix (as-built vs. required)

`A` = athlete, `C` = coach, `O` = owner, `S` = support, `—` = no access. "As-built" reflects that **no authorization exists in the frontend**: every route is reachable by anyone with the URL.

| Route | Required | As-built | Gap |
|---|---|---|---|
| `/` | public | public | Content wrong (§5.2) |
| `/login`, `/register` | anonymous | anonymous | Non-functional |
| `/athlete/today` | A | **anyone** | No guard |
| `/athlete/workout/[id]` | A (own) | **anyone** | No guard |
| `/athlete/progress` | A, C (consent-gated), O (audited) | **anyone** | No guard, no consent surface |
| `/coach/programs` | C, O | **anyone incl. athlete** | ❌ Leak; in athlete bottom nav |
| `/coach/copilot` | C, O | **anyone incl. athlete** | ❌ Leak; in athlete bottom nav |
| `/messages` | A, C | **anyone** | No scoping |
| `/notifications` | all authed | anyone | — |
| `/org/settings` | O | **anyone incl. athlete** | ❌ Leak; it is the athlete "Profile" tab |
| `/org/billing` | O | **anyone** | ❌ Leak |

**Unrepresented states:** suspended, wrong-tenant, support-role, and forbidden have **no UI treatment whatsoever**. Gate 3 requires all seven.

---

## 7. What I did not do, and why

Per the prompt's stop instruction, I did **not**:

- create the `experience/elevation-design-system-v2` branch or open a PR;
- write or modify any application source, token, component, or route;
- touch `PROJECT_STATUS.md`, `PROJECT_CHECKLIST.md`, `CHANGELOG.md`, or `docs/PROMPT_LOG.md`;
- run the full principal-role review board (Gates 1–8 are not reachable from a failed Gate 0);
- make any WCAG, GDPR, HIPAA, PWA, or performance certification claim.

Only the two Gate 0 audit documents named in the prompt were created.

**Branch-discipline note:** the prompt asks for a branch named `experience/elevation-design-system-v2`. This Arena session is bound to `arena/01a0193c-coachos-fitness-coaching-platf` and work on any other branch would be disassociated from the session. When the track is authorized, implementation will proceed on the session branch, and the PR will carry the intended name/description. `main` has not been written to.

---

## 8. Founder decision required

The experience track cannot start until **Decision A** is resolved. B–D can be answered alongside it.

### Decision A — frontend toolchain (blocking)

| Option | Action | Consequence |
|---|---|---|
| **A1. Ratify Next 16** | Formally approve `next@16.3.1` / `vitest@3.2.7` / `eslint@9` + flat config as the new baseline; record an ADR + CHANGELOG entry; separately review the disabled `react-hooks/set-state-in-effect` rule | 0 npm audit findings retained; no rework; policy debt is settled explicitly. **Recommended** |
| **A2. Revert to approved baseline** | Restore Next 14.2.35 / Vitest 1.6 / ESLint 8 / `.eslintrc.json` / `next lint` in a dedicated stabilization PR | Honors original policy, but **reintroduces 10 advisories incl. 1 critical (Vitest RCE)**; requires re-validating Phases 10/12 UI against Next 14 |
| **A3. Ratify + harden** | A1, plus re-enable the disabled lint rule and fix the underlying effects | Cleanest end state; adds scope before design work starts |

My recommendation is **A1**. The migration's security rationale is verified and real, the toolchain passes every gate, and reverting would knowingly reintroduce a critical advisory. The defect is the *process* (a billing PR silently changing the frontend baseline), which is corrected by recording the decision — not by undoing a security improvement.

### Decision B — Phase 12 orphaned UI
Wire `frontend/src/**` into real routes as part of Gate 6, **or** explicitly defer and mark it dead code. Recommend **defer + document**; wiring it is a feature-scope expansion this track disallows.

### Decision C — Phase 08 "runtime correction"
No artifact by that name exists. Confirm whether it is the Phase 08 report itself, a differently-named correction, or a nonexistent reference.

### Decision D — docs synchronization
`PROJECT_STATUS.md` misstates base SHA, test counts, and the frontend framework version. A docs-only sync PR is needed. Exact proposed entries are held in `U1-EXPERIENCE-ELEVATION-CONTRACTS.md` §6 for that separate PR, per the prompt's tracking-file rule.

---

## 9. Proposed entries for the later docs-only synchronization PR

Held here for transcription into the tracking files by the assigned sync PR. **Not applied in this track.**

**`PROJECT_STATUS.md`:**
- Base commit (main) → `6722d5fefc92262334d53200f8be2b010487eb60` (PR #22 merge).
- Aggregate test evidence → backend **369 tests / 87% coverage**; frontend **153 tests / 18 files**.
- §Frontend Shell line 84 → replace "Next.js 14.2 App Router" with the ratified toolchain per Decision A.
- Add a "Toolchain baseline" row recording the Decision A outcome, its ADR, and the PR #20 origin of the change.
- Add Phase 12 UI wiring status per Decision B.

**`CHANGELOG.md`:**
- Under `[Unreleased] / Changed`: "Recorded that the frontend toolchain on `main` is Next.js 16.3.1 / Vitest 3.2.7 / ESLint 9 flat config, reintroduced by PR #20 (Phase 10) after the Phase 06 correction had restored the Next.js 14.2.35 baseline, and propagated to `main` via the PR #19 back-merge. Resolution recorded per founder Decision A."

**`PROJECT_CHECKLIST.md`:**
- Add U1 Gate 0 as complete (audit delivered, track blocked pending Decision A).
- Add a standing check: "frontend toolchain baseline verified against the approved/ratified version" to every future phase's gate list, to prevent a third silent flip.

**`docs/PROMPT_LOG.md`:**
- Log the U1/U2 Experience Elevation prompt, the Gate 0 preflight failure, the evidence, and the founder decision requested.

---

## 10. Evidence appendix — commands run

```bash
git fetch --all --prune
git rev-parse origin/main                    # 6722d5fefc92262334d53200f8be2b010487eb60
gh pr list --state all --limit 40
gh api .../commits?sha=main --jq ...         # merge topology, §2
gh api .../contents/frontend/package.json?ref=<sha>   # per-commit bisect, §1.2
gh api .../commits/6722d5f.../check-runs     # all success, §2
gh api .../pulls/20/files                    # migration origin, §1.2

cd frontend
npm ci                 # 523 packages, 0 vulnerabilities
npm run lint           # pass
npm run type-check     # pass
npm test               # 18 files / 153 tests passed
npm run build          # pass
npm audit              # 0 vulnerabilities (Next 16)
# baseline restored to /tmp/baseline from 6005936:
npm audit              # 10 vulns (3 moderate, 6 high, 1 critical) — §1.3

cd backend
ruff check .           # All checks passed!
ruff format --check .  # 150 files already formatted
pytest --cov=apps --cov=config   # 369 passed, 87% coverage

bash infra/scripts/check-secrets.sh   # ALL COMPLIANCE CHECKS PASSED
git diff --check                      # clean
docker compose config                 # docker unavailable in sandbox (not verified)
```

**No claim of WCAG, GDPR, HIPAA, PWA, or production SLO conformance is made anywhere in this document.**
