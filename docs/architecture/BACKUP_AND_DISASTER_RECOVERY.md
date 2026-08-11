# Backup & Disaster Recovery — CoachOS

**Version:** 1.0.0 Phase 03  
**Status:** Proposed — targets require validation  
**Scope:** Daily PG snapshots, object-storage versioning, restore testing, RPO/RTO proposed, incident/breach response, rollback.

---

## 1. Backup Strategy

### 1.1 PostgreSQL Backups (Proposed)

- **Method:** Managed PG service automated backups (e.g., RDS automated snapshots) + WAL archiving for Point-in-Time Recovery (PITR).
- **Schedule:**
  - Daily full snapshot — retention 30 days proposed (requires founder cost approval).
  - Continuous WAL archiving — allows PITR to any point within retention window (RPO 15min proposed).
  - Manual snapshot before any major migration or release (tag with version).
- **Storage:** Snapshots encrypted at rest (provider AES-256), stored in same region but different AZ, optional cross-region copy for DR (deferred until P1).
- **Verification:** Automated daily `restore to staging` test? Proposed weekly at least — not just snapshot success but actual restore + basic query validation.
- **Encryption:** Snapshots encrypted same as source DB.

### 1.2 Object Storage Backups (Private S3) — Corrected Wording (Task 5)

- **Versioning:** Enabled on all private buckets (`coachos-media-private`, `coachos-progress-private`, `coachos-org-logos`, `coachos-exports-tmp`).
- **Clarification — Versioning Is Not Independent Backup or Cross-Region DR (Correction):**
  - S3 versioning alone is **not** the same as independent backup, nor cross-region disaster recovery. Versioning provides recovery from overwrites/deletes via noncurrent versions and delete markers **within the same bucket and region**, but does **not** protect against region failure, bucket deletion, or account compromise unless combined with cross-region replication and MFA Delete.
  - Versioning does **not** automatically satisfy deletion/erasure requirements (GDPR Art.17 right to erasure). When a user requests erasure (forget-me), versioned objects must be **permanently deleted including all versions and delete markers** (bypass versioning retention), otherwise PII would remain in noncurrent versions. For normal operational deletes (accidental), versioning aids recovery; for erasure, explicit permanent deletion required.
  - Therefore versioning is **one layer** of durability, not a full backup strategy. Independent backup or replication considerations documented below.
- **Replication (Optional but Requires Cost/Legal Approval):** Cross-region replication (CRR) for `progress-private` Tier4 sensitive bucket proposed as P1 — requires founder cost approval and legal review for data residency (Iran/EU). CRR would provide cross-region DR but adds cost and residency complexity, not assumed for MVP.
- **Lifecycle:** 
  - `exports-tmp` expires after 7 days (temporary) — lifecycle rule deletes current and noncurrent versions.
  - Noncurrent versions expire after 30 days? For `media-private` maybe retain 14 days for accidental deletion recovery — but this is **proposed retention**, not guarantee, and must be balanced with erasure requirement (erasure must remove all versions regardless of lifecycle).
  - For `progress-private` Tier4, noncurrent retention must be **short** or bypassed on erasure to respect right to erasure; propose permanent deletion on erasure pipeline.
- **Backup?** S3 is durable (11 9s durability) but versioning alone is not independent backup. No separate backup needed beyond versioning + periodic inventory for MVP **provided** we acknowledge that versioning ≠ cross-region DR and ≠ backup for region failure. For true DR, cross-region replication or periodic inventory copy to different region/account would be needed — deferred P1 pending cost/legal approval. Documented as proposed, not guarantee.

### 1.3 Redis (Cache/Queue) — Corrected Wording (Task 5)

