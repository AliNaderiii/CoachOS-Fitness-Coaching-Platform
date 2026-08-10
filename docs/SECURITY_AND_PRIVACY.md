# Security, Privacy & Data Governance Baseline — CoachOS

**Document version:** 1.0.0 (Phase 01 Baseline)  
**Last updated:** 2026-08-10  
**Compliance Context:** GDPR, HIPAA-adjacent health privacy principles, OWASP Top 10, and regional data protection regulations.  
**Disclaimer:** This specification is an engineering baseline, not formal legal counsel. Prior to commercial deployment handling live health data, qualified legal review is mandatory.

---

## 1. Comprehensive Data Classification Taxonomy

| Data Classification Tier | Description & Scope | Examples | Handling, Storage & Encryption Policies | Access Boundaries |
|---|---|---|---|---|
| **Tier 0: Public Metadata** | Unrestricted public platform assets and marketing copy. | Canonical exercise names, equipment taxonomy, public landing pages. | CDN cacheable; public HTTP GET; zero auth required. | Public / World readable. |
| **Tier 1: Account & Identity Data** | Core user authentication and organization profile records. | Name, email address, password hash, locale preferences, org slug. | Encrypted in transit (TLS 1.3); passwords salted Argon2id/bcrypt; encrypted at rest (AES-256). | Authenticated user (self) and Organization Owner. |
| **Tier 2: Coaching Operational Data** | Non-sensitive athletic training programs, prescriptions, and templates. | Exercise prescriptions, program phases, sets, reps, tempo, workout calendar. | Standard tenant-isolated relational database storage; transactional backups. | Tenant Organization; authoring Coach; assigned Athlete. |
| **Tier 3: Sensitive Health-Adjacent Data** | Physiological metrics, physical limitations, subjective exertion, and readiness logs. | Body weight, body fat %, pain flags, injury history, fatigue ratings, check-in notes. | **Strictly Confidential.** Field-level encryption options; zero logging in web server debug logs; audited reads. | **Assigned Coach Only** via active assignment; Athlete (self); Org Owner escalation. |
| **Tier 4: Progress Media Assets** | Visual body conditioning photographs and private form check videos. | Athlete front/side/back progress photos, technique review clips. | Private S3 object storage; **never public**; access strictly via time-limited (<= 15 min) cryptographically signed URLs. | **Explicit Athlete Consent Required**; Assigned Coach; Athlete (self); Support/Admin strictly blocked unless audited break-glass. |
| **Tier 5: System Audit Logs** | Security and compliance event records. | `AuditEvent` table (actor ID, IP hash, action type, entity ID, timestamp). | Append-only database table; write-once / read-many; tamper-evident; never updated or deleted by normal users. | Platform Administrator; Org Owner (tenant-scoped). |
| **Tier 6: Secrets & Infrastructure Keys** | Cryptographic keys and cloud credentials. | Database connection URIs, JWT signing keys, S3 secret keys, Redis credentials. | Secure Secrets Manager / Environment variables only; **never committed to Git repository**. | Infrastructure / CI pipeline execution only. |
| **Tier 7: Financial & Billing Data (Future P1/Phase 10)** | Payment gateway tokens and transaction history. | Gateway customer IDs, subscription status, invoice metadata (no raw PAN). | PCI-DSS compliant payment tokenization via external gateways (Stripe/Shetab). | Tenant Owner; Finance Admin. |
| **Tier 8: AI Inference Logs (Future Phase 11)** | Prompts, completions, and human review decisions. | AI prompt version, generated workout variant, coach approval state. | Anonymized; stripped of athlete PII prior to model submission; audit logged. | Authoring Coach; Platform AI safety auditor. |

---

## 2. Server-Side Authorization & Tenancy Boundaries

### 2.1 Multi-Tenant Isolation Rule
Every tenant-scoped query must enforce explicit `organization_id` boundaries derived from the caller's authenticated session/token, never trusting client-supplied query parameters alone:
```sql
-- Normative authorization pattern
SELECT * FROM programs
WHERE id = :program_id
  AND organization_id = :authenticated_user_active_org_id;
```

### 2.2 Object-Level Assignment Rules (ABAC)
1. **Coach-to-Athlete Assignment:** A coach can only read or mutate training data, workout logs, and feedback for an athlete if an active `CoachAthleteAssignment` record exists linking them within the same organization.
2. **Athlete Self-Ownership:** Athletes can only read and mutate their own assigned workouts, set logs, and profile records.
3. **Cross-Tenant Obscurity:** When an authenticated user requests a resource ID belonging to another organization, the API must return `HTTP 404 Not Found` (preferred to avoid ID enumeration) or `HTTP 403 Forbidden`.

