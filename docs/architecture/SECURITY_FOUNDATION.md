# Security Foundation Specification — CoachOS

**Document Version:** 1.1.0 (Phase 04 Baseline — Correction Update)  
**Date:** 2026-08-11 (UTC)  
**Status:** Approved Security Baseline  
**Governing ADRs:** ADR-005, ADR-006, ADR-032, ADR-033, ADR-034, ADR-042, ADR-045, ADR-048  

---

## 1. Security Architecture Principles

1. **Zero Client Trust:** The frontend browser environment is completely untrusted. All authorization, validation, rate limiting, and business invariant checks execute strictly on the backend.
2. **Strict Secret Boundary & Fail-Closed Configuration:**
   - Private server secrets (`DJANGO_SECRET_KEY`, `DATABASE_URL`, Redis credentials, S3 private keys) are injected exclusively into backend containers.
   - Production and staging settings fail fast with `ImproperlyConfigured` exceptions if `DJANGO_SECRET_KEY` is missing or insecure, if `DATABASE_URL` is missing (preventing silent fallback to SQLite), or if `ALLOWED_HOSTS` contains wildcards.
   - The frontend receives only explicitly public `NEXT_PUBLIC_*` runtime configuration.
3. **Secure Default DRF Permissions:**
   - `REST_FRAMEWORK` enforces `IsAuthenticated` as the global default permission class.
   - Only explicitly authorized public endpoints (`/healthz`, `/readyz`, `/api/v1/meta`) opt in to `AllowAny`. Future endpoints must opt in explicitly rather than inheriting public access.
4. **Tenant Context Safety:**
   - Tenant scoping derives exclusively from authenticated session state (`request.session.get('active_org_id')`).
   - Client-supplied `X-Organization-ID` headers are ignored in staging and production, and strictly gated behind `ALLOW_TENANT_HEADER_OVERRIDE` (which defaults to `False`).
5. **Correlation ID Validation:**
   - `CorrelationIDMiddleware` validates incoming `X-Request-ID` values (must be a valid UUID string ≤ 36 characters).
   - Malformed, oversized, or log-injection values (e.g. containing `<script>` or newlines) are rejected and replaced with clean, freshly generated UUIDv7 identifiers.
6. **Defense in Depth & Header Delivery:**
   - Backend API responses deliver security headers via `SecurityHeadersMiddleware`.
   - Frontend HTML and static document responses deliver security headers and CSP via `next.config.mjs` / reverse proxy.

---

## 2. Authentication & Session Security Baseline

### 2.1 Session Transport (Recommended MVP)
- **Cookie Name:** `sessionid`
- **Flags:**
  - `HttpOnly: true` — Inaccessible to client JavaScript (prevents token theft via XSS).
  - `Secure: true` — Transmitted strictly over HTTPS in deployed environments (`DEBUG=False`).
  - `SameSite: Lax` — Protects against cross-site request forgery during top-level navigation while maintaining smooth UX.
- **CSRF Defense:**
  - `csrftoken` cookie (readable by frontend client).
  - State-changing HTTP requests (`POST`, `PUT`, `PATCH`, `DELETE`) require the `X-CSRFToken` header matching the cookie.
  - Server verifies token validity before processing request.
- **Token Storage Ban:**
  - **Strictly Prohibited:** Storing long-lived authentication tokens or JWT refresh tokens in `localStorage` or `sessionStorage`.

---

## 3. Security Headers and Content Security Policy (CSP)

### 3.1 HTTP Security Headers Matrix
| Header | Value | Purpose |
|---|---|---|
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains; preload` | Enforces HTTPS strictly |
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-type sniffing |
| `X-Frame-Options` | `DENY` | Prevents clickjacking attacks |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Minimizes referrer leakage |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=()` | Restricts sensitive device hardware |
| `Content-Security-Policy` | See §3.2 below | Mitigates XSS and data injection |

### 3.2 CSP Policy Specification
- **Frontend & Backend Baseline:**
  ```http
  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https: blob:; font-src 'self' data: https:; connect-src 'self' http://localhost:8000 http://127.0.0.1:8000 https:; object-src 'none'; base-uri 'self'; frame-ancestors 'none';
  ```
- **Temporary Development Exception & Hardening Task:**
  - Next.js development server requires `'unsafe-inline'` and `'unsafe-eval'` for Hot Module Reloading (HMR) and client hydration.
  - Tracked under hardening task **`TODO-CSP-001`**: Migrate to per-request cryptographic nonce in production prior to commercial pilot.

---

## 4. Observability and Log Redaction

The backend logging pipeline (`apps.core.middleware.LoggingRedactionMiddleware`) intercepts all log records and scrubs sensitive attributes:
- **Redacted Fields:** `password`, `secret`, `token`, `authorization`, `cookie`, `sessionid`, `csrf_token`, `pain_flag_details`, `body_weight`, `photo_url`, `credit_card`.
- **Correlation ID:** Every HTTP request receives a validated `X-Request-ID` (UUIDv7) that is logged with every entry to correlate traces across services without exposing user PII.

---

## 5. Error Sanitization and RFC 7807 Envelope

All error responses from the API adhere to RFC 7807 Problem Details:

```json
{
  "type": "https://errors.coachos.io/error-validation_failed",
  "title": "Validation Error",
  "status": 400,
  "detail": "The submitted payload contained validation errors.",
  "instance": "/api/v1/resource",
  "message_key": "error.validation_failed",
  "correlation_id": "019fefcb-55b1-7ca6-bcb8-ff471d1a4c32",
  "field_errors": {
    "email": ["Enter a valid email address."]
  }
}
```

Internal 500 server errors return a sanitized message (`"An unexpected server error occurred. Please reference correlation ID."`) and log the full stack trace server-side only.
