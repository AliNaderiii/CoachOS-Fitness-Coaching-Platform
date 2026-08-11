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

### 1.2 Object Storage Backups (Private S3)

- **Versioning:** Enabled on all private buckets (`coachos-media-private`, `coachos-progress-private`, `coachos-org-logos`, `coachos-exports-tmp`).
- **Replication (Optional):** Cross-region replication (CRR) for `progress-private` Tier4 sensitive bucket proposed as P1 — requires cost/legal review.
- **Lifecycle:** 
  - `exports-tmp` expires after 7 days (temporary).
  - Noncurrent versions expire after 30 days? For `media-private` maybe retain 14 days for accidental deletion recovery.
- **Backup?** S3 is durable (11 9s) but versioning provides recovery from overwrites/deletes. No separate backup needed beyond versioning + periodic inventory.

### 1.3 Redis (Cache/Queue)

- **Not source of truth** — cache rebuildable; queue durable? Celery tasks if lost could be retried via DB ExportRequest status. No persistent backup required for MVP. If Redis persistence enabled (AOF/RDB), snapshot daily but loss acceptable.
- **Note:** Rate-limit counters loss acceptable; rebuild on miss.

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

## 3. RPO / RTO Proposed Targets (Require Validation)

| Component | RPO Proposed | RTO Proposed | Notes |
|-----------|--------------|--------------|-------|
| PostgreSQL primary | 15 minutes (WAL PITR) | 1 hour restore + 30 min validation | Losing 15 min workout logs acceptable? Should be lower for pilot? Stress: transaction logs can be streamed more frequently — propose 15 min conservative, 5 min if WAL archive every 5 min |
| S3 media private (exercise demos) | 0 (versioning) — no data loss on overwrite if versioning enabled | 1 hour to restore specific objects | Exercise media can be re-uploaded by coaches/orgs if lost, but canonical would need re-moderation |
| S3 progress-private Tier4 | 0 versioning — deletion recovery via version restore | 1 hour | Most sensitive — must never lose unless hard deleted via erasure (intentional) — versioning protects accidental |
| Redis cache/rate-limit | Loss acceptable — RPO N/A | Minutes (rebuild on demand) | No restore needed |
| Redis queue (Celery jobs pending) | Jobs stored in PG ExportRequest status or re-enqueueable — RPO 0 for jobs persisted in DB; transient jobs in Redis queue could be lost — acceptable if they are retryable from DB status (export jobs) | Minutes | Ensure all important async jobs persisted via DB record before enqueue (outbox pattern) |
| Full platform stack (infra failure) | 15 min data, 2-4 hour infra rebuild | 2-4 hours full DR to new region if needed (proposed) — requires infra IAC | Depends on founder infra budget — single region MVP DR is restore to new AZ, not region |
| Frontend static | 0 (git) | Minutes deploy from git | Vercel/Netlify auto deploy |

All targets labeled proposed until validated.

---

## 4. Disaster Scenarios & Response

| Scenario | Impact | Response | Mitigation |
|----------|--------|----------|------------|
| PG primary AZ failure | DB unavailable | Failover to standby replica (if managed multi-AZ) automatic — manual promotion if not | Enable multi-AZ for prod (proposed) — cost |
| PG data corruption | Data inconsistent | PITR to point before corruption | Daily snapshots + WAL |
| S3 bucket accidental delete policy or objects mass deleted | Media unreachable | Restore from versioning; if bucket deleted, recreate from inventory + recreate objects via backup? S3 bucket deletion prevention via MFA Delete? Enable MFA Delete on Tier4 bucket proposed | Bucket deletion protection, versioning, MFA Delete |
| Redis failure | Rate-limit bypass (fail-open) + cache misses + queue delay | Restart Redis, rebuild cache, re-enqueue Celery jobs from DB pending status | Monitor, alert, autoproc recovery |
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
