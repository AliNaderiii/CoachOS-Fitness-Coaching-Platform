# User Personas — CoachOS

**Document version:** 1.0.0 (Phase 01 Baseline)  
**Last updated:** 2026-08-10  
**Target market context:** Bilingual coaching ecosystem supporting Persian (`fa-IR`, RTL) and English (`en-US`, LTR).  
**Constraint enforcement:** Arabic is strictly out of scope. No Arabic persona data or workflows.

---

## Persona Overview Matrix

| ID | Persona Title | Archetype Name | Primary Domain Role | Economic Model | Target Locale(s) | Phase Alignment |
|----|---------------|----------------|---------------------|----------------|------------------|-----------------|
| **P-ADMIN** | Platform Administrator | Saman / Alex | System Super-Admin & Moderator | Internal Operations | Persian / English | P0 (Core) |
| **P-OWNER** | Gym / Organization Owner | Mehdi / Marcus | Multi-Coach Studio & Gym Operator | Primary Payer (SaaS Org Subscription) | Persian / English | P0 (Core) |
| **P-COACH** | Coach / Personal Trainer | Sarah / Reza | Independent or Gym-Affiliated Coach | Payer (Individual SaaS) or Org Seat | Persian / English | P0 (Core) |
| **P-ATH** | Athlete / Client | Neda / Jordan | Client Receiving Personal Coaching | Free / Included Account | Persian / English | P0 (Core) |
| **P-NUT** | Nutrition Professional | Dr. Mina / Elena | Registered Dietitian / Nutrition Specialist | Future Payer / Seat Add-on | Persian / English | P1 (Backlog) |
| **P-SUP** | Support / Read-Only Staff | Arash / Taylor | Org Assistant / Operations Staff | Included in Org Tier | Persian / English | P0/P1 Optional |

---

## 1. Persona: Platform Administrator (P-ADMIN)

### 1.1 Archetype Profile
- **Names:** Saman (Tehran / International) / Alex (Toronto)
- **Role:** Platform Operations, Trust & Safety, Catalog Curator
- **Environment:** Desktop / Laptop (macOS / Linux / Windows, Chrome/Firefox)
- **Primary Locale:** Persian (`fa-IR`) and English (`en-US`) bilingual proficiency

### 1.2 Goals & Objectives
- Maintain integrity, accuracy, and legal safety of the global exercise and media catalog.
- Monitor multi-tenant isolation, authorization anomalies, and platform availability.
- Moderate user-submitted exercise videos/images for intellectual property compliance and safety.
- Swiftly assist organization owners with account disputes or technical escalations while respecting audit boundaries.

### 1.3 Jobs-To-Be-Done (JTBD)
- *When* a coach submits a new public exercise candidate, *I want to* inspect its metadata, terminology, Persian/English translations, and media provenance *so that* only high-quality, legally cleared content enters the global catalog.
- *When* a security incident or anomalous data access pattern is flagged, *I want to* inspect structured audit logs without viewing raw private health payloads *so that* I can enforce tenant safety and verify compliance.
- *When* an organization owner requests account recovery or closure, *I want to* execute audited administrative actions *so that* business continuity is maintained with complete traceability.

### 1.4 Pain Points & Current Workarounds
- **Pain Points:** Bogus exercise entries with missing cues or incorrect muscle tags; copyright infringement risks from uploaded YouTube/Instagram rips; manual database scripts needed for tenant troubleshooting.
- **Current Workarounds:** Ad-hoc spreadsheet logs, direct database read-replicas, manual reverse-image searches for copyright checks.

### 1.5 Technical Comfort & Privacy Concerns
- **Technical Comfort:** Expert (understands relational databases, HTTP headers, RBAC, OAuth/JWT, audit logs).
- **Privacy Concerns:** Must adhere to strict least-privilege principles. Cannot view athlete private photos or injury notes unless explicitly required and logged in an immutable audit trail.
- **Accessibility Needs:** Standard WCAG 2.2 AA desktop accessibility; rapid keyboard shortcuts for moderation queues.

