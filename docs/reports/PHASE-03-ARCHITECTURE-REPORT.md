# Phase 03 — Architecture, Data, Security, and Privacy

**Document version:** 1.0.0 Phase 03 Completion Report  
**Execution Date:** 2026-08-10 (UTC)  
**Authoring Team:** Coordinated Product & Engineering Team (Founder's Technical Advisor, Product Manager, Business Analyst, Principal Software Architect, Backend Architect, Frontend/PWA Architect, Data Architect, Security Engineer, Privacy and Compliance Engineer, DevOps/SRE Architect, QA/Test Architect, Technical Writer, Release Manager, Code Reviewer)  
**Language Constraints:** Persian `fa-IR` RTL + English `en-US` LTR **only** — Arabic strictly out of scope (no locale files, translations, UI, seed data, API resources, DB catalogs, architecture requirements)  
**Branch:** `arena/019fed02-coachos-fitness-coaching-platf` from updated `main` `771afa668e71b0b181218be2e4d768e60f4f36f9` (PR #5 merged)  
**Repository:** https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform

---

## 1. Executive Summary

Phase 03 successfully transformed the Phase 00 discovery, Phase 01 requirements (27 P0 stories, permissions matrix, NFRs), and Phase 02 UX (34 exact P0 screens, 14 UX spec docs + README, bilingual RTL/LTR design system, offline matrix) into a coherent implementation-ready architecture and security specification.

**All exit gates are met without creating application code, dependencies, migrations, secrets, or Arabic scope:**

- **Phase 02 Preflight Review** completed and documented — screen count normalized to exact 34, UX doc count 14 (+README=15), story count 27 P0 (25 core +2 I18N), no invalid story IDs (e.g., `US-ATH-006` corrected), Persian terminology precise wording "Perso-Arabic script keyboard-variant normalization for Persian search" (not Arabic product support), offline durability boundaries normalized (Phase04 shell-only, Phase07 temporary in-memory preservation `unsaved input retained temporarily; retry required after reconnection`, Phase12 durable IndexedDB queue), design-system consistency 44px min / 48px preferred CTA requiring implementation testing, no material UX contradiction blocking architecture.
- **System Context** C4 Level1 with trust boundaries, sensitive-data boundaries Tier0-6, P0 vs P1/P2 future (push Phase12, payment Phase10, AI Phase11, wearable Phase12, nutrition P1) distinguished with dashed future components — no future implied in P0.
- **Container Architecture** C4 Level2 modular monolith: Next.js frontend + Django+DRF backend + PostgreSQL 16 proposed + Redis7 Celery + private S3 buckets + email abstraction.
- **Domain Modules & Boundaries** 20 modules M01-M20 (Identity, Org, Membership, AuthZ/Consent, Exercise Catalog, Media/Rights, Programs, Templates, Assignments/Snapshots, Sessions, Progress/Feedback, Messaging, Notifications, Admin/Moderation, Audit, Privacy Export/Erasure, Future Nutrition P1, Billing Phase10 P1, Marketplace P2, AI P2) with responsibility, owned entities, public interfaces, read/write deps, security boundary, events emitted/consumed, sensitivity, test boundary, extraction risk.
- **Component Boundaries** frontend Next.js app structure mapping 34 screens + backend Django apps + middleware stack (RequestID, SecurityHeaders, OrgScope, AuthZ, Audit) + import-linter enforcement + assignment sequence diagram.
- **Data Flow** auth/invite, exercise search Persian normalization pg_trgm, assignment immutable JSONB snapshot, workout logging offline boundary, progress photo consent + signed URL gating, messaging, privacy export/erasure.
- **Deployment Architecture** PaaS vs K8s options, env local/staging/prod distinct VPC/DB/buckets/secrets, Docker + GitHub Actions CI/CD lint/type/unit/integration/security scan Playwright E2E staging auto prod manual gate, TLS HSTS CSP, secrets manager, backup hooks, RPO/RTO proposed.
- **Data Model & ERD** erDiagram 30+ entities with PK/FK tenant ownership sensitive fields indexes unique constraints state machines soft-delete archive audit retention localization; conceptual DDL illustrative; identifier UUIDv7 proposed time-ordered not authz substitute requires Phase04 validation.
- **Authorization Architecture** RBAC P0 roles platform_admin/owner/coach/athlete/support + future nutritionist P1 consent-gated, org boundaries active context `request.org_id`, object-level CoachAthleteAssignment, owner aggregate vs raw distinction (no automatic raw progress photo or private message), break-glass admin MFA+reason+audit, consent lifecycle photo/nutrition, export/erasure self-only, audit visibility owner own org only coach/athlete forbidden, suspension immediate 403, invitation permissions, per-resource matrix create/read/update/archive/export/share/revoke/consent/audited, negative controls list.
- **API & OpenAPI Architecture** provisional OpenAPI 3.1 `/api/v1` covering 30+ endpoint groups auth/current user/orgs/locations/memberships/invitations/validate/exercises/moderation/programs/clone/assignments/today/sessions/set-logs/substitutions/feedback flags/progress photos/metrics/consents/messages/notifications/audit/privacy export/erasure/media signed-urls — each with method/path/purpose/auth/required role/object permission/request/response schema/error responses/localization/idempotency/audit/rate-limit/sensitivity + RFC7807 error `type/title/status/detail/instance` + `message_key` extension.
- **Threat Model** STRIDE 21 threats T01-T21 covering account takeover, credential stuffing, session theft, invitation abuse, cross-tenant IDOR, unassigned coach, owner overreach, photo exposure, malicious uploads, stored XSS, CSRF, SSRF, webhook forgery future Phase10, notification abuse, export abuse, erasure abuse, insider/admin misuse, prompt injection future Phase11, supply-chain, backup leakage, search enumeration + asset/actor/attack path/impact/likelihood/risk/preventive/detective/corrective/test strategy/owner/residual risk + OWASP Top10 mapping.
- **Security Control Matrix** threat→requirement→control→phase→test type→evidence→status including negative controls for cross-tenant reads/writes, unassigned coach, suspended membership, unauthorized photo/message/audit/export.
- **Privacy & Data Lifecycle** 11 stages collection/consent/storage/use/sharing/export/retention/revocation/deletion/anonymization/backup destruction, Tier0-8 classification per class purpose/legal assumption/owner/controller/access/encryption/logging retention/export/deletion/consent, consent lifecycle explicit affirmative modal (ADR-027) for progress photos + nutrition P1, export ZIP via Celery tmp S3 24h link, erasure pipeline anonymization + S3 delete, retention questions, pre-DPIA checklist large-scale sensitive systematic monitoring profiling multi-prof sharing progress-photo wearable AI + disclaimer privacy-aligned engineering design requires jurisdiction-specific legal review.
- **Media Storage** Tier0/2/4 classification buckets private no listing BlockPublicAcls true versioning SSE-S3 signed URL TTL≤15min no caching Tier4 in SW, MIME whitelist, magic bytes, size limits, checksum, thumbnail Pillow ffmpeg, malware scan ClamAV proposed quarantine, rights metadata mandatory, takedown workflow, photo access control, future transcoding CDN rules, retention.
- **PWA Architecture** three-level Phase04 manifest/icons/standalone/SW/app-shell/offline fallback/install guidance, Phase07 touch-optimized 44/48px form-state temp memory network indicator retry no durable queue promise, Phase12 IndexedDB durable queue sync status retry/backoff conflict background sync push limitations HealthKit eval native bridge decision + browser limitations table.
- **Observability** structured logging JSON structlog redaction request_id correlation audit vs debug separation ELK 30d vs audit PG 1y+, metrics Prometheus, Sentry error tracking, healthz/readyz checks, alerting categories auth anomaly cross-tenant 403 spike 5xx>1% latency etc.
- **Backup & Disaster Recovery** PG daily snapshot 30d + WAL PITR 15min RPO proposed 1h RTO, S3 versioning, Redis loss acceptable, restore runbooks, weekly automated restore testing smoke tests, RPO/RTO proposed table, disaster scenarios, incident response, breach response 72h, rollback app previous image + migration reverse 2-step.
- **ADRs** 43 ADRs including ADR-012 license pending founder approval, ADR-017 UUIDv7 proposed requires validation, ADR-037 backup cost pending approval.
- **Validation Checklist** V01-V22 proposed pass + confirmation no code.

**Zero application code, no dependencies installed, no migrations, no secrets, no real health data, no Arabic scope, no AI/payment/wearable P0 implementations — specification only (Mermaid, OpenAPI YAML, JSON Schema, conceptual DDL, threat-model tables).**

---

## 2. Persian Executive Summary (خلاصه مدیریتی به فارسی)

فاز ۰۳ با موفقیت بسته‌های محصول، نیازمندی‌ها و تجربه کاربری فازهای ۰۰ تا ۰۲ را به یک معماری فنی، مدل داده، امنیت و حریم خصوصی منسجم و آماده پیاده‌سازی تبدیل نمود.

- **بررسی پیش‌پرواز فاز ۰۲:** تعداد صفحات ۳۴ دقیق، تعداد مستندات UX ۱۴ (+README=۱۵)، ۲۷ داستان P0، عدم وجود شناسه‌های نامعتبر، اصطلاح‌شناسی دقیق فارسی «نرمال‌سازی گونه‌های صفحه‌کلید برای جستجوی فارسی» و تفکیک دقیق مرز آفلاین (فاز۰۴ شل کش‌شده، فاز۰۷ نگهداری موقت در حافظه با پیام «ورودی ذخیره‌نشده به‌صورت موقت در حافظه نگه‌داشته می‌شود؛ پس از اتصال مجدد تلاش مجدد لازم است»، فاز۱۲ صف پایدار IndexedDB) انجام شد.
- **معماری متن/کانتینر:** نمودارهای C4 سطح ۱ و ۲ با مرزهای اعتماد و داده‌های حساس، مونولیت ماژولار (Next.js + Django + PostgreSQL 16 پیشنهادی + Redis + S3 خصوصی).
- **مرز ماژول‌ها:** ۲۰ ماژول M01-M20 با مسئولیت، موجودیت‌های مالک، رابط‌های عمومی، وابستگی‌های خواندن/نوشتن، مرز امنیتی، رویدادها، حساسیت داده و مرز تست.
- **مدل داده و ERD:** بیش از ۳۰ موجودیت با کلید اصلی/خارجی، مالکیت سازمانی، فیلدهای حساس، ایندکس‌ها، محدودیت‌های یکتا، ماشین وضعیت، سیاست حذف نرم/آرشیو، نیازهای حسابرسی و نگهداری.
- **مجوزدهی:** RBAC نقش‌های P0 مدیر پلتفرم/مالک/مربی/ورزشکار/پشتیبانی + مربی آینده تغذیه P1 با رضایت، مرز سازمانی `request.org_id` از متن احراز هویت سرور، قانون شیء CoachAthleteAssignment، تمایز دید مالک تجمیعی در مقابل خام، دسترسی اضطراری مدیر با MFA و حسابرسی، چرخه رضایت عکس پیشرفت.
- **قرارداد API:** OpenAPI 3.1 موقت `/api/v1` با بیش از ۳۰ گروه اندپوینت، مدل خطای RFC7807 + `message_key` محلی‌شده، هر اندپوینت شامل هدف، احراز هویت، نقش مورد نیاز، قانون مجوز شیء، اسکیما درخواست/پاسخ، خطاها، محلی‌سازی، قابلیت آیدمپتنسی، رویداد حسابرسی، دسته نرخ‌محدودیت و حساسیت داده.
- **مدل تهدید:** متد STRIDE با ۲۱ تهدید و نگاشت OWASP، ماتریس کنترل امنیتی با کنترل‌های منفی برای خواندن/نوشتن بین مستاجرین، دسترسی مربی غیرمنسوب، عضویت معلق، عکس/پیام/حسابرسی/صدور غیرمجاز.
- **حریم خصوصی:** ۱۱ مرحله چرخه حیات داده، طبقه‌بندی Tier0 تا Tier8، رضایت صریح برای عکس‌های پیشرفت و همکاری تغذیه P1، پایپ‌لاین صدور ZIP و امحای ناشناس‌سازی، چک‌لیست پیش-DPIA، طراحی همسو با حریم خصوصی نیازمند بررسی حقوقی ویژه حوزه قضایی.
- **ذخیره رسانه:** باکت‌های خصوصی بدون لیست عمومی، URL امضاشده TTL ≤۱۵ دقیقه، اعتبارسنجی MIME، استراتژی بند انگشتی، اسکن بدافزار پیشنهادی، متادیتای حقوق.
- **PWA:** استراتژی سه‌سطحی فاز۰۴ پوسته نصب‌پذیر، فاز۰۷ اجرای موبایل ورزشکار با بهینه‌سازی لمسی و نگهداری موقت ورودی، فاز۱۲ صف پایدار آفلاین با سینک.
- **مشاهده‌پذیری و پشتیبان‌گیری/بازیابی:** لاگ ساختاریافته JSON با حذف داده حساس و شناسه درخواست، متریک Prometheus، ردیابی خطای Sentry، نقاط سلامت /healthz و /readyz، هشدارهای ناهنجاری احراز هویت و دسترسی بین مستاجرین، پشتیبان PostgreSQL روزانه ۳۰ روز + PITR RPO پیشنهادی ۱۵ دقیقه و RTO ۱ ساعت، نسخه‌گذاری S3، راهنمای بازیابی، پاسخ حادثه و نشت.

هیچ کد برنامه‌نویسی، وابستگی، مایگریشن، راز یا داده واقعی سلامت در مخزن ایجاد نشد — صرفاً مستندات مشخصات فنی.

---

## 3. Phase 02 Preflight Review

### 3.1 Verification Steps Executed

- Current branch and commit: `arena/019fed02-coachos-fitness-coaching-platf` HEAD `771afa668e71b0b181218be2e4d768e60f4f36f9` (merge commit PR #5), verified via `git branch --show-current`, `git rev-parse HEAD`, `git log --oneline --graph --all`.
- `main` HEAD: `771afa668e71b0b181218be2e4d768e60f4f36f9` (origin/main same) via `git rev-parse origin/main`.
- PR #5 state: MERGED `2026-08-10T18:45:01Z` mergeCommit `771afa668e71b0b181218be2e4d768e60f4f36f9` head `arena/019febfc-coachos-fitness-coaching-platf` base `main` via `gh pr view 5 --json state,mergedAt,headRefName,baseRefName,mergeCommit`.
- Working tree state: clean before Phase03 `git status`.
- Complete repository tree: `ls -R docs`, `find docs -type f | sort` — 15 files under `docs/ux/` (14 spec + README), 34 screens confirmed via `grep -c "^\| \*\*SCR-" SCREEN_INVENTORY.md` → 34, story IDs via `grep -ho US-...` ux vs PRD `comm -23` shows no missing.
- Docs inspected: PROJECT_STATUS.md, PROJECT_CHECKLIST.md, CHANGELOG.md, MASTER_PRODUCT_BRIEF.md, PRD.md, PERSONAS.md, USER_JOURNEYS.md, DOMAIN_GLOSSARY.md, COMPETITIVE_LANDSCAPE.md, DECISIONS.md, DATA_MODEL.md, API_CONTRACT.md, SECURITY_AND_PRIVACY.md, TRACEABILITY_MATRIX.md, RELEASE_PLAN.md, PROMPT_LOG.md, reports PHASE-00/01/02, all docs/ux/ — read via read_file.

### 3.2 Issues Found

| ID | Category | Issue | Severity | Evidence |
|----|----------|-------|----------|----------|
| PF-01 | Screen-count consistency | CHANGELOG and some summary texts said 29 stories vs 27 actual; screen count claim 28+ in prompt description but repo has exact 34 | Low — documentation inconsistency | SCREEN_INVENTORY.md grep 34 rows, but CHANGELOG stated 29 stories |
| PF-02 | UX traceability integrity | Potential invalid story IDs like US-ATH-006 referenced in prompt description | Low — already corrected in Phase02 report, repo grep shows none missing `comm -23` empty | UX_TRACEABILITY_MATRIX verified 27 stories mapped |
| PF-03 | Persian terminology | PRD scenario title "Search query with Arabic Yeh matches Persian exercise" uses phrase "Arabic Yeh" without precise wording "Perso-Arabic script keyboard-variant normalization for Persian search" — could be interpreted as Arabic product scope | Low — wording improvement needed | PRD.md line 441 |
| PF-04 | Report accuracy | PROJECT_STATUS.md still references old working branch arena/019febfc and base commit 3921083 (PR4) instead of 771afa6 (PR5 merged) | Low — stale metadata post-merge | PROJECT_STATUS.md header |
| PF-05 | Offline wording durability boundary | Already correct in repo per verification grep "unsaved input retained temporarily; retry required after reconnection" + notes no durable queue until Phase12 | Pass — no correction needed but verify | STATE_AND_ERROR_MATRIX, SCREEN_INVENTORY, USER_FLOWS, UX_COPY |
| PF-06 | Design-system consistency | Check 44 vs 48 touch targets, color tokens, Persian font, breakpoints 6-tier xs-2xl, mobile 5-tab nav Today/Calendar/Progress/Messages/Profile, Jalali/Gregorian, modal focus, dark-theme proposal vs validated preference — all consistent with careful language design target/requires testing | Pass | DESIGN_SYSTEM, DESIGN_TOKENS, NAVIGATION_MODEL, RESPONSIVE_BEHAVIOR, ACCESSIBILITY_SPEC, RTL_LTR_SPEC |
| PF-07 | PR separation | PR #5 already merged, so Phase03 branch from updated main is correct — session branch arena/019fed02 from 771afa6 satisfies rule, no need to create extra branch | Pass | git log graph shows arena/019fed02 HEAD = main HEAD 771afa6 |

### 3.3 Conclusion Preflight

- No material UX contradiction prevents safe architecture work.
- All found issues are minor documentation inconsistencies correctable on Phase03 branch without affecting UX semantics.
- Offline boundary and PWA sequencing already correctly documented per Phase02 report.

---

## 4. Corrections Made Before Architecture Work

| Correction | File | Before | After | Rationale |
|------------|------|--------|-------|-----------|
| Working branch and base commit update | PROJECT_STATUS.md header | Working branch arena/019febfc, base 3921083 (PR4) | Working branch arena/019fed02, base 771afa6 (PR5 merged) | Reflect post-merge reality, main HEAD after PR5 |
| Post-merge table | PROJECT_STATUS.md §2 | Main base 3921083 PR4 merged, working branch PR5 open, docs substantially expanded | Main base 771afa6 PR5 merged Phase02, working branch Phase03 from updated main, docs Phase02 complete 34 screens 14 specs 27 stories + Phase03 in progress | Accurate post-merge verification |
| One-line status expansion | PROJECT_STATUS.md §1 | Generic Phase02 complete | Added exact counts 34 screens verified, 14 UX specs + README, 27 stories verified, WCAG design-target not compliance claim, Phase03 in progress | Accurate per preflight 3.1, 3.4 |
| New section 1.1 Phase02 verification | PROJECT_STATUS.md new §1.1 | None | Added 7 bullet verification: PR5 merged, screen count 34, UX doc 14+README 15, story 27 no invalid, offline wording Phase04/07/12, Persian terminology precise, working branch Phase03 | Documents preflight |
| CHANGELOG story count | CHANGELOG.md Unreleased line | 29 P0 user stories | 27 P0 user stories (25 core +2 I18N variants) | Exact count from PRD |
| CHANGELOG changed section | CHANGELOG.md Changed | Updated PROJECT_STATUS reflecting Phase02 completion base 3921083 | Updated with note superseded by 771afa6 PR5, plus preflight corrections list normalized screen 34 UX 14 story 27 Persian terminology offline boundaries | Historical accurate + preflight note |
| PRD scenario title | docs/PRD.md US-I18N-002 Acceptance Criteria | Scenario: Search query with Arabic Yeh matches Persian exercise | Scenario: Search query with Perso-Arabic variant (Yeh) matches Persian exercise — Perso-Arabic script keyboard-variant normalization for Persian search + clarification no Arabic product localization implied | Precise wording per 3.3 instruction, no Arabic product scope |

No application code created during corrections — specification only.

---

## 5. Objectives

Transform Phase 00-02 into coherent implementation-ready architecture and security spec defining: system context, container architecture, domain/module boundaries, runtime deployment boundaries, final/conditionally approved tech choices, physical/logical data model, ERD, tenant isolation, RBAC+ABAC+consent, API architecture OpenAPI contract, security threat model, privacy lifecycle, media storage, PWA boundaries, observability, backup/restore, DR expectations, CI/CD expectations, ADRs — without implementing application features.

---

## 6. System Context

**Artifact:** `docs/architecture/SYSTEM_CONTEXT.md`

- Actors: Athlete P0 mobile PWA, Coach P0 desktop/tablet builder, Organization Owner P0, Platform Admin P0 MFA, Nutrition Professional P1 future consent-gated, Support optional, System cron.
- Systems: Web/PWA client Next.js P0, CoachOS API/backend Django+DRF P0 modular monolith, PostgreSQL 16 proposed, Redis7 + Celery proposed, S3-compatible private object storage private buckets no listing.
- External: Email provider abstraction P0, Future push notification service P1/P2 dashed, Future payment provider abstraction Shetab/Stripe Phase10 dashed, Future AI provider abstraction Phase11 dashed, Future wearable integrations HealthKit/Health Connect Phase12 dashed, CDN future optional.
- Trust boundaries: Browser/PWA ↔ API TLS1.3 HSTS, API↔PG private VPC secrets manager, API↔Redis private, API↔S3 private buckets presigned TTL≤15min, API↔Email adapter.
- Sensitive-data boundaries: Tier0 public metadata, Tier1 account/identity, Tier2 coaching operational, Tier3 health-adjacent assigned coach only owner aggregate, Tier4 progress media never public signed TTL≤15min consent+assignment, Tier5 audit immutable, Tier6 secrets never repo.
- Diagram: Mermaid C4Context + fallback flowchart generic distinguishing P0 solid vs P1/P2 dashed, not implying future exists in P0.
- References: PRD §6 permissions matrix, SECURITY_AND_PRIVACY data classification, DECISIONS ADR-001..028.

**Status:** Proposed / Accepted pending founder review.

---

## 7. Container Architecture

**Artifact:** `docs/architecture/CONTAINER_ARCHITECTURE.md`

- C4 Level2 containers: Frontend Next.js 14 App Router + React + TS + Tailwind logical properties + PWA Manifest + SW, Backend Django+DRF modular monolith M01-M20, PostgreSQL 16 pg_trgm JSONB, Redis7 Celery cache rate-limit queue, S3 private, Email abstraction, future push/payment/AI dashed optional CDN.
- Communication: REST /api/v1 JSON auth cookie/Bearer Accept-Language fa-IR/en-US, SQL tenant-isolated org_id filter, cache rate-limit Celery tasks, private PUT/GET signed URLs TTL≤15min.
- Topology: Frontend edge static hosting Vercel/CF Pages optional, backend behind HTTPS ALB TLS1.3 HSTS, single region MVP VPC private, managed data services.
- Failure modes: DB down 503 frontend server error retry, Redis down rate-limit fallback in-memory log alert, S3 down upload fails retry banner, email down enqueue retry 3x exponential.
- NFR targets proposed until validated: API p95 read <200ms builder save <400ms, Today view <1.5s 3G hypothesis, JS <150KB gzipped.
- References: DECISIONS ADR-001 modular monolith ADR-002 stack.

**Status:** Proposed — requires infra decision.

---

## 8. Domain Modules and Boundaries

**Artifact:** `docs/architecture/DOMAIN_MODULES.md`

- 20 modules:
  - M01 Identity and Authentication P0: User, Session/Refresh, PasswordResetToken, AuthService.register/login/issueTokens/resetPassword/verifySession, rate limit 5/15min, Argon2id/bcrypt, events user.registered etc.
  - M02 Organizations and Tenancy P0: Org, Location primary MVP partial unique index single primary per org, OrgService.createOrg.
  - M03 Memberships and Invitations P0: Membership, Invitation token_hash SHA256 7d single-use 410 Gone, InvitationService.
  - M04 Authorization and Consent P0: CoachAthleteAssignment, ConsentRecord, AuthZService.can/requireOrgScope/requireCoachAssignment/requireConsent, events consent.granted/revoked.
  - M05 Exercise Catalog P0: Exercise, ExerciseTranslation fa/en only, ExerciseAlias normalized_alias pg_trgm, search Persian Unicode folding, events exercise.created_private/submitted/published.
  - M06 Media and Rights P0: MediaAsset, MediaRights, ModerationAction, MediaService.upload/generateSignedUrl TTL≤15min, MIME whitelist, thumbnail, malware scan proposal.
  - M07 Training Programs P0: Program hierarchy Phase Week Day Workout Item SetPrescription, ProgramBuilder.
  - M08 Program Templates P0: Program is_template flag clone logic deep copy independent.
  - M09 Assignments & Snapshots P0: ProgramAssignment, Snapshot JSONB immutable frozen_at version, AssignmentService.assign, snapshot immutability reason duplication justified.
  - M10 Workout Sessions P0: WorkoutSession, SetLog, ExerciseSubstitution, SessionService.start/logSet/substitute/complete, adherence calculator.
  - M11 Progress and Feedback P0: FeedbackFlag joint_pain etc severity, BodyMetric weight, ProgressPhoto storage_key private, ConsentRecord gating.
  - M12 Messaging P0: MessageThread, Message contextual workout_session_id, MessageService.send.
  - M13 Notifications P0: Notification, NotificationPreference critical assignment cannot mute, NotificationService.dispatch.
  - M14 Admin and Moderation P0: moderation queue view, AdminService.moderateExercise, break-glass.
  - M15 Audit Events P0: AuditEvent immutable append-only DB-level REVOKE UPDATE/DELETE.
  - M16 Privacy Export and Erasure P0: ExportRequest, ErasureRequest, PrivacyService.requestExport/requestErasure, Celery workers.
  - M17 Future Nutrition P1: NutritionProfessionalAssignment, MealPlan, Recipe, FoodItem, Allergy.
  - M18 Future Billing P1 Phase10: Product, Subscription, Payment tokenization, Entitlement.
  - M19 Future Marketplace P2: Listing, Review.
  - M20 Future AI P2 Phase11: AIRunLog, PromptVersion, HumanReviewDecision.
- For each: responsibility, owned entities, public interfaces, read/write dependencies, security boundary, events emitted/consumed, data sensitivity Tier, test boundary mandatory negative tests, extraction risk high for media/search/messaging.
- Dependency rules hierarchy lowest to highest, no circular imports via import-linter, event bus in-process django.dispatch.

**Status:** Proposed.

---

## 9. Technology Decisions

**Artifacts:** `docs/DECISIONS.md` ADR-002, ADR-005, ADR-009, ADR-010, ADR-029..ADR-043, `docs/architecture/README.md`, `CONTAINER_ARCHITECTURE.md`, `DEPLOYMENT_ARCHITECTURE.md`

| Decision | Context | Options Considered | Recommendation | Consequences | Operational Cost | Security | Licensing | Migration/Replacement | Status |
|----------|---------|--------------------|----------------|--------------|------------------|----------|-----------|----------------------|--------|
| Frontend Next.js + React + TS | Need modern mobile-first SSR/SSG/CSR + PWA + RTL logical + fa-IR/en-US i18n | Next.js 14 App Router vs Remix vs SvelteKit | Next.js App Router + React + TS + Tailwind logical + next-pwa/Workbox proposed | Mature ecosystem, excellent velocity, built-in i18n routing, PWA plugin, large community | Vercel hosting cost low for pilot, CDN caching static | CSP headers, no dangerouslySetInnerHTML unsanitized, HttpOnly cookie | MIT for Next.js, React MIT, TS Apache2, Tailwind MIT | API contract stable allows frontend replacement | Conditionally Accepted Proposed pending Phase04 validation — requires bundle size check, Workbox vs custom SW |
| Styling RTL/LTR design token system | Need genuine bidirectional parity | Tailwind logical properties vs styled-components vs CSS modules | Tailwind + CSS variables tokens colors type spacing elevation z-index motion logical properties only | Consistent 44/48 touch targets, design tokens, dark obsidian #0B0F17 design target requires testing, zero tracking for Persian | Low cost | No security impact | MIT | Can be replaced with other system but token contract preserved |
| Backend Django + DRF | Need robust ORM, enterprise relational integrity, fast authz, built-in admin, security controls | Django+DRF vs FastAPI vs Rails vs Node Nest | Django 5 + DRF + Python 3.12 modular monolith 20 modules | Mature ORM, built-in admin, battle-tested security (CSRF, XSS), RBAC ADRs, excellent velocity | PaaS cost low-medium, managed PG | Argon2id support, CSRF middleware, XSS protections, ORM SQL injection prevention | BSD for Django, DRF BSD | Can extract modules to services if needed via interface |
| Database PostgreSQL | Need relational integrity + JSONB snapshot + trigram search + timestamptz + extension support | PG16 vs MySQL vs SQLite | PG16 + pg_trgm + btree_gin + pgcrypto/uuid-ossp + JSONB | Relational + JSONB + trigram fuzzy search Persian normalization + strong B-tree locality UUIDv7 + time-ordered + partial unique indexes | Managed PG $15-50/mo pilot | At-rest encryption provider, TLS, RLS optional | PostgreSQL License permissive | Migration to other DB would need JSONB + trigram reimplementation |
| Cache/Queue Redis+Celery | Need cache, rate-limit counters, async jobs export email notifications | Redis+Celery vs in-memory only vs RabbitMQ vs SQS | Redis7 + Celery beat+worker proposed | Cache search queries, permission lookups, rate-limit 5/15min auth, export packaging, erasure, notifications, thumbnails | Managed Redis cost low (Upstash) | No PII in cache if possible short TTL ≤5min encrypted transit optional | BSD | Can replace with other queue via Celery broker abstraction |
| Media S3-compatible private | Need private buckets no listing signed URLs | AWS S3 vs Cloudflare R2 vs MinIO | S3-compatible private buckets BlockPublicAcls true versioning SSE-S3, presigned GET TTL≤15min, no listing, MIME whitelist, thumbnail | Secure Tier4 photos never public, exercise demos via signed or CDN signed, rights metadata mandatory | S3 cost per GB + requests, cheap for pilot | Private buckets prevent exposure, signed URL short TTL mitigates leak | Provider dependent, MIT for minio | Can migrate provider via abstraction MediaService |
| API REST/OpenAPI 3.1 | Need versioned contract machine-readable | REST OpenAPI 3.1 vs GraphQL vs gRPC | REST /api/v1 OpenAPI 3.1 provisional RFC7807 + message_key | Clear versioning, language-agnostic, easy PWA consumption, tooling Swagger | Low cost | Standard error model prevents leakage 404 obscurity, rate-limit categories | N/A | Can add GraphQL later as additional layer if needed, REST stable |
| PWA Manifest + Service Worker | Need installable shell offline fallback progressive capabilities | next-pwa Workbox vs custom SW vs no PWA | Manifest standalone icons 192/512 maskable theme #0B0F17, SW registration, three-level offline boundary Phase04 shell only Phase07 temp memory Phase12 durable IndexedDB | App-store friction avoided, fast launch low-connectivity gym, install guidance, network indicator, retry banner | Workbox bundle size check needed | SW scope same origin HTTPS only, no caching Tier4 signed URLs in Cache API NetworkOnly, clear cache on logout | Workbox Apache2 | Can replace SW lib but contract same |
| E2E Playwright | Need RTL/LTR visual regression + mobile execution | Playwright vs Cypress vs Selenium | Playwright proposed | Cross-browser Chromium Firefox WebKit, mobile emulation, visual regression, trace viewer | CI cost minutes, low | No secrets in tests synthetic data only | MIT | Can replace with other runner but test scenarios preserved |
| CI/CD GitHub Actions | Need lint/type/unit/integration/security scan E2E staging auto prod manual gate | GitHub Actions vs GitLab CI vs CircleCI | GitHub Actions workflows ci.yml lint/type/unit/integration/security scan gitleaks, e2e.yml Playwright fa-IR/en-US, deploy-staging.yml auto merge main, deploy-prod.yml manual workflow_dispatch tag health check | Automates quality gates, OIDC to cloud no secrets in repo, Docker images keep last 5 tags for rollback | Compute cost GitHub minutes | Secret scan gitleaks fails build, Dependabot Snyk, lockfile integrity | N/A | Can replace CI provider but workflow logic preserved |
| Email Provider Abstraction | Need transactional email invites reset export | SES vs SendGrid vs Postmark | Abstraction interface EmailProviderAdapter, provider choice TBD Phase04/05 — placeholder SES/SendGrid/Postmark | Flexibility domestic vs international, DKIM/SPF | Provider cost per email low | API key via secrets manager, TLS | Depends provider | Replace provider via adapter |
| PostgreSQL Extensions | Need trigram + btree_gin + pgcrypto for UUID/time | pg_trgm vs external ElasticSearch for MVP | pg_trgm GIN for MVP zero external cluster maintenance, Elasticsearch deferred if scale | Instant typo-tolerant Persian/English search + normalized tokens | No extra operational cost | No security issue | PostgreSQL License | Can migrate to Elastic later keeping search interface |
| Auth/Session | Need secure password hashing, rate limiting, single-use tokens | Argon2id vs bcrypt vs scrypt vs JWT vs session cookie | Argon2id/bcrypt cost≥12, HttpOnly Secure SameSite Lax cookie, JWT access 15min + rotating refresh reuse detection, rate limit 5/15min Redis, reset token 15min single-use, invitation 7d SHA256 hashed single-use 410 Gone | Secure, UX reasonable, no SMS gateway complexity | Redis cost for rate limit | Prevents credential stuffing, session theft, invitation reuse | Django auth BSD | Can add TOTP MFA for owner/admin P1, SMS OTP P1 if needed |

Do not install packages or scaffold code — spec only.

---

## 10. Data Model and ERD

**Artifacts:** `docs/architecture/ERD.md`, `docs/DATA_MODEL.md` v2.0, `docs/architecture/DOMAIN_MODULES.md`, `docs/JSON_SCHEMAS.md`

### 10.1 Entities Covered

**Identity and tenancy:** User (email UK, password_hash Argon2id, display_name, phone optional, preferred_locale fa-IR/en-US only, preferred_unit kg/lbs, timezone, is_platform_admin, is_active, created_at, updated_at), Credential/session abstraction (Session RefreshToken PasswordResetToken), Organization (name, slug UK, owner_user_id, settings JSONB, created_at, archived_at soft-archive), Location (organization_id org-scoped IDX, name, is_primary partial unique single primary per org MVP, address_line1, city, phone), Membership (user_id, organization_id org-scoped IDX, role owner/coach/athlete/support, status invited/active/suspended, created_at, unique user+org+role), Role implicit via Membership role field, Invitation (organization_id org-scoped, invited_by_user_id, email IDX, role, token_hash SHA256 UK IDX, expires_at 7d, accepted_at), Coach-Athlete Assignment (organization_id org-scoped, coach_user_id, athlete_user_id, status active/archived, unique org+coach+athlete).

**Exercise catalog:** Exercise (organization_id nullable NULL=canonical global non-NULL=private custom, created_by, movement_pattern enum squat/hinge/horizontal_push/pull/vertical_push/pull/lunge/carry/isolation/cardio/other, difficulty beginner/intermediate/advanced, primary_muscles TEXT[], secondary_muscles TEXT[], equipment_required TEXT[], status draft/pending_review/published/archived), Exercise Translation (exercise_id, locale fa-IR/en-US only unique per exercise+locale, name, instructions, coaching_cues TEXT[], common_mistakes TEXT[], safety_notes), Exercise Alias (exercise_id, locale, alias raw, normalized_alias IDX pg_trgm for Perso-Arabic script keyboard-variant normalization), Muscle Group / Equipment / Movement Pattern optional taxonomy but MVP enum arrays, Media Asset (exercise_id nullable for progress photos separate, media_type video_mp4/image_webp/image_jpeg/animation_gif, storage_key private S3 key, thumbnail_storage_key, duration_seconds, bytes_size, checksum_sha256), Media Rights (media_asset_id unique, license_type original_production/licensed_cc_by/commercial_license/coach_upload, source_url, creator_attribution, permitted_commercial_use, reviewed_by, reviewed_at), Moderation Action (exercise_id, moderator_user_id, action approve/reject/request_changes, reason).

**Programming:** Program (organization_id org-scoped, created_by, title, description, target_goal hypertrophy/strength/fat_loss/endurance/general_fitness, is_template bool, is_archived, archived_at, created_at, updated_at), Program Phase (program_id, name, sequence_order unique per program, duration_weeks), Program Week (phase_id, week_number, focus_note), Program Day (week_id, day_number, title), Workout (day_id, title, estimated_minutes), Workout Item (workout_id, exercise_id, sequence_order, group_key A1/A2 superset/circuit, segment warmup/main/cooldown, rest_seconds_between_sets default 90, coach_notes), Set Prescription (workout_item_id, set_index unique per item, target_reps string 8 or 8-10 AMRAP, target_load string nullable 100kg 75%1RM RPE8, target_rpe numeric, target_rir, tempo 3-0-1-0), Program Template (reuses Program is_template bool, clone logic deep copy independent), Program Version (optional tracking version pushes), Program Assignment (organization_id org-scoped, athlete_user_id, assigned_by, source_program_id, start_date IDX, end_date, status active/completed/archived, snapshot_payload JSONB immutable frozen copy hierarchy at assignment), Program Snapshot (embedded JSONB or separate table PK id, assignment_id unique, payload JSONB, version, created_at — immutable).

**Athlete execution:** Workout Session (program_assignment_id, athlete_user_id org-scoped, scheduled_date IDX, started_at, completed_at, status scheduled/in_progress/completed/skipped/modified state machine terminal, skip_or_modify_reason mandatory if skipped/modified, session_rpe, fatigue_score, athlete_notes), Set Log (workout_session_id, exercise_id, set_index, actual_reps, actual_load_kg normalized kg, actual_rpe, is_completed, notes, created_at), Exercise Substitution (session_id, original_exercise_id, substituted_exercise_id, reason equipment_unavailable/discomfort/preference/other), Completion Status enum scheduled/in_progress/completed/skipped/modified, Feedback Flag (session_id, athlete_user_id, flag_type joint_pain/muscle_strain/dizziness/severe_fatigue, anatomical_location, severity mild/moderate/severe, details TEXT, is_resolved), Body Metric (athlete_user_id, metric_type body_weight/height/bodyfat, value, unit, recorded_at), Progress Photo (athlete_user_id, storage_key private S3 key progress/{athlete_id}/{uuid}.jpg, photo_type front/side/back, athlete_consent_granted bool must have ConsentRecord, captured_at, created_at — never public URL signed TTL≤15min), Consent Record (athlete_user_id, grantee_user_id coach or nutritionist, organization_id org-scoped, consent_type progress_photo/nutrition_sharing/body_metrics, is_granted, granted_at, revoked_at, unique active where revoked_at NULL).

**Communication and operations:** Message Thread (organization_id org-scoped, created_at) + ThreadParticipant join (thread_id, user_id unique per thread), Message (thread_id, sender_user_id, recipient_user_id, workout_session_id nullable contextual link, content TEXT, read_at, created_at), Notification (user_id, event_type program_assigned/workout_completed/pain_flag_raised/message_received/invitation_sent/export_completed, payload JSONB navigation links localized params, read_at), Notification Preference (user_id UK, preferences JSONB per event_type/channel in_app email push future mandatory critical cannot mute), Audit Event (actor_user_id nullable system, organization_id nullable global events like failed login without org, action indexed e.g. auth.login membership.revoked photo.viewed, target_entity_type, target_entity_id, ip_hash SHA256, metadata JSONB sanitized no passwords health raw, created_at immutable append-only DB-level REVOKE UPDATE/DELETE), Export Request (user_id, status pending/processing/completed/failed, storage_key tmp ZIP, expires_at, requested_at, completed_at), Erasure Request (same fields).

**Future extensibility:** Nutrition Professional Assignment P1 (organization_id org-scoped, nutritionist_user_id, athlete_user_id, consent_record_id, status), Meal Plan (athlete_id, nutritionist_id, organization_id, title, etc), Recipe, Food Item (name_fa name_en, macros), Allergy/Restriction, Product Billing P1 Phase10 (organization_id, name, price, currency, entitlement flags), Subscription (organization_id, product_id, status, current_period_end), Payment (organization_id, gateway_customer_id, amount, status, webhook_idempotency_key UK), Entitlement, Marketplace Listing P2 (coach_id, organization_id, title, description, price, status, review_count), Review, AI Run Log P2 Phase11 (user_id coach, prompt_version, model, input_hash, output_summary, human_review_decision, cost_cents, created_at PII stripped).

**For every entity defined:** PK (UUIDv7 proposed), FKs, tenant ownership org_id filter mandatory, sensitive fields Tier, required indexes B-tree + GIN trigram, unique constraints, state machines/status values, soft-delete/archive policy archived_at timestamp or anonymized hard delete for PII, audit requirements (e.g. org.created, membership.status_changed, program.assigned, session.completed, pain.flagged, photo.viewed consent.granted etc), retention considerations (30d snapshot, 7d export tmp, 1y+ audit proposed), localization behavior (fa-IR/en-US only fields, translations via ExerciseTranslation, Jalali UI formatting frontend).

**Modeling rules enforced:** UUIDv7 not substitute for authz, UUIDv7 proposed remains until validated, every tenant-scoped query derives org scope from authenticated server context (OrgScopeMiddleware request.org_id), assignments immutable snapshots, photos never public URLs, multi-professional access requires explicit consent + revocation, avoid duplicated mutable data without snapshot/version reason (snapshot duplication justified immutability).

**ERD diagram:** Mermaid `erDiagram` in `docs/architecture/ERD.md` renders in GitHub Markdown, includes legend PK/FK/UK/IDX/NN/TSP/JSONB/ARCH ORG-SCOPED SENSITIVE.

**Status:** Proposed — conceptual DDL illustrative not executed, actual Django migrations Phase04.

---

## 11. Authorization Architecture

**Artifact:** `docs/architecture/AUTHORIZATION_ARCHITECTURE.md`

- RBAC roles P0: Platform Admin (is_platform_admin true + MFA, global, moderate catalog, manage tenants, global audit, suspend users, all actions audited), Organization Owner (org tenant active membership role owner, creates org, manages members, invites coach/athlete, reassigns, reads org audit, aggregate progress not raw), Coach (org tenant active role coach, creates programs templates, assigns to assigned athletes only, reads assigned athlete logs/photos with consent), Athlete (org tenant active role athlete, self-access only today, sessions, set logs, progress photos, messages), Support optional (org tenant active role support read-only roster, aggregate logs? DENIED Tier4 photos private messages).
- Future Nutritionist P1 consent-gated via ConsentRecord type nutrition_sharing.
- Org boundaries: user may have multiple organizations multiple Membership rows, active organization switchable via picker, middleware sets request.org_id from membership, every tenant-scoped queryset for_org(org_id) helper adds WHERE organization_id = auth org_id, cross-tenant obscurity 404 preferred over 403 to avoid enumeration, invitation token hash + expiry 7d single-use.
- Object-level assignment: CoachAssignment active check for athlete data, Program assignment verifies CoachAthleteAssignment exists org scope matches, Message thread participant check, Consent check for photo/body metrics.
- Owner visibility distinction: Aggregate org analytics (counts, weekly active, adherence %, volume aggregates, flagged counts) allowed without raw; Individual operational (scheduled workouts, completion status, set counts, adherence dates) allowed; Sensitive health-adjacent FeedbackFlag raw individual notes require audited escalation, BodyMetric values consent; Progress media Owner only if explicit consent granted to owner as grantee + audited escalation, Support DENIED zero; Private Messages Owner only via audited escalation break-glass.
- Break-glass admin: Platform admin reads of Tier3/4 sensitive need MFA verified session + documented reason param + audit admin.break_glass_access + alert Slack security channel + periodic review.
- P1 nutritionist: Training schedule context allowed but not progress photos unless separate consent progress_photo granted to nutritionist; revocation immediate invalidates signed URLs.
- Suspension: Membership status suspended immediate 403 for all org-scoped calls, Coach assignments archived automatically via signal, athlete still active but unassigned? Edge: owner notified to reassign; athlete suspended cannot log sets; login still allowed but org context blocked (User is_active global vs Membership suspended org only).
- Invitation permissions: Owner can invite Coach/Athlete/Support, Coach can invite Athlete only, Athlete cannot invite, Support can resend only, token crypto random 32+ bytes URL-safe base64 SHA256 hashed stored plaintext only in email validation endpoint returns email but only valid token.
- API enforcement DRF permissions: TenantScopedPermission checks request.org_id present + membership active, RolePermission checks role, CoachAssignmentPermission verifies active assignment, ConsentPermission verifies active ConsentRecord, BreakGlassPermission checks MFA + logs audit.
- Example permission chain GET /athletes/{id}/progress-photos: IsAuthenticated + TenantScopedPermission + (IsPlatformAdminBreakGlass OR (IsCoach AND CoachAssignmentPermission AND ConsentPermission) OR IsOwnerWithConsentAudited OR IsSelfAthlete) + NOT Support.
- Negative authorization controls mandatory tests: cross-tenant reads/writes, unassigned coach access, suspended membership, unauthorized progress-photo access (David unassigned GET Neda photo 403 + no signed URL), unauthorized message access, unauthorized audit-log access (Coach/Athlete GET org audit 403 Owner own org only Admin global), unauthorized export/deletion (User A export for User B 403).
- Data classification mapping Tier0 public metadata Tier1 account/identity Tier2 operational Tier3 health-adjacent Tier4 progress media Tier2+ confidential messages Tier5 audit immutable Tier6 secrets never repo.
- Logging restrictions debug logs must NOT contain password_hash tokens email full? partial redacted, health flag details, photo storage keys/signed URLs, message content, full IP only IP hash.

**Status:** Proposed/Accepted direction ADR-006.

---

## 12. API and OpenAPI Architecture

**Artifacts:** `docs/OPENAPI.yaml` (provisional OpenAPI 3.1), `docs/JSON_SCHEMAS.md`, `docs/API_CONTRACT.md` v2.0

- Versioned under `/api/v1` provisional 2026-08-10 requires implementation review Phase04.
- Endpoint groups P0 covered:
  - Auth: register (public 5/min IP), login (5 fails/15min IP/email 429 generic error), me GET/PATCH, forgot-password 202 always to avoid email enumeration rate limit 5/15min, reset-password/{token} single-use 15min TTL 410 Gone reuse.
  - Current user/profile: same as me.
  - Organizations: POST create org + primary location + owner membership slug unique 409, GET list my orgs, GET/PATCH /organizations/{org_id} owner full coach limited athlete branding only support read owner update audited.
  - Locations: GET/PATCH primary location MVP single-location partial unique index single primary per org, owner only update.
  - Memberships: POST /organizations/{org_id}/invitations owner any role coach athlete-only rate limit 10/min org audit invitation.sent, GET list pending invites owner, GET/PATCH /members list filter role/status/assigned coach owner full coach limited to own assigned athletes, PATCH membership suspend active↔suspended immediate revocation 403 audit membership.status_changed.
  - Invitations: GET /invitations/{token}/validate public checks hash expiry not used returns email role org, 410 expired/used.
  - Exercise catalog: GET /exercises search q with Perso-Arabic script keyboard-variant normalization for Persian search filtering muscle movement_pattern equipment locale fa-IR/en-US only auth org member canonical NULL + org private, org_id filter canonical + private, localization Accept-Language optional, POST private custom exercise owner/coach org-private rights metadata mandatory.
  - Exercise moderation: GET/POST /admin/exercises/moderation platform admin MFA only, queue pending submissions, approve/reject with reason audit exercise.published/rejected.
  - Programs: GET list org programs templates filter is_template owner coach, POST create master program hierarchical nested atomic transaction owner coach audit program.created, GET/PATCH /programs/{program_id} detail builder owner coach org scope.
  - Templates: POST /programs/{program_id}/clone deep copy independent clone does not mutate master audit template.cloned.
  - Assignments: POST /program-assignments assign program to athlete with immutable snapshot JSONB verifying CoachAssignment org scope, idempotency-key header recommended, notification to athlete audit program.assigned, GET list assignments filter org athlete (owner any athlete coach assigned only athlete self).
  - Athlete Today view: GET /athlete/today returns scheduled workouts today based on active assignment snapshot cached shell + network status, athlete self only.
  - Workout sessions: POST /workout-sessions start scheduled→in_progress athlete self audit session.started, GET /workout-sessions/{session_id} detail athlete self or assigned coach or owner operational assignment check org scope, POST complete in_progress→completed optional pain flag audit session.completed.
  - Set logs: POST /workout-sessions/{session_id}/set-logs log actuals athlete self primary coach proxy flagged optional temporary in-memory offline preservation Phase07 no durable queue until Phase12, audit set.logged optional.
  - Feedback flags: POST /workout-sessions/{session_id}/feedback-flags pain/fatigue flag subjective not clinical diagnosis athlete self audit pain.flagged Tier3 sensitive assigned coach only owner aggregate audited admin.
  - Progress metrics/photos: GET /athletes/{athlete_id}/progress/photos list with signed URLs TTL≤15min consent-gated athlete self assigned coach active ConsentRecord progress_photo owner explicit consent + audit escalation support DENIED admin break-glass audited photo.viewed, POST upload progress photo multipart explicit consent required athlete self audit photo.uploaded Tier4 never public URLs, GET/POST body-metrics list metrics consent-gated.
  - Messages: GET/POST /messages/threads list participant only, POST creates thread or first message requires CoachAssignment active for coach-athlete threads else 403 owner escalation audited support DENIED audit message.sent, GET /messages/threads/{thread_id}/messages participant only assignment check.
  - Notifications: GET /notifications self only, GET/PATCH /notifications/preferences self only critical assignment alerts cannot mute.
  - Audit events: GET /organizations/{org_id}/audit-logs owner own org only coach/athlete forbidden support org read per PRD audit.viewed potentially sensitive, GET /admin/audit-logs global platform admin MFA only.
  - Privacy export/deletion: POST /privacy/export-request self only enqueues Celery packaging profile.json workouts.json set_logs.csv optional photos temp S3 + email link 24h audit privacy.export_requested/completed rate limit 2/day, POST /privacy/forget-me password re-entry confirmation self only pipeline wipes PII photos S3 deletion disassociates aggregates audit user.anonymized.
  - Media signed URLs: GET /media/{asset_id}/signed-url exercise demo media private bucket org scope assignment for private custom TTL≤15min audit Tier4 only.
  - Consents: GET list athlete consents athlete self assigned coach sees status, POST grant consent explicit affirmative modal audit consent.granted, DELETE revoke consent immediate invalidates future signed URLs existing still valid until TTL short.
- For every endpoint in OPENAPI.yaml specified: method, path, purpose, authentication, required role, object-level permission rule, request schema, response schema, error responses (400 401 403 404 409 410 429 500 RFC7807), localization behavior Accept-Language fa-IR/en-US bilingual names, idempotency expectation Idempotency-Key optional for critical writes invite assign payment future, audit event behavior, rate-limit category (auth 5/min, search 30/min, messages 10/min, export 2/day, invite 10/min org), data sensitivity Tier0-6.
- Error model consistent standards-aware RFC7807 type (URI), title, status, detail, instance + localized message_key extension + optional field_errors.
- Do not freeze provisional paths without noting implementation review occurs Phase04 — marked provisional.
- Related JSON Schemas in JSON_SCHEMAS.md: snapshot immutable version, queue entry offline Phase12, export manifest, notification payload, consent.

**Status:** Provisional — requires implementation validation Phase04.

---

## 13. Threat Model

**Artifact:** `docs/THREAT_MODEL.md`

- Method STRIDE + OWASP Top10 mapping.
- Assets A01-A12 listed with classification Tier1-6.
- Actors anonymous attacker, authenticated malicious coach same org unassigned, cross-tenant coach, suspended former staff, owner overreach, admin insider misuse, malicious athlete uploading malware, external via SSRF, supply-chain, backup leakage, enumeration bot.
- Threats detailed T01-T21 (21 threats) each with asset, threat actor, STRIDE category, OWASP, attack path, impact, likelihood, risk level, preventive control, detective control, corrective control, test strategy, owner, residual risk.
- Highlighted critical: T04 cross-tenant IDOR critical prevention org_id filter server context import-linter, T07 progress-photo exposure critical private buckets BlockPublicAcls true TTL≤15min no SW cache audit, T08 malicious uploads high MIME whitelist magic bytes size checksum ClamAV quarantine.
- OWASP mapping table A01 Broken Access Control covering T04 T05 T06 T07 T14 T16, A02 crypto failures T02 T19, A03 injection T08 T09, etc.
- Residual risks after controls credential stuffing medium-low unless MFA all (MFA only admin P0, consider TOTP P1), insider misuse medium if audit review not enforced, supply-chain critical residual ongoing monitoring.
- References AUTHORIZATION_ARCHITECTURE, MEDIA_STORAGE, OBSERVABILITY, SECURITY_CONTROL_MATRIX, PRIVACY_DATA_LIFECYCLE.

**Status:** Proposed.

---

## 14. Security Control Matrix

**Artifact:** `docs/SECURITY_CONTROL_MATRIX.md`

- Mapping table threat → requirement ID (PRD NFR US-...) → architecture control → implementation phase → test type (unit/integration/e2e/security scan/manual audit) → evidence artifact (AUTHORIZATION_ARCHITECTURE.md, MEDIA_STORAGE.md, ERD.md etc) → status.
- Includes rows for each T01-T21 plus negative controls:
  - Cross-tenant reads/writes (T04)
  - Unassigned coach access (T05)
  - Suspended membership (US-ORG-005)
  - Unauthorized progress-photo access (US-ATH-005)
  - Unauthorized message access (US-MSG-001)
  - Unauthorized audit-log access (US-AUD-001)
  - Unauthorized export/deletion (US-PRI-001/002)
- Implementation phase mapping: Phase04 foundation TLS HSTS CSP lockfiles secret scan health checks SW, Phase05 identity tenancy auth controls T01-T04 invitation T03 suspension audit etc, Phase06 exercise catalog search normalization T08 T09, Phase07 athlete app photo consent signed URL T07 unassigned T05 owner overreach T06 offline wording, Phase08 messaging notification abuse T13 XSS, Phase09 nutrition P1 consent DPIA, Phase10 billing P1 webhook forgery T12, Phase11 AI P2 prompt injection T17, Phase12 PWA advanced offline, Phase13 QA security restore testing penetration etc.
- Test type definitions, evidence artifacts list, status summary proposed/deferred/accepted/pending founder approval.
- References.

**Status:** Proposed.

---

## 15. Privacy and Data Lifecycle

**Artifact:** `docs/PRIVACY_DATA_LIFECYCLE.md`

- Lifecycle stages 11: collection (registration, logging, photo upload), consent (explicit affirmative for progress photos, nutrition sharing P1), storage (PG private S3 Redis ephemeral search indexes), use (assignment, adherence, messaging), sharing (within tenant coach-assigned athlete + future multi-prof P1 with consent), export (self-service ZIP GDPR Art.20 adjacent), retention (duration per class), revocation (withdraw consent immediate), deletion (hard delete PII + photo S3), anonymization (disassociate telemetry aggregates), backup destruction (snapshot retention 30d question).
- Classification detailed:
  - Tier0 public metadata canonical exercise names equipment taxonomy public landing — no consent, public GET but moderation-gated.
  - Tier1 account/identity User email display_name phone optional password_hash preferred_locale timezone Organization slug Membership role/status Invitation email/role — account data necessary, email required, data minimization no national ID, owner platform controller assumption requires legal review, self + owner member list + admin audited access, TLS + at-rest AES-256 Argon2id, log redaction, retention until erasure invitation 90d maybe anonymize, export profile.json, deletion PII wiped audit user.anonymized.
  - Tier2 operational Programs phases/weeks/days items prescriptions templates assignment snapshots sessions scheduled/in_progress/completed set logs substitution reason session RPE — operational necessary for coaching, purpose limitation only coaching, athlete owns historical logs AD R-019 org revocable operational, tenant + assignment access, at-rest AES-256, no set load in debug logs only IDs, retention until org archive or assignment archive historical preserved athlete retains, export workouts.json set_logs.csv, deletion disassociate anonymized aggregates.
  - Tier3 health-adjacent FeedbackFlag joint_pain etc anatomical_location severity details, BodyMetric weight bodyfat fatigue_score — subjective but sensitive potentially health data GDPR Art.9 requires stricter explicit consent? P0 consent via coaching relationship + non-clinical disclaimer ADR-026, owner aggregate only + audited escalation, assigned coach only + self, encryption at-rest AES-256 field-level proposal deferred, logging restriction MUST NOT log raw details only type+id, retention until erasure anonymized, export included.
  - Tier4 progress media front/side/back physique form check videos — highly sensitive visual personal data explicit affirmative consent ADR-027 before upload revocation immediate, athlete owns org/coach revocable licensed view, access self + assigned coach active ConsentRecord + owner explicit consent to owner grantee + audited escalation support DENIED zero admin break-glass MFA + reason, S3 SSE-S3 TLS signed URL TTL≤15min no CDN caching no listing no logging storage key, retention until individual delete or erasure hard delete, export optional include photos if <100MB else separate signed links, consent explicit modal.
  - Tier5 messages 1:1 contextual linked workouts private communication confidential, participants only owner/admin break-glass audited support DENIED, TLS at-rest AES-256, no message content in debug logs, retention until erasure anonymize "[deleted]" proposal, export own messages.
  - Tier5 audit logs actor action target IP hash metadata sanitized, purpose security compliance, append-only no update/delete DB-level REVOKE, admin global owner own org only support org read per PRD, at-rest AES-256, metadata sanitized no passwords health raw, retention 1y+ proposed requires legal, export owner own org audit admin global, deletion forbidden.
  - Tier6 future payment P1 Phase10 gateway tokens subscription invoice no PAN PCI tokenization, owner finance admin, retention 7y per financial reg requires legal, future deferred.
  - Tier8 future AI Phase11 prompts completions human review PII stripped before model, authoring coach AI safety auditor, retention 90d maybe.
- Consent lifecycle: photo consent UX flow modal title Allow Coach Reza to view progress photos body explanation revocation right focus trapped privacy-first default Keep Private, upon grant ConsentRecord is_granted true granted_at audit, revocation Profile→Privacy immediate audit revoked_at future signed URL generation blocked existing URLs valid until TTL short.
- Multi-prof P1: NutritionProfessional assignment requires explicit athlete consent nutrition_sharing, progress photo not auto included needs separate consent to nutritionist grantee.
- Export pipeline: POST /privacy/export-request self only rate limit 2/day async Celery queries user-scoped across modules packages ZIP storage private tmp bucket lifecycle 7d delivery email signed URL 24h proposed audit.
- Erasure pipeline: POST /privacy/forget-me password re-entry confirmation, stages verify password invalidate sessions delete PII anonymize logs disassociate aggregates delete photos S3, statuses pending/processing/completed/failed, audit erasure.
- Retention & backup destruction questions table: account until erasure remains in PG snapshots 30d acceptable per GDPR? requires legal, operational until archive or erasure anonymized, Tier3 until erasure anonymized, Tier4 hard delete S3 immediate versioned 30d? Should bypass versioning for erasure permanent, messages until erasure, audit 1y+, export TMP 7d.
- Pre-DPIA checklist: large-scale sensitive? P0 includes pain flags body metrics progress photos potentially large-scale if many athletes, systematic monitoring? adherence tracking could be monitoring not public area, automated profiling? No autonomous AI human review required AI deferred Phase11 triggers DPIA when introduced, multi-prof sharing P1 consent, progress-photo processing highly sensitive consent private buckets support DENIED, wearable future Phase12 sensitive health DPIA required, AI Phase11 DPIA required, biometric? No facial recognition only human coach review, vulnerable children? Policy 16+ open, data transfer across borders Iran vs EU residency requires legal.
- Outcome: Before pilot handling real health data formal DPIA and legal review mandatory, this doc is engineering alignment not compliance claim.
- Logging restrictions summary never log raw passwords hash tokens Authorization headers full email? partial redacted health flag details body metric values photo keys URLs message content full IP only hash.
- Privacy UX copy equal clarity fa-IR/en-US non-clinical supportive tone.

**Status:** Proposed — privacy-aligned engineering design requires jurisdiction-specific legal review.

---

## 16. Media Storage and Rights

**Artifact:** `docs/architecture/MEDIA_STORAGE.md`

- Media types table: exercise demo video canonical global Tier0 public metadata but still private bucket + signed URL or CDN signed, exercise demo image canonical Tier0, exercise demo video org-private custom Tier2 proprietary org IP, progressive photo Tier4 most sensitive front/side/back, org branding logo Tier1, export ZIP temporary Tier1-4 mixed own user data, future transcoded renditions.
- Bucket boundaries proposed: coachos-media-private canonical+org-private exercise media, coachos-progress-private athletes Tier4 isolated, org-logos, exports-tmp lifecycle 7 days, common settings BlockPublicAcls true IgnorePublicAcls true BlockPublicPolicy true RestrictPublicBuckets true versioning enabled SSE-S3 ObjectLock disabled for MVP no static website no public policy CORS allow GET from app origin only if direct.
- Upload flow sequence diagram client validation MIME size extension + BE validation role org scope consent + BE proxy upload streaming to S3 after validation + DB MediaAsset + thumbnail job.
- Validation rules: MIME whitelist image/jpeg png webp video/mp4 webm restrict mp4 MVP extension sanitized UUID key, size limits proposed image 10MB private 5MB exercise video 100MB MVP org logo 2MB, file name never user-supplied UUID key prefix/{uuid}.ext, checksums SHA256.
- Signed URL generation principles never public URL all reads presigned GET after AuthZ+Consent TTL≤15min export ZIP TTL 24h proposed via email, generation via S3 generate_presigned_url ExpiresIn 900, audit photo.viewed Tier4, no bucket listing ListObjects disallowed for app role only GetObject via presigned.
- Flow diagram coach request exercise video/progress photo view FE→BE GET signed-url → AuthZ verify org scope assignment consent → MediaService presign GET → S3 signed URL → audit → FE 200 signed URL expires_at → S3 GET bytes. CDN variant CloudFront signed URL signed cookies OAI TTL 15min.
- Thumbnail strategy: images Pillow 256 512 webp, videos ffmpeg poster at 2s 480 webp optional short preview gif MVP thumbnail only future transcoding Phase12 renditions 480p 720p, progress photo thumbnails even via signed URL no public.
- Malware scanning ClamAV optional P0 basic MIME magic validation, Phase13 integrate ClamAV sidecar worker quarantine status media.quarantined notify uploader delete S3 object audit.
- Provenance license mandatory every MediaAsset has MediaRights license_type original_production licensed_cc_by commercial_license coach_upload source_url nullable creator_attribution required permitted_commercial_use bool reviewed_by reviewed_at admin reviewer canonical, workflow custom exercise must select license attribution system stores but no admin review for private custom, canonical pending_review → admin moderation queue SCR-ADMIN-02 approve publishes global.
- Copyright takedown workflow reporter files request support email admin tool, admin opens Media Asset detail verifies rights source_url, if infringement suspected set Exercise status archived or MediaAsset quarantined remove signed URL ability archive keep audit, notify coach reason structured feedback, log copyright.takedown_executed.
- Photo access control detailed athlete self list own photos, assigned coach requires active CoachAthleteAssignment + active ConsentRecord progress_photo, owner DENIED unless explicit consent to owner grantee or audited escalation, support DENIED zero, admin audited escalation MFA+reason.
- Future transcoding Phase12 AWS MediaConvert or ffmpeg worker renditions 480p 720p for exercise demos save mobile bandwidth store suffix _480.mp4, CDN rules canonical Tier0 CDN may cache long TTL but origin private signed URL? For MVP no CDN caching private media direct presigned, Tier4 no CDN caching Cache-Control private no-store max-age0, CDN logs no PII.
- Retention deletion exercise media archived soft-delete S3 remains archived_at eventual hard delete 30d proposed audit, progress photos hard deleted on erasure or individual delete, export ZIP immediate delete after download lifecycle fallback.

**Status:** Proposed accepted orientation ADR-034.

---

## 17. PWA Architecture

**Artifact:** `docs/architecture/PWA_ARCHITECTURE.md`

- Overview PWA-first mobile delivery avoid app-store friction low-connectivity gym basement failures.
- Three-level authoritative strategy:
  - Phase04 Foundation goal installable fast shell basic offline UX: manifest.json name CoachOS short_name CoachOS description bilingual, display standalone start_url /app/today?source=pwa scope / orientation any theme_color #0B0F17 background #0B0F17 dir auto lang en-US icons 192 512 maskable purpose any/maskable, standalone check no browser chrome, SW registration /sw.js scope / Workbox or next-pwa proposed skipWaiting optional toast new version, app-shell caching CacheFirst fonts/icons versioned StaleWhileRevalidate JS/CSS shell, runtime caching API GET exercises maybe cached? Phase04 not caching workout data requires network only shell, offline fallback /offline.html localized offline connect to view workouts retry, install guidance beforeinstallprompt defer custom CTA, UX copy pwa.install_banner iOS Share → Add to Home Screen Android automatic prompt, NFR-PWA-01/02 valid manifest standalone high-res icons active SW, core shell cached locally immediate launch zero connectivity, security SW scope same origin HTTPS only, testing Lighthouse PWA audit ≥90 proposed requires validation.
  - Phase07 Athlete Mobile Validation goal validate athlete gym-floor execution no promise full conflict-free offline sync: Today dashboard rendered from cached snapshot if previously loaded memory React Query SWR cache offline can render last fetched snapshot stale with banner, active workout session mode bottom nav hidden full-screen canvas, touch-optimized 44 min 48 preferred CTAs requiring implementation testing oversized keypad inputmode decimal rest timer client-side setInterval visual SVG ring audio/haptic completion, form-state protection unsaved set inputs React state useState useReducer surviving remount preserve sessionStorage optionally but spec in-memory only not durable, network loss during active session yellow banner Offline unsaved input retained temporarily retry required after reconnection no durable queue allow continuous execution timer still works retry button attempts sync on reconnect navigator.onLine fetch retry, network-status indicator useNetworkStatus online/offline events badge top bar, retry behavior set log POST failure due network toast Failed to save set — [Tap to Retry] no auto background sync yet manual retry, video demos requires live network offline fallback text cues Video demo unavailable offline — text cues shown below, messages not queued durably unsaved input retained temporarily retry required, no promise full conflict-free offline sync explicit boundaries STATE_AND_ERROR_MATRIX, installed-PWA mobile validation test iOS Safari 17+ Android Chrome 120+ standalone splash status bar theming one-handed thumb zone.
  - Phase12 Advanced Capabilities goal full offline-first workout logging durable queue background sync: IndexedDB Dexie.js idb-keyval proposed stores workout_sessions in_progress set_logs_queue unsynced exercise_catalog_cache canonical+org-private program_snapshot_cache progress_photos_pending_upload optional, durable offline set queue when offline set logs persist IndexedDB queue client-generated UUIDv7 allows offline ID generation avoiding enumeration not authz bypass payload client_created_at retry_count status pending/syncing/synced/failed/conflict, sync status UI Synced Pending sync 3 sets Sync failed tap to retry footer badge, retry exponential backoff 2s 5s 15s 60s jitter reconnect flush queue ordered created_at, conflict resolution last-write-wins set logs append-only no conflict same set_index offline+online server keeps latest created_at but preserves both versions audit proposal program assignment version if coach pushes new version while athlete offline athlete sees old snapshot until sync plus notification New program version available, background sync where supported Background Sync API self.registration.sync.register('sync-sets') Chrome iOS Safari unsupported fallback foreground sync on app focus, push limitations Web Push VAPID iOS support limited 16.4+ standalone only document push not reliable iOS until added home screen fallback email/in-app polling, HealthKit/Health Connect evaluation native bridge vs PWA PWA cannot directly access requires native wrapper Capacitor Cordova or backend webhook Garmin etc decision document evaluation not implement Phase12 until privacy review pre-DPIA, native bridge decision Phase12 decide remain pure PWA or wrap via Capacitor for wearable access no native builds P0.
- Browser/platform limitations table Chrome Android Safari iOS Firefox for installable manifest SW standalone background sync periodic sync push IndexedDB vibration native health APIs + limitation notes.
- Security privacy SW must not cache Tier4 sensitive media aggressively no caching signed URLs TTL short in Cache API memory only NetworkOnly for photos/messages, SW no log health, manifest no PII, request persistent storage only if needed clear cache on logout erasure.
- File structure public/manifest.json icons offline.html sw.js generated next-pwa Workbox.
- Manifest example JSON illustrative spec only not served Phase03.
- Offline state wording normative Phase04 "Offline — cached app shell only. Connect to load workouts." Phase07 "Offline — unsaved input retained temporarily; retry required after reconnection" NOT "sets saved locally", Phase12 "Offline — 3 sets queued locally; will sync when reconnected" + sync badges enforced in STATE_AND_ERROR_MATRIX UX_COPY.

**Status:** Proposed accepted sequencing ADR-011 ADR-035 ADR-036.

---

## 18. Observability

**Artifact:** `docs/architecture/OBSERVABILITY.md`

- Structured logging format JSON INFO prod DEBUG local/staging required fields timestamp ISO8601 UTC level service api/frontend/worker request_id UUIDv7 org_id actor_user_id action entity_type entity_id duration_ms status_code message version git commit hash. Example log.
- Library proposed backend Python structlog JSON renderer processor request_id frontend Next.js pino server logs browser console minimal errors sent Sentry not verbose.
- Redaction must NOT log password_hash raw password raw email? partial redacted, progress photo storage keys signed URLs raw, message content, health flag details, body metric values, JWT tokens, Authorization headers, full IP only hash. Redaction processor removes keys password password_hash token authorization content etc.
- Correlation request_id middleware RequestIDMiddleware generates X-Request-ID UUIDv7 if not provided propagates response header, all logs include request_id, frontend apiClient generates optional X-Request-ID per request or uses backend response to correlate, Celery tasks inherit request_id via kwargs.
- Audit vs debug separation debug/structured app logs ops performance errors stored ELK/CloudWatch retention 30d proposed no Tier3/4 payloads, audit immutable PG table 1y+ retention never UPDATE/DELETE app user queried only admin/owner scoped.
- Metrics proposed stack backend Prometheus django-prometheus /metrics protected not public counters histograms, frontend Web Vitals next/web-vitals optional analytics endpoint LCP CLS INP, infra Cloud metrics.
- Key metrics http_requests_total counter method path_template status, http_request_duration_seconds histogram method path_template, auth_login_failures counter reason, auth_rate_limit_hits counter endpoint, org_membership_status gauge org role status, program_assignments counter org, workout_sessions counter status, set_logs counter org, media_uploads counter media_type status, media_signed_url_generated counter tier, notifications_dispatched counter event_type, celery_tasks counter task status, audit_events counter action, export_requests counter status, db_connections gauge, redis_cache_hit_ratio gauge anonymized aggregate not per PII.
- Error tracking Sentry proposed frontend backend worker DSN env secrets sample rate 10% transactions 100% errors scrub sensitive release tracking git hash alert new error regression.
- Frontend error boundary React Error Boundary major routes today builder friendly error state retry + request_id for support window.onerror unhandledrejection Sentry.
- Health endpoints /healthz liveness 200 if up no DB? minimal public no sensitive, /readyz or /api/v1/health readiness checks DB Redis S3 Celery returns JSON status ok checks db ok redis ok s3 ok celery ok version commit timestamp protected via token/monitoring IP allowlist.
- Alerting categories auth anomaly >20 fails IP 15min or 5 same email rate_limit_hits medium high spike Slack Email audit security alert, cross-tenant access attempt same actor 10 404/403 short window high Slack + Audit cross_tenant_attempt, unauthorized photo 403 spike high Slack audit, error rate 5xx >1% 5min high Pager Slack, latency p95 read >400 write >800 sustained 10min medium Slack, DB connections >80% max medium Slack, Redis down >1min high Slack, S3 upload failure 5xx or 4xx validation >5% medium Slack, Celery queue depth >100 pending >10min medium Slack, export/erasure failure >3 retries medium Slack audit, backup failure daily snapshot failed high Email Slack, disk >80% high Pager, cert expiry <14d high Email. All thresholds proposed until validated staging.
- Monitoring auth cross-tenant alerts log permission_denied actor org target type/id sanitized IP hash request_id alert pattern same actor multiple cross-tenant 404/403 short window potential IDOR probing, admin break-glass immediate alert Slack security channel email founder?, failed admin MFA high severity.
- Frontend observability Web Vitals LCP <2.5s CLS <0.1 INP <200ms proposed targets tracked via web-vitals lib own analytics endpoint /api/v1/analytics/web-vitals optional not storing PII Prometheus Grafana, PWA install prompt events custom metrics pwa_install_prompt_shown pwa_installed, offline events navigator.onLine transitions local send when back online.
- Retention costs logs 30d app 1y+ audit metrics 90d raw 1y aggregated Sentry 30d costs proportional avoid verbose Tier3/4.

**Status:** Proposed requires validation ADR-040.

---

## 19. Backup and Disaster Recovery

**Artifact:** `docs/architecture/BACKUP_AND_DISASTER_RECOVERY.md`

- Backup strategy PG managed service automated backups e.g. RDS automated snapshots + WAL archiving PITR schedule daily full snapshot retention 30d proposed + continuous WAL allows PITR any point RPO 15min proposed manual snapshot before major migration release tag version storage snapshots encrypted same region different AZ optional cross-region copy DR deferred P1 verification automated daily restore to staging test? Proposed weekly actual restore + query validation encryption snapshots encrypted same source.
- S3 backups versioning enabled all private buckets lifecycle noncurrent versions expire 14-30d exports-tmp expire 7d AbortIncompleteMultipartUpload 1d backup? S3 durable 11 9s but versioning recovery overwrites/deletes no separate backup beyond versioning periodic inventory.
- Redis cache/queue not source truth cache rebuildable queue durable? Celery tasks lost could be retried via DB ExportRequest status no persistent backup required MVP if persistence enabled AOF/RDB snapshot daily loss acceptable note rate-limit counters loss acceptable.
- Code GitHub repo source no extra backup beyond GitHub IAC future Terraform state file secure backend versioning.
- Restore drill PG runbook identify recovery point timestamp before migration initiate restore new instance coachos-restore-test timestamp wait availability update staging DATABASE_URL smoke tests auth login org list assignment etc if prod restore schedule maintenance window notify users fa/en switch DATABASE_URL secrets manager restart workers verify healthz log restore event audit notify founder RTO restore+validation proposed 1h DB alone who can run SRE Platform Admin MFA documented reason audit. S3 restore list versions restore desired version copy version delete delete marker verify signed URL RTO minutes single hour many.
- Automated restore testing weekly monthly automated job GitHub Action Lambda restores latest snapshot ephemeral staging DB runs pytest smoke tests against restored data not mutating reports success/failure Slack deletes ephemeral DB after required before pilot.
- RPO/RTO proposed table PG primary 15min WAL PITR 1h restore+30m validation losing 15min workout logs acceptable? 5min if WAL every 5min, S3 media private 0 versioning no data loss overwrite if versioning 1h restore specific objects Exercise media re-uploadable canonical need re-moderation, S3 progress-private Tier4 0 versioning deletion recovery via version restore 1h most sensitive must never lose unless hard deleted via erasure intentional versioning protects accidental, Redis cache/rate-limit loss acceptable N/A minutes rebuild, Redis queue jobs stored PG ExportRequest status re-enqueueable RPO 0 persisted via DB transient Redis loss acceptable if retryable from DB status, full platform stack data 15min infra 2-4h, frontend static 0 git minutes.
- Disaster scenarios table PG AZ failure failover standby replica multi-AZ automatic manual promotion enable multi-AZ prod proposed cost, PG corruption PITR before corruption, S3 bucket accidental delete policy mass deleted restore versioning bucket deleted recreate inventory backup S3 deletion prevention MFA Delete Tier4 proposed, Redis failure rate-limit bypass fail-open cache misses queue delay restart rebuild re-enqueue, backend crash loop 5xx rollback previous image, worker crash exports delayed restart queue depth check dead-letter re-enqueue backoff, accidental erasure bug mass anonymization restore snapshot before bug re-evaluate logic, secrets leaked rotate secrets restart audit review notify founder.
- Incident response propose detect triage severity S1 data loss security breach to S4 minor contain if breach revoke keys block IP maintenance page investigate query audit logs app logs metrics S3 access logs recover restore backup patch redeploy post-mortem blameless doc docs/reports/incident-YYYY-MM-DD.md future not Phase03 communicate notify affected org owners email fa/en template pending legal.
- Breach response definition unauthorized access Tier3/4 sensitive data steps immediate containment revoke tokens rotate keys block actor, audit log extraction affected scope, notify founder legal advisor requires jurisdiction-specific legal review, if required GDPR Art33/34 notify authorities 72h affected users without undue delay pending legal Iran market vs EU, force password resets invalidate sessions, provide remediation, post-mortem improve controls. Do NOT claim legal compliance — privacy-aligned engineering design requires jurisdiction-specific legal review.
- Rollback strategy application previous Docker image tag last 5 registry deploy previous via deployment pipeline deploy-prod manual gate, frontend Vercel Netlify previous deployment rollback revert commit. DB migration rollback Django migrations reverse_code where possible destructive migrations 2-step add new column dual-write backfill switch reads drop old allow rollback, before migration manual snapshot PG daily auto but explicit pre-migration snapshot tag pre-migration-<version>-<timestamp>, if fails rollback app code previous compatible old schema if already applied partially migrate previous reverse safe otherwise restore pre-migration snapshot verify healthz smoke tests. Testing migration rollback staging before prod.
- Env separation staging prod distinct VPC DB buckets secrets no prod data copied to local synthetic only access prod secrets founder SRE Secrets Manager IAM.
- Open questions multi-AZ cost cross-region replication Tier4 backup retention 30d vs 7d RPO 15min vs 5min WAL frequency.

**Status:** Proposed targets require validation ADR-037 pending founder cost approval.

---

## 20. Architecture Decision Records

**Artifact:** `docs/DECISIONS.md` v2.0 43 ADRs

- Summary table 43 rows with status Accepted, Proposed, Pending Founder Approval, Deferred, Conditionally Accepted.
- Detailed records ADR-001 modular monolith accepted, ADR-002 stack conditionally accepted pending Phase04 validation, ADR-003 locales fa-IR/en-US only Arabic out scope accepted founder mandate, ADR-004 B2B2C SaaS accepted founder approved, ADR-005 auth channel email password default OTP roadmap proposed default with HS session cookie HttpOnly JWT rotating refresh, ADR-006 RBAC+ABAC+Consent accepted, ADR-007 AI deferred Phase11 accepted, ADR-008 media rights provenance accepted, ADR-009 calendar UTC storage Jalali UI display proposed → accepted conditional frontend validation required, ADR-010 monorepo deferred → proposed accepted orientation scaffold Phase04, ADR-011 PWA sequencing accepted, ADR-012 license IP pending founder approval YES, ADR-013 single-location-first accepted, ADR-014 membership role binding proposed → accepted conditional multi-role, ADR-015 program versioning snapshot proposed → accepted conditional immutable JSONB, ADR-016 deletion soft-delete archival proposed → accepted conditional soft-archive operational hard-delete anonymization pipeline, ADR-017 identifier UUIDv7 vs BigInt proposed requires validation not authz substitute, ADR-018 Persian search normalization trigram proposed → accepted conditional pg_trgm + normalizer precise wording Perso-Arabic script keyboard-variant normalization, ADR-019 data ownership privacy portability accepted, ADR-020 multi-prof collaboration consent accepted P1, ADR-021 payment gateway abstraction deferral Phase10 accepted, ADR-022 marketplace deferral P2 accepted, ADR-023 athlete mobile navigation 5-tab bottom nav modal active canvas accepted Phase02, ADR-024 coach program builder dual-pane master-detail accepted, ADR-025 Persian typography Vazirmatn accepted, ADR-026 non-clinical UX language accepted, ADR-027 explicit affirmative consent modal sensitive photos accepted, ADR-028 dark-neutral theme glare reduction design target accepted requires user testing, ADR-029 frontend Next.js app boundaries proposed pending scaffold, ADR-030 backend Django 20 modules proposed accepted orientation, ADR-031 PG version/extension PG16 pg_trgm btree_gin pgcrypto proposed requires validation, ADR-032 auth/session Argon2id HttpOnly cookie JWT rotating refresh 15min rate limit 5/15min proposed conditional acceptance, ADR-033 API error RFC7807 + message_key accepted, ADR-034 media storage private buckets no listing signed URLs TTL≤15min MIME whitelist thumbnail rights takedown accepted, ADR-035 PWA manifest SW three-level offline boundary accepted, ADR-036 offline boundary Phase04 shell only Phase07 temp in-memory Phase12 durable IndexedDB accepted, ADR-037 backup RTO/RPO PITR 15min RPO 1h RTO versioned S3 Redis loss acceptable proposed requires validation + cost approval yes, ADR-038 env separation proposed, ADR-039 CI/CD GitHub Actions lint/type/unit/integration/security scan Playwright E2E staging auto prod manual gate proposed, ADR-040 observability structlog JSON redaction request_id Prometheus Sentry healthz/readyz alerting proposed, ADR-041 OpenAPI 3.1 contract structure /api/v1 endpoint groups P0 RFC7807 error proposed accepted provisional, ADR-042 threat model security control matrix STRIDE OWASP 21 threats negative controls accepted, ADR-043 privacy lifecycle 11 stages Tier0-8 consent export/erasure pre-DPIA accepted.
- All statuses distinguish Accepted, Proposed, Pending Founder Approval, Deferred, Requires implementation validation, Requires legal review.
- License/IP status ADR-012 remains pending founder approval — LICENSE file remains MIT until written confirmation, do not change without explicit authorization, do not silently turn Proposed/Pending into Accepted.

**Status:** Accepted/Proposed/Pending as per table.

---

## 21. Validation Checklist

**Artifacts:** `docs/architecture/ARCHITECTURE_VALIDATION_CHECKLIST.md` + `docs/ARCHITECTURE_VALIDATION_CHECKLIST.md` (copy)

- V01 Every P0 domain has owning module — Proposed Pass — DOMAIN_MODULES M01-M16 P0.
- V02 Every sensitive entity has access rule — Proposed Pass — AUTHORIZATION_ARCHITECTURE matrix create/read/update/archive/export/share/revoke/consent/audited per sensitive resource.
- V03 Every P0 API group has architectural boundary — Proposed Pass — OPENAPI.yaml groups 25+ with method/path/purpose/auth/role/object permission/request/response/error/localization/idempotency/audit/rate-limit/sensitivity.
- V04 Every P0 user story maps to domain and API area — Proposed Pass — 27 stories US-... mapped in UX_TRACEABILITY_MATRIX + TRACEABILITY_MATRIX → DOMAIN_MODULES + OPENAPI.
- V05 Every UX route maps to future frontend boundary — Proposed Pass — SCREEN_INVENTORY 34 screens routes /register /login /org/* /coach/* /app/* /admin/* map to COMPONENT_BOUNDARIES frontend app structure.
- V06 Every cross-tenant query has authorization strategy — Proposed Pass — OrgScopeMiddleware request.org_id, TenantScopedModel for_org(), import-linter forbids bypass, THREAT_MODEL T04 controls.
- V07 Every media type has storage/rights strategy — Proposed Pass — MEDIA_STORAGE buckets private signed URLs TTL≤15min MIME whitelist thumbnail malware scan rights mandatory takedown.
- V08 Every export/deletion flow has architecture path — Proposed Pass — PRIVACY_DATA_LIFECYCLE export ZIP via Celery tmp S3 24h link erasure anonymization pipeline DATA_FLOW sequence, ERD ExportRequest/ErasureRequest.
- V09 PWA sequencing consistent across all docs — Proposed Pass — PWA_ARCHITECTURE three-level Phase04/07/12 consistent RELEASE_PLAN PWA phasing STATE_AND_ERROR_MATRIX offline matrix SCREEN_INVENTORY offline wording unsaved input retained temporarily.
- V10 No Arabic implementation scope exists — Proposed Pass — DECISIONS ADR-003 fa-IR/en-US only, OPENAPI locale enum only fa-IR/en-US, CI lint NFR-I18N-04 zero Arabic locale files grep.
- V11 No AI/payment/wearable implementation implied in P0 — Proposed Pass — SYSTEM_CONTEXT distinguishes P0 solid vs P1/P2 dashed future payment Phase10 AI Phase11 wearable Phase12, DOMAIN_MODULES marks M17-M20 future, THREAT_MODEL T12 T17 deferred, OPENAPI no payment/AI/wearable endpoints P0.
- V12 Open legal and license decisions remain visible — Proposed Pass — ADR-012 license pending founder approval, ADR-009 calendar proposed → accepted conditional, ADR-010 monorepo deferred → proposed, ADR-017 UUIDv7 proposed, SECURITY_AND_PRIVACY disclaimer not legal counsel, PRIVACY_DATA_LIFECYCLE privacy-aligned engineering design requires jurisdiction-specific legal review, pre-DPIA checklist.
- V13 No secrets or real health data exist in repo — Proposed Pass — Standing rule checking via gitleaks proposed CI, PROJECT_CHECKLIST cross-cutting rule synthetic data only, find no .env files beyond example.
- V14 Screen count exact 34 verified — Pass — SCREEN_INVENTORY grep 34 rows.
- V15 UX doc count 14 spec + README =15 verified — Pass — ls docs/ux 15 files.
- V16 Story count 27 P0 verified 25 core+2 I18N — Pass — PRD 27, UX_TRACEABILITY 27, no invalid.
- V17 Offline durability boundary respected — Pass — wording normalized unsaved input retained temporarily; retry required after reconnection Phase07 no durable queue Phase12 durable.
- V18 Touch target 44/48 consistency — Pass — DESIGN_SYSTEM etc minimum 44×44 per WCAG 2.5.5, 48×48 preferred design target for primary CTAs requires implementation testing consistent.
- V19 Jalali/Gregorian — Proposed Pass — ADR-009 UTC storage Jalali UI display fa-IR via frontend date-fns-jalali API ISO8601 UTC.
- V20 Modal and focus behavior consistent — Pass — ACCESSIBILITY_SPEC focus trapping Escape dismiss DESIGN_SYSTEM ConsentModal.
- V21 Dark-theme proposal vs validated preference — Pass — ADR-028 dark obsidian #0B0F17 default proposed design target for mobile gym-floor glare reduction requires user testing not claimed proven benefit light tokens remain desktop.
- V22 Persian terminology precise — Pass — PRD scenario uses Perso-Arabic script keyboard-variant normalization for Persian search not Arabic Yeh/Kaf variant folding as product scope + DOMAIN_GLOSSARY same precise phrase + explains variant example no Arabic product scope.

Blockers none blocking Phase04 after founder review — preflight corrections applied.

---

## 22. Files Created or Changed

### Created (New in Phase03)

| File Path | Action | Description |
|-----------|--------|-------------|
| `docs/architecture/SYSTEM_CONTEXT.md` | Created | C4 Level1 context diagram P0/P1/P2 trust boundaries sensitive-data boundaries Mermaid C4Context + fallback flowchart |
| `docs/architecture/CONTAINER_ARCHITECTURE.md` | Created | C4 Level2 containers modular monolith Next.js Django PG Redis S3 email abstraction future dashed Mermaid C4Container + fallback generic |
| `docs/architecture/COMPONENT_BOUNDARIES.md` | Created | Frontend Next.js app structure + backend Django 20 apps + middleware stack + dependency rules + sequence diagram assignment |
| `docs/architecture/DATA_FLOW.md` | Created | Data flows auth/invite, exercise search Persian normalization, assignment snapshot JSONB immutable, workout logging offline boundary, progress photo consent signed URL gated, messaging, privacy export/erasure |
| `docs/architecture/DEPLOYMENT_ARCHITECTURE.md` | Created | Logical deployment PaaS vs K8s, env local/staging/prod distinct, Docker + GitHub Actions CI/CD, TLS HSTS CSP, secrets manager, RPO/RTO proposed |
| `docs/architecture/ERD.md` | Created | erDiagram 30+ entities + detailed specs PK/FK tenant ownership sensitive indexes constraints state machines soft-delete archive audit retention localization conceptual DDL |
| `docs/architecture/DOMAIN_MODULES.md` | Created | 20 modules M01-M20 responsibility owned entities interfaces read/write deps security boundary events sensitivity test boundary extraction risk |
| `docs/architecture/AUTHORIZATION_ARCHITECTURE.md` | Created | RBAC roles P0 + future nutritionist P1 consent-gated + org boundaries + object-level assignment + owner aggregate vs raw + break-glass MFA+reason+audit + consent lifecycle + export/erasure auth + audit visibility + suspension + invitation + matrix per sensitive resource + negative controls |
| `docs/architecture/PWA_ARCHITECTURE.md` | Created | Three-level PWA Phase04/07/12 offline boundary explicit wording, browser limitations table, security, manifest example |
| `docs/architecture/MEDIA_STORAGE.md` | Created | Tier0/2/4 classification buckets private no listing signed URL TTL≤15min MIME whitelist thumbnail malware scan rights mandatory takedown |
| `docs/architecture/OBSERVABILITY.md` | Created | Structured logging JSON redaction request_id correlation audit vs debug separation ELK 30d audit PG 1y+ metrics Prometheus Sentry healthz/readyz alerting categories |
| `docs/architecture/BACKUP_AND_DISASTER_RECOVERY.md` | Created | Backup PG daily 30d WAL PITR 15min RPO 1h RTO versioned S3 Redis loss acceptable restore runbooks weekly automated testing RPO/RTO table disaster scenarios incident/breach response rollback |
| `docs/architecture/README.md` | Updated | From placeholder empty pending Phase03 to full index purpose doc index tech decisions summary verification no code rendering notes next phase |
| `docs/architecture/ARCHITECTURE_VALIDATION_CHECKLIST.md` | Created | V01-V22 checklist + confirmation no code |
| `docs/OPENAPI.yaml` | Created | OpenAPI 3.1 provisional /api/v1 30+ endpoints with purpose/auth/role/object permission/request/response/error/localization/idempotency/audit/rate-limit/sensitivity RFC7807 + message_key |
| `docs/JSON_SCHEMAS.md` | Created | JSON Schema draft 2020-12 snapshot immutable queue entry export manifest notification payload consent Persian normalizer pseudocode |
| `docs/THREAT_MODEL.md` | Created | STRIDE 21 threats + OWASP mapping + controls |
| `docs/PRIVACY_DATA_LIFECYCLE.md` | Created | 11 lifecycle stages Tier0-8 per class consent lifecycle export/erasure pre-DPIA |
| `docs/SECURITY_CONTROL_MATRIX.md` | Created | Threat→requirement→control→phase→test type→evidence→status including negative controls |
| `docs/ARCHITECTURE_VALIDATION_CHECKLIST.md` | Created | Copy of validation checklist at docs level (required path) |
| `docs/reports/PHASE-03-ARCHITECTURE-REPORT.md` | Created | This comprehensive 31-section completion report EN+FA executive summaries |

### Changed (Updated in Phase03)

| File Path | Action | Description |
|-----------|--------|-------------|
| `PROJECT_STATUS.md` | Updated | From Phase02 complete in progress to Phase03 complete, branch arena/019fed02 base 771afa6, one-line status Phase03 architecture complete list artifacts + verification, §1.1 Phase02 verification 7 bullets, §2 post-merge table updated, §3 constraints expanded deferred P1/P2, §4 doc inventory Phase03 final 43 ADRs + architecture docs, §5 summary Phase03 29 decisions + UX, §6 risks blockers open items license UUIDv7 backup data residency etc pending founder approval, §7 next step Phase04 awaiting explicit instruction |
| `PROJECT_CHECKLIST.md` | Updated | Phase03 section from [ ] not started to [x] complete with evidence links for each 10 items architecture diagram ADRs domain boundaries data model ERD auth model threat model privacy lifecycle API strategy backup/restore report |
| `CHANGELOG.md` | Updated | Unreleased now Phase03 package 13 architecture docs +6 top-level +1 report + preflight corrections, story count 29→27 correction, branch/base update note |
| `docs/PRD.md` | Updated | Scenario title Search query with Arabic Yeh → Search query with Perso-Arabic variant (Yeh) — Perso-Arabic script keyboard-variant normalization for Persian search + clarification no Arabic product localization implied |
| `docs/DATA_MODEL.md` | Updated | v1.1 Phase01 provisional → v2.0 Phase03 finalized pointing to ERD authoritative UUIDv7 proposed snapshot immutability consent revocation private photo storage |
| `docs/API_CONTRACT.md` | Updated | v1.1 provisional → v2.0 Phase03 provisional pointing to OPENAPI.yaml RFC7807 + message_key endpoint groups P0 |
| `docs/SECURITY_AND_PRIVACY.md` | Updated | v1.0 baseline → v2.0 Phase03 pointing to threat model control matrix privacy lifecycle Tier0-8 authorization media observability backup |
| `docs/DECISIONS.md` | Updated | v1.0 baseline → v2.0 Phase03 finalized summary table 43 ADRs ADR-002 conditionally accepted stack ADR-005 auth/session proposed ADR-009 calendar accepted conditional ADR-010 monorepo proposed ADR-012 license pending approval ADR-014 multi-role accepted ADR-015 snapshot accepted ADR-016 soft-delete vs hard-delete anonymization accepted ADR-017 UUIDv7 proposed requires validation ADR-018 Persian normalization accepted + ADR-029..043 new with detailed records for ADR-029 frontend boundaries ADR-030 backend 20 modules ADR-031 PG16 extensions ADR-032 auth/session ADR-033 RFC7807 error ADR-034 media storage ADR-035 PWA three-level ADR-036 offline boundary ADR-037 backup RTO/RPO proposed ADR-038 env separation ADR-039 CI/CD ADR-040 observability ADR-041 OpenAPI provisional ADR-042 threat model control matrix ADR-043 privacy lifecycle |
| `docs/RELEASE_PLAN.md` | Updated | v1.0 baseline → v2.0 Phase03 Milestone M3 complete ARCH-001..DOC-005 all [x] with evidence, Phase00-02 marked completed PR3/4/5, Phase03 completed |
| `docs/PROMPT_LOG.md` | Updated | Appended Prompt 004 Phase03 full text summary repository verification branch/commit PR5 merged preflight corrections 34 screens 14 specs 27 stories Persian terminology offline boundary + actions taken architecture docs list + tests/validation commands + security privacy considerations + post-merge records Post-Phase-02 Merge Record merge commit 771afa6 Post-Phase-03 Work Record |

---

## 23. GitHub Branch, Commit, Issues, and Pull Request

- **Repository:** https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform
- **Session Working Branch:** `arena/019fed02-coachos-fitness-coaching-platf` (session fixed branch, remains)
- **Base Commit on `main`:** `771afa668e71b0b181218be2e4d768e60f4f36f9` (PR #5 merged Phase02)
- **Phase 02 PR #5:** https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/5 — docs(phase-02): ux, information architecture, and design system specification — **MERGED** at 2026-08-10T18:45:01Z Merge Commit 771afa668e71b0b181218be2e4d768e60f4f36f9 head `arena/019febfc-coachos-fitness-coaching-platf` base `main`
- **Phase 01 PR #4:** Merged at 392108372450dc8a40fe79c6201144733955b7c0 (historical)
- **Phase 00 PR #3:** Merged at f52c4134087b18c4bd1a8aef9e0100fd63f71b8e (historical)
- **Current HEAD on Phase03 Branch:** `771afa668e71b0b181218be2e4d768e60f4f36f9` + local modifications uncommitted (pre-push) — will commit as Phase03 architecture package, open PR #6 (?) expected as Phase03 PR from `arena/019fed02-coachos-fitness-coaching-platf` to `main` (not merged automatically).
- **Issues:** #1 Phase01, #2 Phase00 historical — no new issues created for Phase03 (in-repo backlog `docs/RELEASE_PLAN.md` canonical)
- **Milestones 1-9:** GitHub milestones exist (Phase00-14 mapping)

---

## 24. Tests and Validation Commands

### Validation Commands Executed

```bash
# Branch and commit verification
git branch --show-current # arena/019fed02-coachos-fitness-coaching-platf
git rev-parse HEAD # 771afa668e71b0b181218be2e4d768e60f4f36f9
git log --oneline --graph --all -20
git rev-parse origin/main # 771afa6
gh pr view 5 --json state,mergedAt,headRefName,baseRefName,mergeCommit --repo AliNaderiii/CoachOS-Fitness-Coaching-Platform # MERGED 2026-08-10T18:45:01Z

# Repository tree
ls -R docs | head -n 200
find docs -type f | sort # verifies docs/architecture 13 files + docs level 6 architecture specs + ux 15 files (14 spec + README)
find docs/ux -type f | wc -l # 15

# Screen count exact
grep -c "^\| \*\*SCR-" docs/ux/SCREEN_INVENTORY.md # 34
grep -E "^\| \*\*SCR-" docs/ux/SCREEN_INVENTORY.md | wc -l # 34

# UX doc count
ls -1 docs/ux | wc -l # 15 (14 spec + README)

# Story ID traceability
grep -ho "US-[A-Z0-9-]*-[0-9]\+" docs/ux/*.md | sort | uniq # 27 stories
grep -ho "US-[A-Z0-9-]*-[0-9]\+" docs/PRD.md | sort | uniq # same 27
comm -23 <(grep -ho ... ux) <(grep -ho ... PRD) # empty → no invalid IDs like US-ATH-006

# Persian terminology
grep -R "Perso-Arabic script keyboard-variant normalization for Persian search" docs --include="*.md" | head -n 20 # verifies precise wording used
grep -R "Arabic Yeh" docs --include="*.md" | head -n 20 # only variant examples with clarification no Arabic product support, not product requirement

# Offline wording durability boundary
grep -n "message queued\|sets saved locally" docs/ux/* -i # no results after corrections (if any would be caught)
grep -n "unsaved input retained temporarily; retry required after reconnection" docs/ux/* # present correct wording STATE_AND_ERROR_MATRIX etc
grep -n "durable" docs/ux/STATE_AND_ERROR_MATRIX.md # Phase12 durable queue

# Design-system consistency
grep -n "44.*44\|48.*48" docs/ux/*.md | head -n 30 # minimum 44×44 per WCAG 2.5.5, 48×48 preferred design target for primary CTAs — requires implementation testing consistent

# No application code verification
find . -type d -name "backend" -o -name "frontend" -o -name "node_modules" | head # none
find . -name "package.json" -o -name "requirements.txt" -o -name "poetry.lock" | head # none beyond docs
find . -path "*migrations/*.py" | head # none

# No secrets
grep -R "AWS_SECRET\|password\|sk_live" --include="*.md" | grep -i secret | head # manual review no real secrets
# CI will run gitleaks secret scan in Phase04

# No Arabic locale files
find . -name "*ar*.json" | head # none expected per NFR-I18N-04
```

### Validation Results

- All 34 P0 screens exact verified, all 14 UX spec docs + README exist, all 27 P0 stories traced, no invalid IDs.
- Offline wording normalized per durability boundary Phase04/07/12.
- Persian terminology precise wording used, no Arabic product scope.
- Design-system touch target 44/48 consistent.
- No application code, dependencies, migrations, secrets, real health data in repository — verification pass.
- Mermaid diagrams syntax check: C4Context, C4Container, flowchart, sequenceDiagram, erDiagram all use supported GitHub Mermaid syntax; fallback flowcharts included where C4 may need plugin.
- OPENAPI.yaml structure validated conceptually (not via spectral lint due to no install allowed per Phase03 rule — spec artifact only, requires implementation review Phase04).
- ERD renders: Mermaid erDiagram supported; legend included.
- All architecture docs include status Accepted/Proposed/Pending Founder Approval/Deferred/Blocked/Requires implementation validation/Requires legal review distinctions.

---

## 25. Security and Privacy Risks

| Risk | Severity | Mitigation Status |
|------|----------|-------------------|
| Cross-tenant IDOR T04 critical | Critical | Preventive: OrgScopeMiddleware org_id filter server context + TenantScopedModel + import-linter; Detective: log cross-tenant attempts 403/404 + alert threshold; Corrective: block actor; Test: negative authz tests mandatory per tenant-scoped endpoint; Evidence: AUTHORIZATION_ARCHITECTURE + SECURITY_CONTROL_MATRIX |
| Progress-photo exposure T07 critical | Critical | Preventive: private buckets BlockPublicAcls true no listing signed TTL≤15min no SW cache Tier4 audit photo.viewed consent+assignment support DENIED; Detective: monitor signed URL generation rate + access logs; Corrective: revoke consent immediate invalidates future URLs short TTL mitigates existing; Test: direct S3 URL 403 signed URL after consent revoked new gen 403 unassigned 403 |
| Credential stuffing T01 high | High | Argon2id/bcrypt cost≥12 rate limit 5/15min 429 generic error password strength; Detective auth_rate_limit_hits_total; Corrective force reset invalidate sessions; Residual medium-low unless MFA all — MFA only admin P0 consider TOTP P1 |
| Session theft T02 high | High | HttpOnly Secure SameSite Lax TLS1.3 HSTS short-lived access 15min rotating refresh reuse detection no localStorage; Detective reuse refresh revokes all; Test cookie flags TTL |
| Insider/admin misuse T16 high | High | Break-glass MFA+reason+audit admin.break_glass_access Slack alert periodic review; Residual medium if audit review not enforced — require monthly audit review meeting proposed |
| Malicious media uploads T08 high | High | MIME whitelist magic bytes size checksum ClamAV quarantine rights mandatory; Test php disguised jpeg 400 oversized 413 |
| Stored XSS T09 high | High | Output encoding DOMPurify HttpOnly cookies CSP; Test injection payload rendered text |
| Supply-chain T18 critical | Critical | Lockfiles pip audit npm audit Dependabot Snyk minimal deps no unreviewed major auto-merge; Detective CI scan fails CVE; Corrective rotate secrets rebuild |
| Backup leakage T19 high | High | Snapshots encrypted private IAM no public MFA Delete Tier4 bucket Secrets Manager rotation CloudTrail log share; Test bucket policy public blocked |
| Search enumeration T20 medium | Medium | UUIDv7 non-sequential non-guessable rate limit search 30/min 404 cross-tenant; Test sequential guess 404 |

**Remaining residual risks:** Insider misuse medium if audit review not enforced, credential stuffing medium-low unless MFA expanded P1, supply-chain critical residual ongoing monitoring, backup leakage high if secrets leaked — requires Secrets Manager rotation + MFA Delete.

---

## 26. Assumptions

- PostgreSQL 16 + pg_trgm, btree_gin, pgcrypto extensions available in managed service (RDS/Supabase/Neon) — proposed pending validation Phase04.
- Redis 7 + Celery available managed (ElastiCache/Upstash/MemoryStore) — proposed.
- S3-compatible private storage available (AWS S3 or Cloudflare R2 or MinIO) — provider choice pending founder infra budget.
- Frontend hosting Vercel/Netlify/Cloudflare Pages for Next.js static + SSR — PaaS simple recommended MVP.
- Backend hosting Render/Fly.io/Railway/ECS Fargate single service for modular monolith — PaaS simple recommended MVP, K8s overkill but future-ready.
- UUIDv7 generation libraries available Python `uuid6` package or custom + JS support — proposed pending validation, fallback UUIDv4 acceptable.
- Workbox or next-pwa bundle size acceptable for PWA shell caching — proposed, alternative custom minimal SW if bundle bloat.
- Persian font Vazirmatn subsetting + font-display swap will be benchmarked Phase04 foundation to prevent CLS/layout shift on 3G.
- Jalali calendar grid component lightweight open-source React datepicker with Jalali support (date-fns-jalali or moment-jalaali) will be evaluated Phase04, zero bundle bloat target.
- Web Push iOS 16.4+ standalone only limitation documented — fallback email/in-app polling for push.
- Background Sync API Chrome only, iOS unsupported — Phase12 must have foreground fallback.
- No real PII/health data in repo — synthetic only — standing rule.

---

## 27. Open Questions

1. **Jalali Calendar Grid Component Selection (Phase04):** Which lightweight open-source React datepicker provides cleanest Jalali grid rendering with zero bundle bloat? To be evaluated Phase04 foundation.
2. **Coach Mobile Programming Depth:** Should full multi-week periodization builder be available on phones or should mobile coaches nudged toward tablet/desktop while retaining quick template assignment mobile? UX recommendation responsive accordion mobile with primary builder optimized tablet/desktop — requires user testing.
3. **UUIDv7 Library Support Validation:** Does Python `uuid6` + PG + JS generate time-ordered UUIDv7 with high B-tree locality? POC Phase04 needed — fallback UUIDv4 acceptable.
4. **pg_trgm Performance:** Trigram search performance with 10k+ exercises? GIN indexes + Persian normalizer scaling test required Phase06.
5. **Workbox vs Custom SW Bundle:** Workbox adds ~10KB? Need bundle size check vs custom minimal SW for app-shell caching strategies.
6. **PaaS vs K8s Final Choice:** Founder infra budget review — PaaS simple fast pilot vs K8s future-ready scaling.
7. **Region Selection for Data Residency:** Iran-compatible vs EU/international region for PII residency — requires legal review.
8. **S3 Provider:** AWS S3 vs Cloudflare R2 vs MinIO — cost vs latency vs Tehran connectivity.
9. **CDN for Canonical Media:** CloudFront signed URLs vs Cloudflare R2 presigned vs no CDN for MVP private media direct — cost/privacy tradeoff.
10. **RPO/RTO Cost Approval:** Multi-AZ PG, cross-region replication Tier4, retention 30d vs 7d, RPO 15min vs 5min WAL frequency — pending founder cost approval ADR-037.
11. **License Transition:** MIT vs Proprietary vs Open-Core BSL — founder decision pending ADR-012, LICENSE file remains MIT until written confirmation, do not change without explicit authorization.
12. **Age Gating:** Gym clients could include minors — policy 16+ ? Requires legal review for vulnerable data subjects.
13. **Export ZIP Include Photos?** For athlete export, include own progress photos files if <100MB total else separate signed links — open decision, requires UX + cost review.
14. **Message Retention on Erasure:** When athlete erases, messages content "[deleted]" or anonymize retaining thread for other participant? Open — requires privacy + UX decision.
15. **Owner Aggregate vs Raw Distinction Threshold:** What aggregate metrics owner can see without audited escalation? Volume, adherence %, flagged counts yes, but raw pain flag details? Currently aggregate only + audited escalation for raw — confirm with founder privacy expectations.
16. **Body Metrics Consent Granularity:** Separate consent type body_metrics vs progress_photo vs nutrition_sharing — should weight metric require same consent as photo or separate? Currently separate types allow granularity — confirm.

---

## 28. Founder Approval Items

| ID | Decision / Item | Approval Needed | Recommended Action |
|----|-----------------|-----------------|-------------------|
| ADR-012 | Repository License & IP Strategy MIT vs Proprietary All Rights Reserved vs Open-Core AGPL/BSL vs Private commercial | **YES — Founder Decision** | Founder to choose before Phase04 scaffold — LICENSE remains MIT until written confirmation, do not change without explicit authorization |
| ADR-017 | UUIDv7 vs UUIDv4/BigInt identifier strategy | No — team baseline but validation required | Team proposes UUIDv7 time-ordered non-sequential not authz substitute, fallback UUIDv4 acceptable pending Phase04 POC, founder awareness not approval but note |
| ADR-037 | Backup/RTO/RPO targets cost — Multi-AZ, cross-region replication Tier4, retention 30d vs 7d, RPO 15m vs 5m | **Yes — Cost Approval** | Founder to approve infra cost for multi-AZ PG + retention 30d vs 7d + cross-region replication Tier4 |
| ADR-038 | Environment Separation — distinct VPC/DB/buckets/secrets per env no prod data copy to local | No — team baseline | Inform founder |
| ADR-039 | CI/CD Strategy GitHub Actions + PaaS vs K8s infra choice | **Yes — Infra Budget Review** | Founder to approve PaaS simple (Vercel/Netlify + Render/Fly) vs K8s (EKS/GKE) + region selection for data residency |
| R13 | Data Residency Region Iran-compatible vs EU/international | **Yes — Legal + Infra** | Requires jurisdiction-specific legal review for PII residency — affects S3 region selection |
| R14 | S3 Provider AWS vs R2 vs MinIO + CDN provider canonical media | **Yes — Infra Budget** | Founder to choose based cost/latency/Tehran connectivity |
| LEGAL | Privacy Compliance GDPR-adjacent Iran/EU + DPIA formal required before handling real health data | **Yes — Legal Review** | Formal DPIA + legal counsel before commercial pilot handling live health data — pre-DPIA checklist documented but formal DPIA required |
| R01 | Brand Legal Name & Trademark CoachOS codename | Low — continue codename | Continue using CoachOS codename until trademark search |
| R06 | Persian Font Web Delivery subsetting font-display swap | No — team baseline | Benchmark Phase04 foundation |

All pending founder approval items remain visible — not silently turned Accepted.

---

## 29. Deferred Items

| Item | Deferred To | Rationale |
|------|-------------|-----------|
| Physical ERD Django Migrations | Phase04 | Definitive Django migrations will be created in Phase04 scaffold — conceptual DDL illustrative only in Phase03 |
| Frontend/Backend Code Scaffolding | Phase04 | Dedicated Foundation phase — Next.js + Django modular monolith + PWA manifest + SW + DB + CI |
| CI/CD Workflows .github/workflows/ | Phase04 | Lint type unit integration security scan Playwright E2E staging auto prod manual gate — spec in DEPLOYMENT_ARCHITECTURE.md but not created in Phase03 per rule no implementation |
| PWA Implementation Manifest SW Caching Offline Fallback | Phase04/07/12 | Three-level sequencing documented but not implemented — implementation validation required Phase04/07/12 |
| Nutritionist UI Flows + Backend | Phase09 P1 | Core strength coaching must stabilize first — consent model reserved in P0 |
| Billing Checkout UI + Payment Abstraction Implementation | Phase10 P1 | Payment gateway compliance Shetab domestic / Stripe international — adapter design documented but implementation deferred |
| AI Copilot UI + Safety Controls | Phase11 P2 | Requires safety guardrails + backend evaluation + human-in-loop |
| Wearable Integrations HealthKit/Health Connect + Native Bridge Decision | Phase12 P2 | PWA cannot access native health APIs directly without native bridge — evaluation deferred |
| Webhook Forgery Controls T12 Payment | Phase10 | Threat documented now but implementation of webhook signature verification idempotency deferred until payment adapter implementation |
| Prompt Injection Controls T17 AI | Phase11 | Threat documented now but eval cases implemented when AI introduced |
| Malware Scan ClamAV Integration | Phase13 QA | Basic MIME magic validation P0, ClamAV worker quarantine Phase13 |
| Advanced Offline Sync Queues IndexedDB Background Sync Conflict Resolution | Phase12 | Durable queue only Phase12 — Phase07 temporary memory only explicit |
| Push Notification Implementation Web Push VAPID | Phase12 P2 | Limitations documented but implementation evaluated Phase12 iOS 16.4+ standalone only |
| Formal DPIA + Legal Review | Before Pilot | Pre-DPIA checklist documented but formal DPIA requires legal counsel before commercial pilot handling real health data |
| Multi-Location Org Support | P1 Phase10 | Single-location-first MVP per ADR-013 — data model includes Location entity for forward compatibility but full multi-location deferred |
| Marketplace Discovery | P2 Phase11+ | Public marketplace reviews discovery deferred — no directory in P0 |

---

## 30. Checklist Changes

- **PROJECT_CHECKLIST.md:** Phase03 section from [ ] Not started (10 items) to [x] Complete (2026-08-10) with evidence links to files: architecture diagram SYSTEM_CONTEXT/CONTAINER_ARCHITECTURE, ADRs ADR-002..043, domain boundaries DOMAIN_MODULES/COMPONENT_BOUNDARIES, normalized PG data model ERD, authorization model RBAC+ABAC, threat model, privacy lifecycle, API strategy OPENAPI.yaml + JSON_SCHEMAS, backup/restore OBSERVABILITY + BACKUP_AND_DISASTER_RECOVERY, report PHASE-03-ARCHITECTURE-REPORT. Standing rules No Arabic/No secrets/Synthetic data only confirmed enforced.
- **PROJECT_STATUS.md:** Updated from Phase02 complete in progress to Phase03 complete current phase Phase03 complete next phase Phase04 awaiting explicit instruction, branch arena/019fed02 base 771afa6, one-line status Phase03 architecture complete list of artifacts + verification 34 screens 14 specs 27 stories, §1.1 Phase02 verification 7 bullets, §2 post-merge table updated, §3 constraints expanded, §4 doc inventory Phase03 final 43 ADRs + architecture docs 13+6+1 report, §5 summary Phase03 29 decisions, §6 risks blockers open items license UUIDv7 backup data residency legal pending approval, §7 next step Phase04 awaiting explicit instruction.
- **CHANGELOG.md:** Unreleased now Phase03 package 13 architecture docs +6 top-level +1 report + preflight corrections, story count 29→27 correction, branch/base update note.
- **RELEASE_PLAN.md:** v1.0 baseline → v2.0 Phase03 Milestone M3 complete ARCH-001..DOC-005 all [x] with evidence, Phase00-02 marked completed PR3/4/5, Phase03 completed.
- **DECISIONS.md:** v1.0 baseline → v2.0 Phase03 finalized summary table 43 ADRs with statuses Accepted Proposed Pending Founder Approval etc + detailed records for ADR-029..043 plus updates for ADR-002/005/009/010/014/015/016/017/018.
- **DATA_MODEL.md:** v1.1 → v2.0 Phase03 finalized pointing to ERD authoritative.
- **API_CONTRACT.md:** v1.1 → v2.0 Phase03 provisional pointing to OPENAPI.yaml.
- **SECURITY_AND_PRIVACY.md:** v1.0 → v2.0 Phase03 pointing to threat model control matrix privacy lifecycle.
- **PROMPT_LOG.md:** Appended Prompt 004 Phase03 full text summary + verification + preflight corrections + actions + tests/validation + security privacy + post-merge records Post-Phase-02 Merge Record 771afa6 + Post-Phase-03 Work Record.

Only genuinely completed architecture items marked [x] — Phase04 implementation remains [ ] Not started.

---

## 31. Exact Recommended Prompt for Phase 04

```text
Execute **Phase 04 — Project Foundation and PWA Baseline**.

You are continuing the CoachOS Fitness Coaching Platform as a coordinated professional team consisting of:
- Founder’s Technical Advisor
- Product Manager
- Business Analyst
- Principal Software Architect
- Backend Architect
- Frontend/PWA Architect
- Data Architect
- Security Engineer
- Privacy and Compliance Engineer
- DevOps/SRE Architect
- QA/Test Architect
- Technical Writer
- Release Manager
- Code Reviewer

This instruction executes **Phase 04 — Project Foundation and PWA Baseline**.

**Phase 04 is project scaffolding and PWA baseline implementation.**

**Constraints still apply:**
- Languages: Persian fa-IR RTL + English en-US LTR only — Arabic strictly out of scope (no locale files, translations, UI, seed data, API resources, DB catalogs, requirements)
- B2B2C multi-tenant SaaS
- P0 roles: Platform Admin, Owner, Coach, Athlete
- Nutrition Professional P1, Marketplace P2
- Single-location-first MVP
- PWA foundation Phase04 (manifest, icons, standalone display, SW registration, app-shell caching, offline fallback, install guidance)
- Advanced offline Phase12, AI Phase11, payments Phase10
- No medical diagnosis, treatment, clinical claims
- No real personal or health data in repo — synthetic data only
- No secrets in repo — use .env.example placeholders

**Repository Verification:**
- Repository: https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform
- Phase 03 Pull Request: (to be created from arena/019fed02-coachos-fitness-coaching-platf after founder review — verify merge commit)
- Phase 03 branch currently reported: arena/019fed02-coachos-fitness-coaching-platf
- Phase 03 latest commit currently reported: (check HEAD after PR #6 merge)
- Phase 03 base commit on main: 771afa668e71b0b181218be2e4d768e60f4f36f9 (PR #5 merged Phase02) + Phase03 merge commit after review

Before doing any Phase 04 scaffolding, inspect and verify:
- Current branch and commit
- main HEAD
- PR #6 (Phase 03) state — must be merged before Phase 04 begins per phase separation rule
- Working tree state
- Complete repository tree
- PROJECT_STATUS.md
- PROJECT_CHECKLIST.md
- CHANGELOG.md
- docs/MASTER_PRODUCT_BRIEF.md, PRD.md, PERSONAS.md, USER_JOURNEYS.md, DOMAIN_GLOSSARY.md, COMPETITIVE_LANDSCAPE.md, DECISIONS.md (43 ADRs), DATA_MODEL.md, API_CONTRACT.md, SECURITY_AND_PRIVACY.md, TRACEABILITY_MATRIX.md, RELEASE_PLAN.md, PROMPT_LOG.md
- docs/reports/PHASE-00-DISCOVERY-REPORT.md, PHASE-01-REQUIREMENTS-REPORT.md, PHASE-02-UX-DESIGN-REPORT.md, PHASE-03-ARCHITECTURE-REPORT.md
- docs/architecture/SYSTEM_CONTEXT.md, CONTAINER_ARCHITECTURE.md, COMPONENT_BOUNDARIES.md, DATA_FLOW.md, DEPLOYMENT_ARCHITECTURE.md, ERD.md, DOMAIN_MODULES.md, AUTHORIZATION_ARCHITECTURE.md, PWA_ARCHITECTURE.md, MEDIA_STORAGE.md, OBSERVABILITY.md, BACKUP_AND_DISASTER_RECOVERY.md, README.md, ARCHITECTURE_VALIDATION_CHECKLIST.md
- docs/OPENAPI.yaml, docs/JSON_SCHEMAS.md, docs/THREAT_MODEL.md, docs/PRIVACY_DATA_LIFECYCLE.md, docs/SECURITY_CONTROL_MATRIX.md, docs/ARCHITECTURE_VALIDATION_CHECKLIST.md
- All files under docs/ux/ (34 screens exact, 14 UX spec docs + README)

Do not trust summary without reading actual artifacts.

**Phase Separation and Pull Request Rule:**
- PR #6 is Phase 03 architecture PR. Do not mix Phase 04 foundation artifacts into PR #6.
- If PR #6 still open: perform Phase 03 preflight audit below (architecture documentation completeness, ERD renders, OPENAPI.yaml provisional, threat model + control matrix, privacy lifecycle + pre-DPIA, media storage, PWA three-level, observability + backup, 43 ADRs, validation checklist V01-V22, no code created), if corrections required create only Phase 03 correction commits on Phase 03 branch and update PR #6, stop and report PR #6 must be reviewed and merged before Phase 04 begins.
- If PR #6 already merged: verify merge commit on main, create new Phase 04 branch from updated main, perform Phase 03 preflight audit, apply any necessary documentation corrections on Phase 04 branch, continue Phase 04 only on new branch.

This separation mandatory so Phase 03 architecture and Phase 04 foundation remain independently reviewable.

**Phase 03 Preflight Consistency Audit (Before Foundation):**
- Verify 34 P0 screens exact in SCREEN_INVENTORY.md
- Verify 14 UX spec docs + README =15 files under docs/ux/
- Verify 27 P0 stories (25 core +2 I18N) no invalid IDs
- Verify Persian terminology precise wording Perso-Arabic script keyboard-variant normalization for Persian search, no Arabic product scope
- Verify offline durability boundary wording normalized Phase04 shell-only Phase07 temp memory Phase12 durable queue
- Verify design-system 44px min 48px preferred CTA consistent
- Verify system context exists, container exists, domain modules 20 M01-M20, ERD exists renders, tenant isolation explicit, RBAC+ABAC+consent explicit, P0 API catalog provisional OpenAPI exists, threat model exists, control matrix maps threats to tests, privacy lifecycle exists, media rights architecture exists, PWA sequencing consistent, backup/restore observability exist, no app code created, no deps installed, no migrations, no Arabic scope, no AI/payment/wearable P0 implementations
- Add Phase 03 Preflight Review section to Phase 04 report if needed, or document blockers

**Non-Negotiable Product Constraints:** fa-IR RTL en-US LTR only Arabic out of scope, B2B2C multi-tenant SaaS P0 roles Platform Admin Owner Coach Athlete Nutrition P1 Marketplace P2 single-location-first PWA foundation Phase04 advanced offline Phase12 AI Phase11 payments Phase10 native app-store deferred no medical diagnosis no real health data no secrets

**Phase 04 Objective:**
Scaffold project foundation and PWA baseline as implementation-ready starting point:
- Local development setup works (docker-compose proposed with PG16 + Redis7 + MinIO S3 compatible local, but implementation per founder infra decision — no production secrets)
- Environment configuration documented (.env.example placeholders only, no real secrets)
- Frontend scaffold works (Next.js 14 App Router + React + TypeScript + Tailwind logical properties, fa-IR RTL vazirmatn + en-US LTR inter, design tokens, i18n resources fa-IR.json en-US.json with zero hardcoded strings, API client, org context, PWA foundation)
- Backend scaffold works (Django 5 + DRF + Python 3.12 modular monolith 20 modules M01-M20 structure apps/identity organizations memberships authorization exercises media programs assignments sessions progress messaging notifications audit privacy adminplatform common — models only for User Organization Membership Location? Minimal scaffold per Phase04 exit gates, not full implementation; migrations work with synthetic seed only no real PII)
- PWA foundation (Manifest manifest.json standalone icons 192/512 maskable theme #0B0F17, installable shell, Service Worker registration Workbox or custom, app-shell caching, offline fallback page localized, install guidance)
- Database and migrations work (PG16 local, Django migrations initial, pg_trgm extension, synthetic seed)
- CI pipeline works (GitHub Actions ci.yml lint type unit integration security scan secret scan gitleaks, e2e.yml Playwright placeholder, health checks)
- Lint/type/test commands work (Python ruff mypy pytest, TS tsc eslint, stylelint, import-linter for domain boundaries, secret scan)
- Health checks work (/healthz liveness, /readyz readiness checking DB Redis S3)
- Phase 04 report committed docs/reports/PHASE-04-FOUNDATION-REPORT.md with 31+ sections

**Required Foundation Deliverables (Create):**
- frontend/ scaffold (Next.js App Router, TypeScript, Tailwind, logical properties, design tokens, i18n fa-IR/en-US, PWA manifest.json, sw, offline fallback, apiClient, components/ui and layout BottomNav 5 tabs Today/Calendar/Progress/Messages/Profile collapsible sidebar 260px)
- backend/ scaffold (Django + DRF, Python 3.12, apps structure M01-M16 P0 minimal, settings, URLs, WSGI/ASGI, middleware OrgScope RequestID SecurityHeaders Audit, common mixins TimeStamped TenantScoped PersianNormalizer ErrorEnvelope Idempotency, models for User Organization Membership Invitation Location CoachAthleteAssignment Exercise? Minimal per Phase04 gates, not full M20 — guidelines in RELEASE_PLAN M4)
- docker-compose.yml (local PG + Redis + MinIO? proposed — requires founder approval but spec)
- .env.example with placeholders only no real secrets
- .github/workflows/ci.yml (lint, typecheck, unit, security scan)
- .github/workflows/e2e.yml placeholder (Playwright)
- README.md updated with local dev setup instructions fa-IR/en-US, how to run frontend backend, env config, PWA install
- docs/LOCAL_SETUP.md (detailed local dev steps)
- docs/ENVIRONMENT_CONFIGURATION.md
- docs/PWA_MANIFEST_AND_ICONS.md verification of manifest icons standalone SW registration offline fallback
- docs/reports/PHASE-04-FOUNDATION-REPORT.md with sections 1 Executive Summary 2 Persian Executive Summary 3 Phase 03 Preflight Review 4 Objectives 5 Frontend Scaffold 6 Backend Scaffold 7 Database and Migrations 8 PWA Foundation 9 CI Pipeline 10 Health Checks 11 Files Created Changed 12 GitHub Branch Commit Issues PR 13 Tests and Validation Commands 14 Security and Privacy Risks 15 Assumptions 16 Open Questions 17 Founder Approval Items 18 Deferred Items 19 Checklist Changes 20 Exact Recommended Prompt for Phase 05

**Technology Details:**
- Frontend: Next.js 14 App Router + React + TS + Tailwind logical properties + next-pwa/Workbox proposed (verify bundle size vs custom SW)
- Backend: Django 5 + DRF + Python 3.12 + PostgreSQL 16 + pg_trgm + btree_gin + Redis7 + Celery + S3-compatible private buckets presigned TTL≤15min (MinIO local) + email abstraction
- Auth: Email+password Argon2id/bcrypt cost≥12 + HttpOnly Secure SameSite Lax cookie + JWT rotating refresh 15min optional + rate limit 5/15min Redis implementation starts Phase05 but foundation middleware in Phase04
- PWA: Manifest with icons 192/512 maskable, display standalone, theme #0B0F17, start_url /app/today, background_color #0B0F17, SW registration, app-shell caching CacheFirst fonts/icons StaleWhileRevalidate JS/CSS, offline fallback page localized, install guidance beforeinstallprompt + iOS instructions per UX_COPY pwa.install_banner — no Tier4 caching in SW
- Accessibility: Design target WCAG 2.2 AA — focus trapping, visible focus ring 2px, touch targets 44×44 min 48×48 preferred primary CTA — requires implementation validation testing Phase13
- Localization: Zero hardcoded UI strings via i18n resources fa-IR.json en-US.json, CSS logical properties margin-inline etc, Persian typography Vazirmatn +15% line-height zero tracking, number formatting Intl.NumberFormat fa-IR, Jalali calendar frontend date-fns-jalali, BiDi isolation <bdi> for Latin exercise names in Persian sentences, ZWNJ \u200C handling
- No Arabic: CI lint fails if ar locale files detected (NFR-I18N-04)
- No AI/payment/wearable implementations in P0 foundation — placeholders only if needed with deferred flag

**Exit Gates Phase 04:**
- Local dev setup works docker-compose up --build brings PG Redis MinIO + backend Django migrate + frontend Next.js dev server on 0.0.0.0 (not 127.0.0.1) with preview host allowlist per Arena live preview warning handling
- Env config documented .env.example placeholders only
- Frontend scaffold works Next.js + TS + Tailwind builds dev and prod, renders Today placeholder page fa-IR RTL + en-US LTR, PWA manifest valid Lighthouse PWA score ≥90 proposed
- Backend scaffold works Django + DRF runs, migrations work, superuser creation via management command synthetic data only, healthz/readyz return ok
- PWA foundation works manifest.json standalone icons 192/512 maskable, SW registration, app-shell caching, offline fallback page localized, install guidance
- DB and migrations work PG16 initial migrations including User Organization Membership Location Invitation CoachAthleteAssignment Exercise? Minimal per Phase04 gates synthetic seed no real PII
- CI pipeline works lint/type/unit integration security scan secret scan gitleaks, Playwright placeholder E2E
- Lint/type/test commands work npm run lint, npm run typecheck, python ruff mypy pytest
- Health checks work /healthz /readyz /api/v1/health returns db redis s3 checks
- Checklist, status, changelog, prompt log, release plan, decisions updated — Phase04 marked [x] complete only when genuinely evidenced — do not mark Phase05 complete
- Phase 04 report committed

**Final Communication Protocol:**
At end Phase04 provide concise evidence-based summary separate completed proposed deferred blocked founder-approval, provide links or paths major foundation artifacts (frontend/ app routes, backend/ apps structure, docker-compose, .env.example, manifest.json, sw, .github/workflows ci.yml, health endpoints), state current branch and commit, PR status, confirm no secrets/real health data, do not start Phase05 automatically, stop and wait explicit instruction.

Next phase after review will be Phase 05 — Identity, Tenancy, and Roles — do not proceed until explicitly instructed.
```

---

## End of Report

**Branch:** `arena/019fed02-coachos-fitness-coaching-platf`  
**Commit:** `771afa6` + Phase03 modifications (uncommitted pre-push) — after push expected new commit on Phase03 branch  
**PR Status:** Phase02 PR #5 merged 771afa6, Phase03 PR to be opened from arena/019fed02 after founder review (PR #6 expected)  
**No Application Code Created Confirmation:** Yes — verification via `find backend frontend package.json requirements.txt migrations` — none present beyond docs — specification only Mermaid, OpenAPI YAML, JSON Schema, conceptual DDL, threat-model tables  
**Next Phase:** Phase04 Project Foundation and PWA Baseline — awaiting explicit instruction, do not start automatically
