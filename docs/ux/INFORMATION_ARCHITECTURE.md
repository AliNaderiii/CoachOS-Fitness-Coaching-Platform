# Information Architecture & Navigation Hierarchy — CoachOS

**Document version:** 1.0.0 (Phase 02 Baseline)  
**Last updated:** 2026-08-10  
**Supported Locales:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR)  
**Strict constraint:** Arabic is strictly out of scope.  
**Design Phase:** Phase 02 — Documentation and specifications only. No application source code.

---

## 1. Information Architecture Principles

1. **Role-Tailored Workspaces:** The application surfaces distinct, contextual primary views tailored to the active user role (`Athlete`, `Coach`, `Organization Owner`, `Platform Administrator`).
2. **Athlete Mobile-First Streamlining:** The athlete workspace is structured around a zero-friction daily loop: *Today's Workout -> Log Sets -> Review Progress -> Message Coach*.
3. **Coach Multi-Pane Efficiency:** The coach workspace prioritizes high-density, multi-pane desktop and tablet layouts for fast program building and bulk log reviews, with responsive mobile support for on-the-floor coaching.
4. **Tenant-Safe Context Encapsulation:** All organization management, coach rosters, athlete profiles, and templates exist strictly within the active organization boundary. Multi-org users switch tenants through an explicit tenant switcher.
5. **Bidirectional Structural Symmetry:** Every hierarchical level, navigation drawer, and data table preserves identical logical hierarchy in both Persian RTL and English LTR layouts.

---

## 2. Global Site Map & Role Routing Hierarchy

```
CoachOS Application Root (/)
├── Public / Unauthenticated Space
│   ├── /login (Login Screen)
│   ├── /register (Self-Registration)
│   ├── /forgot-password (Password Reset Request)
│   ├── /reset-password/:token (Password Reset Confirmation)
│   └── /invite/:token (Organization Invitation Acceptance)
│
├── Athlete Workspace (/app) [Mobile-First PWA]
│   ├── /app/today (Today's Scheduled Workout Dashboard)
│   ├── /app/workouts/:session_id (Active Workout Execution & Set Logging)
│   ├── /app/workouts/:session_id/summary (Post-Workout Summary & Feedback)
│   ├── /app/calendar (Workout Schedule & Historical Training Calendar)
│   ├── /app/exercises/:id (Exercise Detail, Instructions & Video Demos)
│   ├── /app/progress (Body Metrics, Volume Charts & Progress Photos)
│   ├── /app/messages (1:1 Contextual Coach Chat Thread)
│   ├── /app/notifications (In-App Activity Notifications)
│   └── /app/profile (Account, Locale Switcher, Units, Privacy & Data Export)
│
├── Coach Workspace (/coach) [Desktop / Tablet / Mobile]
│   ├── /coach/dashboard (Overview, Active Roster, Unread Logs, Pain Alerts)
│   ├── /coach/athletes (Assigned Athlete Roster)
│   │   ├── /coach/athletes/:id (Athlete Profile, Training History & Metrics)
│   │   ├── /coach/athletes/:id/assign (Program Assignment Workflow)
│   │   └── /coach/athletes/:id/logs/:session_id (Workout Log Review & Set Feedback)
│   ├── /coach/programs (Program Management)
│   │   ├── /coach/programs/new (Hierarchical Program Builder)
│   │   ├── /coach/programs/:id/builder (Program Editor: Phases, Weeks, Days, Items)
│   │   └── /coach/programs/templates (Reusable Gym Templates Library)
│   ├── /coach/exercises (Exercise Library)
│   │   ├── /coach/exercises/:id (Exercise Detail & Media Viewer)
│   │   └── /coach/exercises/new (Custom Private Gym Exercise Creator)
│   ├── /coach/messages (Multi-Athlete Messaging Inbox)
│   ├── /coach/notifications (Real-Time Workout & Feedback Alerts)
│   └── /coach/settings (Coach Profile, Locale, Notification Preferences)
│
├── Organization Owner Workspace (/org) [Desktop & Responsive Mobile]
│   ├── /org/dashboard (Gym Overview, Coach Performance, Athlete Adherence)
│   ├── /org/members (Member Management)
│   │   ├── /org/members/coaches (Coach Roster & Assignment Controls)
│   │   ├── /org/members/athletes (All Gym Athletes Directory)
│   │   └── /org/members/invitations (Pending & Expired Invitation Tokens)
│   ├── /org/facility (Primary Location Profile & Gym Details)
│   ├── /org/templates (Gym-Wide Master Program Template Library)
│   ├── /org/analytics (Aggregated Adherence & Workout Telemetry)
│   ├── /org/audit (Organization Security & Membership Audit Log)
│   └── /org/settings (Tenant Branding, Timezone, Default Units, Billing [P1])
│
└── Platform Administrator Workspace (/admin) [Desktop Console]
    ├── /admin/dashboard (Platform Telemetry, Health & Moderation Queues)
    ├── /admin/exercises (Global Exercise Catalog Management)
    │   ├── /admin/exercises/moderation (Pending Exercise & Media Rights Queue)
    │   └── /admin/exercises/:id/review (Exercise Curation, Aliases & Licensing)
    ├── /admin/organizations (Tenant Management & Status Controls)
    ├── /admin/users (Global User Directory & Account Suspension)
    └── /admin/audit-logs (System-Wide Security & Compliance Audit Trail)
```

