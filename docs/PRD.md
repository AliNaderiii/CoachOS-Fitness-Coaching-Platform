# Product Requirements Document (PRD) — CoachOS

**Document version:** 1.0.0 (Phase 01 Implementation-Ready Specification)  
**Last updated:** 2026-08-10  
**Languages supported:** Persian (`fa-IR`, RTL), English (`en-US`, LTR)  
**Strict constraint:** Arabic is explicitly out of scope. No Arabic locale, translations, or seed data.  
**Business model:** B2B2C Multi-Tenant SaaS (Gyms/Coaches pay; Athletes included)

---

## 1. Product Overview

### 1.1 Product Vision
CoachOS is a bilingual, mobile-first coaching operating system that empowers fitness professionals, boutique training studios, and gym organizations to design structured training programs, deliver frictionless workout execution to athletes on gym floors, monitor actual performance logs and physiological feedback, and maintain strict data privacy, auditability, and multi-tenant isolation. Over time, CoachOS evolves into a unified platform connecting strength coaches, nutrition professionals, and athletes with safe, human-supervised AI assistance.

### 1.2 Problem Statement
Personal trainers, strength coaches, and gym owners lose 5–15 hours every week juggling workout programming, client check-ins, media demos, and messaging across fragmented tools (WhatsApp, Telegram, Excel spreadsheets, Google Drive, and paper notebooks). Existing Western fitness platforms (e.g., Trainerize, Everfit, TrueCoach) suffer from critical shortcomings for bilingual and regional markets:
1. **Zero Persian RTL Support:** Broken bidirectional rendering, missing Persian fitness terminology, and inability to handle Persian character search variants (`ی`/`ي`, `ک`/`ك`).
2. **Bandwidth & App-Store Friction:** Clunky 150MB native apps that fail inside low-connectivity gym basements and create app-store download resistance.
3. **Disconnected Workflows:** Disjointed communication where client feedback on specific sets is lost in general chat threads.
4. **Lack of Tenant-Safe Collaboration:** Siloed tools preventing gym owners from maintaining institutional client data continuity when coaches depart.

### 1.3 Target Market Hypothesis
- **Primary Market Segment 1 (Regional / Persian-First):** Independent personal trainers, strength & conditioning coaches, and boutique fitness facilities in Iran and the broader Persian-speaking diaspora seeking a modern, native Persian RTL fitness operating system.
- **Primary Market Segment 2 (International / Bilingual):** Coaches and gyms worldwide requiring a clean, mobile-first English LTR coaching platform with transparent B2B pricing and PWA-first accessibility.

### 1.4 Target Customers & Personas
- **P-OWNER (Gym / Organization Owner):** Manages multi-coach gyms, controls client data ownership, and tracks operational adherence.
- **P-COACH (Coach / Personal Trainer):** Programs workouts, builds template libraries, reviews logs, and provides contextual feedback.
- **P-ATH (Athlete / Client):** Executes workouts via mobile PWA, logs set actuals, views cues, and tracks personal progress.
- **P-ADMIN (Platform Administrator):** Curates global catalog, moderates media rights, oversees security, and reviews audit events.
- **P-NUT (Nutrition Professional — P1):** Delivers meal plans and monitors nutrition under explicit athlete consent.

### 1.5 Product Positioning & Value Proposition
- **For Gym Owners:** Institutional client data retention, team management, and professional brand presentation without per-client penalty pricing.
- **For Coaches:** 70% reduction in weekly programming time via fluid template builders and instant contextual feedback on athlete actuals.
- **For Athletes:** Fast, distraction-free "Today's Workout" mobile execution that works seamlessly even when gym cellular signals drop.

### 1.6 Business Model
- **B2B2C Multi-Tenant SaaS:** Organizations and independent coaches subscribe to monthly/annual tiers (e.g., Solo Coach, Studio, Multi-Coach Gym).
- **Athlete Accounts Free / Included:** Athletes never face paywalls or friction when invited by an active coach/gym.
- **Future Monetization (P1/P2):** Add-on nutrition seats, branded custom domains, and marketplace program sales (deferred).

### 1.7 Strategic Differentiation Hypotheses
1. **First-Class Persian RTL & English LTR Parity:** Engineered from day one with CSS logical properties, native Persian typography (`Vazirmatn`), and zero compromise in either language.
2. **Intelligent Persian Search Normalization:** Instant fuzzy and character-folded search across canonical and colloquial Persian exercise names.
3. **PWA-First Gym Floor Resilience:** Sub-second loading on 3G-class mobile networks with offline-resilient workout logging.
4. **Strict IP & Media Rights Provenance:** 100% verified copyright metadata on all catalog demonstration assets.
5. **Consent-Governed Multi-Professional Architecture (P1 Ready):** Clean separation of strength and nutrition coaching around a unified athlete profile.
6. **Privacy, Security & Auditability:** Immutable audit logging, zero cross-tenant leakage, and automated data portability.

### 1.8 Product Principles
1. **Smallest Valuable Increment:** Ship solid, testable foundations before adding edge-case complexity.
2. **Modular Monolith First:** Maintain domain boundaries within a single deployable unit for MVP speed and data integrity.
3. **Athlete Mobile-First, Coach Desktop/Mobile Parity:** Athlete workout logging is optimized for one-handed mobile gym use; coach programming is optimized for desktop and tablet speed.
4. **AI is a Constrained Copilot:** Never replace professional human judgment; zero autonomous medical or diagnostic claims.
5. **Privacy by Default:** Health data is strictly sensitive; user consent is mandatory for multi-professional sharing.
6. **No Unlicensed Content:** Zero scraped or proprietary third-party media without documented provenance.

### 1.9 MVP Boundaries & Scope Rules
- **Languages:** `fa-IR` and `en-US` only. **Arabic is strictly out of scope.**
- **Location Scope:** Single primary location per organization for MVP. Multi-location is P1.
- **Calendar Strategy:** UTC/Gregorian backend persistence with Persian Jalali UI formatting for `fa-IR`.

### 1.10 Explicit Non-Goals for P0
- No Arabic locale, translations, or RTL adjustments for Arabic script.
- No public marketplace or coach discovery directory (P2).
- No integrated payment processing or billing checkouts (P1 / Phase 10).
- No nutrition professional UI or meal-planning builder (P1 / Phase 09).
- No wearable hardware integrations (Apple Watch, Garmin, HealthKit, Health Connect) (Phase 12).
- No native iOS/Android binary app-store packages (PWA-first; native deferred to post-PWA review).
- No autonomous AI exercise prescriptions or clinical diagnosis features.

---

## 2. Proposed Business Goals & Hypotheses

*Note: All numerical targets below represent initial hypotheses to be empirically validated during Phase 14 pilot operations.*

