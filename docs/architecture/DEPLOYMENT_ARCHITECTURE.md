# Deployment Architecture — CoachOS

**Version:** 1.0.0 Phase 03  
**Status:** Proposed (requires founder infra decision)  
**Target:** Single region MVP, modular monolith, managed data services.

---

## 1. Deployment Topology (Logical)

```mermaid
flowchart TB
    subgraph Client [Client Layer — Untrusted]
        Browser[Browser / PWA - Desktop & Mobile<br/>fa-IR RTL / en-US LTR]
    end

    subgraph Edge [Edge / CDN — Proposed]
        CDN[CDN/Static Hosting<br/>Vercel / Netlify / CF Pages<br/>+ CloudFront for media edge — optional]
        WAF[WAF / Rate-limit at Edge<br/>Proposed Cloudflare / AWS WAF]
    end

    subgraph LB [Load Balancer / TLS Termination]
        ALB[HTTPS ALB<br/>TLS1.3, HSTS, CSP headers]
    end

    subgraph App [Application Layer — VPC Private]
        FE[Frontend Container<br/>Next.js SSR/SSG/CSR<br/>Node 20]
        BE[Backend Container<br/>Django + DRF + Gunicorn/Uvicorn<br/>Python 3.12]
        Worker[Celery Worker<br/>beat + worker pods]
    end

    subgraph Data [Data Layer — Private Subnets Only]
        PG[(Managed PostgreSQL 16<br/>RDS / Cloud SQL / Supabase<br/>PITR + daily snapshot)]
        Redis[(Managed Redis 7<br/>ElastiCache / Upstash / MemoryStore)]
        S3[(Private S3-Compatible<br/>Buckets: coachos-media-private,<br/>coachos-exports-tmp,<br/>coachos-org-logos<br/>No public access)]
    end

    subgraph Observ [Observability]
        Logs[Structured Logs<br/>ELK / CloudWatch / Sentry]
        Metrics[Prometheus/Grafana or Cloud Metrics]
        SentryErr[Error Tracking Sentry]
        Health[Health Endpoint /healthz + /readyz]
    end

    subgraph External [External Services]
        EmailSvc[Email Provider<br/>SES / SendGrid / Postmark]
        SecretMgr[Secrets Manager<br/>AWS SM / GCP SM / env]
    end

    Browser -->|HTTPS| WAF --> CDN
    CDN --> ALB
    ALB --> FE
    ALB --> BE
    FE -->|/api/v1| BE
    BE --> PG
    BE --> Redis
    BE --> S3
    Worker --> PG
    Worker --> Redis
    Worker --> S3
    Worker --> EmailSvc
    BE --> EmailSvc
    BE --> SecretMgr
    Worker --> SecretMgr
    FE -->|Public runtime config only<br/>NEXT_PUBLIC_* vars<br/>NO private secrets| BE
    BE --> Logs
    BE --> Metrics
    BE --> SentryErr
    BE --> Health
    Worker --> Logs
```

---

## 2. Environment Strategy (Proposed)

| Env | Purpose | Deploy Trigger | Data | Notes |
|-----|---------|----------------|------|-------|
| local | Developer machine | `docker-compose` (future Phase04) | Synthetic seed only | No real secrets |
| staging | Pre-production integration | GitHub Actions on `main` or `arena/*` push | Anonymized synthetic copy, no prod PII | E2E Playwright, security scans |
| production | Live pilot | Tag `v0.x.x` + manual approval gate | Real user data (Tier1-4) | PITR, backups, audit enforced |

**Separation:** Distinct VPC, DB instances, buckets, secrets per env.

---

## 3. Container / Runtime Strategy (Proposed Options)

- **Option A: PaaS Simple (Recommended MVP):**
  - Frontend: Vercel / Netlify auto-deploy from GitHub `main`.
  - Backend + Worker: Render / Fly.io / Railway / ECS Fargate single service.
  - Data: Managed PG (Supabase/Neon/RDS), Upstash Redis, S3 (AWS or Cloudflare R2).
  - Pros: Fastest pilot, low ops.
  - Cons: Vendor lock-in partly.

- **Option B: Kubernetes (EKS/GKE) — Overkill for MVP but future-ready:**
  - Frontend Deployment + Backend Deployment + Worker Deployment.
  - HPA based on CPU/latency.
  - Managed PG + Redis still external.

- **Recommendation:** Start with Option A (PaaS) for Phase04 pilot, document migration path to K8s. Status: Proposed pending founder decision recorded in DECISIONS.md ADR-010 deferred + new ADR needed.

---

## 4. Docker & CI/CD (GitHub Actions — Proposed)

### 4.1 CI Pipeline (Phase04 target)