### 1.6 Success & Abandonment Criteria
- **Success Criteria:** Zero copyright violation claims; moderation queue turnaround < 24 hours; zero cross-tenant data leakage.
- **Abandonment Triggers:** Inability to audit actions, opaque black-box database state, lack of moderation tooling leading to catalog pollution.

### 1.7 Critical Workflows
1. Log in via administrative portal with MFA.
2. Review pending exercise submissions in the moderation queue.
3. Validate Persian and English names, aliases, instructions, and media license provenance.
4. Approve, reject with structured feedback, or edit canonical exercise entries.
5. Review platform audit logs filtered by organization ID, actor ID, or event type.

---

## 2. Persona: Gym / Organization Owner (P-OWNER)

### 2.1 Archetype Profile
- **Names:** Mehdi (Tehran / Isfahan) / Marcus (London)
- **Role:** Owner / Director of a boutique training studio, gym franchise, or online coaching group (5–25 coaches, 100–500 athletes)
- **Environment:** Desktop/Laptop (office management) + Smartphone (on-the-floor check-ins)
- **Primary Locale:** Persian (`fa-IR`, RTL) or English (`en-US`, LTR)

### 2.2 Goals & Objectives
- Centralize coaching operations under a unified organization brand and single management dashboard.
- Onboard, organize, and monitor staff coaches without losing client relationship history if a coach leaves.
- Maintain a single primary location profile for MVP while ensuring data ownership stays with the business.
- Track overall athlete retention, workout completion rates, and coach responsiveness.

### 2.3 Jobs-To-Be-Done (JTBD)
- *When* I hire a new personal trainer, *I want to* send them an organization invitation link with the `Coach` role *so that* they immediately get access to our training templates and can be assigned athletes.
- *When* a coach departs the gym, *I want to* revoke their membership and reassign their active athletes to another coach *so that* client training continues uninterrupted and client data remains within the organization.
- *When* reviewing monthly operations, *I want to* view high-level client adherence and active coach metrics *so that* I can identify struggling clients and high-performing trainers.

### 2.4 Pain Points & Current Workarounds
- **Pain Points:** Coaches managing clients in personal WhatsApp/Telegram chats, causing client churn when coaches leave; fragmented spreadsheets for workouts; lack of professional Persian-language fitness management tools in the local market.
- **Current Workarounds:** Shared Google Sheets, WhatsApp groups, paper binders, generic studio management tools that lack workout programming capabilities.

### 2.5 Technical Comfort & Privacy Concerns
- **Technical Comfort:** Moderate (familiar with web dashboards, WhatsApp, POS systems, Instagram business).
- **Privacy Concerns:** Demands tenant isolation. Client data must never be visible to competing gyms on the platform. Requires clear data ownership contracts.
- **Accessibility Needs:** High contrast UI, clean typography in Persian (`Vazirmatn` or equivalent readable web font), mobile-friendly responsive admin views.

### 2.6 Willingness-To-Pay & Failure Triggers
- **Willingness-to-Pay Assumption:** High. Willing to pay a recurring monthly/annual B2B SaaS subscription per coach seat ($15–$35/coach/month or localized equivalent) for business continuity, centralization, and professional brand presentation.
- **Failure & Abandonment Triggers:** Complex onboarding taking more than 15 minutes; software crashes on mobile; coaches refusing to use the app due to sluggish UI; lack of Persian payment options or locale bugs.

### 2.7 Critical Workflows
1. Register organization account and establish primary location profile.
2. Select organization default locale (Persian RTL or English LTR).
3. Invite staff coaches via email invitations.
4. Monitor member roster, assign/reassign athletes to coaches.
5. Review high-level organization analytics (active athletes, adherence rates, workout logs).
6. Manage subscription billing and organization settings.

---

## 3. Persona: Coach / Personal Trainer (P-COACH)

