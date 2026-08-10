# Security and Privacy Baseline — CoachOS

**Status:** Baseline policy (Phase 00)  
**Last updated:** 2026-08-10  
**Disclaimer:** This document is an engineering baseline, **not legal advice**. Production launch with real health-related data requires qualified legal/privacy counsel for applicable jurisdictions.

---

## 1. Data classification

| Class | Examples | Handling |
|-------|----------|----------|
| Public | Published exercise names, marketing copy | CDN-ok; still license-aware |
| Account | Email, name, locale, org membership | AuthN/AuthZ; minimize logs |
| Coaching operational | Programs, assignments, workout logs | Tenant + assignment scoped |
| **Sensitive health-related** | Body metrics, progress photos, pain flags, injury notes, nutrition, sleep | Strict ACL, consent, audit, encryption in transit; at-rest encryption where platform supports |
| Secrets | API keys, DB URLs, signing keys | Env/secret manager only; never git |

Treat health, body composition, injury, nutrition, sleep, wearable, and progress media as **sensitive** by default.

## 2. Principles

1. **Data minimization** — collect only what features need  
2. **Purpose limitation** — sharing permissions per purpose where relevant  
3. **Least privilege** — RBAC + object-level checks server-side  
4. **Defense in depth** — authn, authz, validation, rate limits, headers  
5. **Auditability** — sensitive reads/writes produce audit events  
6. **User control** — export and deletion workflows  
7. **No secrets in repo** — `.env.example` only  
8. **No real PII/PHI in fixtures, screenshots, or reports**  

## 3. Authentication (target)

- Email+password MVP (see ADR-005) with modern password hashing (e.g., Argon2/bcrypt via framework defaults)  
- Secure password reset tokens; single-use; short TTL  
- Session expiration and/or JWT access+refresh with rotation if token-based  
- MFA strategy for professional/admin accounts (timing TBD; document before pilot)  
- Rate limit login, signup, reset  

## 4. Authorization (target)

- Roles: Platform Admin, Org Owner, Coach, Athlete (MVP); extend later  
- Object rules: coach↔athlete assignment; org boundary; admin break-glass audited  
- **Never** trust client-supplied role/org/athlete IDs  
- Sensitive notes/photos: additional visibility constraints + consent  

## 5. Privacy and consent

- Explicit consent flows for progress photos and multi-professional access (P1 multi-pro)  
- Athletes can see who has access to their coaching data (target UX)  
- Privacy policy placeholder before public launch  
- Jurisdiction-specific retention rules: **TODO legal**  

## 6. Data lifecycle

| Event | Target behavior |
|-------|-----------------|
| Export | Authenticated user can request machine-readable export of their data |
| Deletion | Request workflow + staged delete; respect legal retention holds |
| Backups | Encrypted backups; tested restore; retention documented (Phase 03/13) |
| Media | Signed URLs; no public bucket listing; virus/content-type validation on upload |

## 7. Application security controls

- HTTPS only in deployed environments  
- Secure cookies (`HttpOnly`, `Secure`, `SameSite` as appropriate)  
- CSRF protection for cookie session flows  
- CORS allowlist — no `*` with credentials  
- Security headers (CSP progressively, `X-Content-Type-Options`, frame protections compatible with deployment)  
- Input validation and output encoding  
- File upload: size limits, MIME sniffing, extension allowlist, malware scanning strategy documented  
- Dependency scanning in CI (Phase 04+)  
- Container scanning if containers used  

## 8. Logging and monitoring

- Structured logs  
- **Redact** tokens, passwords, raw health payloads, photo URLs with signatures where possible  
- Alert on auth anomaly spikes (target)  
- Audit log distinct from debug logs for sensitive domain events  

## 9. AI-specific (future)

- Minimize sensitive data in prompts  
- Log model, prompt template version, input scope, output, reviewer action  
- Human approval for professional-facing recommendations  
- Rate limits, cost caps, kill switch  
- No invented medical contraindications or diagnoses  

## 10. Threat model (initial — expand Phase 03)

| Threat | Mitigation direction |
|--------|----------------------|
| Cross-tenant data access | Org scoping + tests |
| Coach enumerates unassigned athletes | Object-level authZ + tests |
| Invitation token abuse | Single-use, expiry, rate limit |
| Media hotlinking / leakage | Signed URLs, short TTL |
| XSS stealing sessions | CSP, encoding, HttpOnly |
| CSRF mutating actions | Framework CSRF / SameSite |
| Stolen refresh tokens | Rotation + revoke |
| Prompt injection (future AI) | Isolation, tool allowlists, human review |
| Dependency compromise | Lockfiles, scanning, least install |
| Insider misuse | Audit logs, least privilege admin |

## 11. Compliance TODOs (not complete)

- [ ] Privacy policy draft for public launch  
- [ ] Terms of service  
- [ ] Data processing roles (controller/processor) per deployment region  
- [ ] Counsel review for health-related data in target markets  
- [ ] Breach notification runbook  
- [ ] DPIA-style assessment if required by law  

## 12. Secure development checklist (standing)

- [ ] No secrets committed  
- [ ] AuthZ tests for every new sensitive endpoint  
- [ ] i18n does not leak authorization via translated error detail  
- [ ] Fixtures use synthetic data only  
- [ ] Security section updated when features touch health data  

## 13. Related

- `docs/DECISIONS.md` (ADR-003, ADR-006, ADR-007)  
- Phase 03 will deepen threat model, encryption-at-rest choices, and backup design  