```mermaid
flowchart LR
    Push[Git Push to arena/* or main] --> Lint[Lint + TypeCheck<br/>Python ruff/mypy<br/>TS tsc + eslint]
    Lint --> Tests[Unit + Integration<br/>Negative authz tests mandatory]
    Tests --> SecScan[Security Scan<br/>Dependabot, pip audit, npm audit, secret scan gitleaks]
    SecScan --> Build[Build Docker Images<br/>FE + BE]
    Build --> E2E[Playwright E2E<br/>RTL/LTR visual checks<br/>fa-IR + en-US]
    E2E --> DeployStaging[Deploy to Staging<br/>Auto]
    DeployStaging --> ManualGate[Manual Approval for Prod]
    ManualGate --> DeployProd[Deploy to Prod<br/>Tag + health check]
```

### 4.2 Expected Workflows (`.github/workflows/` — not created in Phase03)

- `ci.yml` — lint, type, unit, security scan on every PR.
- `e2e.yml` — Playwright against staging.
- `deploy-staging.yml` — auto deploy on merge to main.
- `deploy-prod.yml` — manual workflow_dispatch with tag.

**No secrets in repo:** Use GitHub OIDC to AWS/GCP/Cloud provider.

---

## 5. Scaling & Resilience (Proposed)

- **Horizontal:** Backend stateless (session via DB/JWT + HttpOnly cookie + Redis), can scale replicas behind ALB.
- **Worker scaling:** Celery workers scaled on queue depth.
- **DB:** Read replica optional post-pilot (P1). Connection pooling via PgBouncer / Django CONN_MAX_AGE + pgbouncer.
- **Cache:** Redis for rate limit + short-lived search cache; fail-open acceptable for cache miss but must not bypass authz.

---

## 6. Secrets & Configuration (Corrected Boundary)

- **Secrets Manager Boundary (Critical Correction):**
  - **Frontend (Next.js) MUST NEVER access Secrets Manager directly.** Browser and frontend runtime (including SSR Node.js serving frontend) never receive private secrets.
  - Private secrets — database URLs, Django `SECRET_KEY`, Redis credentials, S3 access keys/secret keys, email provider API keys, JWT signing keys, VAPID private keys, any provider secrets — are available **only** to backend and worker runtimes through server-side secret injection (Secrets Manager / environment variables injected at deploy time, not bundled).
  - Frontend receives **only explicitly public runtime configuration** via build-time `NEXT_PUBLIC_*` variables (e.g., `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_SENTRY_DSN` public, `NEXT_PUBLIC_APP_NAME`). No private secret may be prefixed with `NEXT_PUBLIC_` or included in client bundle, server component props, or API proxy.
  - Frontend MUST NOT receive, render, bundle, or proxy private secrets. `FE --> SecretMgr` relationship is explicitly **forbidden** and removed from topology diagrams. Only `BE --> SecretMgr` and `Worker --> SecretMgr` are allowed.
  - Verification: CI build checks that `NEXT_PUBLIC_` contains no secret patterns, and bundle scan ensures no database URL, secret key, or S3 secret appears in frontend chunks. Secret scan via gitleaks fails build if secret pattern detected in frontend bundle or repo.

- **Secrets Manager:** All private secrets stored in Secrets Manager / env. Never committed to Git.
- **Config example `.env.example` (proposed placeholders, not real secrets):**
  ```
  # Private — backend/worker only — never NEXT_PUBLIC
  DJANGO_SECRET_KEY=change-me-in-production
  DATABASE_URL=postgres://user:pass@host:5432/coachos
  REDIS_URL=redis://host:6379/0
  AWS_S3_ACCESS_KEY_ID=placeholder
  AWS_S3_SECRET_ACCESS_KEY=placeholder
  EMAIL_PROVIDER_API_KEY=placeholder
  JWT_SIGNING_KEY=placeholder

  # Public — frontend allowed (explicitly public)
  NEXT_PUBLIC_API_BASE_URL=https://api.coachos.example.com/api/v1
  NEXT_PUBLIC_APP_NAME=CoachOS
  NEXT_PUBLIC_SENTRY_DSN_PUBLIC=placeholder-public-dsn
  ```
- **CI:** gitleaks + custom check for `NEXT_PUBLIC_*` containing secret-like values fails build. Frontend bundle secret scan in Phase 04 hardening task.

---

## 7. TLS & Security Headers (Proposed — Corrected CSP Strategy)

