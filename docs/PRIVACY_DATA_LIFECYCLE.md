# Privacy & Data Lifecycle — CoachOS

**Version:** 1.0.0 Phase 03  
**Status:** Proposed — privacy-aligned engineering design, requires jurisdiction-specific legal review (Iran, EU GDPR perspectives)  
**Languages:** fa-IR RTL + en-US LTR only, Arabic out of scope.

---

## 1. Lifecycle Stages

CoachOS defines 11 lifecycle stages for personal data:

1. **Collection** — data intake from user actions (registration, workout logging, photo upload)
2. **Consent** — explicit affirmative consent capture for sensitive types (progress photos, nutrition sharing P1)
3. **Storage** — persistence in PG, private S3, Redis (ephemeral), search indexes
4. **Use** — business processing (program assignment, adherence calculation, messaging)
5. **Sharing** — within tenant (coach-assigned athlete) + future multi-professional P1 with consent
6. **Export** — self-service machine-readable archive (GDPR Art.20 adjacent)
7. **Retention** — duration policy per class
8. **Revocation** — user withdraws consent → immediate effect
9. **Deletion** — hard delete PII + photo objects (GDPR Art.17 adjacent)
10. **Anonymization** — disassociate historical telemetry into aggregates without PII
11. **Backup Destruction** — how backups handle deletion/anonymization (retention question)

---

## 2. Data Classification Detailed (Privacy-Aligned)

### Tier 0: Public Metadata

- **Examples:** Canonical exercise names, movement pattern enum, equipment taxonomy, public landing pages, marketing copy.
- **Purpose:** Provide searchable catalog, filtered browsing.
- **Legal/Privacy Assumption:** No personal data, public domain or licensed CC-BY; no consent required.
- **Data Owner/Controller Assumption:** Platform as controller curating public library; contributions reviewed.
- **Access Rules:** Public/canonical exercise via authenticated read? Actually canonical exercises require auth but considered Tier0 — readable by all authenticated users, not tenant-scoped beyond org private distinction.
- **Encryption Expectation:** TLS transit, at-rest AES-256 but not field-level.
- **Logging Restriction:** No PII.
- **Retention:** Until archived by moderation.
- **Export Behavior:** Included in global catalog? Not user-specific export.
- **Deletion Behavior:** Archive only, not user-deletable.
- **Consent Requirement:** No.

### Tier 1: Account / Identity Data

- **Examples:** User email, display_name, phone_number optional, password_hash, preferred_locale, timezone, Organization name/slug, Membership role/status, Invitation email/role.
- **Purpose:** Authentication, tenancy, role binding, org management, invitation.
- **Legal Assumption:** Account data necessary for service provision; email required; phone optional. Data minimization: no extraneous PII (no national ID).
- **Owner/Controller:** User is data subject, Platform is controller for account, Org Owner controller for tenant membership? Propose Platform controller, Org processor for P0? Requires legal review — mark as "controller assumption requires jurisdiction-specific legal review".
- **Access Rules:** Self + Org Owner (member list) + Platform Admin audited + Coach limited? Coach can see assigned athlete display_name/email? Actually per matrix, coach can read assigned athlete profiles — yes. Owner can read org members. Support read-only org members.
- **Encryption:** In transit TLS1.3, at rest AES-256, password Argon2id/bcrypt salted.
- **Logging Restriction:** Do NOT log password_hash, full email in debug logs (partial or hashed). Log user_id instead.
- **Retention Question:** Until erasure request; invitation records retain 90 days after expiry for audit? Proposed 90 days then anonymize email? Open question.
- **Export Behavior:** Included in profile.json export.
- **Deletion Behavior:** On erasure, email/name/phone wiped, memberships anonymized or archived, audit event `user.anonymized` retains actor_id but not PII? Audit metadata should not retain email after erasure? Proposed audit retains user_id only disassociated.
- **Consent Requirement:** Registration implies consent to account processing but explicit checkbox for terms? UI checkbox "I agree to Terms" — proposed.

