# Screen Inventory & Specifications — CoachOS

**Document version:** 1.0.0 (Phase 02 Baseline)  
**Last updated:** 2026-08-10  
**Supported Locales:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR)  
**Strict constraint:** Arabic is strictly out of scope.  
**Design Phase:** Phase 02 — Documentation and specifications only. No application source code.

---

## Screen Inventory Index

| Screen ID | Screen Title | Route | Primary Role | Device Priority | Related User Story |
|---|---|---|---|---|---|
| **SCR-AUTH-01** | User Registration | `/register` | Public / All | Mobile & Desktop | `US-AUTH-001` |
| **SCR-AUTH-02** | User Login | `/login` | Public / All | Mobile & Desktop | `US-AUTH-002` |
| **SCR-AUTH-03** | Password Reset Request | `/forgot-password` | Public / All | Mobile & Desktop | `US-AUTH-003` |
| **SCR-AUTH-04** | Password Reset Confirm | `/reset-password/:token` | Public / All | Mobile & Desktop | `US-AUTH-003` |
| **SCR-AUTH-05** | Invitation Accept & Onboarding | `/invite/:token` | Invited User | Mobile & Desktop | `US-ORG-003`, `US-ORG-004` |
| **SCR-ORG-01** | Organization Workspace Creator | `/org/new` | `P-OWNER` | Desktop & Tablet | `US-ORG-001` |
| **SCR-ORG-02** | Organization Management Dashboard | `/org/dashboard` | `P-OWNER` | Desktop & Tablet | `US-ORG-001` |
| **SCR-ORG-03** | Primary Location Setup | `/org/facility` | `P-OWNER` | Desktop & Tablet | `US-ORG-002` |
| **SCR-ORG-04** | Member Roster & Assignment Manager | `/org/members` | `P-OWNER` | Desktop & Tablet | `US-ORG-005` |
| **SCR-ORG-05** | Invitation Dispatcher Modal | `/org/members/invite` | `P-OWNER`, `P-COACH` | Desktop & Mobile | `US-ORG-003`, `US-ORG-004` |
| **SCR-ORG-06** | Organization Audit Trail Viewer | `/org/audit` | `P-OWNER` | Desktop Console | `US-AUD-001` |
| **SCR-COACH-01** | Coach Home Dashboard | `/coach/dashboard` | `P-COACH` | Desktop & Mobile | `US-PRG-003`, `US-ATH-004` |
| **SCR-COACH-02** | Assigned Athlete Roster | `/coach/athletes` | `P-COACH` | Desktop & Tablet | `US-ORG-004` |
| **SCR-COACH-03** | Athlete Training Profile & History | `/coach/athletes/:id` | `P-COACH` | Desktop & Tablet | `US-ATH-006` |
| **SCR-COACH-04** | Workout Log Review & Feedback Form | `/coach/athletes/:id/logs/:sid` | `P-COACH` | Desktop & Tablet | `US-MSG-001`, `US-ATH-004` |
| **SCR-COACH-05** | Program Library & Template List | `/coach/programs` | `P-COACH` | Desktop & Tablet | `US-PRG-002` |
| **SCR-COACH-06** | Hierarchical Program Builder | `/coach/programs/:id/builder` | `P-COACH` | Desktop (Primary) | `US-PRG-001` |
| **SCR-COACH-07** | Program Assignment Modal | `/coach/programs/:id/assign` | `P-COACH` | Desktop & Tablet | `US-PRG-003` |
| **SCR-COACH-08** | Exercise Catalog Explorer | `/coach/exercises` | `P-COACH` | Desktop & Tablet | `US-EX-001`, `US-I18N-002` |
| **SCR-COACH-09** | Exercise Detail & Demo Video Viewer | `/coach/exercises/:id` | `P-COACH`, `P-ATH` | Desktop & Mobile | `US-EX-001` |
| **SCR-COACH-10** | Custom Private Exercise Creator | `/coach/exercises/new` | `P-COACH` | Desktop & Tablet | `US-EX-002` |
| **SCR-ATH-01** | Athlete "Today's Workout" Dashboard | `/app/today` | `P-ATH` | Mobile PWA (Primary) | `US-ATH-001` |
| **SCR-ATH-02** | Active Workout Execution & Set Logger | `/app/workouts/:id` | `P-ATH` | Mobile PWA (Primary) | `US-ATH-002` |
| **SCR-ATH-03** | Exercise Substitution Modal | `/app/workouts/:id/substitute` | `P-ATH` | Mobile PWA (Primary) | `US-ATH-003` |
| **SCR-ATH-04** | Pain / Discomfort Flag Modal | `/app/workouts/:id/pain-flag` | `P-ATH` | Mobile PWA (Primary) | `US-ATH-004` |
| **SCR-ATH-05** | Workout Summary & Session Feedback | `/app/workouts/:id/summary` | `P-ATH` | Mobile PWA (Primary) | `US-ATH-004` |
| **SCR-ATH-06** | Athlete Training Calendar | `/app/calendar` | `P-ATH` | Mobile PWA (Primary) | `US-ATH-001` |
| **SCR-ATH-07** | Progress, Metrics & Photos | `/app/progress` | `P-ATH` | Mobile PWA (Primary) | `US-ATH-005`, `US-ATH-006` |
| **SCR-ATH-08** | Contextual 1:1 Messaging Inbox | `/app/messages` | `P-ATH`, `P-COACH` | Mobile & Desktop | `US-MSG-001` |
| **SCR-ATH-09** | Profile, Locale & Privacy Settings | `/app/profile` | `P-ATH`, `P-COACH` | Mobile & Desktop | `US-I18N-001`, `US-PRI-001` |
| **SCR-ADMIN-01** | Platform Admin Telemetry Console | `/admin/dashboard` | `P-ADMIN` | Desktop Console | `US-ADM-001` |
| **SCR-ADMIN-02** | Exercise Moderation & Rights Queue | `/admin/exercises/moderation` | `P-ADMIN` | Desktop Console | `US-EX-003`, `US-ADM-001` |
| **SCR-ADMIN-03** | Global Organization & User Directory | `/admin/organizations` | `P-ADMIN` | Desktop Console | `US-ADM-001` |
| **SCR-ADMIN-04** | Global Security Audit Log Viewer | `/admin/audit-logs` | `P-ADMIN` | Desktop Console | `US-AUD-001` |

