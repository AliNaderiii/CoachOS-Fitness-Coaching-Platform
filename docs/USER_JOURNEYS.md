# User Journeys — CoachOS

**Document version:** 1.0.0 (Phase 01 Baseline)  
**Last updated:** 2026-08-10  
**Languages covered:** Persian (`fa-IR`, RTL), English (`en-US`, LTR)  
**Constraint enforcement:** Arabic is strictly out of scope.

This document details the end-to-end user journeys for the CoachOS platform. Every journey specifies actors, preconditions, step-by-step main flows, alternate and error flows, server-side permission checks, data access/mutations, notification triggers, localization rules, privacy boundaries, and testable success criteria.

---

## 1. Journey: Organization Owner Onboarding & Management (UJ-OWNER-01)

### 1.1 Actor & Scope
- **Primary Actor:** `P-OWNER` (Gym / Organization Owner)
- **Phase Alignment:** P0 Core MVP
- **Device Context:** Desktop / Laptop (primary) or Mobile Responsive Web

### 1.2 Preconditions
- The user has access to a valid email account.
- The CoachOS platform web application is accessible online.

### 1.3 Main Flow (Step-by-Step)
1. **Registration:** Owner navigates to `/register`, enters display name, email, and password.
2. **Locale Selection:** Owner selects preferred locale (`fa-IR` Persian RTL or `en-US` English LTR). The UI instantly flips direction and re-renders all text in the chosen language.
3. **Organization Creation:** Owner enters organization business name (e.g., "Sepahan Performance Club" or "Iron & Oak Gym") and custom URL slug.
4. **Organization Configuration:** Owner configures default time zone, measurement units (`kg`/`lbs`), and contact info.
5. **Primary Location Definition (MVP Single-Location):** Owner optionally enters the primary gym facility address, city, and phone number (stored as the organization's single primary location).
6. **Coach Invitation:** Owner clicks "Invite Coach", enters the coach's email address and assigns role `Coach`.
7. **Roster Review:** Owner views the organization member table showing pending invitations and active members.
8. **Activity & Analytics Inspection:** Owner navigates to the organization overview dashboard to inspect total active athletes, assigned programs, and weekly workout completion rates.
9. **Membership Management:** Owner manages coach status (active, suspended) and reassigns athletes as necessary.

### 1.4 Alternate Flows
- **Existing User Creates New Org:** If the user already has a CoachOS account, they log in and navigate to `/organizations/new` rather than registering a new user record.
- **Location Setup Skipped:** The owner skips defining a physical facility address during onboarding (common for 100% online coaching organizations); the organization functions with a default virtual primary location.

### 1.5 Error States & Handling
- **Duplicate Email:** System displays localized error: "An account with this email already exists" with a "Log in instead" button.
- **Invalid Org Slug / Slug Collision:** Real-time validation flags slug conflicts before submission with suggestion alternatives.
- **Invitation Delivery Failure:** If email fails to deliver, the invitation row displays a "Resend Link" and "Copy Invitation Link" action button.

### 1.6 Server-Side Permission Checks
- `POST /api/v1/organizations`: Requires authenticated user. Automatically binds creating user as `Owner` membership role.
- `POST /api/v1/organizations/{org_id}/invitations`: Verifies authenticated user holds `Owner` role on `{org_id}`.
- `GET /api/v1/organizations/{org_id}/analytics`: Verifies caller holds `Owner` role. Other roles (Coach, Athlete) are rejected with `403 Forbidden`.

### 1.7 Data Created & Read
- **Created:** `User` (if new), `Organization`, `Location` (optional), `Membership` (role: `owner`), `Invitation` (role: `coach`, status: `pending`, token hash, TTL: 7 days), `AuditEvent`.
- **Read:** Organization member list, aggregated organization adherence statistics.

### 1.8 Notifications
- System dispatches a localized email notification to the invited coach containing a secure, single-use acceptance token.
- In-app notification to Owner when the coach accepts the invitation.

### 1.9 Localization & Privacy Considerations
- **Localization:** Persian RTL layout applies full mirroring for form labels, directional icons, and numeric inputs (`Vazirmatn` font).
- **Privacy:** Multi-tenant database queries filter strictly on `organization_id`. The Owner cannot see other organizations' data.

### 1.10 Success Criteria
- Owner can complete account creation, org setup, and coach invitation in < 3 minutes.
- Audit event `organization.created` and `invitation.created` recorded with user ID and timestamp.

---

## 2. Journey: Coach Program Building, Assignment & Feedback (UJ-COACH-01)

### 2.1 Actor & Scope
- **Primary Actor:** `P-COACH` (Coach / Personal Trainer)
- **Phase Alignment:** P0 Core MVP
- **Device Context:** Desktop / Tablet (builder) + Mobile (review & messaging)

### 2.2 Preconditions
- The coach has received an invitation email from an Organization Owner.
- An Athlete account exists and has been assigned to this Coach within the Organization.

### 2.3 Main Flow (Step-by-Step)
1. **Accept Invitation:** Coach clicks the secure invitation link in their email, sets their password and profile name.
2. **Locale Selection:** Coach chooses `fa-IR` or `en-US` locale. UI renders in matching layout direction.
3. **Dashboard & Roster View:** Coach views their assigned athlete roster and pending notifications.
4. **Exercise Library Exploration:** Coach navigates to the Exercise Catalog, searches for exercises using Persian or English terms (e.g., "اسکوات" or "Squat"), and filters by muscle group (Quadriceps) and equipment (Barbell).
5. **Review Exercise Details:** Coach opens an exercise modal to review coaching cues, mistakes to avoid, and demonstration media.
6. **Create Training Program:** Coach clicks "New Program", specifies title (e.g., "Hypertrophy Block A - 8 Weeks"), target goal, and description.
7. **Build Structure:** Coach defines Program Phases (Phase 1: Accumulation), Weeks (Weeks 1–4), and Days (Day 1: Upper Body, Day 2: Lower Body).
8. **Prescribe Exercises & Sets:** Coach adds exercises into workout days, configuring sets, reps (e.g., 8–10), load prescription (e.g., "75% 1RM" or "80 kg"), tempo (`3-0-1-0`), RPE/RIR target (RPE 8 / RIR 2), rest interval (90s), and custom athlete notes.
9. **Save Template:** Coach saves the completed structure as an Organization Template for future reuse.
10. **Assign Program to Athlete:** Coach selects an assigned athlete, specifies the program start date (e.g., Next Monday), and clicks "Assign Program". The system creates an immutable program snapshot.
11. **Review Athlete Execution Logs:** On training days, the coach opens the athlete's log card to view logged actual weights, completed reps, RPE, and elapsed session duration.
12. **Contextual Messaging & Feedback:** Coach identifies a set where the athlete flagged shoulder pain, taps "Comment on Set", and sends a direct coaching recommendation.
13. **Review Adherence:** Coach inspects the athlete's 30-day adherence chart to evaluate readiness for the next training phase.

### 2.4 Alternate Flows
- **Custom Private Exercise Creation:** If a desired exercise does not exist in the canonical library, the coach creates a private exercise with custom Persian/English names, instructions, and video demo URL/upload, tagging rights/provenance.
- **Cloning Existing Template:** Coach selects an existing organization template, clicks "Duplicate & Edit", modifies set counts for a specific athlete, and assigns directly.

### 2.5 Error States & Handling
- **Unassigned Athlete Access Attempt:** If a coach attempts to view or assign a program to an athlete belonging to the same org but not assigned to this coach, the system returns `403 Forbidden` (unless organization policy explicitly enables open rosters).
- **Validation Failure on Empty Program:** Builder prevents assigning a program that contains zero workouts or invalid set prescriptions with clear field-level validation messages.

### 2.6 Server-Side Permission Checks
- `POST /api/v1/programs`: Verifies coach membership in active organization.
- `POST /api/v1/programs/{program_id}/assign`: Verifies `coach_athlete_assignment` relationship exists and is active.
- `GET /api/v1/athletes/{athlete_id}/logs`: Verifies coach is assigned to `{athlete_id}` within the organization.

### 2.7 Data Created & Read
- **Created:** `Exercise` (if custom), `Program`, `ProgramPhase`, `ProgramWeek`, `ProgramDay`, `Workout`, `WorkoutItem`, `SetPrescription`, `ProgramAssignment`, `ProgramSnapshot`, `Message`, `AuditEvent`.
- **Read:** Canonical exercise library, athlete profile, workout session logs, set actuals, feedback flags.

### 2.8 Notifications
- Email and in-app push notification dispatched to the Athlete: "Coach Sarah assigned you a new program: Hypertrophy Block A".
- In-app notification to Coach when the athlete completes a workout or submits a pain/fatigue flag.

### 2.9 Localization & Privacy Considerations
- **Localization:** Mixed-direction text (e.g., "حرکت Barbell Bench Press با ۳ ست") is correctly isolated with Unicode BiDi markers. Persian digits (`۰-۹`) and units (`کیلوگرم`) format according to active locale.
- **Privacy:** Proprietary program templates created by the coach are isolated to their organization. Coach cannot view athletes assigned to other coaches without explicit permissions.

### 2.10 Success Criteria
- Coach can build and assign a 4-week program in < 10 minutes using templates.
- Snapshot creation guarantees that subsequent edits to the master template do not alter the athlete's active program log.

---

## 3. Journey: Athlete Workout Execution & Progress Logging (UJ-ATH-01)

### 3.1 Actor & Scope
- **Primary Actor:** `P-ATH` (Athlete / Client)
- **Phase Alignment:** P0 Core MVP
- **Device Context:** Mobile PWA (iOS / Android smartphone inside gym)

### 3.2 Preconditions
- Athlete has received an invitation email from their Coach/Gym.
- Coach has assigned an active training program with scheduled workouts.

### 3.3 Main Flow (Step-by-Step)
1. **Accept Invitation & Onboard:** Athlete opens the invitation link on their smartphone, sets password, selects preferred language (`fa-IR` Persian RTL or `en-US` English LTR), and sets preferred units (`kg` or `lbs`).
2. **PWA Install Prompt:** System prompts athlete to "Add CoachOS to Home Screen". Athlete installs the PWA.
3. **Open Today's Workout:** On training day, athlete launches the PWA and lands directly on "Today's Workout" showing Day 1: Lower Body Strength.
4. **Inspect Exercise Cues & Media:** Athlete taps the first exercise (Barbell Back Squat), views previous week's logged weight (e.g., 100 kg x 5 reps), reads coach's coaching cue ("Drive knees outward on ascent"), and watches a 5-second looped technique clip.
5. **Start Workout:** Athlete taps "Start Workout". Session timer begins.
6. **Log Set Actuals:** Athlete completes Set 1, enters actual load (102.5 kg), actual reps (5), and subjective RPE (8), then taps the checkmark icon.
7. **Rest Timer:** The app initiates a 90-second countdown rest timer with visual and audio/vibration notification on completion.
8. **Subsequent Sets:** Athlete logs remaining prescribed sets in succession.
9. **Exercise Modification / Substitution:** For Exercise 3 (Leg Extension), the machine is broken. Athlete taps "Modify / Substitute", selects "Dumbbell Goblet Squat", and selects reason: "Equipment Unavailable".
10. **Record Feedback & Pain Flags:** On Set 4 of deadlifts, athlete feels minor lower-back strain. Athlete checks "Pain / Discomfort Flag", selects body area "Lower Back", intensity "Mild (3/10)", and types a quick note.
11. **Complete Workout:** Athlete completes all exercises, taps "Finish Workout", enters overall session RPE (7.5/10) and energy rating, and submits the session.
12. **Summary & Celebration:** Athlete receives a celebratory summary showing total volume lifted (kg), session duration, and personal record highlights.
13. **Review Progress & Message Coach:** Athlete views updated 30-day volume progression and taps "Message Coach" to ask a question regarding next session.

### 3.4 Alternate Flows
- **Workout Rest Day / Calendar Exploration:** Athlete opens the app on a non-training day, views "Rest & Recovery" status with next scheduled workout date, and browses the workout calendar to review past completed logs.
- **Skip Workout with Reason:** Athlete is ill or traveling, opens scheduled workout, taps "Skip Workout", and selects reason "Illness / Travel". System updates calendar status to `Skipped` and notifies coach.

### 3.5 Error States & Handling
- **Temporary Network Loss (Gym Dead Zone):** If cellular data drops during workout execution, the mobile PWA caches logged set actuals locally in client storage and displays an offline indicator ("Offline - changes saved locally"). Upon network restoration, the queue automatically syncs to the server with zero data loss.
- **Invalid Number Inputs:** Negative numbers or unrealistic values (e.g., 9999 kg) trigger immediate inline validation warnings.

### 3.6 Server-Side Permission Checks
- `GET /api/v1/athletes/me/today`: Authenticates athlete user; resolves active program assignment.
- `POST /api/v1/workout-sessions/{session_id}/sets`: Verifies `session_id` belongs to the authenticated athlete. Rejects requests from unauthorized actors.
- `POST /api/v1/workout-sessions/{session_id}/complete`: Validates ownership and transitions status to `Completed`.

### 3.7 Data Created & Read
- **Created:** `WorkoutSession` (started_at, completed_at, status), `SetLog` (actual_reps, actual_load, actual_rpe, notes, completed), `FeedbackFlag` (pain_area, severity, notes), `Message` (if sent), `AuditEvent`.
- **Read:** Scheduled workout items, prescribed sets/reps/load, historical logs for same exercise, video media URLs.

### 3.8 Notifications
- In-app confirmation on successful session submission.
- Instant alert to Coach when athlete logs a pain flag or completes a workout.

### 3.9 Localization & Privacy Considerations
- **Localization:** Persian RTL numbers and units formatted correctly. Big numerical keypad inputs optimized for quick gym interaction.
- **Privacy:** Athlete's workout logs and pain flags are strictly accessible only to their assigned Coach and Organization Owner. Never exposed publicly.

### 3.10 Success Criteria
- Athlete can record a set in < 3 taps (< 5 seconds).
- Zero data loss during intermittent network drops on the gym floor.
- Workout log persists and immediately updates coach dashboard.

---

## 4. Journey: Platform Administrator Content Curation & Safety (UJ-ADMIN-01)

### 4.1 Actor & Scope
- **Primary Actor:** `P-ADMIN` (Platform Administrator)
- **Phase Alignment:** P0 Core MVP
- **Device Context:** Desktop / Laptop (Admin Console)

### 4.2 Preconditions
- Admin user has an active account with `is_platform_admin = true` and multi-factor authentication (MFA) enabled.

### 4.3 Main Flow (Step-by-Step)
1. **Admin Login:** Admin authenticates via `/admin/login` with MFA.
2. **Dashboard Overview:** Admin views platform health metrics: active organizations, total registered coaches/athletes, pending exercise moderation items, and system error rates.
3. **Exercise Moderation Queue:** Admin navigates to `/admin/exercises/moderation` to review community-submitted or coach-submitted exercise candidates for the global catalog.
4. **Inspect Metadata & Provenance:** Admin inspects exercise title in Persian and English, anatomical muscle tags, movement pattern categorization, coaching cues, and media rights metadata (License: CC-BY / Original / Permitted, Source URL, Creator Attribution).
5. **Approve / Reject Media:** Admin verifies that instructional video contains no copyright-infringing watermarks or inappropriate content. Admin clicks "Approve & Publish to Global Catalog".
6. **User & Organization Oversight:** Admin searches for a reported organization or user account by ID or email to investigate an abuse or support report.
7. **Inspect Audit Log:** Admin filters audit events by actor ID or action type (`auth.failed_login_spike`, `data.export_requested`) to verify compliance and investigate anomalies.
8. **Archive / Restore Content:** Admin archives deprecated or problematic exercise records without breaking historical athlete workout logs.

### 4.4 Alternate Flows
- **Reject Exercise Submission:** Admin clicks "Reject", selects reason ("Inadequate video quality / Missing Persian cues / Unverified copyright license"), and inputs feedback. System updates status to `Rejected` and notifies submitting coach.

### 4.5 Error States & Handling
- **Unauthorized Break-Glass Attempt:** If a non-admin user attempts to access `/admin/*` or `/api/v1/admin/*`, the server returns `403 Forbidden` and logs a high-severity security audit event.

### 4.6 Server-Side Permission Checks
- `GET/POST /api/v1/admin/*`: Enforces `user.is_platform_admin == true`.
- All admin mutations log an immutable `AuditEvent` with `actor_id`, target entity, IP hash, and timestamp.

### 4.7 Data Created & Read
- **Created / Mutated:** `Exercise` (status: `published` / `archived`), `MediaRights` (reviewed_by, reviewed_at), `ModerationAction`, `AuditEvent`.
- **Read:** Platform-wide telemetry, user registries, exercise moderation queues, audit logs.

### 4.8 Notifications
- Email and in-app notification to coach when their submitted exercise is approved or rejected by admin.

### 4.9 Localization & Privacy Considerations
- **Localization:** Admin portal is fully bilingual (Persian & English).
- **Privacy:** Admin views operational metadata and audit logs, but cannot browse private athlete progress photos or personal chat logs unless part of a formally logged, audited support escalation.

### 4.10 Success Criteria
- Global exercise catalog contains zero unmoderated or copyright-unverified media.
- 100% of administrative mutations produce queryable audit log entries.

---

## 5. Journey: Future Nutrition Professional Consent-Based Collaboration (UJ-NUT-01) — [P1 Backlog]

### 5.1 Actor & Scope
- **Primary Actor:** `P-NUT` (Nutrition Professional / Dietitian) + `P-ATH` (Athlete) + `P-COACH` (Coach)
- **Phase Alignment:** P1 Backlog (Detailed Specification for Future Architecture Readiness)
- **Device Context:** Desktop / Laptop (Nutritionist) + Mobile PWA (Athlete)

### 5.2 Preconditions
- Organization has enabled Nutrition Services (P1 tier).
- Nutritionist is invited and onboarded to the Organization.
- Athlete has an active membership and strength program with their primary Coach.

### 5.3 Main Flow (Step-by-Step)
1. **Assignment & Consent Request:** Organization Owner assigns Nutritionist Dr. Mina to Athlete Neda. The platform generates an explicit Consent Request.
2. **Athlete Grants Consent:** Athlete Neda receives an in-app notification: "Dr. Mina has been assigned as your Nutritionist. Do you grant permission to view your body metrics, training schedule, and share dietary logs?". Athlete taps "Review & Grant Consent".
3. **Nutritionist Onboarding & Intake:** Dr. Mina opens Neda's profile, views permitted health metrics (Height, Weight, Body Fat %, Training Days: Mon/Wed/Fri), and sends a localized nutrition intake questionnaire.
4. **Establish Calorie & Macro Targets:** Dr. Mina establishes training day targets (e.g., 2,200 kcal / 140g Protein / 250g Carbs / 70g Fat) vs rest day targets (e.g., 1,800 kcal / 140g Protein / 160g Carbs / 65g Fat).
5. **Build Persian & International Meal Plan:** Dr. Mina builds a 7-day meal plan selecting authentic Iranian foods (e.g., Grilled Chicken Breast with Kateh Rice and Mast-o-Khiar) with accurate macro calculations from the bilingual food database.
6. **Assign Meal Plan:** Dr. Mina assigns the meal plan to Neda's calendar.
7. **Athlete Food Logging:** Athlete opens the PWA "Nutrition" tab, reviews prescribed meals, and logs consumed food items and water intake.
8. **Multi-Professional Collaboration:** Coach Sarah opens Neda's training card, views the macro compliance badge ("100% protein target met on heavy squat day"), and leaves an internal collaborative note for Dr. Mina: "Increased Neda's squat volume this week; energy levels reported high."
9. **Progress Review & Plan Adjustment:** Dr. Mina reviews 14-day weight trend and food logs, adjusting carbohydrate timing around morning workouts.
10. **Assignment Termination & Access Revocation:** When the nutrition package ends, the Owner or Athlete ends the assignment. Dr. Mina's access to Neda's live logs is immediately revoked, and historical records are archived according to data retention policies.

### 5.4 Alternate Flows
- **Athlete Denies Consent:** If Athlete denies or revokes consent, Nutritionist cannot view athlete body metrics or logs. System notifies Organization Owner.
- **Granular Consent Selection:** Athlete permits access to training schedule and food logs, but withholds permission for private progress photos.

### 5.5 Error States & Handling
- **Attempted Access Post-Revocation:** If Nutritionist attempts to query `/api/v1/nutrition/athletes/{id}/*` after assignment revocation, server returns `403 Forbidden` with error code `consent_revoked`.

### 5.6 Server-Side Permission Checks
- Every nutrition endpoint verifies: (1) active organization membership, (2) active nutritionist-athlete assignment, and (3) valid unexpired athlete consent record.

### 5.7 Data Created & Read (P1)
- **Created:** `NutritionistAssignment`, `ConsentRecord`, `MealPlan`, `MealItem`, `FoodLog`, `DietaryComment`, `AuditEvent`.
- **Read:** Permitted body metrics, workout schedule, food database items.

### 5.8 Localization & Privacy Considerations
- **Localization:** Bilingual Iranian and international food catalog with Persian search normalization.
- **Privacy:** Strict purpose-bound data isolation. Athlete retains unilateral right to revoke nutritionist access at any time.

### 5.9 Success Criteria (P1 Validation)
- Multi-professional access respects granular consent without data leaks between unassigned staff.