| Metric ID | Business Goal Area | Proposed Pilot Hypothesis / Target | Measurement Window | Strategic Intent |
|-----------|--------------------|-----------------------------------|--------------------|------------------|
| **BG-01** | Coach Onboarding Velocity | Coach completes registration to first assigned program in < 15 minutes | Pilot Week 1–4 | Validate builder ergonomics and template usability |
| **BG-02** | Athlete Invitation Activation | > 85% of invited athletes complete profile setup within 48 hours | 30-Day Cohort | Verify low-friction onboarding and clear invite emails |
| **BG-03** | Athlete Workout Engagement | > 75% of active athletes open "Today's Workout" on scheduled training days | Ongoing Weekly | Ensure high daily utility on the gym floor |
| **BG-04** | Workout Logging Completion | > 70% of initiated workouts are submitted with completed set logs | Ongoing Weekly | Validate fast, one-handed mobile set entry |
| **BG-05** | Coach Weekly Retention | > 80% of onboarded coaches remain Weekly Active Coaches (WAC) at Day 60 | 60-Day Cohort | Prove long-term coaching workflow dependency |
| **BG-06** | Athlete Monthly Retention | > 75% 60-day athlete retention under active coaches | 60-Day Cohort | Measure client satisfaction and coaching accountability |
| **BG-07** | B2B SaaS Trial-to-Paid Conversion | > 25% of trial organizations convert to paid subscription tiers | Post-Trial (P1) | Validate commercial willingness-to-pay |
| **BG-08** | Security & AuthZ Safety | Zero (0) critical cross-tenant data leaks or authorization bypass incidents | Continuous | Enforce non-negotiable security baseline |
| **BG-09** | Localization Quality | < 1% of support inquiries related to RTL layout, font rendering, or BiDi issues | Continuous | Deliver flawless Persian and English experiences |

---

## 3. Measurable Success Metrics

| Metric Name | Formal Definition | Event Trigger / Calculation | Target Direction | Phase Scope | Risk of Misinterpretation & Guardrails |
|-------------|-------------------|-----------------------------|------------------|-------------|----------------------------------------|
| **Time to First Program Assigned (TTFA)** | Elapsed time between coach account creation and the first successful `ProgramAssignment` creation | `program_assignment.created_at - user.created_at` | Minimizing (Target < 15 min) | P0 / Phase 05–06 | Fast assignment might produce empty or low-quality programs; verify program contains >= 3 workout items. |
| **Athlete Activation Rate (AAR)** | Percentage of invited athletes who set a password, choose a locale, and open their dashboard | `(activated_athletes / total_invitations_sent) * 100` | Maximizing (Target > 85%) | P0 / Phase 05 | High activation with zero workout logs indicates fake or dormant signups. |
| **Today's Workout Open Rate** | Ratio of scheduled workout views to total scheduled workouts on a given date | `(unique_athletes_viewed_today / total_athletes_with_scheduled_workout)` | Maximizing (Target > 75%) | P0 / Phase 07 | Athletes might open the app just to see the workout but log on paper; pair with completion rate. |
| **Workout Completion Rate (WCR)** | Percentage of initiated `WorkoutSessions` marked `Completed` with actual set logs | `(completed_sessions / started_sessions) * 100` | Maximizing (Target > 70%) | P0 / Phase 07 | Quick button clicks without actual load data could artificially inflate WCR; require set actual validation. |
| **Weekly Active Coaches (WAC)** | Distinct coaches who build a program, review a log, or message an athlete in a 7-day window | `COUNT(DISTINCT coach_id)` performing operational action in 7 days | Maximizing | P0 / Phase 05+ | Passive logins without coaching mutations do not count as active engagement. |
| **Weekly Active Athletes (WAA)** | Distinct athletes who log at least one workout set or message their coach in a 7-day window | `COUNT(DISTINCT athlete_id)` logging >= 1 set in 7 days | Maximizing | P0 / Phase 07+ | Distinguish between passive viewers and active lifters logging sets. |
| **Coach Response Time (CRT)** | Median time taken for a coach to view or reply to an athlete's completed workout log or feedback flag | `median(coach_comment_time - workout_completed_time)` | Minimizing (Target < 4 hours) | P0 / Phase 08 | Coaches might batch-review once a week; allow async workflows without penalizing rest days. |
| **RTL / i18n Issue Rate** | Volume of UI layout, text truncation, or BiDi display bug reports per 1,000 active sessions | `(i18n_bugs / active_sessions) * 1000` | Zero (Target < 0.5) | P0 / Phase 04–07 | Ensure bugs are categorized specifically as typography, layout mirroring, or translation string errors. |
| **Critical Authorization Bugs** | Confirmed incidents where a user accessed data outside their tenant or assignment scope | Count of verified security bugs/incidents | **Strictly Zero (0)** | P0 / Continuous | Immediate P0 blocker if > 0. Validated via automated negative security test suites. |

---

## 4. P0 Functional Scope & Epic Breakdown

### Summary of P0 Epics
- **Epic E1: Identity, Tenancy & Access Control (AUTH & ORG)**
- **Epic E2: Internationalization & Localization (I18N)**
- **Epic E3: Bilingual Exercise Library & Content Moderation (EX)**
- **Epic E4: Training Programming & Versioned Builder (PRG)**
- **Epic E5: Mobile Athlete Execution & Progress Logging (ATH)**
- **Epic E6: Contextual Communication & Notifications (MSG & NTF)**
- **Epic E7: Platform Administration, Audit & Data Privacy (ADM, AUD, PRI)**
- **Epic E8: PWA Foundation & Installable Shell (PWA)**

---

## 5. Detailed P0 User Stories & Acceptance Criteria

### Epic E1: Identity, Tenancy & Access Control

```
===============================================================================
US-AUTH-001: User Registration & Email Credential Onboarding
===============================================================================
- Persona: P-OWNER, P-COACH, P-ATH
- Business Value: Secure, self-serve account creation enabling role-based onboarding.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 05 (Identity & Tenancy)
- Traceability Link: FR-AUTH-01 -> REQ-AUTH-001

User Story:
As an unauthenticated user,
I want to register an account using my email and a secure password,
So that I can securely access the CoachOS platform and establish my profile.

Preconditions:
- User has access to a valid email account.
- User is on the `/register` page.

Main Flow:
1. User enters display name, email, and password (minimum 8 characters with strength requirements).
2. User submits registration form.
3. System validates input, hashes password using Argon2/bcrypt, creates `User` record with `is_active=True`, and issues session/tokens.
4. System redirects user to the onboarding flow based on their entry route (Org creation for owners, invitation accept for coaches/athletes).

Alternate Flow:
- User was invited via an organization link: system pre-fills the email address and automatically links the membership upon registration completion.

Error Flow:
- User submits an already-registered email: system returns a clear, localized message ("An account with this email already exists") and prompts login.
- Weak password submitted: inline validation displays specific unmet criteria.

Permission Requirements:
- Public endpoint; rate-limited (maximum 5 requests/minute per IP).

Data Requirements:
- Creates `User` record (id, email, password_hash, display_name, preferred_locale, timezone, created_at).

Acceptance Criteria (Gherkin):
Scenario: Successful user registration
  Given a visitor navigates to the registration screen
  When they provide a unique email "coach@example.com" and a valid password "P@ssw0rd123!"
  Then a new user account is created with encrypted credentials
  And the user is authenticated and issued a secure session
  And an audit event "user.registered" is recorded

Scenario: Registration with duplicate email rejected
  Given a user exists with email "existing@example.com"
  When a visitor attempts to register with "existing@example.com"
  Then the request is rejected with a 409 Conflict error
  And no password reset token or account data is leaked
```