---

## Detailed Specifications for Core P0 Screens

### 1. Screen: Athlete "Today's Workout" Dashboard (`SCR-ATH-01`)
- **Route:** `/app/today`
- **Primary Role:** `P-ATH` (Athlete / Client)
- **Device Priority:** Mobile PWA (Viewport 360px–428px)
- **Purpose:** Surfaces the athlete's scheduled workout for today with immediate actionability and historical targets.
- **Entry Points:** PWA app launch; bottom nav tab "Today"; push notification "Time to train".
- **Exit Points:** Launch Active Session (`/app/workouts/:id`); tap exercise detail modal; navigate bottom bar.
- **Main Actions:**
  1. *Primary Button:* "Start Workout" (large sticky CTA).
  2. *Secondary Action:* "Preview Workout Plan" / "Skip Workout with Reason".
  3. *Quick Actions:* View exercise video cues; inspect last week's logged weight per exercise.
- **Data Displayed:** Scheduled workout title; phase/week/day indicators; ordered list of exercise cards with target sets/reps/load; previous week's logged performance; coach's session notes.
- **Data Mutated:** Transitions session status from `Scheduled` to `In Progress` upon tapping "Start Workout".
- **Permission Requirements:** Authenticated athlete assigned to the scheduled program.
- **Localization:** Persian RTL layout flips card orientation, displays numbers in Persian digits, formats weights in `کیلوگرم` (or `پوند`), uses `Vazirmatn` font.
- **Privacy Sensitivity:** Coaching operational data (private to athlete and assigned coach).
- **Loading State:** Skeleton card loaders reflecting 4 exercise placeholders.
- **Empty State (Rest Day):** Illustrative rest day card: *"Rest & Recovery Day — Next session scheduled for tomorrow"*.
- **Error State:** Localized error banner with "Retry Loading" button.
- **Offline / Network Loss (Phase 04/07):** Displays cached workout shell if previously loaded; presents offline indicator banner; prevents navigation disruption.
- **Accessibility:** Semantic `<h1>Today's Workout</h1>`; `aria-labelledby` linking exercise cards; 48x48px touch targets.
- **Related User Stories:** `US-ATH-001`, `US-I18N-001`, `US-PWA-001`.

