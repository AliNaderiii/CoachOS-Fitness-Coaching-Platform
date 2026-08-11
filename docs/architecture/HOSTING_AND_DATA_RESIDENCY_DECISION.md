# Hosting, Infrastructure, and Data Residency Strategy — CoachOS

**Document Version:** 1.0.0 (Phase 04 Foundation Baseline)  
**Status:** Architectural Decision Record & Evaluation Matrix  
**Date:** 2026-08-11 (UTC)  
**Authors:** Principal Software Architect, DevOps/SRE Engineer, Security Engineer, Founder's Technical Advisor  
**Governing ADR:** ADR-012, ADR-049  

---

## 1. Executive Summary

Pursuant to the Founder Mandate established in Phase 04:
1. **Commercial Model & Licensing:** Proprietary / All Rights Reserved (ADR-012).
2. **Geographic Strategy:** Dual-region architectural capability supporting:
   - Persian / Iran-related users (requiring high-resilience network routing, low latency across national boundaries, and compatibility with domestic banking/telecom rails in Phase 10).
   - European and International users (requiring strict GDPR alignment, high availability, and standard EU cloud compliance).
3. **Phase 04 Boundary:** Build a **strictly provider-neutral, containerized foundation** for local development and staging environments. Production deployment remains behind an explicit founder decision gate. **Zero real production infrastructure or cloud credentials** are provisioned in Phase 04.

---

## 2. Infrastructure Deployment Models Comparison

| Dimension | Option A: Managed PaaS (e.g. Render / Fly.io / Railway / Vercel) | Option B: EU Managed Cloud / IaaS (e.g. Hetzner Cloud / Scaleway / AWS EU) | Option C: Bare VPS / Self-Hosted Docker Swarm | Option D: Dual-Region Active-Passive (Iran Edge Proxy + EU Primary) | Option E: Dual-Region Active-Active (Full Replication) |
|---|---|---|---|---|---|
| **Monthly Cost (MVP/Pilot)** | Medium ($35 – $120/mo) | Low-Medium ($25 – $80/mo) | Low ($15 – $40/mo) | Medium-High ($100 – $250/mo) | Very High ($300 – $800+/mo) |
| **Operational Complexity** | Very Low (Zero DevOps overhead, managed DB/TLS) | Medium (Requires Terraform/Ansible, OS patching) | High (Manual maintenance, custom monitoring & backups) | High (Dual network ingress, DNS routing, split-tunnel monitoring) | Extreme (Multi-master PG replication, conflict resolution, CRDTs) |
| **Iran User Latency & Uptime** | Variable (Depends on edge CDN routing, risk of IP blocking) | Good (Frankfurt/Falkenstein latency 60-110ms to Iran) | Good (Custom VPS with clean IP range) | Optimal (Iran reverse proxy / CDN edge cache < 30ms static) | Optimal (< 30ms latency for all traffic) |
| **GDPR & Data Residency** | Strong if EU region chosen (Frankfurt/Amsterdam) | Strong (Strict EU data center sovereignty) | Medium (Depends on data center location & physical security) | Complex (Split data residency requires formal DPIA) | High Risk (Sensitive health/photo data replication across borders) |
| **Payment Rail Compatibility** | Stripe native; Shetab requires outbound IP allowlisting | Clean static egress IPs for Shaparak/Shetab + Stripe | Custom static IPs for Shaparak/Shetab | Dedicated Iran egress for Shetab; EU egress for Stripe | Native local gateway bindings |
| **Disaster Recovery / Backups** | Automated snapshots, PITR available on managed plans | Automated volume snapshots + S3 backup hooks | Custom BorgBackup / pg_dump to offsite S3 | Cross-region backup replication | Instant failover across active regions |
| **Vendor Lock-in** | Low (Containerized Django + Next.js standard images) | Very Low (Standard Linux VMs + Docker) | None | Low (Provider-agnostic reverse proxy) | High (Depends on distributed DB technologies) |

---

## 3. Detailed Architectural Evaluation

### 3.1 Option A — Managed PaaS (Render / Railway / Vercel)
- **Strengths:** Rapid setup, zero Linux system administration, automated zero-downtime deployments via Git, managed PostgreSQL with automated daily backups, built-in Redis.
- **Weaknesses:** Higher cost per compute unit at scale; limited control over outbound egress IPs (challenging for Iranian domestic payment gateway IP whitelisting in Phase 10); potential CDN domain filtering during national network throttling events.
- **Suitability:** Ideal for Phase 04 staging and developer testing.

### 3.2 Option B — EU Managed Cloud / IaaS (Hetzner Cloud / Scaleway / AWS Frankfurt)
- **Strengths:** Exceptional cost-to-performance ratio (Hetzner Falkenstein/Nuremberg provides direct peering to major Middle East backbones with 60–90ms round-trip latency to Tehran); dedicated IPv4/IPv6 addresses; strict German/EU privacy law compliance (DSGVO/GDPR); ISO 27001 certified datacenters.
- **Weaknesses:** Requires explicit infrastructure-as-code (Terraform/Ansible) and automated backup script maintenance.
- **Suitability:** Strong candidate for Single-Region Production Launch (Phase 13).