---

## 3. Role-Specific Navigation Specifications

### 3.1 Athlete Navigation Architecture

| Navigation Node | Route | Primary Device | Key Actions | Required Data | Privacy Level | P0 / P1 Status |
|---|---|---|---|---|---|---|
| **Today's Workout** | `/app/today` | Mobile PWA | View today's exercises; launch active workout session; view last week's weights | Active assigned workout snapshot; target sets/reps/load | Private to Athlete & Assigned Coach | **P0 (Core)** |
| **Active Session** | `/app/workouts/:id` | Mobile PWA | Log set actuals (load, reps, RPE); trigger rest timer; substitute exercise; report pain flag | Prescribed set list; historical logs; demo video signed URLs | Private to Athlete & Assigned Coach | **P0 (Core)** |
| **Workout Summary** | `/app/workouts/:id/summary` | Mobile PWA | Enter session RPE & fatigue rating; submit coach notes; view volume summary | Completed set actuals; calculated tonnage | Private to Athlete & Assigned Coach | **P0 (Core)** |
| **Training Calendar** | `/app/calendar` | Mobile PWA | Browse scheduled, completed, and skipped workouts across months (Jalali/Gregorian) | Program schedule; session completion states | Private to Athlete & Assigned Coach | **P0 (Core)** |
| **Exercise Library** | `/app/exercises/:id` | Mobile PWA | Watch looped demonstration videos; read coaching cues & safety warnings | Canonical & custom exercise translations; media assets | Public / Organization Private | **P0 (Core)** |
| **Progress & Body Metrics** | `/app/progress` | Mobile PWA | View 30/60/90-day volume trends; log body weight; upload consent-governed progress photos | Historical set logs; body metric timeseries; private photo signed URLs | **Strictly Sensitive** (Requires Explicit Consent) | **P0 (Core)** |
| **Coach Messages** | `/app/messages` | Mobile PWA | 1:1 contextual chat with assigned coach; reference workout sessions | Message thread history; linked session badges | Private (1:1 Coach-Athlete) | **P0 (Core)** |
| **Notifications** | `/app/notifications` | Mobile PWA | View assignment updates, coach feedback on sets, and system alerts | Notification feed; unread counters | Private to Athlete | **P0 (Core)** |
| **Profile & Settings** | `/app/profile` | Mobile PWA | Switch locale (`fa-IR`/`en-US`); toggle units (`kg`/`lbs`); trigger data export or erasure | User profile; locale preference; consent toggles | Private to Athlete | **P0 (Core)** |

---

### 3.2 Coach Navigation Architecture

| Navigation Node | Route | Primary Device | Key Actions | Required Data | Privacy Level | P0 / P1 Status |
|---|---|---|---|---|---|---|
| **Coach Dashboard** | `/coach/dashboard` | Desktop / Tablet | Review recent athlete workout logs; review high-priority pain flags; view weekly schedule | Roster summary; recent completions; unresolved feedback flags | Operational Coaching Data | **P0 (Core)** |
| **Athlete Roster** | `/coach/athletes` | Desktop / Tablet | Search/filter assigned athletes; view individual adherence %; initiate assignment | Assigned athlete profiles; 30-day compliance metrics | Operational Coaching Data | **P0 (Core)** |
| **Athlete Profile & Logs** | `/coach/athletes/:id` | Desktop / Tablet | Inspect full training history; review set-by-set actuals; add contextual set comments | Workout session logs; set actuals; pain flags; progress metrics | **Sensitive Health Data** (Assigned Coach Only) | **P0 (Core)** |
| **Program Builder** | `/coach/programs/new` | Desktop / Tablet | Build multi-week programs; configure phases, weeks, days, supersets, tempo, RPE | Exercise catalog; prescription models; template library | Organization Intellectual Property | **P0 (Core)** |
| **Program Templates** | `/coach/programs/templates` | Desktop / Tablet | Manage reusable gym templates; clone template to athlete with date offset | Template catalog; phase structure | Organization Intellectual Property | **P0 (Core)** |
| **Exercise Library** | `/coach/exercises` | Desktop / Tablet | Search bilingual exercise catalog (Persian variant folding); create private gym exercises | Canonical & private exercise translations; media metadata | Organization Intellectual Property | **P0 (Core)** |
| **Contextual Messaging** | `/coach/messages` | Desktop / Mobile | Chat with athletes; respond to workout set comments; send voice/text cues | 1:1 message threads; linked session previews | Private (1:1 Coach-Athlete) | **P0 (Core)** |
| **Coach Settings** | `/coach/settings` | Desktop / Tablet | Manage profile; set default locale; configure notification channels | User account; org membership; preferences | Private to Coach | **P0 (Core)** |

