# Observability Architecture — CoachOS

**Version:** 1.0.0 Phase 03  
**Status:** Proposed — requires implementation validation  
**Scope:** Structured logging, metrics, error tracking, health endpoints, alerting.

---

## 1. Structured Logging

### 1.1 Format

- JSON structured logs at INFO level for production, DEBUG for local/staging.
- Required fields: `timestamp` ISO8601 UTC, `level`, `service` (api/frontend/worker), `request_id` (X-Request-ID UUIDv7), `org_id` if applicable, `actor_user_id` if authenticated, `action`, `entity_type`, `entity_id`, `duration_ms`, `status_code`, `message`, `version` (git commit hash).

Example:
```json
{"timestamp":"2026-08-10T14:30:00.123Z","level":"INFO","service":"api","request_id":"019fed02-...","org_id":"019f...","actor_user_id":"019f...","action":"program.assigned","entity_type":"ProgramAssignment","entity_id":"019f...","duration_ms":85,"status_code":201,"message":"Program assigned to athlete"}
```

### 1.2 Logging Library (Proposed)

- Backend Python: `structlog` with JSON renderer + processor for request_id.
- Frontend Next.js: `pino` or similar for server logs; browser console logs minimal, errors sent to Sentry (not verbose).

### 1.3 Sensitive-Data Redaction

- **Must NOT log:** password_hash, raw password, raw email? Email maybe considered PII but needed for debugging? Propose log user_id not email by default; if email needed, redact partially `r***@example.com` or hash.
- Must NOT log: progress photo storage keys raw? Maybe log key prefix only `progress/{athlete_id}/` not full signed URL.
- Must NOT log: message content, FeedbackFlag.details raw, BodyMetric values, JWT tokens, Authorization headers.
- Must NOT log: full IP — store ip_hash SHA256 in audit, but debug logs store hashed or truncated.
- Implement redaction processor in structlog that removes keys `password`, `password_hash`, `token`, `authorization`, `content` (for messages), etc.

### 1.4 Correlation / Request IDs

- Middleware `RequestIDMiddleware` generates `X-Request-ID` UUIDv7 if not provided, propagates to response header `X-Request-ID`.
- All logs include `request_id`.
- Frontend `apiClient` generates optional `X-Request-ID` per request or uses backend response to correlate.
- Celery tasks inherit `request_id` via task kwargs.

### 1.5 Audit Logs vs Debug Logs — Separation

- **Debug/Structured App Logs:** For ops, performance, errors — stored in ELK/CloudWatch, retention 30 days proposed, no Tier3/4 sensitive payloads.
- **Audit Logs:** Immutable `AuditEvent` table in PG — security/compliance events only — retention long (1 year+ proposed, pending legal), never UPDATE/DELETE by app user, queried only by admin/owner scoped.

Never mix: Audit events must not be only in app logs — must be in DB table.

---

## 2. Metrics

### 2.1 Proposed Metrics Stack

- **Backend:** Prometheus metrics via `django-prometheus` or `prometheus_client` exposing `/metrics` (protected, not public) — counters, histograms.
- **Frontend:** Web Vitals via `next/web-vitals` reporting to analytics endpoint (optional) — LCP, CLS, INP.
- **Infra:** Cloud provider metrics (RDS CPU, Redis memory, S3 requests).

### 2.2 Key Metrics

| Metric Name | Type | Labels | Purpose |
|-------------|------|--------|---------|
| `http_requests_total` | Counter | method, path_template, status | Request volume |
| `http_request_duration_seconds` | Histogram | method, path_template | API latency p95 target <200ms reads, <400ms writes |
| `auth_login_failures_total` | Counter | reason | Brute-force detection |
| `auth_rate_limit_hits_total` | Counter | endpoint | Rate limiting visibility |
| `org_membership_status` | Gauge? | org_id, role, status | Roster health |
| `program_assignments_total` | Counter | org_id | Business metric |
| `workout_sessions_total` | Counter | status (scheduled/completed) | Engagement |
| `set_logs_total` | Counter | org_id | Volume |
| `media_uploads_total` | Counter | media_type, status | Upload health + malicious attempt 4xx |
| `media_signed_url_generated_total` | Counter | tier (0/2/4) | Photo access tracking |
| `notifications_dispatched_total` | Counter | event_type | Notification engine health |
| `celery_tasks_total` | Counter | task_name, status | Worker health |
| `audit_events_total` | Counter | action | Security auditing |
| `export_requests_total` | Counter | status | Privacy operations |
| `db_connections` | Gauge | — | Connection pool |
| `redis_cache_hit_ratio` | Gauge | — | Cache efficiency |