```
===============================================================================
US-AUTH-002: Secure Password Authentication & Rate Limiting
===============================================================================
- Persona: All Personas
- Business Value: Prevents unauthorized account access and brute-force credential stuffing attacks.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 05 (Identity & Tenancy)
- Traceability Link: FR-AUTH-01 -> REQ-AUTH-002

User Story:
As a registered user,
I want to authenticate using my email and password,
So that I can access my coaching organization and private training records.

Preconditions:
- User possesses an active CoachOS account.

Main Flow:
1. User enters email and password on `/login`.
2. System verifies credentials against stored hash.
3. Upon success, system resets failed login counters and establishes an authenticated session.
4. User is redirected to their default dashboard based on their active membership role.

Error Flow:
- Invalid password: system increments failed attempt counter and returns generic "Invalid email or password" error.
- Account locked/rate limited: after 5 consecutive failed attempts within 15 minutes, IP and email are rate-limited with HTTP 429 Too Many Requests.

Acceptance Criteria (Gherkin):
Scenario: Successful login resets failed attempts
  Given a valid user with email "reza@example.com"
  When they submit the correct password
  Then an authenticated session is established
  And their failed login attempt counter is reset to 0

Scenario: Brute-force rate limiting triggered
  Given a user account "sarah@example.com"
  When an actor submits 5 incorrect passwords within 5 minutes
  Then the 6th login attempt is rejected with HTTP 429 Too Many Requests
  And an audit security alert "auth.login_rate_limit_exceeded" is logged
```

```
===============================================================================
US-AUTH-003: Password Reset Workflow
===============================================================================
- Persona: All Personas
- Business Value: Enables secure, self-service account recovery without administrative overhead.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 05 (Identity & Tenancy)
- Traceability Link: FR-AUTH-02 -> REQ-AUTH-003

User Story:
As a user who forgot their password,
I want to request a secure password reset link via email,
So that I can regain access to my account safely.

Main Flow:
1. User enters email on `/forgot-password`.
2. System generates a cryptographically random, single-use reset token with a 15-minute expiration time.
3. System dispatches a localized email containing the reset link.
4. User clicks link, enters a new valid password, and confirms.
5. System updates password hash, invalidates all existing active sessions/tokens, and marks reset token as used.

Acceptance Criteria (Gherkin):
Scenario: Password reset token single-use enforcement
  Given a user requested a password reset and received a valid token
  When the user successfully resets their password using the token
  And an attacker attempts to reuse the same reset token
  Then the second attempt is rejected with HTTP 400 Bad Request
  And the password remains unchanged
```

```
===============================================================================
US-ORG-001: Organization Creation & Tenancy Initialization
===============================================================================
- Persona: P-OWNER
- Business Value: Establishes a secure, multi-tenant customer workspace for gyms and coaching teams.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 05 (Identity & Tenancy)
- Traceability Link: FR-ORG-01 -> REQ-ORG-001

User Story:
As an authenticated gym owner,
I want to create an organization workspace with a name and slug,
So that I can manage my coaches, athletes, and templates under a centralized tenant.

Main Flow:
1. Owner submits organization name (e.g., "Alborz Athletic Club") and slug ("alborz-ac").
2. System verifies slug uniqueness, creates `Organization` record, and automatically creates an `Owner` `Membership` for the user.
3. System provisions default tenant settings (units, timezone, locale).

Acceptance Criteria (Gherkin):
Scenario: Organization created with owner membership
  Given an authenticated user "Mehdi"
  When Mehdi creates an organization named "Rostam Gym" with slug "rostam-gym"
  Then the organization is saved in the database
  And Mehdi is granted the "Owner" membership role for "rostam-gym"
  And an audit log "org.created" is recorded with Mehdi's user ID
```

```
===============================================================================
US-ORG-002: Single Primary Location Profile Configuration (MVP)
===============================================================================
- Persona: P-OWNER
- Business Value: Associates physical facility metadata with an organization without multi-location complexity.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 05 (Identity & Tenancy)
- Traceability Link: FR-ORG-01 -> REQ-ORG-002

User Story:
As an organization owner,
I want to configure our primary gym facility address and phone number,
So that our organization profile reflects our physical coaching location.

Main Flow:
1. Owner opens Organization Settings -> Facility Profile.
2. Owner inputs facility name, address, city, and primary contact phone.
3. System persists the record as the organization's single primary location.

Acceptance Criteria (Gherkin):
Scenario: Primary location updated by owner
  Given an authenticated Owner of organization "Tehran Fitness"
  When they update the primary facility address to "Valiasr St, Tehran"
  Then the primary location details are updated
  And coaches within "Tehran Fitness" can view the facility information
```

```
===============================================================================
US-ORG-003: Coach Invitation & Role Assignment
===============================================================================
- Persona: P-OWNER
- Business Value: Allows gym owners to scale their coaching staff under an organization umbrella.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 05 (Identity & Tenancy)
- Traceability Link: FR-ORG-02 -> REQ-ORG-003

User Story:
As an organization owner,
I want to invite a personal trainer to join our gym via email as a Coach,
So that they can access organization templates and train assigned athletes.

Main Flow:
1. Owner navigates to Team -> Invite Member, enters coach's email, and selects role `Coach`.
2. System generates a secure, 7-day single-use invitation token and sends an email.
3. When coach accepts, system creates/links their user account with `Membership(role=Coach, status=Active)`.

Acceptance Criteria (Gherkin):
Scenario: Coach invitation cannot be reused
  Given an active invitation token for "coach.reza@example.com"
  When Reza accepts the invitation and creates his account
  And another actor attempts to accept using the same invitation link
  Then the request is rejected with HTTP 410 Gone / Expired
```