### Tier 2: Coaching Operational Data

- **Examples:** Programs, phases/weeks/days, workout items, set prescriptions, templates, assignments snapshots, workout sessions scheduled/in_progress/completed, set logs actuals, exercise substitution reason, session RPE/fatigue notes excluding pain flag details? Actually session RPE/fatigue considered operational but somewhat sensitive? Classify as operational for now but treat as partially sensitive.
- **Purpose:** Core coaching workflow — building, assigning, logging, adherence.
- **Legal Assumption:** Operational data necessary for coaching service, not special category? Could be considered health-related but for fitness coaching not medical. Still privacy-sensitive; purpose limitation: only for coaching.
- **Owner:** Athlete owns historical logs fundamentally (per ADR-019), org holds revocable operational access during active coaching.
- **Access:** Tenant-scoped + assignment: Owner org athletes operational (not raw health? but set logs allowed), Coach assigned athletes only, Athlete self, Admin audited.
- **Encryption:** At rest AES-256, TLS.
- **Logging Restriction:** Do not log set load values in debug? Maybe okay but avoid health details in logs; log only IDs + volume aggregates not per-set load.
- **Retention:** Until org archive or assignment archive? Historical logs preserved even if assignment archived for continuity — athlete retains. If athlete erasure, disassociate.
- **Export:** Include workouts.json, set_logs.csv.
- **Deletion:** On org archive, operational data archived not deleted? On athlete erasure, disassociate anonymized aggregates retained for reporting but set logs disassociated from PII? Proposed anonymize athlete_user_id to anonymized ID and retain volume.
- **Consent:** No explicit consent beyond coaching relationship? But assignment itself is consent to coach? Implicit via invitation acceptance.

### Tier 3: Sensitive Health-Adjacent Data

- **Examples:** FeedbackFlag joint_pain/muscle_strain/dizziness/severe_fatigue with anatomical_location, severity, details; BodyMetric body_weight, bodyfat; fatigue_score, session_rpe? The latter could be sensitive if used for health profiling.
- **Purpose:** Contextual readiness and subjective discomfort signals for coach review to adjust volume/form feedback — NOT medical diagnosis (mandatory disclaimer).
- **Legal/Privacy Assumption:** Sensitive personal data under GDPR Art.9? Potentially health data — requires stricter handling, explicit consent? For P0, consent via coaching relationship but with explicit UI disclaimers non-clinical. Pre-DPIA required for large-scale sensitive data.
- **Owner:** Athlete owns; coach holds revocable access via assignment but not owner automatic raw access (owner aggregate only).
- **Access Rules:** Athlete self, Assigned Coach only, Owner aggregate counts but not raw details, Support read flags summary? Per PRD support can read flags — propose support can read flag type/severity but not details free-text? To be safe, support read flags but details maybe limited — document open. Admin audited break-glass.
- **Encryption:** At rest AES-256; field-level encryption consideration for FeedbackFlag.details proposed (deferred pending review) — may be overkill for MVP.
- **Logging Restriction:** MUST NOT log raw details (anatomical location, severity free-text) in debug logs — only type + id.
- **Retention Question:** Until erasure? Feedback flags may be needed for safety audit trail? Retain anonymized? Proposed retain until erasure then anonymize.
- **Export Behavior:** Include in workouts export? Pain flags included in export for athlete own review — yes.
- **Deletion Behavior:** On erasure, wipe details; aggregates disassociated?
- **Consent Requirement:** Athlete self-disclosure voluntary; no additional consent beyond coaching relationship but UI provides disclaimer.

### Tier 4: Progress Media Assets