- **Not source of truth — but important async jobs must have durable DB state or outbox/retry strategy (Correction):**
  - Redis is **not** source of truth — cache rebuildable, queue transient.
  - However, important asynchronous jobs (export ZIP generation, erasure pipeline, email invitations, thumbnail generation, notification dispatch) **must not rely solely on Redis queue durability**.
  - **Requirement:** For every important async job, create durable database record first (e.g., `ExportRequest` status pending, `ErasureRequest` pending, `Invitation` created, `Notification` pending) before enqueuing Celery task. Celery worker then processes and updates DB record. If Redis queue loses task (crash, restart), job can be re-enqueued from DB pending status via periodic reconciliation job or manual retry. This is outbox/retry pattern.
  - Rate-limit counters loss acceptable — rebuild on miss, fail-open acceptable but must not bypass authz.
  - If Redis persistence enabled (AOF/RDB), snapshot daily but loss still acceptable; not considered backup for critical data.
- **Note:** Rate-limit counters loss acceptable; rebuild on miss. Durable jobs must have DB state.

### 1.4 Code & Configuration

- **GitHub repo** is source — no extra backup needed beyond GitHub.
- **Infrastructure as Code (future):** If Terraform/CloudFormation used, state file stored in secure backend with versioning.

---

## 2. Restore & Drill Process (Proposed)

### 2.1 Restore Runbook — PostgreSQL

```text
1. Identify target recovery point (timestamp or before migration).
2. Initiate restore from snapshot or PITR to new instance (e.g., coachos-restore-test-20260810).
3. Wait for instance availability.
4. Update staging backend DATABASE_URL to point to restored instance.
5. Run smoke tests: auth login, org list, program assignment fetch, workout session fetch, audit count.
6. If production restore needed: schedule maintenance window, notify users (fa/en), switch DATABASE_URL in secrets manager, restart backend workers, verify healthz.
7. Log restore event to audit (if possible) + notify founder.
```

- **RTO:** Restore + validation proposed 1 hour for DB alone.
- **Who can run:** SRE / Platform Admin with MFA + documented reason + audit.

### 2.2 Restore Runbook — S3 Object

- If object deleted or overwritten:
  1. List versions for key: `aws s3api list-object-versions --bucket ... --prefix ...`
  2. Restore desired version by copying version or deleting delete marker.
  3. Verify via signed URL generation.
- **RTO:** Minutes if single object, hour if many.

### 2.3 Automated Restore Testing

- Weekly or monthly automated job (GitHub Action or Lambda) that:
  - Restores latest PG snapshot to ephemeral staging DB.
  - Runs `pytest` smoke tests against restored data (not mutating).
  - Reports success/failure to Slack.
  - Deletes ephemeral DB after.
- **Required before pilot release** per EXIT GATE.

---

## 3. RPO / RTO Proposed Targets (Require Validation — Proposed Targets, Not Guarantees — Correction Task 5)

**Important Correction:** RPO/RTO figures below are **proposed targets, not guarantees**. They require validation via restore drills and depend on managed service capabilities, WAL archive frequency, and operational readiness. They are engineering hypotheses to be benchmarked in Phase13, not SLA commitments. Cross-region replication, multi-AZ, retention, and residency require cost/legal approval (founder).