```
===============================================================================
US-ORG-004: Athlete Invitation & Coach Assignment
===============================================================================
- Persona: P-OWNER, P-COACH
- Business Value: Onboards clients directly into a coach's roster with zero payment friction for the athlete.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 05 (Identity & Tenancy)
- Traceability Link: FR-ORG-02 -> REQ-ORG-004

User Story:
As a coach or gym owner,
I want to invite an athlete by email and assign them to a specific coach,
So that the athlete can immediately view and log workouts designed for them.

Main Flow:
1. Coach clicks "Add Athlete", inputs athlete email and name.
2. System creates pending `Membership(role=Athlete, status=Invited)` and `CoachAthleteAssignment`.
3. Athlete receives invitation email with single-use onboarding link.

Acceptance Criteria (Gherkin):
Scenario: Athlete assigned to coach upon invite
  Given Coach Sarah invites athlete "neda@example.com"
  When Neda clicks the invitation link and sets her password
  Then Neda's membership status becomes "Active"
  And Neda is explicitly bound to Coach Sarah in the CoachAthleteAssignment table
```

```
===============================================================================
US-ORG-005: Membership Management & Role Revocation
===============================================================================
- Persona: P-OWNER
- Business Value: Protects gym intellectual property and client data continuity when staff changes.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 05 (Identity & Tenancy)
- Traceability Link: FR-AUTHZ-01 -> REQ-ORG-005

User Story:
As an organization owner,
I want to suspend a departing coach's membership and reassign their athletes,
So that the departing coach loses access to gym data while athletes continue training seamlessly.

Acceptance Criteria (Gherkin):
Scenario: Suspended coach immediately loses access
  Given Coach Reza's membership in "Gym A" is changed to "Suspended" by the Owner
  When Reza makes an API request to view Gym A's athlete roster
  Then the server returns HTTP 403 Forbidden
  And no athlete records are returned
```

---

### Epic E2: Internationalization & Localization (`i18n`)

```
===============================================================================
US-I18N-001: Language & Direction Switching (`fa-IR` RTL / `en-US` LTR)
===============================================================================
- Persona: All Personas
- Business Value: Provides an uncompromising native experience for Persian and English users.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 04–07 (Foundation through Athlete App)
- Traceability Link: FR-I18N-01 -> REQ-I18N-001

User Story:
As a user,
I want to switch the application language between Persian and English at any time,
So that the entire interface renders in my preferred language and natural reading direction.

Acceptance Criteria (Gherkin):
Scenario: Persian locale renders RTL with Persian typography
  Given a user selects "فارسی" (fa-IR) in the language selector
  When the page renders
  Then the HTML document tag has dir="rtl" and lang="fa-IR"
  And all visible strings originate from Persian translation resources
  And typography uses the Persian font stack (Vazirmatn)
  And no Arabic strings or Arabic-specific resources are loaded

Scenario: English locale renders LTR
  Given a user selects "English" (en-US) in the language selector
  When the page renders
  Then the HTML document tag has dir="ltr" and lang="en-US"
  And all visible strings originate from English translation resources
```

```
===============================================================================
US-I18N-002: Persian Search Normalization & Character Variant Folding
===============================================================================
- Persona: P-COACH, P-ATH
- Business Value: Guarantees search matches regardless of Arabic vs Persian keyboard inputs.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 06 (Exercise Library)
- Traceability Link: FR-EX-01 -> REQ-I18N-002

User Story:
As a Persian-speaking coach,
I want exercise search to normalize Arabic character variants (ي to ی, ك to ک),
So that I can quickly find exercises regardless of device keyboard settings.

Acceptance Criteria (Gherkin):
Scenario: Search query with Arabic Yeh matches Persian exercise
  Given an exercise in the catalog named "پرس سینه دمبل"
  When a coach searches for "پرس سينه" (using Arabic Yeh 'ي')
  Then the search returns "پرس سینه دمبل" in the result list
  And search scoring ranks exact normalized matches first
```

---

### Epic E3: Bilingual Exercise Library & Content Moderation

```
===============================================================================
US-EX-001: Bilingual Canonical Exercise Catalog Browsing & Filtering
===============================================================================
- Persona: P-COACH, P-ATH
- Business Value: Comprehensive, anatomically classified exercise library speeding up programming.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 06 (Exercise Library)
- Traceability Link: FR-EX-01 -> REQ-EX-001

User Story:
As a coach,
I want to browse and filter the canonical exercise library by muscle group, movement pattern, equipment, and difficulty,
So that I can quickly select appropriate exercises for client programs.

Acceptance Criteria (Gherkin):
Scenario: Filter exercises by muscle and equipment
  Given the coach opens the exercise catalog
  When they filter by Muscle: "Quadriceps" and Equipment: "Barbell"
  Then only barbell quad exercises (e.g., Back Squat, Front Squat) are displayed
  And each exercise displays bilingual names and primary movement pattern
```

```
===============================================================================
US-EX-002: Custom Private Exercise Creation with Media Provenance
===============================================================================
- Persona: P-COACH
- Business Value: Allows coaches to add unique variations with mandatory copyright protection.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 06 (Exercise Library)
- Traceability Link: FR-EX-02 -> REQ-EX-002

User Story:
As a coach,
I want to create a custom exercise for my gym with demo video links and rights metadata,
So that my athletes can view our private exercise variations legally and safely.

Acceptance Criteria (Gherkin):
Scenario: Custom exercise requires rights metadata
  Given a coach creates a custom exercise "B-Stance Hip Thrust"
  When they attach a demonstration video URL
  Then the system requires selecting a license type (e.g., Original Content / Licensed)
  And the custom exercise is visible only to members of the coach's organization
```

```
===============================================================================
US-EX-003: Platform Admin Exercise Moderation & Catalog Approval
===============================================================================
- Persona: P-ADMIN
- Business Value: Ensures global public library contains only verified, legally cleared, high-quality content.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 06 (Exercise Library)
- Traceability Link: FR-ADM-01 -> REQ-EX-003

User Story:
As a platform administrator,
I want to review submitted exercise candidates, verify cues, and approve media rights,
So that only safe, high-quality exercises are published to the global catalog.

Acceptance Criteria (Gherkin):
Scenario: Admin approves candidate exercise
  Given a pending exercise submission "Bulgarian Split Squat"
  When the Platform Admin reviews translations and approves copyright metadata
  Then the exercise status transitions to "Published"
  And it becomes visible in the global library for all organizations
```

---

### Epic E4: Training Programming & Versioned Builder

