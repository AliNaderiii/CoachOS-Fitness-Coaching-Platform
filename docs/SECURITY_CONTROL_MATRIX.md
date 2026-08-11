# Security Control Matrix — CoachOS

**Version:** 1.0.0 Phase 03  
**Status:** Proposed  
**Mapping:** Threat → Requirement ID → Architecture Control → Implementation Phase → Test Type → Evidence Artifact → Status

---

## 1. Control Matrix

| Threat ID | Requirement ID (PRD/NFR) | Architecture Control | Implementation Phase | Test Type | Evidence Artifact | Status |
|-----------|---------------------------|----------------------|---------------------|-----------|-------------------|--------|
| T01 Credential Stuffing / Brute Force | NFR-SEC-03, NFR-SEC-01, US-AUTH-002 | Argon2id/bcrypt cost>=12, Redis rate limit 5/15min per IP/email → 429, generic error, password strength validation | Phase05 | Unit (hash cost, strength), Integration (6th attempt 429), E2E login lockout | `identity` module tests, `SECURITY_AND_PRIVACY.md`, rate-limit metrics `auth_rate_limit_hits_total` | Proposed |
| T02 Session Theft | NFR-SEC-04 | HttpOnly; Secure; SameSite=Lax cookies, TLS1.3 HSTS, short-lived access 15min + rotating refresh + reuse detection, no localStorage token, CSP | Phase05 | Unit cookie flags, Integration refresh reuse → revoke all sessions, Security scan CSP | `authorization` middleware, `OPENAPI.yaml` cookieAuth, `OBSERVABILITY.md` | Proposed |
| T03 Invitation Token Abuse | US-ORG-003, US-ORG-004, FR-ORG-02 | Crypto random 32+ bytes, SHA256 hash stored, plaintext only in email, expiry 7d, single-use 410 Gone on reuse | Phase05 | Integration token reuse 410, expiry 410, random guess 404, unit hash storage | `memberships` module, `DATA_FLOW.md` invite flow | Proposed |
| T04 Cross-Tenant IDOR | NFR-AUTHZ-02, NFR-AUTHZ-01, FR-AUTHZ-01 | OrgScopeMiddleware extracts active org from membership, TenantScopedModel.filter `organization_id=auth org_id` mandatory, permission TenantScopedPermission, cross-tenant returns 404/403 obscurity, import-linter prevents bypass | Phase05 | Negative authz tests mandatory: coach OrgA tries GET OrgB members → 404/403, programs, sessions etc. Integration suite for every tenant-scoped endpoint | `AUTHORIZATION_ARCHITECTURE.md`, `CONTAINER_ARCHITECTURE.md`, `ERD.md` org indexes | Proposed |
| T05 Unassigned Coach Access | FR-ATH-02, US-ATH-005, NFR-AUTHZ-03 | CoachAssignmentPermission checks active CoachAthleteAssignment, photo consent + assignment, message participant check | Phase07 | Negative: Coach David unassigned to Neda cannot read sessions 403, cannot view photo 403 (no signed URL) | `AUTHORIZATION_ARCHITECTURE.md`, `THREAT_MODEL.md` T05 | Proposed |
| T06 Owner Overreach | NFR-PRV-02, US-ATH-005, ADR-027, ADR-019 | Owner aggregate analytics only, raw progress photo requires explicit consent granted to owner + audited escalation, private messages audited escalation, set logs operational allowed but pain details aggregate only | Phase07 | Negative: Owner without consent GET progress photo → 403, Owner GET private thread without audit reason → 403 or audited | `AUTHORIZATION_ARCHITECTURE.md` matrix, `PRIVACY_DATA_LIFECYCLE.md` | Proposed |
| T07 Progress-Photo Exposure | NFR-SEC-05, US-ATH-005, Tier4 | Private buckets BlockPublicAcls true, no listing, signed URL TTL ≤15min, no SW cache for Tier4, audit photo.viewed, consent + assignment gating, support DENIED zero, no logging of URLs | Phase07 | Negative: direct S3 URL without sig 403, signed URL after consent revoked new gen 403, unassigned coach 403 + no URL generated, support 403 | `MEDIA_STORAGE.md`, `AUTHORIZATION_ARCHITECTURE.md`, `ERD.md` ProgressPhoto | Proposed |
| T08 Malicious Media Uploads | NFR-SEC-05, US-EX-002, FR-EX-02 | MIME whitelist image/jpeg/png/webp video/mp4, magic bytes validation python-magic, extension sanitized UUID key, size limits 10MB image 100MB video, checksum SHA256, optional ClamAV worker quarantine, rights metadata mandatory for exercise media | Phase06/07 | Unit MIME validation, integration upload php disguised as jpeg 400, oversized 413, E2E upload flow | `MEDIA_STORAGE.md`, `DOMAIN_MODULES.md` M06 | Proposed (ClamAV Phase13) |
| T09 Stored XSS in Notes/Messages | NFR-SEC-06, FR-MSG-01, US-MSG-001 | Backend output encoding, frontend DOMPurify defense-in-depth, HttpOnly cookies prevent token theft even if XSS, CSP script-src self, no dangerouslySetInnerHTML without sanitization | Phase06/08 | Unit sanitization, E2E injection payload rendered as text, Security scan CSP | `COMPONENT_BOUNDARIES.md`, `OBSERVABILITY.md` Sentry | Proposed |
| T10 CSRF | NFR-SEC-04 | SameSite=Lax cookie, double-submit CSRF token if cookie auth, prefer Bearer Authorization header (intrinsically CSRF resistant), Django CSRF middleware | Phase05 | Integration cross-origin POST without CSRF → 403 | `CONTAINER_ARCHITECTURE.md` middleware, `SYSTEM_CONTEXT.md` trust boundaries | Proposed |
| T11 SSRF via Media URLs | NFR-SEC-06 | No server-side fetch of arbitrary remote media URLs — source_url stored as text only, no fetch. If fetch ever needed, allowlist + no internal IP + timeout + disable metadata IP 169.254.169.254 | Phase06 (documented) | Integration attempt submit media with internal IP URL → stored but not fetched (no outbound), Code review no fetch | `MEDIA_STORAGE.md`, `THREAT_MODEL.md` T11 | Proposed / Deferred (no fetch in P0) |
| T12 Webhook Forgery Future Payments | P1-PAY-01 deferred Phase10 | Verify webhook signature HMAC with provider secret, idempotency key for webhook events, replay protection (timestamp tolerance) | Phase10 Future | Integration invalid signature 400, replay old webhook 400, idempotent double delivery not double-charge | `DOMAIN_MODULES.md` M18 future, `THREAT_MODEL.md` T12 | Deferred to Phase10 — documented now |
| T13 Notification Abuse | FR-NTF-01, US-NTF-001 | Rate limit message creation 10/min per sender, notification dispatch throttling, mandatory critical alerts cannot be muted, abuse detection monitoring notifications_dispatched_total spike | Phase08 | Unit rate limit, Integration spam 429, E2E notification prefs | `DOMAIN_MODULES.md` M12/M13, `OBSERVABILITY.md` metrics | Proposed |
| T14 Data Export Abuse | FR-PRI-01, US-PRI-001, NFR-PRV-03 | Export only self (auth user id), time-limited signed URL via verified email TTL 24h proposed, rate limit 2/day per user, worker verifies active, audit export_requested/completed | Phase05/13 | Negative User A attempts export for User B 403, unauthenticated download of export ZIP via direct S3 without sig 403 | `PRIVACY_DATA_LIFECYCLE.md`, `AUTHORIZATION_ARCHITECTURE.md` export row, `OPENAPI.yaml` /privacy/export-request | Proposed |
| T15 Erasure Abuse | FR-PRI-01, US-PRI-002, NFR-PRV-03 | Erasure requires password re-entry + confirmation, authenticated self only, admin execute only verified request + audit, immediate anonymization + S3 photo delete, pipeline status pending/processing/completed | Phase05/13 | Negative User A attempts erasure for User B 403, integration password wrong 400 | `PRIVACY_DATA_LIFECYCLE.md`, `OPENAPI.yaml` /privacy/forget-me | Proposed |
| T16 Insider/Admin Misuse | NFR-PRV-02, US-AUD-001, FR-AUD-01 | Break-glass MFA + reason required + audit admin.break_glass_access + alert Slack security channel + periodic audit review, no audit log mutation DB-level REVOKE | Phase05+ | Integration non-admin GET /admin/* 403, admin sensitive read generates audit, attempt UPDATE audit row fails DB level | `AUTHORIZATION_ARCHITECTURE.md` break-glass, `ERD.md` AuditEvent immutability, `OBSERVABILITY.md` alerts | Proposed |
| T17 Prompt Injection Future AI | P2-AI-01 Phase11, ADR-007 | Constrained AI with retrieval only over verified catalog, system prompts fixed, output requires human review, no autonomous action, no cross-tenant data in prompt unless authorized, prompt+completion+human decision logged, cost/rate limit | Phase11 Future Deferred | Future eval cases injection attempts blocked/flagged, human review 100% for AI suggestions | `DOMAIN_MODULES.md` M20, `THREAT_MODEL.md` T17, `PRIVACY_DATA_LIFECYCLE.md` pre-DPIA | Deferred to Phase11 — documented |
| T18 Supply-Chain | NFR-SEC-06 | Lockfiles, pip audit, npm audit, Dependabot, Snyk, minimal dependencies, no unreviewed major auto-merge, verify signatures | Phase04 CI | CI security scan fails on CVE, unit lockfile integrity | `DEPLOYMENT_ARCHITECTURE.md` CI pipeline, `OBSERVABILITY.md` | Proposed |
| T19 Backup Leakage | NFR-REL-02, NFR-SEC-06 | Snapshots encrypted at rest, private IAM, no public access, MFA Delete on Tier4 bucket, Secrets Manager rotation, audit bucket policies, CloudTrail log snapshot share | Phase04/05 | Integration bucket policy public attempt blocked, CI gitleaks secret scan, manual audit | `BACKUP_AND_DISASTER_RECOVERY.md`, `MEDIA_STORAGE.md` | Proposed |
| T20 Search/Data Enumeration | NFR-AUTHZ-02, REQ-I18N-02, ADR-017, ADR-018 | UUIDv7 proposed non-sequential non-guessable, rate limit search 30/min per user, pg_trgm indexes not leaking count, 404 for cross-tenant, no enumeration via timing | Phase06 | Negative sequential ID guess 404, integration brute force search 429 | `DATA_MODEL.md`, `ERD.md`, `AUTHORIZATION_ARCHITECTURE.md` | Proposed |
| T04 Cross-Tenant Reads (Negative Control Category) | — | Same control T04 | Phase05 | Automated negative suite per each tenant-scoped endpoint | `ARCHITECTURE_VALIDATION_CHECKLIST.md` | Proposed |
| T04 Cross-Tenant Writes (Negative) | — | Same T04 | Phase05 | POST/PATCH to other org's resource 403 | Same | Proposed |
| T05 Unassigned Coach Access (Negative) | — | T05 | Phase07 | Unassigned coach cannot GET athlete sessions 403 | Same | Proposed |
| Suspended Membership | US-ORG-005 | Middleware checks Membership status active, suspended → 403 immediate, assignments archived | Phase05 | Suspended coach any org-scoped call 403 | `AUTHORIZATION_ARCHITECTURE.md` suspension | Proposed |
| Unauthorized Progress-Photo Access (Negative) | US-ATH-005 | Consent + assignment gating, no signed URL generation for unauthorized, support DENIED | Phase07 | David unassigned GET Neda photo 403 | `AUTHORIZATION_ARCHITECTURE.md`, `MEDIA_STORAGE.md` | Proposed |
| Unauthorized Message Access (Negative) | US-MSG-001 | Participant only + assignment check, owner escalation audited, support DENIED | Phase08 | David non-participant GET private thread 403 | `AUTHORIZATION_ARCHITECTURE.md` | Proposed |
| Unauthorized Audit-Log Access (Negative) | US-AUD-001 | Role checks: Owner own org only, Coach/athlete forbidden, Admin global MFA, Support org read per PRD | Phase05 | Coach GET org audit 403, Owner GET other org audit 404/403, Athlete GET audit 403 | `AUTHORIZATION_ARCHITECTURE.md` audit row | Proposed |
| Unauthorized Export/Deletion Requests (Negative) | US-PRI-001/002 | Self-only for export/erasure, password confirm for erasure, rate limit | Phase05/13 | User A attempts export for User B 403, unauth download 403 | `PRIVACY_DATA_LIFECYCLE.md` | Proposed |

---

## 2. Implementation Phase Mapping

| Phase | Controls Implemented |
|-------|---------------------|
| Phase04 Foundation | TLS, HSTS, CSP, lockfiles, secret scan, health checks, SW registration, PWA manifest, backup config proposed |
| Phase05 Identity & Tenancy | All auth controls T01-T04, invitation T03, suspension, audit immutable, org isolation, break-glass admin MFA, export/erasure pipeline design, backup snapshot automation |
| Phase06 Exercise Catalog | Search normalization ADDR-018, Persian variant folding, malicious upload validation T08, XSS sanitization T09 |
| Phase07 Athlete App | Photo consent + signed URL T07, unassigned coach T05, owner overreach T06, offline wording temporary memory only, rest timer client-side |
| Phase08 Messaging | Message thread authz, notification abuse rate limiting T13, XSS sanitization for messages |
| Phase09 Nutrition P1 Future | Consent gating multi-prof T17? Actually nutrition consent — DPIA |
| Phase10 Billing P1 Future | Webhook forgery T12, entitlements |
| Phase11 AI P2 Future | Prompt injection T17, AI run log |
| Phase12 PWA Advanced P2 Future | Offline durable queue + conflict resolution, background sync, push limitations, wearable eval |
| Phase13 QA Security | Restore testing, penetration testing, dependency scan, E2E negative authz suite full, CSRF, SSRF, XSS, backup leakage audit |

---

## 3. Test Type Definitions

- **Unit:** Pure function / service layer isolated, mock DB/Redis.
- **Integration:** API endpoint + DB + Redis + S3 mock/minio, checking status codes + audit logs.
- **E2E:** Frontend + backend + Playwright, RTL/LTR visual checks, PWA install, mobile execution flow, offline banner, negative authz via UI.
- **Security Scan:** pip audit, npm audit, gitleaks, Dependabot, Snyk, CSP header check, cookie flags.
- **Manual/Audit Review:** Periodic review of admin break-glass audit logs, consent revocation effectiveness, backup restore drill.

---

## 4. Evidence Artifacts (Where Control Proven)

- `docs/architecture/AUTHORIZATION_ARCHITECTURE.md` — matrix + break-glass
- `docs/architecture/MEDIA_STORAGE.md` — buckets private + signed URLs
- `docs/architecture/ERD.md` — org indexes, immutable audit, consent tables
- `docs/OPENAPI.yaml` — error envelope, required roles, object permissions per endpoint
- `docs/THREAT_MODEL.md` — threats detailed
- `docs/PRIVACY_DATA_LIFECYCLE.md` — lifecycle + DPIA checklist
- `docs/architecture/DOMAIN_MODULES.md` — module boundaries + test boundaries
- CI logs: lint, security scan, negative authz test results (future Phase04+)
- Audit logs in PG (future operational)

---

## 5. Status Summary

| Status | Count |
|--------|-------|
| Proposed | ~23 P0 controls + 2 future deferred |
| Deferred to P1/P2 | T12 webhook forgery Phase10, T17 prompt injection Phase11, plus advanced offline etc |
| Accepted | ADR-001 modular monolith, ADR-006 RBAC+ABAC, ADR-011 PWA sequencing — direction accepted |
| Pending Founder Approval | License ADR-012, UUIDv7 ADR-017, monorepo ADR-010, backup retention RPO/RTO |

---

## 6. References

- `THREAT_MODEL.md`, `AUTHORIZATION_ARCHITECTURE.md`, `MEDIA_STORAGE.md`, `OBSERVABILITY.md`, `BACKUP_AND_DISASTER_RECOVERY.md`, `DECISIONS.md`, `PRD.md` §6, `SECURITY_AND_PRIVACY.md`
