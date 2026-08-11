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
    FE --> SecretMgr
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

## 6. Secrets & Configuration

- **Secrets Manager:** All secrets (DB URL, Django SECRET_KEY, Redis URL, S3 keys, Email API key, JWT signing keys) stored in Secrets Manager / env. Never committed.
- **Config example `.env.example` (proposed placeholders, not real secrets):**
  ```
  DJANGO_SECRET_KEY=change-me-in-production
  DATABASE_URL=postgres://user:pass@host:5432/coachos
  REDIS_URL=redis://host:6379/0
  AWS_S3_BUCKET_PRIVATE=coachos-media-private
  EMAIL_PROVIDER_API_KEY=placeholder
  ```
- **CI:** gitleaks/secret scan fails build if secret pattern detected.

---

## 7. TLS & Security Headers (Proposed)

- Enforce TLS 1.3 only in ALB.
- HSTS: `max-age=31536000; includeSubDomains; preload` (proposed).
- CSP: `default-src 'self'; img-src 'self' data: https: blob: <s3-signed-domain>; media-src 'self' https:; script-src 'self' 'unsafe-inline' ? (Next.js requires; fine-tune)` — to be hardened in Phase04 implementation review.
- `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, Referrer-Policy strict.

---

## 8. Backup & Restore Hooks (Links)

- Detailed in `BACKUP_AND_DISASTER_RECOVERY.md`.
- Daily PG snapshots + WAL archiving for PITR, 30-day retention proposed.
- S3 versioning + cross-region replication optional, lifecycle rules for tmp exports deletion after 7 days proposed.
- Restore drills quarterly proposed before pilot.

---

## 9. RPO/RTO Targets (Proposed — Require Validation)

| Tier | RPO Proposed | RTO Proposed | Justification |
|------|--------------|--------------|---------------|
| PostgreSQL primary | 15 min (PITR) | 1 hour restore + validation | Pilot data not extreme scale but must not lose workout logs |
| S3 media private | 0 (versioning) | 1 hour | Media durable, can re-upload if lost? Tier4 sensitive — need backup |
| Redis (cache) | Loss acceptable (rebuild) | Minutes | Not source of truth |
| Complete platform | 15 min data, 2 hour infra | 2-4 hour full DR | Proposed — requires founder review |

All targets labeled proposed until validated.

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