```
===============================================================================
US-PRG-001: Hierarchical Training Program Builder
===============================================================================
- Persona: P-COACH
- Business Value: Fast, flexible programming supporting modern strength & conditioning methodologies.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 06 (Exercise Library & Programs)
- Traceability Link: FR-PRG-01 -> REQ-PRG-001

User Story:
As a coach,
I want to construct a multi-week training program with phases, days, workouts, supersets, and set prescriptions (sets, reps, load, tempo, RPE, rest),
So that I can build comprehensive periodized training regimens for my clients.

Acceptance Criteria (Gherkin):
Scenario: Constructing a workout with supersets and tempo
  Given a coach is editing "Week 1 - Day 1"
  When they add Exercise A (Bench Press) and Exercise B (Chest-Supported Row) into Group "A" (Superset)
  And configure Bench Press with 4 sets, 8 reps, 80kg, tempo "3-1-1-0", and RPE 8
  Then the workout structure is persisted
  And preview reflects the superset pairing and prescription details
```

```
===============================================================================
US-PRG-002: Reusable Program Templates
===============================================================================
- Persona: P-COACH
- Business Value: Multiplies coach productivity by eliminating repetitive program drafting.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 06 (Exercise Library & Programs)
- Traceability Link: FR-PRG-01 -> REQ-PRG-002

User Story:
As a coach,
I want to save a completed program as a reusable organization template,
So that I can clone and adapt it for multiple athletes in seconds.

Acceptance Criteria (Gherkin):
Scenario: Cloning an existing program template
  Given an organization template "12-Week Powerbuilding"
  When Coach Reza clones the template for athlete "Jordan"
  Then an independent program copy is created
  And edits made to Jordan's program do not mutate the master template
```

```
===============================================================================
US-PRG-003: Program Assignment & Immutable Snapshot Creation
===============================================================================
- Persona: P-COACH
- Business Value: Binds programs to athlete calendars while protecting historical log integrity.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 06 (Exercise Library & Programs)
- Traceability Link: FR-PRG-02 -> REQ-PRG-003

User Story:
As a coach,
I want to assign a program to an athlete starting on a specific date,
So that the athlete's workout calendar is populated and an immutable snapshot is preserved.

Acceptance Criteria (Gherkin):
Scenario: Program assignment creates immutable version snapshot
  Given Coach Sarah assigns "Hypertrophy Block" to Athlete Neda starting next Monday
  When the assignment transaction completes
  Then a point-in-time ProgramSnapshot is generated
  And Neda's calendar displays scheduled workouts starting next Monday
  And subsequent modifications to Coach Sarah's draft template do not alter Neda's active snapshot
```

---

### Epic E5: Mobile Athlete Execution & Progress Logging

```
===============================================================================
US-ATH-001: Athlete "Today's Workout" Dashboard
===============================================================================
- Persona: P-ATH
- Business Value: Immediate, zero-click clarity on what exercises and targets to train today.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 07 (Athlete App & Progress)
- Traceability Link: FR-ATH-01 -> REQ-ATH-001

User Story:
As an athlete,
I want to open CoachOS on my phone and instantly view today's scheduled workout,
So that I know exactly what exercises, weights, and coaching cues to perform without searching.

Acceptance Criteria (Gherkin):
Scenario: Athlete views Today's Workout on training day
  Given an athlete has a scheduled workout "Leg Day" for today's date
  When they open the application
  Then the "Today's Workout" card is prominently displayed
  And tapping it reveals the list of prescribed exercises, targets, and previous logs
```

```
===============================================================================
US-ATH-002: Workout Execution & Set Logging Actuals
===============================================================================
- Persona: P-ATH
- Business Value: High-speed, one-handed set logging that captures accurate training data at the gym.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 07 (Athlete App & Progress)
- Traceability Link: FR-ATH-02 -> REQ-ATH-002

User Story:
As an athlete,
I want to record my actual completed weight, reps, and RPE for each set with minimal taps,
So that I can log my workout effortlessly between sets and trigger rest countdowns.

Acceptance Criteria (Gherkin):
Scenario: Athlete logs set actuals and triggers rest timer
  Given an active workout session for Athlete Jordan
  When Jordan enters "100 kg" and "8 reps" for Set 1 and taps complete
  Then the set actual is recorded with a timestamp
  And a 90-second rest countdown timer begins automatically
  And the coach dashboard reflects the completed set
```

```
===============================================================================
US-ATH-003: Exercise Modification / Substitution with Reason
===============================================================================
- Persona: P-ATH
- Business Value: Maintains training momentum while recording structured reasons for deviations.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 07 (Athlete App & Progress)
- Traceability Link: FR-ATH-02 -> REQ-ATH-003

User Story:
As an athlete on the gym floor,
I want to substitute an exercise or skip a set with a mandatory reason,
So that my coach understands why I modified the prescribed plan.

Acceptance Criteria (Gherkin):
Scenario: Athlete substitutes exercise due to busy equipment
  Given a prescribed exercise "Leg Press"
  When the athlete selects "Substitute" -> "Dumbbell Lunge" and picks reason "Equipment Unavailable"
  Then the workout session updates to reflect the substitution
  And a notification flag is attached to the session for coach review
```

```
===============================================================================
US-ATH-004: Pain, Fatigue & Session Feedback Reporting
===============================================================================
- Persona: P-ATH
- Business Value: Early injury prevention and objective readiness tracking for coaches.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 07 (Athlete App & Progress)
- Traceability Link: FR-ATH-02 -> REQ-ATH-004

User Story:
As an athlete completing a workout,
I want to report my overall session exertion, fatigue score, and any joint pain flags,
So that my coach can adjust my volume before injuries occur.

Acceptance Criteria (Gherkin):
Scenario: Pain flag alerts coach immediately
  Given an athlete completes a workout and flags "Mild Shoulder Pain (4/10)" on Bench Press
  When the athlete submits the workout
  Then the workout status transitions to "Completed"
  And the coach receives a high-priority in-app alert: "Athlete Neda reported shoulder pain on Bench Press"
```

```
===============================================================================
US-ATH-005: Permissioned Progress Photo & Body Metric Privacy
===============================================================================
- Persona: P-ATH
- Business Value: Safe physiological tracking under strict athlete-controlled privacy.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 07 (Athlete App & Progress)
- Traceability Link: FR-ATH-02 -> REQ-ATH-005

User Story:
As an athlete,
I want to upload progress photos and record body weight with explicit privacy controls,
So that only my assigned coach can view my photos and they are never publicly exposed.

Acceptance Criteria (Gherkin):
Scenario: Unauthorized user cannot access progress photos
  Given Athlete Neda uploaded a private progress photo
  And Coach Sarah is assigned to Neda
  And Coach David belongs to the same gym but is not assigned to Neda
  When Coach David requests Neda's progress photo URL
  Then the server returns HTTP 403 Forbidden
  And media storage signed URLs are never generated for unauthorized actors
```

---

### Epic E6: Contextual Communication & Notifications