### 3.1 Archetype Profile
- **Names:** Sarah (Tehran / Shiraz) / Reza (Mashhad / Dubai) / David (Austin)
- **Role:** Full-time Personal Trainer, Online Strength Coach, or Gym Staff Coach (managing 15–50 active 1:1 athletes)
- **Environment:** Desktop / Tablet (for weekly program building) + Smartphone (for daily messaging, quick log review, and on-the-floor coaching)
- **Primary Locale:** Persian (`fa-IR`, RTL) or English (`en-US`, LTR)

### 3.2 Goals & Objectives
- Build, customize, and assign multi-week periodized training programs in minutes rather than hours.
- Monitor athlete workout execution, actual weights lifted, RPE, and adherence in real time.
- Provide fast, contextual coaching feedback directly attached to specific exercises or workout days.
- Maintain a private, reusable template library and custom exercise variations with clear video demos.

### 3.3 Jobs-To-Be-Done (JTBD)
- *When* onboarding a new athlete, *I want to* clone an existing 4-week Hypertrophy template, adjust the volume/load for their level, and assign it to their calendar *so that* they have their complete plan ready immediately.
- *When* an athlete logs a workout with a pain flag or high RPE on squats, *I want to* receive an immediate notification and review their notes *so that* I can adjust their next session or message them with form cues.
- *When* searching for an exercise in Persian (e.g., "پرس سینه دمبل"), *I want* intelligent character normalization to find the exercise instantly regardless of Arabic/Persian letter variants (`ی`/`ي`, `ک`/`ك`).

### 3.4 Pain Points & Current Workarounds
- **Pain Points:** Spending 10+ hours every Sunday writing custom programs in Excel/Word; scrolling through endless WhatsApp chat threads to find last week's squat weight; athletes forgetting their prescribed weights and form cues; English-only international apps confusing Persian-speaking clients.
- **Current Workarounds:** Excel spreadsheets sent as PDFs, voice notes on WhatsApp/Telegram, YouTube links for exercise demos, Instagram saved collections.

### 3.5 Technical Comfort & Privacy Concerns
- **Technical Comfort:** Moderate to High (power user of mobile apps, social media, fitness trackers; values speed, keyboard shortcuts on desktop, and drag-and-drop builders).
- **Privacy Concerns:** Needs assurance that proprietary program templates are private to their organization/account and cannot be stolen or seen by other coaches.
- **Accessibility Needs:** Clear touch targets (minimum 44x44px), rapid number keypad inputs, support for both metric (`kg`) and imperial (`lbs`) units.

### 3.6 Willingness-To-Pay & Failure Triggers
- **Willingness-to-Pay Assumption:** Moderate to High. If independent, willing to pay $20–$50/month for software that saves 5+ hours of programming per week and elevates client retention. If gym-employed, covered by the gym owner.
- **Failure & Abandonment Triggers:** Clunky, slow program builder requiring too many clicks per set; athlete complaints that the app is confusing or fails to load at the gym; missing Persian exercises or broken RTL layout.

### 3.7 Critical Workflows
1. Accept gym invitation or register independent coach profile.
2. Search canonical exercise catalog and create custom private exercises with demo links.
3. Build a structured training program (phases, weeks, days, workouts, supersets, sets, reps, load, RPE, tempo, rest).
4. Save program as a reusable template and assign to athlete with start date.
5. Review daily athlete workout execution logs, actuals, RPE, and pain/fatigue flags.
6. Send contextual coaching messages directly on workout logs.

---

## 4. Persona: Athlete / Client (P-ATH)

### 4.1 Archetype Profile
- **Names:** Neda (Tehran / Karaj) / Jordan (Chicago) / Kian (Isfahan)
- **Role:** Working professional, amateur athlete, or fitness enthusiast receiving 1:1 remote or hybrid coaching
- **Environment:** Mobile-First (iOS / Android smartphone via PWA / mobile browser, often inside gym environments with spotty cellular data)
- **Primary Locale:** Persian (`fa-IR`, RTL) or English (`en-US`, LTR)

### 4.2 Goals & Objectives
- Open the app at the gym and instantly see "What exercises, sets, and weights do I do today?"
- Watch short, clear exercise demonstration videos and read Persian/English coaching cues.
- Quickly log completed weights, reps, and RPE with minimal taps and zero friction between sets.
- Track personal strength progression, body metrics, and communicate directly with their coach.