- **Examples:** Front/side/back progress photos, technique form check videos (private).
- **Purpose:** Visual physiological tracking for coach assessment under strict privacy.
- **Legal Assumption:** Highly sensitive personal visual data — requires explicit affirmative consent (ADR-027) before upload, right to revocation.
- **Owner:** Athlete owns; org/coach holds revocable licensed view.
- **Access:** Athlete self, Assigned Coach with active ConsentRecord progress_photo, Owner with explicit consent granted to owner + audited escalation, Support DENIED zero, Admin break-glass audited MFA + reason.
- **Encryption:** S3 SSE-S3/SSE-KMS, transfer TLS, signed URL TTL ≤15min private, no CDN caching, no public ACL.
- **Logging Restriction:** NEVER log storage key full or signed URL; log only photo_id + actor.
- **Retention:** Until athlete deletes individual photo or erasure request triggers hard delete from S3.
- **Export:** Include in export ZIP? For athlete export, include own photos? Proposed yes if athlete requests include media checkbox — but large ZIP — optional. For MVP, export includes photo metadata + signed URLs? Better include photo files if feasible? Proposed include photos in ZIP if total < 100MB else provide separate signed links. Open question.
- **Deletion:** Hard delete S3 object + DB record on individual delete or erasure.
- **Consent Requirement:** Explicit affirmative modal consent dialog before upload (UX_COPY), grant allows coach view, revocation immediate blocks future access + invalidates future signed URLs (existing URLs still valid until TTL expiry — short TTL mitigates).

### Tier 3/4 Combined — Body Metrics with Photos?

Body weight etc may be considered Tier3 but often paired with progress photos. Consent model allows separate consent types: `progress_photo`, `body_metrics`, `nutrition_sharing` for granularity.

### Tier 5: Messages

- **Examples:** 1:1 coach-athlete message threads linked to workout sessions.
- **Purpose:** Contextual communication.
- **Classification:** Tier2+ confidential — not health in itself but may contain health disclosures; treat as private.
- **Legal Assumption:** Private communication — requires protection similar to Tier3.
- **Access:** Participants only (sender/recipient) + Owner/Admin break-glass audited, Support DENIED.
- **Encryption:** TLS, at rest AES-256.
- **Logging Restriction:** Do NOT log message content in debug logs, only IDs + thread metadata.
- **Retention:** Until erasure? On erasure, messages? Proposed: messages permanently deleted or anonymized? Depends — if deleting erases conversation history for other participant, maybe disassociate? Propose anonymize content to "[deleted]" for erasure but keep thread for other participant? Open decision.
- **Export:** Include own messages in export.
- **Consent:** Implicit via assignment but user can delete? No edit for P0.
- **Deletion:** Erasure pipeline.

### Tier 6: Audit Data

- **Examples:** AuditEvent actor, action, target, IP hash, metadata sanitized.
- **Purpose:** Security, compliance traceability.
- **Legal Assumption:** Audit required for security, but may itself contain PII (actor_id). Must be protected, append-only, not deletable by normal users.
- **Access:** Platform Admin global, Owner own org only, Coach/Athlete none, Support org read per PRD.
- **Encryption:** At rest AES-256.
- **Logging Restriction:** Metadata sanitized — no passwords, no raw health, no full message content, IP stored as SHA256 hash not raw.
- **Retention:** Proposed 1 year+ (requires legal review — some regs require longer for security incidents). Question.
- **Export/Deletion:** Export of audit logs: Owner can export own org audit; Admin global export. Deletion forbidden — no update/delete by app role DB-level REVOKE.
- **Consent:** Not applicable — security necessity.

### Tier 7: Future Payment Data (P1 Phase10)

- **Examples:** Gateway customer IDs, subscription status, invoice metadata (no raw PAN).
- **Legal Assumption:** PCI-DSS tokenization via external gateways, no card numbers stored.
- **Owner:** Tenant Owner.
- **Access:** Owner, Finance Admin.
- **Encryption:** Tokenized, at rest AES-256.
- **Retention:** Per financial regulation 7 years? Requires legal review.
- **Status:** Future, deferred, not implemented in P0.

### Tier 8: Future AI Data (Phase11)

- **Examples:** AI prompt version, generated workout variant, coach approval state, retrieval context.
- **Legal Assumption:** Prompts stripped of athlete PII before model submission, audit logged.
- **Access:** Authoring Coach, Platform AI safety auditor.
- **Retention:** Log retention per AI safety — maybe 90 days? Requires review.
- **Status:** Future, not in P0.

