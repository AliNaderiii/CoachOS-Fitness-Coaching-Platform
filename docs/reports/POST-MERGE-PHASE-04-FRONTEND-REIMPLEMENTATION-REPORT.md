# Post-Merge Phase 04 Frontend Reimplementation Report

**Date:** 2026-08-11 (UTC)
**Remediation type:** Founder-authorized, specification-based reimplementation
**Repository:** `AliNaderiii/CoachOS-Fitness-Coaching-Platform`
**Verified base on `main`:** `1c4a552ab86f6bca7b522492c8488614ae0d97de`
**Working branch:** `arena/019ff11c-coachos-fitness-coaching-platf`
**Clean-validated implementation commit:** `8c268db973530157fb1468bc1838f8bca59f7310`
**Original Phase 04 report:** [`PHASE-04-FOUNDATION-REPORT.md`](./PHASE-04-FOUNDATION-REPORT.md)

---

## 1. Correction Statement

After Phase 04 was merged through PR #7, the nine `frontend/lib/` files listed in the original Phase 04 report were not present in the resulting `main` tree. The repository's broad Python-oriented `lib/` ignore rule had hidden the untracked frontend directory during the original delivery. An audit of reachable Git history, PR #7 metadata, local candidates, and recoverable Git objects did not locate authoritative original source for those files.

The founder explicitly authorized a **specification-based reimplementation**. This remediation therefore does **not** claim restoration, byte-for-byte recovery, original-source recovery, or behavior-for-behavior recovery. The implementation was derived independently from the tracked Phase 00–04 specifications, ADRs, UX copy, existing tests, and existing frontend call sites.

The original Phase 04 report has not been silently rewritten. This separate correction report records the provenance limitation, authorization, assumptions, implementation, tests, and validation evidence.

---

## 2. Scope and Boundaries

Exactly these missing implementation files were reimplemented:

1. `frontend/lib/config/env.ts`
2. `frontend/lib/i18n/config.ts`
3. `frontend/lib/i18n/dictionaries/fa-IR.json`
4. `frontend/lib/i18n/dictionaries/en-US.json`
5. `frontend/lib/i18n/formatters.ts`
6. `frontend/lib/i18n/normalizer.ts`
7. `frontend/lib/i18n/bidi.ts`
8. `frontend/lib/api/client.ts`
9. `frontend/lib/pwa/register-sw.ts`

The remediation also includes focused tests, the narrow `.gitignore` correction required to track `frontend/lib/`, this report, and narrow updates to `PROJECT_STATUS.md`, `PROJECT_CHECKLIST.md`, `CHANGELOG.md`, and `docs/PROMPT_LOG.md`.

No Phase 05 domain code, authentication flow, tenancy model, role system, exercise/program/workout functionality, durable offline queue, IndexedDB synchronization, notification feature, wearable integration, payment feature, AI feature, dependency upgrade, or GitHub Actions workflow activation is included.

---

## 3. Specification and Contract Sources

The reimplementation treated tracked tests and call sites as hard contracts and used these primary specifications:

- `docs/DECISIONS.md` — ADR-003, ADR-009, ADR-018, ADR-045, ADR-046, and ADR-047.
- `docs/architecture/SECURITY_FOUNDATION.md` — public/private configuration boundary, cookie-session CSRF transport, request correlation, and sanitized error handling.
- `docs/architecture/PWA_FOUNDATION.md` — Level 1 service-worker boundary and SSR-safe registration.
- `docs/architecture/PHASE04_FOUNDATION_DECISIONS.md` — Phase 04 frontend foundation decisions.
- `docs/ux/UX_COPY.md` — current bilingual UI strings.
- Existing frontend imports and tests under `frontend/app/`, `frontend/components/`, and `frontend/tests/`.
- `infra/scripts/check-secrets.sh` and `infra/ci/*.yml` as local quality-gate command references only; no workflow activation was performed.

---

## 4. Recorded Implementation Assumptions

Because authoritative original source was unrecoverable, the following decisions were necessary and are explicit:

1. **Locale governance:** supported locales are exactly `fa-IR` and `en-US`; `fa-IR` is the default; metadata is Persian/RTL and English/LTR; no fallback or Arabic locale is created.
2. **Dictionary inventory:** dictionaries cover the current tracked shell and placeholder call sites. They contain 54 matching, non-empty leaf keys. A governance test enumerates every current tracked UI key rather than relying only on key-count parity.
3. **Date display:** timestamps are parsed as ISO input and rendered from UTC calendar parts to avoid host-timezone drift. `fa-IR` uses deterministic algorithmic Gregorian-to-Jalali display; `en-US` uses deterministic Gregorian month names. Invalid source dates and invalid Gregorian date parts raise `RangeError` rather than being normalized silently.
4. **Number display:** only finite numbers are accepted. Persian display uses Persian digits and `fa-IR`; English display uses `en-US`. Weight formatting supports only `kg` and `lbs`.
5. **Persian search normalization:** Unicode NFKC normalization, Arabic keyboard-variant folding (`ي`/`ى` to `ی`, `ك` to `ک`), Arabic-Indic digit folding, diacritic removal, trimming, and whitespace collapse are applied. ZWNJ is preserved by default to match the existing frontend contract and may be removed explicitly.
6. **BiDi handling:** Unicode First Strong Isolate and Pop Directional Isolate are used around mixed-direction dynamic values. The prescription helper is intentionally minimal and is not a workout-domain implementation.
7. **Public configuration:** frontend source reads only the two explicit public variables it needs: `NEXT_PUBLIC_API_BASE_URL` and `NEXT_PUBLIC_APP_NAME`. Safe non-public process metadata such as `NODE_ENV` is accepted by the standalone validator, while private/secret-like keys and credential-bearing API URLs are rejected without echoing values.
8. **API base URL:** `/api/v1` is the safe relative default. Configuration may be relative or an HTTP(S) URL without embedded credentials. Individual request paths are resolved below the configured base, and external absolute request paths are not accepted.
9. **API transport:** browser cookies are included; `Accept-Language` is always sent; an explicitly supplied request ID is forwarded as `X-Request-ID`; when that header is absent, the backend `CorrelationIDMiddleware` generates and returns the correlation ID. The frontend client does not generate a request ID. A caller-supplied idempotency key is sent only when explicitly provided; no idempotency key is generated automatically.
10. **CSRF:** the readable Django `csrftoken` cookie is decoded and sent as `X-CSRFToken` only for unsafe methods. No access token, refresh token, or secret is stored in `localStorage` or `sessionStorage`.
11. **Problem Details:** non-success responses become typed `ApiError` instances. Only bounded, expected RFC 7807 fields and response request ID are copied; arbitrary server payloads, response bodies, stack traces, and secrets are not exposed.
12. **Service-worker registration:** registration occurs only when called in a browser that exposes `navigator.serviceWorker`; it registers `/sw.js` with scope `/`, returns `null` on unsupported/error paths, and adds no logging or advanced background behavior.
13. **Dependency posture:** the existing lockfile is authoritative for this correction. Dependency upgrades and the audit findings emitted by `npm ci` are out of this narrow remediation scope.

---

## 5. Implementation Summary

### 5.1 Public environment boundary

`frontend/lib/config/env.ts` provides a standalone `validatePublicEnv` guard and an immutable public configuration object. It prevents private key access, detects secret-like public key names, rejects credential-bearing URLs, does not include secret values in error messages, and reads only explicit statically analyzable `NEXT_PUBLIC_*` names.

### 5.2 Locale metadata and dictionaries

`frontend/lib/i18n/config.ts` defines exact locale types, metadata, default locale, validation, and direction lookup. The Persian and English dictionaries parse as JSON, have matching structures, provide non-empty values for all current tracked call sites, and add no Arabic resource.

### 5.3 Formatters, normalization, and BiDi isolation

The i18n helpers provide finite number/weight formatting, strict UTC-derived Gregorian and Jalali display, Persian keyboard/digit/diacritic normalization with explicit ZWNJ behavior, and Unicode isolation for mixed Persian/Latin content.

### 5.4 Minimal API client

`frontend/lib/api/client.ts` is a typed foundation wrapper around `fetch`. It includes locale, forwarding of explicitly supplied request IDs, exposure of backend response request IDs, optional explicit idempotency, readable CSRF cookie handling for unsafe methods, JSON request/response support, `credentials: "include"`, and bounded RFC 7807 error sanitization. It does not implement authentication or any Phase 05 domain API.

### 5.5 Service-worker registration

`frontend/lib/pwa/register-sw.ts` is SSR-safe and unsupported-browser-safe. It registers only `/sw.js` with scope `/` and silently returns `null` if registration cannot be completed.

### 5.6 Git tracking correction

The root `lib/` ignore rule is retained. Only these exceptions were added:

```gitignore
!/frontend/lib/
!/frontend/lib/**
```

This is the narrowest repository-root exception needed to track the authorized TypeScript source while preserving the general Python `lib/` ignore behavior.

---

## 6. Tests Added or Expanded

- **New `frontend/tests/api-client.test.ts` — 5 tests:** GET locale/request-ID/credentials behavior; unsafe-method CSRF and explicit idempotency; cookie decoding; JSON success handling; bounded RFC 7807 error sanitization and secret non-disclosure.
- **New `frontend/tests/register-sw.test.ts` — 3 tests:** unsupported environment; exact successful registration; safe registration failure.
- **Expanded `frontend/tests/config.test.ts`:** private-key matrix, secret-value non-disclosure, and credential-bearing API URL rejection while retaining safe-value behavior.
- **Expanded `frontend/tests/formatters.test.ts`:** timezone-boundary UTC behavior plus malformed/impossible date rejection.
- **Expanded `frontend/tests/normalizer.test.ts`:** default ZWNJ preservation, explicit ZWNJ removal, trimming, and whitespace collapse.
- **Expanded `frontend/tests/i18n.test.ts`:** exact locale metadata plus exhaustive governance for all 54 current tracked bilingual UI keys and non-empty values.
- Existing BiDi, component, PWA, security-header, and no-Arabic tests remain unchanged and passing.