### 4.3 Jobs-To-Be-Done (JTBD)
- *When* I arrive at the gym, *I want to* tap "Today's Workout" and see my ordered exercise list with my coach's target weights and last week's logged performance *so that* I know exactly what load to put on the barbell.
- *When* a prescribed machine is occupied or my shoulder hurts, *I want to* substitute the exercise or log a modification with a reason *so that* my coach understands why I adjusted the plan.
- *When* I finish my workout, *I want to* submit my session with overall fatigue and pain feedback *so that* my coach can review my progress and adjust my next cycle.

### 4.4 Pain Points & Current Workarounds
- **Pain Points:** Squinting at tiny PDF attachments on their phone while standing in a busy gym; forgetting what weight was used last week; confusing English terminology for Persian speakers; losing coach messages in crowded WhatsApp chats; apps that require heavy data downloads on slow gym Wi-Fi.
- **Current Workarounds:** Notes app on phone, paper notebooks, messaging the coach voice notes between sets, guessing weights.

### 4.5 Technical Comfort & Privacy Concerns
- **Technical Comfort:** Average consumer (expects intuitive, Instagram/Spotify-level mobile UX, zero tutorial required, fast touch response, offline resilience during workout logging).
- **Privacy Concerns:** High sensitivity regarding body weight, progress photos, and injury notes. Demands that progress photos are private between them and their coach, never public.
- **Accessibility Needs:** Large, legible typography; high contrast numbers; large hit targets for sweaty gym fingers; native Persian number formatting; screen-reader labels for all icons.

### 4.6 Willingness-To-Pay & Failure Triggers
- **Willingness-to-Pay Assumption:** Free / Included. The athlete account is paid for by their coach or gym. Zero tolerance for mandatory paywalls or unexpected subscription popups.
- **Failure & Abandonment Triggers:** App fails to load or loses logged sets when cellular connection drops inside the gym; confusing workout interface requiring too many taps; broken Persian RTL rendering making numbers look backwards.

### 4.7 Critical Workflows
1. Receive email invitation from coach/gym and set up profile (name, preferred locale, units).
2. Install PWA to smartphone home screen.
3. Open "Today's Workout" on training days.
4. View exercise demonstration videos and coaching cues.
5. Enter actual reps, load (`kg`/`lbs`), and RPE per set.
6. Use rest timer between sets.
7. Record workout completion with fatigue score, pain flags, and athlete notes.
8. View personal workout history and message coach.

---

## 5. Persona: Nutrition Professional (P-NUT) — [P1 Backlog]

### 5.1 Archetype Profile
- **Names:** Dr. Mina (Tehran / Tabriz) / Elena (San Francisco)
- **Role:** Registered Dietitian, Sports Nutritionist, or Certified Macro Coach collaborating with coaches and athletes
- **Environment:** Desktop / Laptop (meal plan building) + Mobile (client food log check-ins)
- **Primary Locale:** Persian (`fa-IR`, RTL) or English (`en-US`, LTR)

### 5.2 Goals & Objectives (P1 Target)
- Prescribe calorie, macronutrient, and micronutrient targets tailored to athlete training phases.
- Build flexible meal plans utilizing culturally relevant Persian foods (e.g., Ghormeh Sabzi, Chelo Kabab, Sangak bread) and standard international foods.
- Review athlete food logs, adherence percentages, and body composition trends.
- Seamlessly collaborate with the athlete's strength coach under explicit, consent-governed boundaries.

### 5.3 Jobs-To-Be-Done (JTBD)
- *When* an athlete is assigned to me by an organization, *I want* the athlete to grant explicit consent *so that* I can access their body metrics, training schedule, and dietary intake history.
- *When* designing a meal plan for a Persian athlete, *I want to* select authentic Iranian foods with accurate macro breakdowns *so that* the client can adhere to the plan using local groceries.
- *When* an athlete experiences digestive distress or energy crashes on heavy training days, *I want to* view their workout schedule and adjust intra-workout nutrition in sync with the coach.