| Component | RPO Proposed (Target, Not Guarantee) | RTO Proposed (Target, Not Guarantee) | Notes + Cost/Legal Approval Required |
|-----------|--------------------------------------|--------------------------------------|--------------------------------------|
| PostgreSQL primary | 15 minutes (WAL PITR) — Proposed target, not guarantee — requires WAL archive every 15min validated | 1 hour restore + 30 min validation — Proposed target | Losing 15 min workout logs acceptable? Propose 15 min conservative, 5 min if WAL archive every 5 min — requires validation. Multi-AZ for high availability proposed but requires cost approval (founder). |
| S3 media private (exercise demos) | **Versioning ≠ Backup:** RPO 0 for overwrite recovery via versioning **within same region only** — not independent backup, not cross-region DR — Proposed target. No data loss on overwrite if versioning enabled **and** within same bucket/region, but region failure would still cause loss unless CRR enabled (deferred pending cost/legal). | 1 hour to restore specific objects via version restore — Proposed | Exercise media can be re-uploaded by coaches/orgs if lost, but canonical would need re-moderation. S3 durability 11 9s but versioning alone not cross-region DR — requires cost/legal approval for CRR. |
| S3 progress-private Tier4 | **Versioning ≠ Backup and ≠ Erasure Compliance:** RPO 0 for accidental deletion recovery via version restore within same region — Proposed target, not guarantee. Versioning does NOT automatically satisfy erasure — erasure must permanently delete all versions. | 1 hour — Proposed | Most sensitive — must never lose unless hard deleted via intentional erasure pipeline (which must delete all versions). Versioning protects accidental deletes but not region failure; cross-region replication deferred P1 pending cost/legal approval. |
| Redis cache/rate-limit | Loss acceptable — RPO N/A — Proposed | Minutes (rebuild on demand) — Proposed | No restore needed, cache rebuildable. |
| Redis queue (Celery jobs pending) — Important Jobs Must Have Durable DB State | Jobs stored in PG ExportRequest/ErasureRequest/Invitation/Notification status or re-enqueueable — RPO 0 for jobs persisted in DB; transient jobs in Redis queue could be lost — acceptable **only if** they are retryable from DB status via outbox/retry pattern (see 1.3 corrected). Propose outbox pattern: create DB record first, then enqueue, reconciliation job re-enqueues pending. | Minutes — Proposed | Ensure all important async jobs persisted via DB record before enqueue (outbox pattern) — correction Task 5. |
| Full platform stack (infra failure) | 15 min data (PG WAL), 2-4 hour infra rebuild — Proposed targets not guarantees — single region MVP DR is restore to new AZ, not region, unless cross-region replication approved | 2-4 hours full DR to new region if needed (proposed) — requires infra IAC + cost/legal approval | Depends on founder infra budget — single region MVP DR is restore to new AZ, not cross-region, unless CRR approved. Proposed targets. |
| Frontend static | 0 (git) — Proposed, git is source | Minutes deploy from git — Proposed | Vercel/Netlify auto deploy |

All targets labeled **proposed targets, not guarantees** until validated via restore drills. Cross-region replication, multi-AZ, retention, residency require founder cost approval and legal review.

**Open Questions & Founder Approval (Corrected Wording):** Multi-AZ PG cost vs availability — pending founder infra budget; cross-region replication Tier4 cost vs data residency legal review Iran/EU — pending; backup retention 30d vs 7d cost; RPO 15m vs 5m WAL frequency cost/performance.

---

## 4. Disaster Scenarios & Response (Corrected Wording — Versioning ≠ Backup, Cross-Region Requires Approval)

| Scenario | Impact | Response | Mitigation (Corrected) |
|----------|--------|----------|------------------------|
| PG primary AZ failure | DB unavailable | Failover to standby replica (if managed multi-AZ) automatic — manual promotion if not | Enable multi-AZ for prod (proposed) — **requires founder cost approval**, not guarantee; single-AZ MVP would need manual restore from snapshot |
| PG data corruption | Data inconsistent | PITR to point before corruption (proposed RPO 15min target) | Daily snapshots + WAL — RPO/RTO proposed targets not guarantees |
| S3 bucket accidental delete policy or objects mass deleted — Versioning ≠ Backup nor Cross-Region DR | Media unreachable — versioning provides recovery within same bucket/region via noncurrent versions/delete markers, but **not** cross-region DR, **not** independent backup for region failure, **not** automatic erasure compliance | Restore from versioning within same region: list versions `aws s3api list-object-versions`, restore desired version copying or deleting delete marker; if bucket deleted, recreate bucket from inventory + recreate objects via backup inventory (if available) or re-upload; if region failure, need CRR for DR (deferred pending cost/legal) | Bucket deletion protection via IAM policy + versioning + MFA Delete on Tier4 bucket proposed (requires cost/legal approval); versioning ≠ independent backup — for true DR need cross-region replication or periodic inventory copy to different region/account (deferred P1); for erasure, must permanently delete all versions, not just add delete marker |
| Redis failure — Not source of truth but durable DB state required for important jobs | Rate-limit bypass (fail-open) + cache misses + queue delay — transient queue jobs could be lost | Restart Redis, rebuild cache, re-enqueue Celery jobs from DB pending status via outbox/retry pattern (see 1.3 corrected: important jobs must have durable DB state) | Monitor, alert, autoproc recovery; ensure outbox pattern for important jobs (ExportRequest, ErasureRequest, Invitation, Notification) — create DB record first then enqueue, reconciliation job re-enqueues pending |
| Backend container crash loop | 5xx spike | Rollback to previous image version (see rollback strategy) | Health checks + auto-rollback |
| Worker container crash | Exports/emails/notifs delayed | Restart worker, check dead-letter queue, re-enqueue failed tasks with backoff | Monitor queue depth |
| Accidental erasure pipeline bug wipes too much | Mass anonymization | Restore PG from snapshot before bug; re-evaluate erasure logic | Code review + strong tests for erasure pipeline |
| Secrets leaked | Credential rotation required | Rotate secrets in Secrets Manager + restart services + audit log review + notify founder | No secrets in repo enforced via gitleaks |