```
===============================================================================
US-MSG-001: Contextual Coach-Athlete 1:1 Message Threads
===============================================================================
- Persona: P-COACH, P-ATH
- Business Value: Keeps coaching feedback directly connected to training data rather than lost in chat apps.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 08 (Communication & Notifications)
- Traceability Link: FR-MSG-01 -> REQ-MSG-001

User Story:
As a coach or athlete,
I want to send 1:1 messages linked to specific workout sessions or check-in dates,
So that our communication remains organized and contextualized.

Acceptance Criteria (Gherkin):
Scenario: Contextual message linked to workout log
  Given Coach Reza reviews Athlete Jordan's Squat log
  When Reza clicks "Comment on Workout" and types "Great depth on set 3, keep chest tall"
  Then the message is saved in the contextual thread linked to WorkoutSession ID
  And Jordan receives an in-app notification with a direct link to the squat set
```

```
===============================================================================
US-NTF-001: In-App Notification System & Preferences
===============================================================================
- Persona: All Personas
- Business Value: Keeps users informed of training milestones without notification fatigue.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 08 (Communication & Notifications)
- Traceability Link: FR-NTF-01 -> REQ-NTF-001

User Story:
As a user,
I want to receive in-app notifications for assignments, messages, and feedback, and configure my channel preferences,
So that I stay updated on critical coaching events.

Acceptance Criteria (Gherkin):
Scenario: Disabling non-critical notifications
  Given an athlete toggles off "Marketing & General Updates" in notification preferences
  When a general platform announcement is dispatched
  Then the athlete does not receive an in-app toast or email
  And training-critical assignment alerts continue to deliver
```

---

### Epic E7: Platform Administration, Audit & Data Privacy

```
===============================================================================
US-AUD-001: Immutable Audit Logging for Sensitive Operations
===============================================================================
- Persona: P-ADMIN, P-OWNER
- Business Value: Guarantees compliance, security traceability, and operational accountability.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 05+ (Foundation & Security)
- Traceability Link: FR-AUD-01 -> REQ-AUD-001

User Story:
As a security engineer or platform administrator,
I want all authentication, authorization changes, member revocations, and sensitive health reads logged in an immutable audit log,
So that every security-critical event is traceable and verifiable.

Acceptance Criteria (Gherkin):
Scenario: Sensitive role change generates audit log
  Given Owner Mehdi changes Coach Reza's role from "Coach" to "Suspended"
  When the transaction commits
  Then an immutable AuditEvent is created with:
    | actor_id | Mehdi |
    | action | membership.status_changed |
    | target_id | Reza |
    | org_id | Org A |
    | metadata | {"old_status": "active", "new_status": "suspended"} |
  And the audit log cannot be modified or deleted by any regular tenant user
```

```
===============================================================================
US-PRI-001: Athlete Data Export Workflow Design & Endpoint
===============================================================================
- Persona: P-ATH
- Business Value: Satisfies GDPR/data portability rights and establishes strong athlete trust.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 03 / Phase 13 (Architecture & Security)
- Traceability Link: FR-PRI-01 -> REQ-PRI-001

User Story:
As an athlete,
I want to request a complete machine-readable export of my profile and workout history,
So that I retain full ownership of my fitness records regardless of gym affiliation.

Acceptance Criteria (Gherkin):
Scenario: Athlete requests data export archive
  Given an authenticated Athlete Jordan
  When Jordan triggers "Request Data Export"
  Then the system generates a secure, encrypted archive containing profile.json, workouts.json, and set_logs.csv
  And dispatches a time-limited download link to Jordan's verified email
```

```
===============================================================================
US-PRI-002: Athlete Account Deletion / Right-to-Erasure Workflow
===============================================================================
- Persona: P-ATH
- Business Value: Ensures privacy compliance (GDPR Right to Erasure) while maintaining audit integrity.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 03 / Phase 13 (Architecture & Security)
- Traceability Link: FR-PRI-01 -> REQ-PRI-002

User Story:
As an athlete,
I want to permanently delete my account and erase my personal health data,
So that my private information is not retained after I leave the platform.

Acceptance Criteria (Gherkin):
Scenario: Account erasure wipes PII and anonymizes logs
  Given an authenticated athlete submits a confirmed deletion request
  When the deletion workflow executes
  Then athlete name, email, phone, progress photos, and private notes are permanently purged
  And historical workout volume aggregates are disassociated from the personal identity
```

---

### Epic E8: PWA Foundation & Installable Shell

```
===============================================================================
US-PWA-001: PWA Foundation: Web App Manifest & Installable Shell
===============================================================================
- Persona: P-ATH, P-COACH
- Business Value: Enables home-screen installation, fullscreen app view, and sub-second load times without app store friction.
- Priority: P0 (Core MVP)
- Planned Phase: Phase 04 (Project Foundation)
- Traceability Link: FR-PWA-01 -> REQ-PWA-001

User Story:
As an athlete or coach on a mobile device,
I want to install CoachOS to my smartphone home screen and use it as a fullscreen app,
So that I get a native app experience with zero app-store download delays.

Acceptance Criteria (Gherkin):
Scenario: PWA install prompt criteria met
  Given a mobile user visits CoachOS on iOS Safari or Android Chrome
  When the browser evaluates manifest.json and Service Worker registration
  Then the app meets PWA installability criteria
  And launching from home screen opens in standalone fullscreen mode without browser URL chrome
```

---

## 6. Comprehensive Permissions Matrix

The following matrix defines the authoritative server-side authorization boundaries across all system roles.