### 3.3 Option C — Self-Hosted Bare VPS / Docker Swarm
- **Strengths:** Maximum flexibility, lowest raw hardware cost.
- **Weaknesses:** Unacceptable single-point-of-failure risk for a lean startup team; manual maintenance of security patches, firewalling, and backup automation.
- **Suitability:** Rejected for production; acceptable only for private developer sandboxes.

### 3.4 Option D — Dual-Region Active-Passive (Iran Edge Proxy + EU Primary Core)
- **Architecture:**
  - **EU Core (Primary Datacenter):** Authoritative PostgreSQL 16 database, Redis queue, Celery workers, S3 private media vault, and primary Django API.
  - **Iran Edge (Stateless Proxy / Static CDN):** Nginx / HAProxy edge reverse proxy caching Next.js PWA static assets (HTML/CSS/JS/WASM), terminating local TLS, and tunneling dynamic API requests to EU Core over encrypted wireguard / TLS tunnel.
- **Strengths:** Solves frontend load latency in Iran; ensures PWA app-shell installs instantly even during international internet bandwidth throttling; maintains single source of truth for database without distributed replication conflicts.
- **Weaknesses:** Outbound international tunnel can experience jitter during severe national network isolation events.

### 3.5 Option E — Dual-Region Active-Active
- **Architecture:** Synchronous or asynchronous multi-master database replication between an Iranian datacenter (e.g. Asiatech / Afranet) and an EU datacenter.
- **Evaluation:** **Strictly Rejected for P0/MVP.**
  - Duplicating sensitive athlete health telemetry, progress photos (Tier 4), and personal identity across jurisdictions creates acute GDPR compliance conflicts and regulatory compliance complexity.
  - Resolving write conflicts on relational set logs and program assignments without CRDTs introduces catastrophic data corruption risk.

---

## 4. Legal, Privacy, and Data Residency Analysis

### 4.1 GDPR / EU Compliance Constraints
- Under EU GDPR (General Data Protection Regulation, Regulation (EU) 2016/679), personal data (Tier 1) and sensitive health-adjacent telemetry (Tier 3/4) of EU residents must not be transferred to third countries without adequate safeguards (Chapter V GDPR).
- Storing primary databases in the EU (e.g., Germany/Finland) satisfies EU sovereignty requirements.
- Any future caching of EU athlete data on non-EU edge servers would require explicit affirmative consent and standard contractual clauses (SCCs).

### 4.2 Persian / Iranian User Privacy & Sovereignty Considerations
- Iranian users benefit from low-latency static asset delivery and stable DNS resolution.
- Payment processing for Iranian bank cards (Phase 10) mandates direct communication with Shaparak-approved payment service providers (PSPs) from verified IP blocks.
- Maintaining application container neutrality ensures CoachOS can deploy edge proxies or dedicated regional backends if regulatory requirements mandate domestic residency for specific institutional clients.

---

## 5. Phase 04 Recommendation & Decision Gate

```
+-----------------------------------------------------------------------------+
|                            DEVELOPMENT PHASE 04                             |
|                                                                             |
|   +---------------------------------------------------------------------+   |
|   | Local Development Environment (Docker Compose)                      |   |
|   | - PostgreSQL 16 (pg_trgm, UUIDv7)                                   |   |
|   | - Redis 7 (Cache + Celery Broker)                                   |   |
|   | - Django 5 + DRF Backend Shell (:8000)                             |   |
|   | - Next.js 14 App Router PWA Shell (:3000)                           |   |
|   +---------------------------------------------------------------------+   |
|                                      |                                      |
|                                      v                                      |
|   +---------------------------------------------------------------------+   |
|   | Staging Pipeline (Automated CI/CD)                                  |   |
|   | - Single-Region EU Container Environment (Provider-Neutral)        |   |
|   | - Anonymized / Synthetic Test Data Only                             |   |
|   | - Ephemeral Preview Deployments                                     |   |
|   +---------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------+
                                       |
                   [FOUNDER DECISION GATE — PRE-PILOT]
                                       |
        +------------------------------+------------------------------+
        |                                                             |
        v                                                             v
+-------------------------------+             +-------------------------------+
| Path 1: Single-Region EU      |             | Path 2: Dual-Region Hybrid    |
| (Frankfurt / Hetzner Cloud)   |             | (EU Core + Iran Edge Proxy)   |
| - Fast, cost-effective launch |             | - High-resilience Iran PWA    |
| - Lowest operational overhead |             | - Direct Shetab gateway proxy |
+-------------------------------+             +-------------------------------+
```

### 5.1 Concrete Phase 04 Directives
1. **Container Portability:** Write all `Dockerfile` and `docker-compose.yml` definitions using vendor-neutral OCI-compliant base images (`python:3.11-slim`, `node:22-alpine`, `postgres:16-alpine`, `redis:7-alpine`).
2. **Environment Variable Decoupling:** Never hardcode cloud-specific storage endpoints or region keys. Use standard 12-factor configuration (`DATABASE_URL`, `REDIS_URL`, `S3_ENDPOINT_URL`, `S3_REGION_NAME`).
3. **No Cloud Credentials in Git:** CI workflows and repository files must contain zero AWS/Hetzner/Cloudflare API keys.
4. **Formal Decision Gate:** Production hosting choice remains deferred to Phase 13 (QA, Security, and Release), pending founder budget authorization and formal pre-DPIA review.