---

### 3.3 Organization Owner Navigation Architecture

| Navigation Node | Route | Primary Device | Key Actions | Required Data | Privacy Level | P0 / P1 Status |
|---|---|---|---|---|---|---|
| **Gym Dashboard** | `/org/dashboard` | Desktop / Tablet | Monitor total active athletes, active coaches, and overall gym adherence % | Aggregated tenant statistics; coach activity metrics | Aggregate Operational Data | **P0 (Core)** |
| **Member Management** | `/org/members` | Desktop / Tablet | Manage coach and athlete rosters; assign/reassign athletes to coaches; suspend departing staff | Member records; roles; assignment mappings | Organization Administrative Data | **P0 (Core)** |
| **Invitations Manager** | `/org/members/invitations` | Desktop / Tablet | Dispatch coach/athlete invitations by email; resend expired links; revoke tokens | Invitation records; token statuses | Organization Administrative Data | **P0 (Core)** |
| **Primary Location Profile** | `/org/facility` | Desktop / Tablet | Configure primary gym name, address, contact phone (Single-location MVP) | Location entity; facility address | Organization Operational Data | **P0 (Core)** |
| **Master Program Library** | `/org/templates` | Desktop / Tablet | View all gym-owned master templates; control organizational programming standards | Program templates; creator metadata | Organization Intellectual Property | **P0 (Core)** |
| **Gym Adherence Analytics** | `/org/analytics` | Desktop / Tablet | Review aggregated workout completion trends and retention rates across coaches | Anonymized aggregate workout volume & completion data | **Aggregate Only** (No raw private health notes) | **P0 (Core)** |
| **Organization Audit Log** | `/org/audit` | Desktop / Tablet | Inspect member role changes, invitations, and administrative actions | Tenant-scoped `AuditEvent` records | Audit & Compliance Data | **P0 (Core)** |
| **Organization Settings** | `/org/settings` | Desktop / Tablet | Configure gym branding, default timezone, units, and subscription billing (P1) | Organization settings JSON; owner credentials | Organization Administrative Data | **P0 (Core)** |

---

### 3.4 Platform Administrator Navigation Architecture

| Navigation Node | Route | Primary Device | Key Actions | Required Data | Privacy Level | P0 / P1 Status |
|---|---|---|---|---|---|---|
| **Admin Dashboard** | `/admin/dashboard` | Desktop Console | Monitor platform-wide tenant counts, user registrations, and moderation queue size | Platform telemetry; system health metrics | System Operational Data | **P0 (Core)** |
| **Exercise Moderation Queue** | `/admin/exercises/moderation` | Desktop Console | Review community/coach submitted exercises; inspect Persian/English cues & media rights | Pending `Exercise` & `MediaRights` records | Platform Catalog Data | **P0 (Core)** |
| **Catalog Curator** | `/admin/exercises/:id/review` | Desktop Console | Edit canonical translations, anatomical tags, and approve/reject demonstration videos | Exercise translations; video storage keys | Platform Catalog Data | **P0 (Core)** |
| **Organization Oversight** | `/admin/organizations` | Desktop Console | Search/inspect organizations; manage tenant status (active, suspended, archived) | Global organization registry | Platform Administrative Data | **P0 (Core)** |
| **User Management** | `/admin/users` | Desktop Console | Search users by email/ID; inspect memberships; suspend abusive accounts | Global user registry; active sessions | Platform Administrative Data | **P0 (Core)** |
| **System Audit Trail** | `/admin/audit-logs` | Desktop Console | Query immutable audit logs across actors, event types, and IP hashes | Global `AuditEvent` repository | **High Security / Audit Data** | **P0 (Core)** |

---

## 4. Deep-Linking, Context & Modal Hierarchy

### 4.1 Global Context Switchers
1. **Organization Switcher (Coaches & Owners):** Located in the top navigation bar. Allows multi-gym coaches to switch active tenant context. Switching context immediately scopes all queries, rosters, and template libraries to the selected `organization_id`.
2. **Language & Direction Switcher (Global):** Accessible on all authentication screens, athlete mobile headers, and coach utility bars. Toggling between `فارسی` and `English` instantly flips the document direction (`dir="rtl"` vs `dir="ltr"`), dynamically swaps typography (`Vazirmatn` vs `Inter`), and re-renders all externalized strings.

### 4.2 Modal vs Full-Screen Overlay Strategy
- **Full-Screen Overlays (Distraction-Free):**
  - Athlete Active Workout Session (`/app/workouts/:id`)
  - Coach Hierarchical Program Builder (`/coach/programs/:id/builder`)
- **Center Modals / Bottom Drawers (Contextual Micro-Workflows):**
  - Exercise Demonstration & Coaching Cues Viewer
  - Exercise Substitution Selector (with mandatory reason capture)
  - Pain / Discomfort Flag Submission Modal
  - Member Invitation & Role Assignment Dialog
  - Progress Photo Privacy Consent Confirmation Dialog
  - Data Export Request & Account Erasure Confirmation Dialog