---

## 5. Incident Response (Proposed Process)

1. **Detect:** Alert from observability (error rate,DB down, backup failure) + user report.
2. **Triage:** Severity classification S1 (data loss / security breach) to S4 (minor).
3. **Contain:** If breach or data leak, revoke compromised keys, block IP, set maintenance page if needed.
4. **Investigate:** Query audit logs, app logs, metrics, S3 access logs.
5. **Recover:** Restore from backup if needed, patch, redeploy.
6. **Post-mortem:** Blameless post-mortem doc in `docs/reports/incident-YYYY-MM-DD.md` (future) — not created in Phase03.
7. **Communicate:** Notify affected org owners via email (fa/en) — template pending legal review.

---

## 6. Breach Response (Proposed)

- **Definition:** Unauthorized access to Tier3/4 sensitive data (progress photos, pain flags, private messages, body metrics).
- **Steps:**
  1. Immediate containment (revoke tokens, rotate keys, block actor).
  2. Audit log extraction of affected data scope (how many users, which orgs).
  3. Notify founder + legal advisor (requires jurisdiction-specific legal review).
  4. If required by law (GDPR Art.33/34): notify authorities within 72h and affected users without undue delay — pending legal review for Iran market vs EU.
  5. Force password resets for affected users, invalidate sessions.
  6. Provide remediation steps to users.
  7. Document breach in post-mortem, improve controls.

Do NOT claim legal compliance — use "privacy-aligned engineering design, requires jurisdiction-specific legal review".

---

## 7. Rollback Strategy

### 7.1 Application Rollback

- Backend: Previous Docker image tag available in registry (keep last 5). Deploy previous tag via deployment pipeline `deploy-prod.yml` with manual gate.
- Frontend: Vercel/Netlify auto previous deployment rollback via dashboard or revert commit.

### 7.2 Database Migration Rollback

- **Django migrations:** Each migration must have `reverse_code` where possible. For destructive migrations (drop column, change type), need 2-step: add new column → dual-write → backfill → switch reads → drop old — to allow rollback.
- **Before migration:** Manual snapshot of PG (daily auto but also explicit pre-migration snapshot) — tag `pre-migration-<version>-<timestamp>`.
- **If migration fails in prod:**
  1. Rollback app code to previous version compatible with old schema.
  2. If migration already applied partially, run `python manage.py migrate <app> <previous_migration>` reverse if safe, otherwise restore from pre-migration snapshot (if destructive).
  3. Verify healthz + smoke tests.
- **Testing:** Migration rollback tested in staging before prod.

---

## 8. Environment Separation (Security)

- Staging and production use separate VPC, separate DB instances, separate buckets, separate secrets.
- No prod data ever copied to local dev — synthetic data only locally.
- Access to prod secrets limited to founder + SRE role via Secrets Manager IAM.

---

## 9. Open Questions & Founder Approval

- Multi-AZ for PG: cost vs availability trade-off — pending founder infra budget.
- Cross-region replication for Tier4 bucket: pending cost + data residency legal review (Iran vs EU).
- Backup retention 30 days vs 7 days: cost.
- RPO 15 min vs 5 min: WAL archive frequency.

---

## 10. References

- `OBSERVABILITY.md`, `DEPLOYMENT_ARCHITECTURE.md`, `SECURITY_CONTROL_MATRIX.md`, `PRIVACY_DATA_LIFECYCLE.md`