---

### 2. Screen: Active Workout Execution & Set Logger (`SCR-ATH-02`)
- **Route:** `/app/workouts/:id`
- **Primary Role:** `P-ATH` (Athlete / Client)
- **Device Priority:** Mobile PWA (One-handed gym interaction)
- **Purpose:** Fast, distraction-free logging of completed reps, weights, and RPE during live gym training.
- **Entry Points:** "Start Workout" on `SCR-ATH-01` or active session banner.
- **Exit Points:** "Finish Workout" -> `SCR-ATH-05`; "Save & Pause" modal -> `/app/today`.
- **Main Actions:**
  1. Input actual load (`kg`/`lbs`) and completed reps via oversized numeric keypad / stepper controls.
  2. Tap Set Complete Checkmark (triggers vibration/haptic feedback and rest countdown timer).
  3. Tap "Substitute Exercise" (`SCR-ATH-03`) or "Flag Discomfort" (`SCR-ATH-04`).
  4. Advance rest timer (+30s / Skip).
  5. Tap "Finish Workout" CTA.
- **Data Displayed:** Sticky header (Workout title, active session timer, finish button); active exercise card with video thumbnail, target prescription, and historical best; set rows with input fields (Weight, Reps, RPE); floating rest timer countdown.
- **Data Mutated:** Creates `SetLog` records; updates `WorkoutSession` status.
- **Permission Requirements:** Athlete owning the workout session.
- **Localization:** Persian RTL numbers, right-aligned input labels, mirrored timer progress ring.
- **Privacy Sensitivity:** Private personal fitness telemetry.
- **Loading State:** Immediate rendering from active memory/cache.
- **Error State:** Inline validation for negative numbers or missing load fields.
- **Offline / Network Loss (Phase 07):** Preserves entered form values in local component memory; displays non-intrusive offline toast; allows continuous workout execution.
- **Accessibility:** High-contrast set completion indicators (green background + checkmark icon); accessible timer announcements for screen readers via `aria-live="polite"`.
- **Related User Stories:** `US-ATH-002`, `US-ATH-003`, `US-ATH-004`.

---

### 3. Screen: Hierarchical Program Builder (`SCR-COACH-06`)
- **Route:** `/coach/programs/:id/builder`
- **Primary Role:** `P-COACH` (Coach / Personal Trainer)
- **Device Priority:** Desktop (1280px+) and Tablet Landscape (1024px)
- **Purpose:** High-density, rapid drafting of multi-week periodized training regimens.
- **Entry Points:** Program list -> "New Program" or "Edit Template".
- **Exit Points:** "Save Template" -> `SCR-COACH-05`; "Assign to Athlete" -> `SCR-COACH-07`.
- **Main Actions:**
  1. Add/reorder Program Phases, Weeks, and Days.
  2. Search and insert exercises from canonical and private catalogs.
  3. Configure prescriptions: Sets, Target Reps, Load, Tempo (`3-1-1-0`), Target RPE/RIR, Rest seconds, and Coach Cues.
  4. Group exercises into Supersets/Circuits (A1/A2).
  5. Duplicate days/weeks across mesocycles with 1-click volume scaling.