---

## 3. Consent Lifecycle

### 3.1 Progress Photo Consent UX (ADR-027)

1. Athlete clicks upload photo.
2. System checks active ConsentRecord for grantee coach.
3. If none, frontend shows modal: title "Allow Coach Reza to view progress photos", body plain explanation of usage + unilateral revocation right.
4. Primary action "Grant Consent", secondary "Keep Private".
5. Focus trapped modal, privacy-first default focus on "Keep Private".
6. Upon grant, backend creates ConsentRecord `is_granted=true`, `granted_at=now`, audit `consent.granted`.
7. Upload proceeds.
8. Revocation via Profile → Privacy → Revoke — immediate, audit `consent.revoked`, future signed URL generation blocked.

### 3.2 Multi-Professional Collaboration Consent (P1)

- When Org Owner assigns Nutrition Professional to athlete, athlete receives consent prompt: "Allow Nutritionist Sara to view training schedule and body metrics".
- Separate consent type `nutrition_sharing`.
- Progress photo not automatically included — needs separate `progress_photo` consent granted to nutritionist as grantee.

### 3.3 Consent Revocation

- Immediate effect: `revoked_at` set, future authz queries filter `revoked_at IS NULL`.
- Existing signed URLs still valid until TTL ≤15min — short TTL mitigates window.
- No caching of Tier4 media in SW for this reason.

---

## 4. Export Pipeline (GDPR Art.20 Adjacent)

- **Trigger:** `POST /api/v1/privacy/export-request` authenticated self only.
- **Rate limit:** 2/day per user proposed.
- **Async job:** Celery worker queries all user-scoped data across modules, packages ZIP `profile.json`, `workouts.json`, `set_logs.csv`, optionally photos.
- **Storage:** Temporary S3 private bucket `coachos-exports-tmp` with lifecycle 7 days.
- **Delivery:** Email to verified email with time-limited signed URL (24h proposed).
- **Audit:** `privacy.export_requested`, `export_completed`.
- **Security:** Signed URL requires HTTPS, no listing, single-use? Proposed single-use + expiry.

---

## 5. Erasure Pipeline (GDPR Art.17 Adjacent) — Anonymization & Hard Deletion

- **Trigger:** `POST /api/v1/privacy/forget-me` with password re-entry (and maybe email confirmation second step P1).
- **Pipeline stages (proposed):**
  1. **Verify password** + confirm.
  2. **Invalidate sessions** — all active refresh tokens revoked, memberships set to suspended? Actually memberships archived, user is_active false?
  3. **Delete PII:** Name, email, phone, profile picture, progress photos S3 deletion.
  4. **Anonymize logs:** Historical workout volume aggregates disassociated from PII — `SetLog` `athlete_user_id` replaced with anonymized placeholder? Or `WorkoutSession` retained but athlete identifier hashed? Proposal: Set `athlete_user_id` to NULL? But FK constraint? Use anonymized UUID placeholder and keep audit? Need DB design: allow nullable or anonymized.
  5. **Messages:** Either delete content "[deleted]" or anonymize? Proposed delete private notes but retain thread for other participant with anonymized name.
  6. **Audit:** Generate `user.anonymized` event with actor system, target user_id (now anonymized id).
  7. **Backups:** Question — backups contain PII until retention expires. Document: backup destruction deferred until backup retention 30 days expiry. Requires legal review.

- **Statuses:** pending → processing → completed/failed.
- **Audit:** erasure requested/completed.

---

## 6. Retention & Backup Destruction Questions (Open for Legal Review)