| Resource / Domain Entity | Operation | Platform Admin (`P-ADMIN`) | Organization Owner (`P-OWNER`) | Coach (`P-COACH`) | Athlete (`P-ATH`) | Nutritionist (`P-NUT` P1) | Support Staff (`P-SUP`) |
|---|---|---|---|---|---|---|---|
| **Users / Credentials** | Create / Register | Self | Invite Org Staff | Invite Athletes | Self | Self (via Invite) | None |
| | Read Profile | All (Audited) | Org Members | Self & Assigned Athletes | Self & Assigned Coach | Permitted Athletes | Org Read-Only |
| | Update Profile | Self / Suspend Any | Org Members | Self Only | Self Only | Self Only | None |
| | Delete / Erase PII | Execute Erasure | Org Scope (Pending Hold) | None | Request Self Erasure | None | None |
| **Organizations** | Create | Unrestricted | Create Tenant | None | None | None | None |
| | Read Settings | All | Own Org | Own Org (Limited) | Own Org (Branding Only) | Own Org (Limited) | Own Org (Read) |
| | Update Settings | All (Audited) | Own Org | None | None | None | None |
| | Archive / Delete Org | All (Audited) | Own Org | None | None | None | None |
| **Locations (MVP 1 Primary)** | Create / Update | All | Own Org Primary Location | Read Only | Read Only | Read Only | Read Only |
| **Memberships & Invites** | Create Invite | All | Owner / Coach / Athlete | Athlete Only | None | None | Resend Only |
| | Revoke / Suspend | All (Audited) | Own Org Members | Assigned Athletes (Remove) | None | None | None |
| **Exercise Library** | Create Canonical | **Yes (Direct Publish)** | None | Submit for Review | None | None | None |
| | Create Private Custom | None | Own Org Private | Own Org Private | None | None | None |
| | Read Catalog | All | All + Org Private | All + Org Private | All + Org Private | Read Catalog | Read Catalog |
| | Moderate / Approve | **Yes (Full Authority)** | None | None | None | None | None |
| | Archive / Restore | All (Audited) | Org Private Only | Org Private Created | None | None | None |
| **Programs & Templates** | Create Master Template | Global Template | Own Org Templates | Own Org Templates | None | None | None |
| | Read Templates | All | Own Org Templates | Own Org Templates | Assigned Snapshots Only | Read Training Context | Read Templates |
| | Assign to Athlete | None | Any Org Athlete | **Assigned Athletes Only** | None | None | None |
| | Snapshot / Version | Auto-Created | Auto-Created | Auto-Created | Read Bound Version | Read Bound Version | Read Bound Version |
| **Workout Logs & Actuals** | Create / Log Set | None | None | Log on Behalf (Proxy) | **Log Own Sets (Primary)** | None | None |
| | Read Workout Logs | All (Audited) | Own Org Athletes | **Assigned Athletes Only** | **Own Logs Only** | Permitted Athlete Logs | Read Org Logs |
| | Comment / Feedback | System Notes | Own Org Athletes | Assigned Athletes | Own Sessions | Collaborative Note | None |
| **Sensitive Health & Photos** | Upload Progress Photo | None | None | None | **Own Photos (Consent)** | None | None |
| | View Progress Photo | Strictly Audited Escalation | Assigned Athletes (If Permitted) | **Assigned Athletes Only** | **Own Photos Only** | Explicit Consent Only | **DENIED (Zero Access)** |
| | View Pain / Injury Flags | All (Audited) | Own Org Athletes | **Assigned Athletes Only** | **Own Flags Only** | Permitted Athletes | Read Flags |
| **Messages & Threads** | Send 1:1 Message | System Broadcast | Own Org Staff/Athletes | Assigned Athletes & Org Owner | Assigned Coach & Org Owner | Assigned Athletes | None |
| | Read Private Threads | Audited Escalation Only | Org Admin Escalation | Assigned Threads Only | Own Threads Only | Assigned Threads Only | **DENIED** |
| **Audit Logs** | Read Audit Trail | **Global Audit Trail** | **Own Org Audit Trail** | None | None | None | Org Audit (Read) |
| | Mutate Audit Trail | **STRICTLY FORBIDDEN (Immutable DB Rules)** | **FORBIDDEN** | **FORBIDDEN** | **FORBIDDEN** | **FORBIDDEN** | **FORBIDDEN** |

---

## 7. Prioritized Backlog (P1 & P2)

### 7.1 P1 Backlog: Nutrition, Scheduling & Coach Business Operations

| Item ID | Feature Title | User Problem & Expected Value | Complexity | Dependencies | Key Risks | Why Not in P0? | Proposed Success Metric | Suggested Phase |
|---------|---------------|-------------------------------|------------|--------------|-----------|----------------|-------------------------|-----------------|
| **P1-NUT-01** | Nutrition Professional Role & Consent-Based Access | Athletes need unified macro coaching alongside strength programs without privacy leaks. | High | E1 (Auth), E7 (Privacy) | Consent revocation edge cases; data isolation complexity. | Core strength MVP must stabilize before adding dietary engine. | > 30% of multi-coach gyms onboard a nutritionist seat. | Phase 09 |
| **P1-NUT-02** | Persian & International Food Catalog & Macro Calculator | Existing macro databases lack authentic Iranian food items (e.g., Sangak, Ghormeh Sabzi). | High | P1-NUT-01 | Food database accuracy and licensing. | Requires curated nutritional research and verified calorie tables. | > 5,000 localized food items indexed with verified macros. | Phase 09 |
| **P1-NUT-03** | Meal Plan Builder & Client Food Logging | Dietitians need to design flexible meal plans; athletes need frictionless food logging. | High | P1-NUT-02 | Client logging drop-off; complex UI. | High UI surface area; deferred to dedicated nutrition sprint. | > 65% 7-day food log completion rate. | Phase 09 |
| **P1-HAB-01** | Structured Daily Habits & Weekly Check-ins | Coaches need accountability tracking for water intake, sleep, and steps beyond workouts. | Medium | E5 (Athlete App) | Habit fatigue if over-prescribed. | Basic workout pain/fatigue flags in P0 cover immediate readiness. | > 70% weekly check-in submission rate. | Phase 07 / 09 |
| **P1-SCH-01** | 1:1 Session Scheduling & Calendar Booking | Coaches spend hours scheduling in-person PT slots and assessment calls. | Medium | E1 (Tenancy), ADR-009 (Jalali) | Jalali/Gregorian time zone synchronization bugs. | MVP focuses on asynchronous workout execution delivery. | > 500 coaching sessions booked through platform monthly. | Phase 08 / 10 |
| **P1-PAY-01** | Payment Gateway Abstraction & Coach Subscriptions | Coaches need to collect recurring client fees and sell training packages. | High | E1 (Tenancy) | Dual-gateway (Shetab domestic vs Stripe international) compliance. | Payment integrations have distinct legal and banking hurdles. | $0 gateway reconciliation errors; 100% automated subscription billing. | Phase 10 |
| **P1-LOC-01** | Multi-Location Gym & Staff Management | Multi-branch gym franchises need branch-specific coach rosters and reporting. | High | E1 (Org Tenancy) | Complex cross-location membership routing. | Single-location MVP validates 95% of target boutique gyms faster. | Multi-branch gyms manage > 3 locations on single subscription. | Phase 10 |

### 7.2 P2 Backlog: Marketplace, Wearables, AI Copilot & Advanced Scale