- **Data Displayed:** Dual-pane layout: Left pane tree (Phase -> Week -> Day -> Exercise list); Right pane detail form (prescriptions, set parameters, notes).
- **Data Mutated:** Creates/updates `Program`, `ProgramPhase`, `ProgramWeek`, `ProgramDay`, `Workout`, `WorkoutItem`, `SetPrescription`.
- **Permission Requirements:** Coach or Owner membership in owning organization.
- **Localization:** Full bidirectional support (tree on right in Persian RTL, left in English LTR); bilingual exercise name previews.
- **Privacy Sensitivity:** Organization proprietary intellectual property.
- **Loading State:** Shimmer tree nodes and skeleton form inputs.
- **Error State:** Real-time form validation highlighting empty workout days or unselected exercises.
- **Accessibility:** Full keyboard tree navigation (Arrow keys, Enter to select, Space to expand); ARIA tree grid semantics.
- **Related User Stories:** `US-PRG-001`, `US-PRG-002`, `US-I18N-001`.

---

### 4. Screen: Member Roster & Assignment Manager (`SCR-ORG-04`)
- **Route:** `/org/members`
- **Primary Role:** `P-OWNER` (Gym / Organization Owner)
- **Device Priority:** Desktop & Tablet
- **Purpose:** Centralized administration of gym coaches, athletes, and coach-athlete bindings.
- **Entry Points:** Owner sidebar navigation -> "Members".
- **Exit Points:** Open member profile; open invitation dialog (`SCR-ORG-05`).
- **Main Actions:**
  1. Filter member table by role (`Coach`, `Athlete`), status (`Active`, `Invited`, `Suspended`), and assigned coach.
  2. Assign or reassign athletes to specific coaches via dropdown modal.
  3. Suspend departing staff members (immediately revoking tenant access).
  4. Resend or revoke pending invitation tokens.
- **Data Displayed:** Member name, email, role badge, assigned coach/athletes count, date joined, active status toggle.
- **Data Mutated:** `Membership` status, `CoachAthleteAssignment` bindings, `AuditEvent`.
- **Permission Requirements:** Verified `Owner` membership role on active organization.
- **Localization:** Persian RTL table layout with right-aligned text and mirrored action menus.
- **Privacy Sensitivity:** Administrative organization personnel data.
- **Loading State:** Table skeleton rows (5 rows shimmer).
- **Empty State:** Illustrated empty card: *"No coaches invited yet — invite your first personal trainer"*.
- **Accessibility:** `<caption>` on data tables; sortable column headers with `aria-sort`; accessible action dropdown menus.
- **Related User Stories:** `US-ORG-004`, `US-ORG-005`, `US-AUTHZ-001`.

---

### 5. Screen: Exercise Moderation & Media Rights Queue (`SCR-ADMIN-02`)
- **Route:** `/admin/exercises/moderation`
- **Primary Role:** `P-ADMIN` (Platform Administrator)
- **Device Priority:** Desktop Console
- **Purpose:** Quality control, copyright verification, and publication approval for global exercise catalog additions.
- **Entry Points:** Platform Admin sidebar -> "Moderation Queue".
- **Exit Points:** Exercise review detail (`SCR-ADMIN-03`); Admin Dashboard.
- **Main Actions:**
  1. Inspect submitted Persian and English names, cues, and anatomical muscle tags.
  2. Play demonstration video and verify copyright licensing metadata (Original / CC-BY / Permitted).
  3. "Approve & Publish to Global Catalog" (transitions status to `Published`).
  4. "Reject with Feedback" (captures structured rejection reason and alerts submitting coach).
- **Data Displayed:** Queue list of pending exercises; submitting coach and gym name; submission timestamp; video preview player; media license fields.
- **Data Mutated:** `Exercise` status, `MediaRights` review timestamp and reviewer ID, `AuditEvent`.
- **Permission Requirements:** `is_platform_admin = true` with active MFA session.
- **Localization:** Bilingual curation UI allowing side-by-side editing of `fa-IR` and `en-US` translation strings.
- **Privacy Sensitivity:** Platform catalog administration.
- **Accessibility:** Keyboard shortcuts (Shift+A to approve, Shift+R to reject); video player with accessible controls.
- **Related User Stories:** `US-EX-003`, `US-ADM-001`, `US-AUD-001`.