All business metrics anonymized aggregate, not per PII.

---

## 3. Error Tracking

### 3.1 Sentry (Proposed)

- Frontend + Backend + Worker integration via `sentry-sdk`.
- DSN via env secrets.
- Sample rate 10% for transactions proposed, 100% for errors.
- Scrub sensitive data: same redaction rules as logs.
- Release tracking via git commit hash.
- Alert on new error type, regression.

### 3.2 Frontend Error Boundary

- React Error Boundary around major routes (today, builder) showing friendly error state with retry + request_id for support.
- `window.onerror` and unhandledrejection captured to Sentry.

---

## 4. Health Endpoints

### 4.1 Proposed Endpoints

- `GET /healthz` — liveness: returns 200 if process up, no DB check? Or minimal. Public but no sensitive.
- `GET /readyz` or `/api/v1/health` — readiness: checks DB connectivity, Redis connectivity, S3 connectivity (list bucket? Actually Head bucket). Returns JSON:
```json
{"status":"ok","checks":{"db":"ok","redis":"ok","s3":"ok","celery":"ok"},"version":"771afa6...","timestamp":"..."}
```
- For DB check: `SELECT 1`.
- For Redis: `PING`.
- For S3: `HEAD Bucket` or simple.
- Protected? `healthz` public, `readyz` internal or protected via token/monitoring IP allowlist.

### 4.2 Dependency Health

- If DB down → readiness 503 → load balancer removes instance from pool → alert.
- Worker health: Celery beat heartbeat + queue depth metric.

---

## 5. Alerting Categories (Proposed — Requires Validation)

| Category | Condition | Severity | Channel | Owner |
|----------|-----------|----------|---------|-------|
| Auth Anomaly | > 20 failed logins same IP in 15min or > 5 same email rate_limit_hits | Medium / High if spike | Slack/Email + audit security alert | Backend / Security |
| Cross-tenant Access Attempt | Any 403/404 due to org scope mismatch spike > threshold (e.g., 10 same actor 5min) | High | Slack + Audit `authz.cross_tenant_attempt` | Security |
| Unauthorized Photo Access | 403 on progress photo endpoint spike | High | Slack + audit | Security |
| Error Rate | 5xx rate > 1% for 5min | High | Pager/ Slack | SRE / Backend |
| Latency p95 | Read > 400ms or builder save > 800ms sustained 10min | Medium | Slack | Backend |
| DB Connections Saturation | > 80% of max connections | Medium | Slack | SRE |
| Redis Down | Redis unreachable > 1min | High | Slack | SRE |
| S3 Upload Failure | Upload 5xx or 4xx validation > 5% | Medium | Slack | Backend |
| Celery Queue Depth | Queue > 100 pending for >10min | Medium | Slack | Backend |
| Export/Erasure Failure | Export job failed > 3 times | Medium | Slack + audit | Privacy |
| Backup Failure | Daily snapshot failed | High | Email + Slack | SRE |
| Disk Space | PG disk > 80% | High | Pager | SRE |
| Certificate Expiry | TLS cert < 14 days | High | Email | SRE |

All thresholds proposed until validated in staging pilot.

---

## 6. Monitoring Auth & Cross-Tenant Alerts

- Log every `permission_denied` with actor, org, target type/id (sanitized), IP hash, request_id.
- Alert on pattern: same actor multiple cross-tenant 404/403 in short window → potential IDOR probing.
- Admin break-glass access logs immediate alert to Slack security channel + email to founder?
- Failed admin MFA attempts → high severity.

---

## 7. Frontend Observability

- Web Vitals (LCP < 2.5s, CLS <0.1, INP <200ms proposed targets) tracked via `web-vitals` lib -> own analytics endpoint `/api/v1/analytics/web-vitals` (optional, not storing PII) -> Prometheus/Grafana.
- PWA install prompt events logged as custom metrics `pwa_install_prompt_shown`, `pwa_installed`.
- Offline events: `navigator.onLine` transitions logged locally? Send when back online.

---

## 8. Retention & Costs

- Logs 30 days proposed for app logs; audit logs 1 year+.
- Metrics 90 days raw, 1 year aggregated.
- Sentry events 30 days.
- Costs proportional to volume — avoid verbose logging of Tier3/4.

---

## 9. References

- `BACKUP_AND_DISASTER_RECOVERY.md`, `SECURITY_CONTROL_MATRIX.md`, `THREAT_MODEL.md`