| Item ID | Feature Title | User Problem & Expected Value | Complexity | Dependencies | Key Risks | Why Not in P0? | Proposed Success Metric | Suggested Phase |
|---------|---------------|-------------------------------|------------|--------------|-----------|----------------|-------------------------|-----------------|
| **P2-MKT-01** | Public Coach Marketplace & Discovery Directory | Independent coaches want new inbound leads; athletes want verified coaching reviews. | Very High | P1-PAY-01, E1 (Auth) | Two-sided marketplace liquidity chicken-and-egg problem; review fraud. | Building a directory before perfecting the coaching OS guarantees failure. | > 1,000 organic client-coach matches per quarter. | Phase 11+ |
| **P2-AI-01** | Constrained AI Workout Adaptation Copilot | Coaches need fast program variations based on athlete fatigue and equipment limits. | High | E4 (Programs), E5 (Logs) | AI hallucinating unsafe volume or dangerous exercise progressions. | Requires stable exercise data model, safety guardrails, and human review UI. | > 85% coach acceptance rate on AI-generated suggestions without edits. | Phase 11 |
| **P2-WRB-01** | Wearable Integrations (HealthKit, Health Connect, Garmin) | Athletes want heart rate, recovery, and step data automatically imported. | Very High | E5 (Athlete App), Phase 12 | Battery drain; platform policy changes (Apple/Google). | PWA cannot access native health APIs directly without native bridge/APIs. | > 40% of active athletes sync daily wearable data. | Phase 12 |
| **P2-WHT-01** | Custom Branded Mobile Apps & White-Label Domains | Large gym franchises want their custom logo in App Stores and custom domain URLs. | Very High | PWA Foundation | App Store review rejections; multi-tenant SSL cert management. | Highly bespoke; enterprise feature for mature SaaS stage. | > 20 enterprise gym contracts signed. | Phase 12+ |

---

## 8. Non-Functional Requirements (NFRs)

### 8.1 Security & Integrity Requirements
- **NFR-SEC-01 (Password Hashing):** All passwords hashed using Argon2id or bcrypt (cost factor >= 12) with unique cryptographic salts.
- **NFR-SEC-02 (Transport Security):** Strict HTTPS/TLS 1.3 enforced for all traffic; HSTS headers with `max-age=31536000; includeSubDomains`.
- **NFR-SEC-03 (Authentication Rate Limiting):** Login and password reset endpoints limited to maximum 5 attempts per 15 minutes per IP/account; HTTP 429 returned on breach.
- **NFR-SEC-04 (Token & Session Security):** Session cookies configured with `HttpOnly; Secure; SameSite=Lax`. JWT tokens (if used) have max 15-minute access token TTL and rotating refresh tokens.
- **NFR-SEC-05 (Media Asset Isolation):** Private user media (progress photos) stored in non-public buckets; accessed exclusively via cryptographically signed URLs with maximum 15-minute TTL.
- **NFR-SEC-06 (No Secrets in Repository):** Static analysis in CI checks every commit for credentials, API tokens, or private keys; zero secrets permitted in repository.

### 8.2 Authorization & Tenancy Boundaries
- **NFR-AUTHZ-01 (Server-Side Enforcement):** 100% of authorization checks executed on backend API handlers; client-side route guards are treated as cosmetic UX only.
- **NFR-AUTHZ-02 (Tenant Isolation Guarantee):** Every database query touching tenant data must include explicit `organization_id` filters; cross-tenant leakage prevented by automated security test assertions.
- **NFR-AUTHZ-03 (Object-Level Authorization):** Coaches can only query athletes linked via active `CoachAthleteAssignment` records; unauthorized access returns HTTP 403 or 404.

### 8.3 Privacy & Data Governance
- **NFR-PRV-01 (Data Minimization):** Zero collection of extraneous PII; health metrics limited strictly to coaching-relevant physiological variables.
- **NFR-PRV-02 (Immutable Audit Logging):** All authentication events, role escalations, member suspensions, and sensitive health reads produce append-only audit events stored with actor ID, timestamp, and IP hash.
- **NFR-PRV-03 (Data Portability & Deletion):** Self-service endpoints for full JSON/CSV data export and account anonymization/erasure pipeline (GDPR Article 17/20 compliant).
- **NFR-PRV-04 (No Real PII in Development):** Test fixtures, seed data, and documentation must exclusively use synthetic, fictionalized data.

### 8.4 Accessibility (WCAG 2.2 AA)
- **NFR-A11Y-01 (Color Contrast):** Minimum 4.5:1 contrast ratio for standard text and 3:1 for large text and interactive UI controls.
- **NFR-A11Y-02 (Keyboard & Screen Reader Navigability):** All interactive components (inputs, modals, buttons, workout cards) fully operable via keyboard with visible focus indicators and ARIA labels.
- **NFR-A11Y-03 (Touch Target Sizing):** Mobile interactive targets (e.g., set checkmark buttons, number keypad inputs) possess a minimum touch dimension of 44x44 CSS pixels.

### 8.5 Performance & Low-Bandwidth Usability
- **NFR-PERF-01 (Today's Workout Loading):** Athlete "Today's Workout" dashboard loads and renders interactive content in < 1.5 seconds on a simulated 3G mobile network (750kbps / 100ms RTT).
- **NFR-PERF-02 (API Latency):** 95th percentile (p95) API response time < 200ms for read endpoints; < 400ms for complex builder save operations under standard load.
- **NFR-PERF-03 (Frontend Bundle Size):** Initial mobile JavaScript payload < 150KB compressed (Gzip/Brotli) to guarantee fast gym parsing on budget smartphones.

### 8.6 Reliability & Data Integrity
- **NFR-REL-01 (Transactional Integrity):** Multi-entity mutations (program assignments, workout completions, member suspensions) execute within atomic database transactions.
- **NFR-REL-02 (Automated Backups & Restore Testing):** Daily automated PostgreSQL snapshots with Point-in-Time Recovery (PITR); documented and tested restore runbook before pilot release.
- **NFR-REL-03 (Workout Offline Resilience):** Set actuals logged during temporary gym network loss are persisted in browser IndexedDB/localStorage and automatically synced upon reconnection.

### 8.7 Localization (`fa-IR` & `en-US`)
- **NFR-I18N-01 (Zero Hardcoded Strings):** 100% of user-facing UI text sourced from externalized localization resource bundles (`fa-IR.json`, `en-US.json`).
- **NFR-I18N-02 (Logical CSS Layout):** Layouts use CSS logical properties (`margin-inline`, `padding-inline`, `start`/`end`) ensuring automatic and bug-free bidirectional rendering.
- **NFR-I18N-03 (Persian Typography & Numbers):** Persian locale loads `Vazirmatn` web font; numbers, dates, and weights format according to the active locale without directional distortion.
- **NFR-I18N-04 (Arabic Exclusion):** Automated CI lint checks verify that zero Arabic locale files or Arabic translation keys exist in the codebase.

### 8.8 Progressive Web App (PWA) Baseline
- **NFR-PWA-01 (Installability):** Valid `manifest.json` with standalone display mode, high-res icons (192px, 512px, maskable), and active Service Worker registration.
- **NFR-PWA-02 (Offline Shell Caching):** Core app shell and static assets cached locally to allow immediate application launch in zero-connectivity environments.