| Data Class | Proposed Retention P0 | Backup Destruction Expectation | Open Question |
|------------|-----------------------|--------------------------------|---------------|
| Account/Identity | Until erasure | Wiped from active DB immediately, remains in PG snapshots until 30-day retention expires | Acceptable per GDPR? Requires legal review — snapshot deletion not immediate |
| Operational (sessions, set logs) | Until assignment archive or erasure; after erasure anonymized aggregates retained | Same snapshot retention |
| Tier3 health-adjacent | Until erasure; anonymized aggregates? | Same |
| Tier4 progress photos | Until individual delete or erasure — hard delete S3 + DB immediate, versioned S3 retains version until version expiry 30 days proposed | Versioned S3 deletion recovery possible 30 days? Should hard delete include delete markers + version removal for erasure? Propose immediate permanent deletion for erasure (bypass versioning) to respect right to erasure |
| Messages | Until erasure or thread archive | Same snapshot |
| Audit | 1 year+ (proposed) — not deleted upon user erasure; actor_id anonymized? But audit needs actor traceability for security — anonymize actor_id to hashed? Open | 1 year+ retention requires legal basis — security |
| Export TMP | 7 days lifecycle | Immediate delete after download? |

All retention labeled proposed until validated + legal review.

---

## 7. Pre-DPIA Checklist (Data Protection Impact Assessment precursor)

Any processing that may trigger DPIA per GDPR Art.35 must be documented before implementation (requires legal review).

| Checklist Item | Applies? | CoachOS P0? | Notes / Mitigation |
|----------------|----------|-------------|--------------------|
| Large-scale sensitive data (health) | Yes if > threshold | P0 includes pain flags, body metrics, progress photos — potentially large-scale if many athletes | Privacy-aligned design: tenant isolation, consent, audited, minimized, no medical claims, DPIA checklist documented — requires formal DPIA before commercial launch if systematic monitoring |
| Systematic monitoring of data subjects | Possibly | Athlete adherence tracking could be considered monitoring but not public area. Requires assessment |
| Automated profiling / decision making | No for P0 | No autonomous AI; human review required; AI deferred Phase11 — AI profiling triggers DPIA when introduced |
| Multi-professional sharing | Yes P1 | Nutrition sharing with consent — multi-professional data sharing increases risk — consent model in ADR-020 |
| Progress-photo processing | Yes | Visual body conditioning photos highly sensitive — explicit consent, private buckets, signed URLs, support DENIED |
| Future wearable data | Yes P2 | HealthKit/Health Connect, HR, recovery — sensitive health data — DPIA required before integration, Phase12 |
| AI processing | Yes P2 | Phase11 AI copilot with health data — DPIA required before launch |
| Large-scale biometric? | No | No biometric identification planned — only progress photos for human coach review, not facial recognition |
| Vulnerable data subjects (children)? | Potentially | Gym clients could include minors? Policy: require 16+? Open decision — requires legal review for age gating |
| Data transfer across borders? | Yes | Iran vs EU data residency question — requires legal review |

**Outcome:** Before pilot handling real health data, formal DPIA and legal review mandatory. This document is engineering alignment, not legal compliance claim.

---

## 8. Logging Restrictions Summary

- Never log raw passwords, password_hash, tokens, Authorization headers, full email? partial redacted okay, health flag details, body metric values, progress photo storage keys/signed URLs, message content, full IP (store hash).
- Log actor_user_id, org_id, entity_type/id, action, request_id, status.

---

## 9. Privacy UX Copy Requirements

- All consent prompts and data export notices must be rendered with equal clarity in fa-IR and en-US (non-clinical, supportive tone per UX_COPY).
- Mandatory disclaimers for pain/fatigue reporting: "This report will be sent to your coach for workout adjustment. It is not a medical diagnosis."

---

## 10. References

- `SECURITY_AND_PRIVACY.md` baseline data classification (now expanded)
- `AUTHORIZATION_ARCHITECTURE.md` photo/message access matrix
- `MEDIA_STORAGE.md` private buckets + signed URLs
- `THREAT_MODEL.md` privacy-related threats T05 owner overreach, T07 photo exposure, T14/15 export/erasure abuse
- `DECISIONS.md` ADR-019 data ownership, ADR-020 multi-prof consent, ADR-027 consent UX, ADR-026 non-clinical language
