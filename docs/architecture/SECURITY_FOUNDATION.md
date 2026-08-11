# Security Foundation Specification — CoachOS

**Document Version:** 1.0.0 (Phase 04 Baseline)  
**Date:** 2026-08-11 (UTC)  
**Status:** Approved Security Baseline  
**Governing ADRs:** ADR-005, ADR-006, ADR-032, ADR-033, ADR-034, ADR-042, ADR-045, ADR-048  

---

## 1. Security Architecture Principles

1. **Zero Client Trust:** The frontend browser environment is completely untrusted. All authorization, validation, rate limiting, and business invariant checks execute strictly on the backend.
2. **Strict Secret Boundary:** Private server secrets (database credentials, Redis connection strings, Django secret keys, S3 private keys, email credentials) are injected exclusively into backend containers. The frontend receives only explicitly public `NEXT_PUBLIC_*` runtime configuration.
3. **Defense in Depth:** Multiple independent security layers protect every request (HTTPS/TLS, HSTS, CSP, HttpOnly session cookies, SameSite, CSRF double-submit tokens, object-level access controls, structured logging redaction).
4. **Information Leakage Prevention:** Production API error responses follow RFC 7807 Problem Details and never expose internal stack traces, database schema details, or server directory paths.

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
- **Production Baseline (Target):**
  ```http
  Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}' 'strict-dynamic'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https: blob:; font-src 'self' data:; connect-src 'self' http://localhost:8000 https://api.coachos.io; object-src 'none'; base-uri 'self'; frame-ancestors 'none';
  ```
- **Temporary Development Exception:**
  - Next.js development server requires `'unsafe-inline'` and `'unsafe-eval'` for hot module reloading (HMR).
  - Tracked under hardening task **`TODO-CSP-001`**: Migrate to per-request cryptographic nonce in production prior to commercial pilot.

---

## 4. Observability and Log Redaction

The backend logging pipeline (`apps.core.middleware.LoggingRedactionMiddleware`) intercepts all log records and scrubs sensitive attributes:
- **Redacted Fields:** `password`, `secret`, `token`, `authorization`, `cookie`, `sessionid`, `csrf_token`, `pain_flag_details`, `body_weight`, `photo_url`, `credit_card`.
- **Correlation ID:** Every HTTP request receives a unique `X-Request-ID` (UUIDv7/UUIDv4) that is logged with every entry to correlate traces across services without exposing user PII.

---

## 5. Error Sanitization and RFC 7807 Envelope

All error responses from the API adhere to RFC 7807 Problem Details:

```json
{
  "type": "https://errors.coachos.io/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "The submitted payload contained invalid fields.",
  "instance": "/api/v1/resource",
  "message_key": "error.validation_failed",
  "field_errors": {
    "email": ["Enter a valid email address."]
  }
}
```

Internal 500 server errors return a sanitized message (`"An unexpected error occurred. Please reference correlation ID: <uuid>"`) and log the full stack trace server-side only.