---

## 3. Privacy, Consent Hooks & Data Governance

### 3.1 Athlete Data Ownership Guarantee
- The personal training history, physiological metrics, and workout logs belong fundamentally to the **Athlete User**.
- Gym organizations hold a revocable operational license to view and manage these records during the active coaching relationship.

### 3.2 Granular Consent Hooks
1. **Progress Photo Consent:** Before an athlete uploads their first progress photo, the UI displays an explicit consent modal: *"Allow Coach [Name] to view progress photos for physique assessment"*. Upload is blocked until consent is logged.
2. **Multi-Professional Collaboration Consent (P1 Scope):** When an organization assigns a Nutrition Professional to an athlete, the athlete must explicitly accept a consent prompt before the nutritionist is granted read access to training schedules or body metrics.
3. **Consent Revocation:** An athlete can revoke photo or nutritionist access at any time via Profile -> Privacy Settings. Revocation immediately invalidates existing signed URLs and blocks subsequent API queries.

### 3.3 Data Portability & Machine-Readable Export (GDPR Art. 20)
- Any authenticated user can trigger `POST /api/v1/privacy/export-request`.
- A background worker packages the user's profile, training programs, historical workout sessions, and set logs into a standardized ZIP archive containing `profile.json`, `workouts.json`, and `set_logs.csv`.
- The user receives an authenticated, time-limited download link via verified email.

### 3.4 Right to Erasure / Account Anonymization (GDPR Art. 17)
- User triggers `POST /api/v1/privacy/forget-me` with password re-entry.
- The pipeline executes:
  1. Permanent deletion of personal identifiers (Email, Display Name, Phone Number, Profile Picture, Progress Photos, Contextual Messages).
  2. Invalidation of active memberships and sessions.
  3. Disassociation of historical workout telemetry (volume, sets completed) into an anonymized statistical aggregate for gym business reporting.
  4. Generation of an immutable `user.anonymized` audit event.

---

## 4. Threat Model & Security Controls

| Threat Vector | Potential Impact | Architecture & Security Mitigation Strategy |
|---|---|---|
| **Cross-Tenant Data Tampering (IDOR)** | Malicious coach views/edits another gym's proprietary templates or athlete logs. | Strict server-side RBAC and object-level permission guards; automated negative authorization test suites in CI. |
| **Credential Stuffing & Brute Force** | Account takeover via automated password guessing. | Rate limiting (5 failed attempts per 15 min -> HTTP 429); modern Argon2id hashing; account lockout triggers. |
| **Progress Photo Media Hotlinking / Exposure** | Public exposure of private athlete conditioning photos. | Private S3 buckets with blocked public access; time-limited cryptographically signed URLs (TTL <= 15 min); strict auth verification before URL generation. |
| **Cross-Site Scripting (XSS)** | Attacker steals session tokens via malicious exercise notes. | Automated HTML output encoding; strict Content Security Policy (CSP); session tokens stored in `HttpOnly; Secure; SameSite=Lax` cookies. |
| **Cross-Site Request Forgery (CSRF)** | Unauthorized state-changing actions executed via malicious third-party sites. | Double-submit CSRF tokens on state-mutating requests; `SameSite=Lax` cookie enforcement. |
| **Session Hijacking & Token Theft** | Stolen tokens used to impersonate coach or admin. | Short-lived access tokens (15 min); rotating refresh tokens with automatic reuse detection and revocation. |
| **Insider Misuse / Unauthorized Admin Snooping** | Platform admin or gym owner reads private messages or health logs without justification. | Immutable `AuditEvent` logging on all administrative reads; support escalation break-glass workflows requiring documented reason. |
| **Supply Chain & Dependency Vulnerabilities** | Compromised third-party packages introduce backdoors. | Automated dependency vulnerability scanning (Dependabot / Snyk) in CI; lockfile integrity checks. |

---

## 5. Security & Privacy Standing Rules for Engineering

1. **No Real PII or Health Data in Repository:** All test fixtures, database seeds, and documentation must exclusively use synthetic, fictionalized data.
2. **Zero Secrets in Git:** API keys, database credentials, and signing secrets must never be committed. `.env.example` contains only non-sensitive template keys.
3. **Negative Authorization Test Mandate:** Every sensitive API endpoint must have corresponding negative test cases proving that unauthorized roles and cross-tenant actors receive `403 Forbidden` or `404 Not Found`.
4. **Bilingual Privacy Notices:** All consent prompts and data export notices must be rendered with equal clarity in Persian (`fa-IR`) and English (`en-US`).