- Enforce TLS 1.3 only in ALB.
- HSTS: `max-age=31536000; includeSubDomains; preload` (proposed).
- **CSP Proposed Strategy (Correction):**
  - **Production preferred:** Nonce- or hash-based script authorization.
    - Example proposal: `default-src 'self'; img-src 'self' data: https: blob: https://*.coachos-media.example.com; media-src 'self' https: blob:; style-src 'self' 'nonce-{random}' https:; script-src 'self' 'nonce-{random}' 'strict-dynamic' https:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; connect-src 'self' https://api.coachos.example.com https://*.sentry.io; font-src 'self' data:;`
    - Nonce generated per request server-side for SSR pages, or hash of inline scripts computed at build time where compatible.
    - No `unsafe-inline` in production baseline.
  - **Framework limitation temporary exception (if needed):**
    - Next.js historically required `unsafe-inline` for some inline scripts unless nonce is configured via `next.config.js` `experimental` or middleware generating nonce. If during Phase 04 foundation `unsafe-inline` is temporarily required to unblock SSR hydration:
      - Explicitly mark as **temporary**, document risk: XSS via inline injection if other controls fail, increased attack surface, bypasses CSP protection for inline scripts.
      - Define hardening task: `TODO-CSP-001` — migrate to nonce-based CSP before pilot, remove `unsafe-inline` from `script-src`, validate via CSP evaluator and Lighthouse.
      - Document temporary exception in `docs/DECISIONS.md` and Phase 04 report, not presented as accepted production control.
  - **Do not claim CSP finalized before implementation validation:** CSP policy is proposed strategy requiring implementation validation, header testing via securityheaders.com and CSP evaluator, and E2E tests that inline scripts still work with nonce.
  - Additional: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin` or `strict-origin`, `Permissions-Policy` restrictive.
- **Implementation note:** ALB or Next.js middleware sets CSP header; `next.config.js` headers() function can inject nonce via `request.headers` if using middleware.

---

## 8. Backup & Restore Hooks (Links — Corrected Wording Task 5)

- Detailed in `BACKUP_AND_DISASTER_RECOVERY.md` (corrected wording for versioning ≠ independent backup, versioning ≠ erasure compliance, RPO/RTO proposed not guarantees).
- Daily PG snapshots + WAL archiving for PITR, 30-day retention proposed — **proposed target, not guarantee, requires cost approval, validation via restore drills**.
- **S3 versioning is NOT independent backup nor cross-region DR** — versioning provides recovery from overwrites/deletes within same bucket/region via noncurrent versions, but does **not** protect against region failure or bucket deletion unless combined with cross-region replication (CRR) which requires cost/legal approval. **Versioning does NOT automatically satisfy deletion/erasure requirements** — erasure (forget-me) must permanently delete all versions and delete markers, bypassing lifecycle. Lifecycle rules for tmp exports deletion after 7 days proposed.
- Restore drills quarterly proposed before pilot — required before pilot per exit gate.
- **Redis not source of truth but important async jobs must have durable DB state or outbox/retry** — create DB record (ExportRequest, ErasureRequest, Invitation, Notification) first then enqueue Celery, reconciliation job re-enqueues pending.

---

## 9. RPO/RTO Targets (Proposed — Require Validation — Corrected Wording: Proposed Targets Not Guarantees)

| Tier | RPO Proposed (Target, Not Guarantee) | RTO Proposed (Target, Not Guarantee) | Justification + Cost/Legal Approval |
|------|--------------------------------------|--------------------------------------|-------------------------------------|
| PostgreSQL primary | 15 min (PITR) — Proposed target, requires WAL archive every 15min validated | 1 hour restore + validation — Proposed | Pilot data not extreme scale but must not lose workout logs — multi-AZ proposed requires cost approval |
| S3 media private | **Versioning ≠ Backup nor Cross-Region DR:** 0 for overwrite recovery via versioning within same bucket/region — Proposed target, not independent backup, not cross-region DR | 1 hour — Proposed | Media durable 11 9s but versioning alone not cross-region DR — CRR requires cost/legal approval. Exercise media can be re-uploaded but canonical needs re-moderation |
| Redis (cache) | Loss acceptable — RPO N/A — Proposed | Minutes (rebuild) — Proposed | Not source of truth, cache rebuildable |
| Redis queue (important jobs) | **Durable DB state required:** Jobs stored in PG ExportRequest/ErasureRequest status or re-enqueueable — RPO 0 for jobs persisted in DB; transient Redis queue loss acceptable only if retryable via outbox pattern | Minutes — Proposed | Ensure all important async jobs persisted via DB record before enqueue (outbox pattern) — correction Task 5 |
| Complete platform | 15 min data (PG WAL), 2 hour infra — Proposed targets not guarantees | 2-4 hour full DR to new region if needed (proposed) — requires infra IAC + cost/legal approval | Depends on founder infra budget — single region MVP DR is restore to new AZ, not region unless CRR approved |

All targets labeled **proposed targets, not guarantees** until validated via restore drills. Cross-region replication, multi-AZ, retention, residency require founder cost approval and legal review.

---

## 10. Language & Locale Deployment

- Frontend builds with both locales baked (`fa-IR.json`, `en-US.json`) + runtime switch.
- No Arabic artifact deployed — CI lints for `ar` locale files fail build per NFR-I18N-04.

---

## 11. Open Decisions

- PaaS vs K8s final choice — pending founder infra budget review.
- Region selection for data residency — Iran-compatible? International? Requires legal review for PII residency.
- CDN provider for private media edge — CloudFront signed URLs vs Cloudflare R2 presigned.

---

## 12. References

- `SYSTEM_CONTEXT.md`, `CONTAINER_ARCHITECTURE.md`, `BACKUP_AND_DISASTER_RECOVERY.md`, `OBSERVABILITY.md`, `DECISIONS.md` ADR-010, ADR-002