### 5.4 Pain Points & Current Workarounds
- **Pain Points:** International nutrition apps (e.g., MyFitnessPal) have poor Persian food databases and zero coach-dietitian collaboration; Western meal planning templates prescribe ingredients unavailable or unaffordable in local markets; dietitians and strength coaches working in silos with conflicting advice.
- **Current Workarounds:** Excel macro sheets, PDF meal plan printouts, WhatsApp photo exchanges of meal plates.

### 5.5 Technical Comfort & Privacy Concerns
- **Technical Comfort:** Moderate to High.
- **Privacy Concerns:** Extremely high. Health, dietary habits, eating disorders, and biometric data require strict confidentiality, explicit consent mechanisms, and clear audit logging.
- **Accessibility Needs:** Standard WCAG 2.2 AA desktop accessibility.

### 5.6 Willingness-To-Pay & Failure Triggers
- **Willingness-to-Pay Assumption:** High. Willing to pay $25–$60/month for an integrated nutrition platform that syncs with fitness coaching and supports regional Persian food databases.
- **Failure & Abandonment Triggers:** Inability to customize food database; lack of Iranian food items; complex multi-step logging that clients abandon after 3 days.

### 5.7 Critical Workflows (P1 Target)
1. Accept invitation to join organization as Nutritionist.
2. Request and verify athlete consent for dietary profile access.
3. Establish daily caloric and macronutrient targets linked to training vs rest days.
4. Build meal plans using bilingual food database (including localized Iranian items).
5. Review athlete daily food logs and adherence scores.
6. Leave comments and adjust meal plans in collaboration with the assigned coach.

---

## 6. Persona: Support / Read-Only Staff (P-SUP) — [Optional / Baseline]

### 6.1 Archetype Profile
- **Names:** Arash (Tehran) / Taylor (Denver)
- **Role:** Gym Front-Desk Assistant, Customer Success Specialist, or Read-Only Audit Assistant
- **Environment:** Desktop / Tablet / Smartphone
- **Primary Locale:** Persian (`fa-IR`) or English (`en-US`)

### 6.2 Goals & Objectives
- Verify athlete membership status, coach assignment, and class/session attendance without having permission to alter training programs or access private medical/progress photos.
- Provide first-tier technical support (e.g., resending invitation emails, verifying password reset status).

### 6.3 Jobs-To-Be-Done (JTBD)
- *When* an athlete arrives at the front desk, *I want to* verify their active membership and assigned coach *so that* facility access is confirmed.
- *When* an athlete reports not receiving their invitation email, *I want to* check invitation status and resend the link *so that* the client is not blocked.

### 6.4 Pain Points, Comfort, & Constraints
- **Pain Points:** Accidental modification of coach programs; exposure to sensitive client medical information.
- **Technical Comfort:** Basic to Moderate.
- **Privacy Constraints:** Strictly read-only on administrative fields; zero access to private progress photos, sensitive health notes, or coach-athlete private message threads.

---

## 7. Persona Comparison & Priority Alignment

| Attribute | P-ADMIN | P-OWNER | P-COACH | P-ATH | P-NUT (P1) | P-SUP |
|-----------|---------|---------|---------|-------|------------|-------|
| **MVP Priority** | P0 (Core) | P0 (Core) | P0 (Core) | P0 (Core) | P1 (Deferred) | P0 Baseline |
| **Primary Device** | Desktop | Desktop/Mobile | Desktop/Tablet/Mobile | Mobile PWA | Desktop/Mobile | Desktop/Tablet |
| **Primary Payer?** | No (Internal) | **Yes** (Org SaaS) | **Yes** (Seat / Pro) | No (Included) | Yes (P1 Add-on) | No (Org Seat) |
| **RTL/LTR Criticality** | High | Extreme | Extreme | Extreme | Extreme | High |
| **Data Sensitivity** | Audit/Catalog | Org Business | Client Logs/Notes | Personal Health/Media | Diet/Biometrics | Restricted |
| **Offline Need** | Low | Low | Low | **High** (Gym Floor) | Low | Low |