Initial remediation clean-validation result at implementation commit `8c268db973530157fb1468bc1838f8bca59f7310`: **11 test files passed; 49 tests passed; 0 failed**.

---

## 7. Clean Tracked-Only Validation Evidence

A detached clean worktree was created from implementation commit `8c268db973530157fb1468bc1838f8bca59f7310`. Its initial and post-validation `git status --short` output was empty; implementation and test inputs therefore came only from tracked files.

| Gate | Command / audit | Result |
|---|---|---|
| Frontend install | `npm ci` | PASS — 562 packages installed from lockfile |
| Frontend lint | `npm run lint` | PASS — no ESLint warnings/errors |
| Frontend types | `npm run type-check` | PASS — zero TypeScript errors |
| Frontend tests | `npm test` | PASS — 11 files, 49 tests |
| Frontend build | `npm run build` | PASS — compiled; 18 static pages generated |
| Backend tests | `pytest` | PASS — 37 tests |
| Backend lint/format | `ruff check .` and `ruff format --check .` | PASS — 36 files already formatted |
| Repository compliance | `bash infra/scripts/check-secrets.sh` | PASS — secrets, Arabic resources, public-env file, and manifest checks |
| Dictionary governance | tracked-only JSON parse/flatten audit | PASS — exactly 2 dictionaries; 54 matching non-empty leaves |
| Public-env governance | tracked-only `git grep` | PASS — exactly 2 reads, both explicit `NEXT_PUBLIC_*`; no browser storage APIs |
| PWA scope | tracked-only registration/forbidden-feature scan | PASS — exact `/sw.js` + `/`; no IndexedDB, sync, push, notifications, queues, or wearables |
| Language resources | tracked-file path audit | PASS — no Arabic locale resource |
| Workflow separation | base-to-implementation file audit | PASS — no `.github/workflows/` change |
| Whitespace | `git diff --check 1c4a552...HEAD` | PASS |
| Ignore behavior | `git check-ignore` plus `--no-index -v` diagnostics | PASS — tracked file not reported ignored; explicit negation matched |
| Tracked source audit | `git ls-files frontend/lib` | PASS — exactly the 9 authorized files |

`npm ci` also reported 10 dependency audit findings (3 moderate, 6 high, 1 critical) from the existing locked dependency graph. This remediation neither introduced nor upgrades dependencies; dependency remediation requires a separately reviewed dependency/security task.

A preliminary governance command incorrectly expected 55 dictionary leaves and failed on the actual count of 54. The tracked-key inventory and exhaustive test both establish 54 as the correct current contract; the corrected audit passed without changing product code or inventing an unused key.

---

## 8. Source-Control and Remote Evidence

- Verified `origin/main` before implementation and before commit: `1c4a552ab86f6bca7b522492c8488614ae0d97de`.
- Merge base with the remediation branch at start: `1c4a552ab86f6bca7b522492c8488614ae0d97de`.
- Clean-validated implementation commit: `8c268db973530157fb1468bc1838f8bca59f7310`.
- Documentation is intentionally recorded in a follow-up commit so this report can cite the already clean-validated implementation tree.
- The remediation is to be pushed only from `arena/019ff11c-coachos-fitness-coaching-platf` and opened as a PR targeting `main`.
- The PR must remain unmerged pending founder review. Remote branch, file-list, commit, and PR evidence are release-process evidence and do not convert this work into an original-source restoration.

---

## 9. Risks and Deferred Work

1. Original source provenance remains unavailable; this is an independently reviewed specification-based implementation.
2. Browser-level service-worker lifecycle behavior is unit-tested at the registration boundary but is not an end-to-end browser test in this correction.
3. Existing dependency audit findings require a separate dependency review; forced or breaking upgrades are intentionally excluded.
4. GitHub Actions are not active in this remediation. `infra/ci/` remains command-reference material; workflow activation requires a separate PR and appropriate GitHub Workflows permission.
5. Phase 05 remains blocked pending explicit founder authorization after this remediation is reviewed and merged.

---

## 10. Required Next Step

1. Push this remediation branch.
2. Open one narrowly scoped PR targeting `main`.
3. Verify remote commit and the nine `frontend/lib/` paths.
4. Leave the PR open; do not merge automatically.
5. Do not activate workflows or begin Phase 05 in this PR.
