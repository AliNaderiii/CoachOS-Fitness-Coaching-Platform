# CI/CD Foundation Specification — CoachOS

**Document Version:** 1.0.0 (Phase 04 Baseline)  
**Date:** 2026-08-11 (UTC)  
**Target Platform:** GitHub Actions  
**Governing ADR:** ADR-039, ADR-044  

---

## 1. Objectives and Guardrails

The Phase 04 Continuous Integration (CI) foundation guarantees code quality, architectural consistency, and security boundaries on every Pull Request and commit to `main`.

### 1.1 Non-Negotiable CI Gates
1. **Frontend Verification:**
   - ESLint validation with zero errors.
   - TypeScript strict mode type-check (`tsc --noEmit`).
   - Vitest unit tests covering i18n, RTL/LTR layout direction, public config boundaries, BiDi isolation, and PWA registration.
   - Web App Manifest JSON schema validation.
   - Next.js production build verification (`npm run build`).
2. **Backend Verification:**
   - Ruff code linting and formatting verification.
   - Pytest test suite covering `/healthz`, `/readyz`, `/api/v1/meta`, RFC 7807 error envelopes, correlation ID middleware, security headers, UUIDv7 generation, and Persian text normalizer.
3. **Security & Secret Scanning:**
   - Automated secret scanning searching for private keys, AWS access credentials, database connection strings, JWT signing keys, and private tokens.
   - Frontend bundle check verifying zero private server environment variables are exposed in client builds.
4. **Localization & Language Governance:**
   - Strict Arabic exclusion check: Fails the build immediately if any Arabic locale file (`ar-*.json`, `ar.po`), Arabic route, or Arabic translation resource is introduced.
   - Bilingual parity check: Ensures all translation keys in `fa-IR.json` exist in `en-US.json` and vice versa.

---

## 2. GitHub Actions Workflow Architecture

```
.github/
└── workflows/
    ├── ci.yml               # Unified CI pipeline (Frontend, Backend, Security, i18n)
    └── security-scan.yml     # Secret scanning & dependency vulnerability audit
```

### 2.1 Pipeline Jobs Matrix

| Job Name | Runner | Triggers | Steps & Commands |
|---|---|---|---|
| `backend-quality` | `ubuntu-latest` | `push`, `pull_request` | Python 3.11 setup, cache pip, `ruff check .`, `pytest --cov` |
| `frontend-quality` | `ubuntu-latest` | `push`, `pull_request` | Node 22 setup, cache npm, `npm run lint`, `npm run type-check`, `npm test`, `npm run build` |
| `security-and-governance` | `ubuntu-latest` | `push`, `pull_request` | Secret pattern scan, Arabic file scan, translation key parity check |
| `pwa-validation` | `ubuntu-latest` | `push`, `pull_request` | Manifest validation, icon presence & dimensions check |

---

## 3. Secret and Deployment Separation

- **Zero Cloud Credentials in Git:** The repository contains no real API keys, tokens, or infrastructure passwords.
- **Workflow Placeholders:** Staging deployment jobs (when activated in future phases) will utilize OpenID Connect (OIDC) federated role assumptions rather than static long-lived credentials.
- **No Production Deploy in Phase 04:** Production releases remain blocked behind a manual approval gate and founder authorization.
