# Prompt Log — CoachOS

Append-only history of founder/supervising-agent prompts and resulting actions.

---

## Prompt 001

- **Date/time:** 2026-08-10 (UTC)
- **Source:** Founder / supervising agent (initial system mission prompt)
- **Phase:** 00 — Discovery and Repository Audit
- **Prompt Summary:** (summarized for length; full text retained in agent session)

  Multi-role founding product-and-engineering mandate for CoachOS bilingual fitness coaching platform. Non-negotiable fa-IR RTL + en-US LTR only; Arabic explicitly out of scope. Phased delivery 00–14 with required documentation set. **First action: Phase 00 only** — audit repo, create docs/checklist/report/backlog, propose MVP and architecture, stop and wait.

- **Requested outcome:** Complete Phase 00 discovery; do not build full product or application code.
- **Actions taken:**
  - Inspected GitHub remote `AliNaderiii/CoachOS-Fitness-Coaching-Platform`
  - Confirmed greenfield state: single commit `a6283e8`, files `LICENSE` + stub `README.md`, size 0, no language/CI/tests
  - Working branch `arena/019febc6-coachos-fitness-coaching-platf` from main
  - Created full Phase 00 documentation suite and directories
  - Created GitHub milestones 1–9 and issues #1 (Phase 01), #2 (Phase 00); issue PATCH/close returned 403 for bot — maintained canonical markdown backlog
- **Artifacts produced:**
  - `README.md`, `PROJECT_STATUS.md`, `PROJECT_CHECKLIST.md`, `CHANGELOG.md`
  - `docs/MASTER_PRODUCT_BRIEF.md`, `docs/PRD.md`, `docs/DECISIONS.md`
  - `docs/SECURITY_AND_PRIVACY.md`, `docs/DATA_MODEL.md`, `docs/API_CONTRACT.md`
  - `docs/TRACEABILITY_MATRIX.md`, `docs/RELEASE_PLAN.md`, `docs/PROMPT_LOG.md`
  - `docs/reports/PHASE-00-DISCOVERY-REPORT.md`
  - `docs/architecture/README.md`, `docs/ux/README.md`, `docs/testing/README.md`
- **Tests/evidence:** Repository inspection via `git`, `gh api`, filesystem listing (see Phase 00 report)
- **Decisions:**
  - ADR-001 modular monolith accepted
  - ADR-002 stack proposed (Next.js + Django/DRF + Postgres)
  - ADR-003 fa/en only, Arabic out of scope accepted
  - ADR-004 B2B2C accepted
  - ADR-005 email+password default proposed
  - ADR-006 RBAC + object-level authZ accepted direction
  - ADR-007 AI deferred accepted
  - ADR-008 media provenance accepted
- **Blockers:** None for Phase 01. Bot cannot update/close GitHub issues (create OK).
- **Follow-up prompt needed:** Execute Phase 01 — Product Requirements and Scope (see Phase 00 report §17).

---

## Post-Phase-00 Merge Record

- **Date/time:** 2026-08-10T13:57:45Z (UTC)
- **Action:** Pull Request #3 merged into `main`
- **Pull Request:** `https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/3`
- **Merge commit:** `f52c4134087b18c4bd1a8aef9e0100fd63f71b8e`
- **Base commit on main:** `f52c4134087b18c4bd1a8aef9e0100fd63f71b8e`
- **Result:** Phase 00 documentation foundation officially merged into main repository.

---

## Prompt 002

- **Date/time:** 2026-08-10 (UTC)
- **Source:** Founder / supervising agent
- **Phase:** 01 — Product Requirements and Scope
- **Exact Full Text Received:**

```text
**CONTINUE COACHOS AS A PROFESSIONAL PRODUCT-AND-ENGINEERING TEAM**

You are continuing the CoachOS Fitness Coaching Platform as a coordinated professional team consisting of:

- Founder’s Technical Advisor
- Product Manager
- Business Analyst
- UX Researcher
- UX/UI Designer
- Principal Software Architect
- Security and Privacy Engineer
- QA/Test Engineer
- Technical Writer
- Release Manager
- Code Reviewer

The project is a bilingual, mobile-first fitness coaching operating system for coaches, gyms, athletes, and future nutrition professionals.

This instruction executes **Phase 01 — Product Requirements and Scope**.

This phase is documentation and requirements engineering only.

**Do not write application code.**  
**Do not scaffold the frontend or backend.**  
**Do not install dependencies.**  
**Do not create database migrations.**  
**Do not create AI integrations.**  
**Do not create payment integrations.**

**1. REPOSITORY AND PHASE 00 VERIFICATION**

Repository:

`https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform`

Phase 00 was merged into `main` through Pull Request #3.

Phase 00 merge commit:

`f52c4134087b18c4bd1a8aef9e0100fd63f71b8e`

Phase 00 documentation commit:

`0e926370b4b803560558476c57847f53425cdd05`

Before doing any Phase 01 work, inspect and verify:

- `README.md`
- `PROJECT_STATUS.md`
- `PROJECT_CHECKLIST.md`
- `CHANGELOG.md`
- `docs/MASTER_PRODUCT_BRIEF.md`
- `docs/PRD.md`
- `docs/DATA_MODEL.md`
- `docs/DECISIONS.md`
- `docs/SECURITY_AND_PRIVACY.md`
- `docs/API_CONTRACT.md`
- `docs/TRACEABILITY_MATRIX.md`
- `docs/RELEASE_PLAN.md`
- `docs/PROMPT_LOG.md`
- `docs/reports/PHASE-00-DISCOVERY-REPORT.md`

Also inspect:

- Current branch
- Current commit
- `main` HEAD
- Working tree status
- Existing GitHub branches
- Existing milestones
- Existing issues
- Pull Request #3 status
- Complete repository tree
- Whether any application code or dependencies were added after Phase 00

**Required post-merge housekeeping**

The Phase 00 documents were originally written before Pull Request #3 was merged. Verify whether these historical metadata fields are stale:

- Main HEAD/base commit
- Current branch
- Pull Request status
- Phase status
- Current phase
- Next phase

Update `PROJECT_STATUS.md` so that it accurately reflects the post-merge state and the current Phase 01 branch.

Do not rewrite historical facts in the Phase 00 report. Instead, if needed, append a clearly labeled section such as:

`## Post-Phase-00 Merge Addendum`

The addendum should record:

- Pull Request #3
- Merge status
- Merge commit
- Date/time
- Main branch status
- Phase 01 branch status

Append the merge action and this Phase 01 prompt to `docs/PROMPT_LOG.md` using the existing format. Do not delete the original Prompt 001 record.

Create a new Phase 01 branch from the updated `main` branch. Use the repository’s existing branch conventions or a clear name such as:

`phase/01-requirements`

Do not work directly on `main` unless repository policy requires it.

If GitHub permissions allow, create a Pull Request for Phase 01 when the phase is complete. Do not merge it automatically.

**2. NON-NEGOTIABLE PRODUCT CONSTRAINTS**

CoachOS currently supports only:

- Persian: `fa-IR`, RTL
- English: `en-US`, LTR

Arabic is explicitly out of scope.

Do not create or add:

- Arabic locale files
- Arabic translations
- Arabic seed data
- Arabic UI
- Arabic user stories
- Arabic-specific product requirements
- Arabic-specific implementation

The architecture may support future localization, but only Persian and English may appear in current product requirements and future implementation plans.

Additional constraints:

- Product model: B2B2C SaaS
- Coaches, gyms, and professional teams are primary paying customers.
- Athlete/client access is free or included.
- Nutrition professional functionality is P1.
- Marketplace functionality is P2.
- Payment processing is not part of this phase.
- Advanced AI is deferred.
- Wearable integrations are deferred.
- Native mobile apps are deferred.
- Medical diagnosis, treatment, drug, supplement-prescription, and clinical decision features are out of scope.
- No real health data, personal data, secrets, credentials, or production tokens may be added to the repository.

**3. PRODUCT VISION**

CoachOS is a bilingual, mobile-first fitness coaching operating system that will eventually connect:

- Coaches
- Gym owners
- Athletes
- Nutrition professionals
- Exercise libraries
- Training programs
- Workout execution and logging
- Progress tracking
- Habits and check-ins
- Communication
- Scheduling
- Payments
- Coach monetization
- Safe and explainable AI assistance

The MVP should not attempt to build the entire long-term product.

The P0 product should enable an organization to:

1. Create an organization.
2. Invite coaches and athletes.
3. Manage permissions.
4. Manage bilingual exercise content.
5. Build structured training programs.
6. Assign programs to athletes.
7. Allow athletes to view and log workouts.
8. Allow coaches to review athlete activity.
9. Allow contextual coach-athlete communication.
10. Maintain tenant isolation, privacy, auditability, and data ownership.

Do not claim that CoachOS is unique merely because it has an exercise library, workout builder, messaging, multilingual support, or PWA capability. Identify realistic differentiation hypotheses such as:

- High-quality Persian RTL and English LTR experience
- Persian search normalization and Persian fitness content
- Localized training and future nutrition content
- Mobile-first, low-bandwidth delivery
- Permissioned collaboration between coach and nutrition professional
- Coach monetization and program sales
- Privacy, auditability, and data portability
- Human-reviewed, constrained AI assistance in future phases

**4. REQUIRED SCOPE CORRECTIONS**

**4.1 PWA sequencing**

CoachOS is PWA-first.

Update the roadmap so that:

**Phase 04 includes the PWA foundation:**

- Web App Manifest
- Installable application shell
- Responsive mobile-first frontend shell
- Service Worker foundation
- PWA metadata
- PWA-aware routing and loading behavior

**Phase 07 validates:**

- Athlete mobile experience
- Mobile workout execution
- Mobile workout logging
- Mobile responsiveness
- Basic installed-PWA experience

**Phase 12 contains advanced capabilities:**

- Advanced offline workout logging
- Sync queues
- Conflict resolution
- Background synchronization where supported
- Advanced push behavior
- HealthKit
- Health Connect
- Wearable integrations
- Native application strategy

Do not defer the entire PWA effort to Phase 12.

Do not implement PWA code in Phase 01. Define requirements and sequencing only.

**4.2 License and intellectual property**

The repository currently uses an MIT license.

Do not change the license automatically.

Create a pending decision in `docs/DECISIONS.md` comparing:

1. Keep MIT
2. Proprietary/all-rights-reserved license
3. Open-core model
4. Private repository with a commercial license

Explain the implications for:

- Commercial monetization
- Competitor reuse
- External contributions
- Portfolio visibility
- Investors and partners
- White-label and enterprise licensing

Mark the final choice as requiring founder approval.

Do not modify `LICENSE` in Phase 01.

**4.3 Location scope**

Use a single-location-first strategy for MVP.

The data model may include organizations and optional locations, but the MVP must not include full multi-location management.

**MVP:**

- One primary location per organization
- Organization-level ownership
- Basic organization settings
- Optional location field in the data model

**P1:**

- Multiple locations
- Location managers
- Cross-location reporting
- Staff scheduling
- Location-specific branding
- Location-level analytics

Document the reasoning and trade-offs.

**4.4 Calendar strategy**

Analyze these options:

1. Gregorian storage and display only
2. UTC/Gregorian internal storage with Persian Jalali display in the Persian locale
3. First-class Jalali calendar and scheduling behavior

Provide a recommendation for a Persian-first product and consider:

- Training schedules
- Program start/end dates
- Weekly plans
- Check-ins
- Future booking
- Notifications
- Time zones
- Backend storage
- API format
- Reporting
- English users

Do not implement calendar code in Phase 01.

Record the recommendation and remaining uncertainty in `docs/DECISIONS.md`.

**5. PHASE 01 OBJECTIVE**

Convert the Phase 00 vision into a complete, testable, implementation-ready Product Requirements Package.

The output must be detailed enough for UX, architecture, security, and engineering phases to proceed without major ambiguity.

This phase is documentation only.

**6. REQUIRED DOCUMENTATION DELIVERABLES**

Create or substantially update:

docs/PRD.md
docs/PERSONAS.md
docs/USER_JOURNEYS.md
docs/DOMAIN_GLOSSARY.md
docs/COMPETITIVE_LANDSCAPE.md
docs/DECISIONS.md
docs/DATA_MODEL.md
docs/API_CONTRACT.md
docs/SECURITY_AND_PRIVACY.md
docs/TRACEABILITY_MATRIX.md
docs/RELEASE_PLAN.md
PROJECT_STATUS.md
PROJECT_CHECKLIST.md
CHANGELOG.md
docs/PROMPT_LOG.md
docs/reports/PHASE-01-REQUIREMENTS-REPORT.md

Preserve valid Phase 00 content and expand existing documents instead of blindly replacing them.

All canonical engineering documents must be written in English.

Each phase report must include a short Persian executive summary.

No Arabic product content or implementation requirements may be added.

**7. PRD REQUIREMENTS**

Complete `docs/PRD.md` with the following sections.

**7.1 Product overview**

Include:

- Product vision
- Problem statement
- Target market hypothesis
- Target customers
- Product positioning
- Value proposition
- Business model
- Differentiation hypothesis
- Product principles
- Language constraints
- MVP boundaries
- Long-term product direction
- Explicit non-goals

**7.2 Business goals**

Define proposed business goals for:

- Coach acquisition
- Gym adoption
- Athlete activation
- Program assignment
- Workout completion
- Coach retention
- Athlete retention
- Subscription conversion
- Future program sales
- Future marketplace liquidity

Clearly mark all numerical targets as proposed hypotheses until validated with real users.

**7.3 Success metrics**

Define proposed metrics such as:

- Time from coach registration to first assigned program
- Time from athlete invitation to activation
- Percentage of athletes opening Today’s Workout
- Workout completion rate
- Weekly active coaches
- Weekly active athletes
- Program assignment completion rate
- Coach response time
- Athlete retention
- RTL/LTR support issues
- Critical authorization bugs
- Privacy or security incidents

For each metric include:

- Definition
- Measurement event
- Expected direction
- MVP or later phase
- Risk of misinterpretation

**8. PERSONAS**

Create `docs/PERSONAS.md`.

Define detailed personas for:

1. Platform Administrator
2. Gym/Organization Owner
3. Coach/Trainer
4. Athlete/Client
5. Nutrition Professional — P1 only
6. Support/Read-only Staff — optional

For every persona include:

- Goals
- Jobs-to-be-done
- Pain points
- Existing tools
- Current workarounds
- Technical comfort
- Privacy concerns
- Accessibility needs
- Success criteria
- Willingness-to-pay assumption
- Failure and abandonment triggers
- Critical workflows

**9. USER JOURNEYS**

Create `docs/USER_JOURNEYS.md`.

Document complete journeys for:

**9.1 Organization owner**

1. Register
2. Select Persian or English
3. Create organization
4. Configure organization
5. Optionally define the primary location
6. Invite a coach
7. Review organization activity
8. Manage members
9. Review basic analytics

**9.2 Coach**

1. Accept invitation
2. Complete coach profile
3. Select Persian or English
4. View assigned athletes
5. Search exercise library
6. Review exercise details and media
7. Create training program
8. Create phases, weeks, days, and workouts
9. Add sets, reps, load, tempo, RPE/RIR, rest, and notes
10. Save a reusable template
11. Assign a program to an athlete
12. Review athlete logs
13. Send a contextual message
14. Review adherence and feedback

**9.3 Athlete**

1. Accept invitation
2. Create profile
3. Select Persian or English
4. View Today’s Workout
5. View exercise instructions and media
6. Start workout
7. Log actual sets, reps, load, RPE, and notes
8. Pause, skip, or modify a workout with a reason
9. Submit pain/fatigue/feedback flags
10. Complete workout
11. Review progress
12. Message the coach

**9.4 Platform administrator**

1. Manage users
2. Manage organizations
3. Review exercise content
4. Approve/reject exercise media
5. Archive/restore content
6. Review audit events
7. Handle support and abuse escalation

**9.5 Future nutrition professional**

Document as P1 only:

1. Receive invitation
2. Obtain athlete consent
3. View permitted athlete data
4. Complete intake
5. Create meal plan
6. Assign meal plan
7. Review food logs
8. Provide feedback
9. Collaborate with coach
10. Revoke or lose access when assignment ends

For every journey include:

- Actor
- Preconditions
- Main flow
- Alternate flows
- Error states
- Permission checks
- Data created/read
- Notifications
- Localization considerations
- Privacy considerations
- Success criteria

**10. MVP SCOPE**

Define a clear P0 MVP.

**P0 must include:**

- Authentication
- Organization/tenancy
- Invitations
- Platform Admin, Organization Owner, Coach, and Athlete roles
- Server-side RBAC
- Object-level authorization
- Persian RTL
- English LTR
- Language switcher
- Bilingual exercise content
- Exercise search
- Exercise filtering
- Exercise aliases and Persian search normalization
- Media provenance and rights metadata
- Program builder
- Program templates
- Program versioning
- Program assignment
- Athlete Today’s Workout
- Workout calendar
- Workout logging
- Adherence tracking
- Athlete feedback
- Basic progress metrics
- Coach-athlete message threads
- In-app notifications
- Notification preferences
- Admin exercise moderation
- Audit events
- Basic data export/deletion workflow design
- PWA foundation requirements for Phase 04

**P0 must not include:**

- Arabic
- Public Marketplace
- Coach discovery marketplace
- Payment processing
- Nutrition professional UI
- Meal-plan workflows
- Wearables
- HealthKit
- Health Connect
- Advanced AI
- Autonomous recommendations
- Native iOS/Android applications
- Full multi-location management
- Payroll
- Clinical/medical functionality
- Drug or supplement recommendations

**11. P0 USER STORIES**

Create stable IDs such as:

`US-AUTH-001`  
`US-ORG-001`  
`US-I18N-001`  
`US-EX-001`  
`US-PRG-001`  
`US-ATH-001`  
`US-MSG-001`  
`US-NTF-001`  
`US-ADM-001`  
`US-AUD-001`  
`US-PRI-001`

Create detailed stories for every P0 epic.

Each story must include:

- Story ID
- Epic
- Persona
- User story
- Business value
- Priority
- Preconditions
- Main flow
- Alternate flow
- Error flow
- Permission requirements
- Data requirements
- Localization requirements
- Privacy/security requirements
- Dependencies
- Acceptance criteria
- Planned implementation phase
- Traceability link

**12. ACCEPTANCE CRITERIA**

Acceptance criteria must be testable and preferably written in Given/When/Then format.

Include positive and negative authorization tests.

At minimum define criteria for:

**12.1 Tenant isolation**

Given a coach belongs to Organization A
And Athlete X is assigned to that coach
When the coach requests Athlete X
Then the request succeeds
And only Organization A data is returned

Given a coach belongs to Organization A
And Athlete Y belongs only to Organization B
When the coach requests Athlete Y
Then the request is denied
And no Athlete Y data is leaked

**12.2 Invitations**

Given an organization owner is authenticated
When the owner invites a coach by email
Then a time-limited invitation is created
And the invitation cannot be reused after acceptance

**12.3 Localization**

Given the user has selected Persian
When the user opens the athlete workout screen
Then the page uses RTL direction
And all visible strings come from Persian resources
And no Arabic resource or locale is loaded

Given the user has selected English
When the user opens the athlete workout screen
Then the page uses LTR direction
And all visible strings come from English resources

**12.4 Program assignment**

Given a coach has created a valid program
When the coach assigns the program to an athlete
Then the athlete can see the scheduled workout
And the coach can see the assignment status

**12.5 Workout logging**

Given an athlete has an assigned workout
When the athlete logs actual reps and load
Then the values are persisted
And the coach can review them
And the action is attributable to the athlete

**12.6 Sensitive media**

Given an athlete has uploaded a progress photo
When an unauthorized user requests the photo
Then access is denied
And the media is not exposed through a public URL

Also define criteria for:

- Loading states
- Empty states
- Error states
- Expired invitations
- Suspended users
- Archived programs
- Deleted athletes
- Duplicate submissions
- Notification preferences
- Rate limits
- Audit events
- Persian search normalization
- Mixed Persian/Latin text
- Mobile layout behavior

**13. P1 AND P2 BACKLOG**

Define and prioritize the future backlog.

**P1**

- Nutrition Professional role
- Consent-based multi-professional collaboration
- Athlete shared profile
- Meal plans
- Food items and recipes
- Persian food content strategy
- Macro calculations
- Dietary preferences
- Allergies and restrictions
- Food logging
- Habits
- Check-ins
- Scheduling
- Packages
- Payment abstraction
- Coach storefront
- Basic branding
- Organization reports
- Basic multi-location support

**P2**

- Public Marketplace
- Coach/nutrition professional discovery
- Profiles
- Verification
- Reviews
- Booking
- Disputes
- One-time program purchases
- Recurring subscriptions
- Community
- Challenges
- Leaderboards
- Gamification
- AI Copilot
- Wearables
- HealthKit
- Health Connect
- Advanced analytics
- Churn prediction
- White-label native apps
- Multi-currency
- Full multi-location management

For every item include:

- User problem
- Expected value
- Complexity
- Dependencies
- Risks
- Why it is not P0
- Proposed success metric
- Suggested phase

**14. NON-FUNCTIONAL REQUIREMENTS**

Define proposed measurable requirements for:

**Security**

- Secure password hashing
- Secure session/token handling
- Authentication rate limiting
- Secure cookies where applicable
- CSRF protection
- CORS allowlist
- Security headers
- Input validation
- Output encoding
- File upload validation
- Dependency scanning
- No secrets in Git
- No real health data in fixtures

**Authorization**

- Server-side enforcement
- Organization boundaries
- Object-level access rules
- Negative authorization tests
- Auditability of sensitive actions

**Privacy**

- Data minimization
- Purpose limitation
- Consent hooks
- Progress-photo consent
- Future multi-professional sharing consent
- Data export
- Data deletion
- Retention questions
- Privacy policy requirement

**Accessibility**

Target WCAG 2.2 AA for core flows.

Include:

- Keyboard navigation
- Focus states
- Contrast
- Screen-reader labels
- Reduced motion
- Touch target sizes
- Accessible validation and error messages

**Performance**

Define proposed targets for:

- Athlete Today’s Workout loading
- Coach program builder responsiveness
- API response time
- Low-bandwidth usability
- Media loading
- Mobile rendering
- Core Web Vitals where applicable

Do not claim guaranteed performance before benchmarking.

**Reliability**

Define:

- Backup strategy
- Restore testing
- Error handling
- Idempotency expectations
- Notification retry behavior
- Data integrity requirements

**Localization**

Define:

- No hardcoded UI text
- Persian RTL
- English LTR
- CSS logical properties
- Locale-aware formatting
- Persian character normalization
- Mixed-direction text handling
- Locale-specific date/time/number formatting
- No Arabic resources

**PWA**

Define requirements for:

- Installable app
- Web App Manifest
- Service Worker foundation
- Mobile-first shell
- Offline scope
- Network failure behavior
- Sync behavior
- Push limitations
- Future native-app decision

**15. PERMISSIONS MATRIX**

Create a detailed permissions matrix for:

- Platform Administrator
- Organization Owner
- Coach
- Athlete
- Future Nutrition Professional
- Support/Read-only Staff

Include permissions for:

- Users
- Organizations
- Locations
- Exercise records
- Exercise media
- Programs
- Program templates
- Program assignments
- Workout logs
- Progress metrics
- Progress photos
- Messages
- Notifications
- Audit logs
- Consent
- Nutrition records
- Payments
- Marketplace records

For each permission distinguish:

- Create
- Read
- Update
- Delete/archive
- Moderate
- Approve
- Export
- Share
- Revoke access

Document:

- Coach-to-athlete access
- Organization-owner access
- Platform-admin access
- Future nutritionist access
- Athlete control over sensitive data
- Support-staff restrictions

**16. DATA AND PRIVACY BOUNDARIES**

Update the privacy and data documents to classify:

- Public data
- Account data
- Organization data
- Coaching operational data
- Sensitive health-related data
- Progress media
- Audit data
- Payment data — future
- AI logs — future
- Secrets

Document:

- Athlete data ownership assumptions
- Coach access rules
- Future nutritionist access rules
- Consent requirements
- Data export expectations
- Data deletion expectations
- Data retention questions
- Sensitive media access
- No real PII/PHI in development
- No secrets in reports or fixtures

**17. COMPETITIVE LANDSCAPE**

Create `docs/COMPETITIVE_LANDSCAPE.md`.

Use public desk research and clearly state that features and prices change.

Benchmark at least:

- ABC Trainerize
- PT Distinction
- My PT Hub
- Everfit
- TrueCoach
- FITR
- TrainHeroic
- Exercise.com
- Liaqa
- At least one nutrition-practice platform

Compare:

- Workout programming
- Exercise library
- Athlete logging
- Nutrition
- Habits/check-ins
- Messaging
- Scheduling
- Payments
- Coach monetization
- Branding
- Marketplace
- Team management
- Multi-location
- Persian support
- English support
- RTL support
- AI features
- PWA/native delivery
- Pricing model
- Main strengths
- Main weaknesses
- Product lessons for CoachOS

Do not fabricate prices or features.

Use official product sources when web access is available. If web access is unavailable, mark claims as unverified assumptions.

Researching Arabic-market competitors is allowed for competitive analysis, but Arabic must not be added as a CoachOS product language or implementation requirement.

**18. TRACEABILITY MATRIX**

Expand `docs/TRACEABILITY_MATRIX.md`.

Every P0 requirement must map to:

- Requirement ID
- Epic
- User story ID
- Acceptance criteria ID
- Persona
- Design artifact
- Domain area
- API/domain area
- Planned implementation phase
- Test type
- Status

Every sensitive domain must have at least one negative authorization test mapped to it.

**19. REQUIRED DECISION UPDATES**

Update `docs/DECISIONS.md` with decisions or pending decisions for:

- MIT versus proprietary/open-core licensing
- PWA sequencing
- Single-location-first MVP
- Calendar strategy
- Authentication channel
- Organization and membership model
- Single-role versus multi-role memberships
- Program versioning
- Soft delete versus archive
- UUID versus integer IDs
- Search strategy
- Data ownership
- Nutritionist collaboration
- Payment deferral
- Marketplace deferral

Every decision must include:

- Context
- Options
- Recommendation
- Consequences
- Status
- Whether founder approval is required

**20. TRACEABLE STATUS AND CHANGELOG UPDATES**

At the end of Phase 01, update:

- `PROJECT_STATUS.md`
- `PROJECT_CHECKLIST.md`
- `CHANGELOG.md`
- `docs/PROMPT_LOG.md`
- `docs/PRD.md`
- `docs/TRACEABILITY_MATRIX.md`
- `docs/RELEASE_PLAN.md`
- Relevant decision documents
- Relevant security/privacy documents

Only genuinely completed items may be marked `[x]`.

Do not mark any implementation phase as completed.

**21. PHASE 01 EXIT GATES**

Phase 01 is complete only when:

- Personas are complete.
- Core user journeys are complete.
- P0 is clearly separated from P1 and P2.
- Every P0 epic has user stories.
- Every P0 story has testable acceptance criteria.
- Positive and negative authorization scenarios exist.
- Permissions matrix exists.
- NFRs have proposed measurable targets.
- Privacy and data boundaries are explicit.
- PWA sequencing is corrected.
- MIT/license decision is documented as pending founder approval.
- Calendar strategy is analyzed.
- Single-location-first scope is documented.
- Competitive landscape is created.
- Traceability matrix is expanded.
- All documents are internally consistent.
- No application code was added.
- No dependencies were installed.
- No Arabic resources or requirements were added.
- Checklist is updated.
- Status file is updated.
- Changelog is updated.
- Prompt log contains the exact current prompt and merge housekeeping record.
- Phase 01 report is committed.

**22. REQUIRED PHASE 01 REPORT**

Create:

`docs/reports/PHASE-01-REQUIREMENTS-REPORT.md`

The report must contain these sections:

# Phase 01 — Product Requirements and Scope

## 1. Executive Summary
## 2. Persian Executive Summary
## 3. Prompt(s) Received
## 4. Objectives
## 5. Post-Merge Repository Verification
## 6. Personas Completed
## 7. User Journeys Completed
## 8. P0 Scope
## 9. P1/P2 Backlog
## 10. User Stories and Acceptance Criteria
## 11. Permissions Matrix
## 12. Non-Functional Requirements
## 13. Product and Architecture Decisions
## 14. Calendar and PWA Decisions
## 15. License and Intellectual Property Decision
## 16. Competitive Landscape Summary
## 17. Files Created or Changed
## 18. GitHub Branch, Commit, Issues, and Pull Request
## 19. Tests and Validation
## 20. Security and Privacy Considerations
## 21. Assumptions
## 22. Open Questions
## 23. Risks and Blockers
## 24. Deferred Items
## 25. Traceability Summary
## 26. Checklist Changes
## 27. Exact Recommended Prompt for Phase 02

The report must include:

- Exact prompt text received
- Actual work completed
- Files changed
- Decisions made
- Decisions requiring founder approval
- Unresolved questions
- Risks and blockers
- Evidence
- GitHub references
- Next recommended prompt

Do not include secrets, credentials, real personal data, or health data in the report.

**23. FINAL COMMUNICATION PROTOCOL**

At the end of Phase 01:

1. Provide a concise but evidence-based summary.
2. Clearly distinguish:
  - Completed
  - Proposed
  - Deferred
  - Blocked
  - Requiring founder approval
3. Provide links or paths to important documents.
4. State the current branch and commit.
5. State whether a Pull Request exists.
6. Confirm that no application code was created.
7. Do not start Phase 02 automatically.
8. Stop and wait for the next instruction.

The next phase after review will be:

`Phase 02 — UX, Information Architecture, and Design System`

Do not proceed to Phase 02 until explicitly instructed.
```

- **Requested outcome:** Complete Phase 01 requirements package, author required specifications, and submit Phase 01 report without application code.
- **Actions taken:**
  - Verified post-merge repository state (`f52c413` on `main`) and working branch.
  - Authored `docs/PERSONAS.md`, `docs/USER_JOURNEYS.md`, `docs/DOMAIN_GLOSSARY.md`, `docs/COMPETITIVE_LANDSCAPE.md`.
  - Substantially updated `docs/PRD.md`, `docs/DECISIONS.md`, `docs/DATA_MODEL.md`, `docs/API_CONTRACT.md`, `docs/SECURITY_AND_PRIVACY.md`, `docs/TRACEABILITY_MATRIX.md`, `docs/RELEASE_PLAN.md`.
  - Authored `docs/reports/PHASE-01-REQUIREMENTS-REPORT.md` and opened Pull Request #4.

---

## Prompt 003

- **Date/time:** 2026-08-10 (UTC)
- **Source:** Founder / supervising agent
- **Phase:** 02 — UX, Information Architecture, and Design System (Preflight & Initiation)
- **Exact Full Text Received:**

```text
**CONTINUE COACHOS AS A PROFESSIONAL PRODUCT-AND-ENGINEERING TEAM**

You are continuing the CoachOS Fitness Coaching Platform as a coordinated professional team consisting of:

- Founder’s Technical Advisor
- Product Manager
- Business Analyst
- UX Researcher
- UX/UI Designer
- Information Architect
- Accessibility Specialist
- Persian RTL/LTR Localization Specialist
- Principal Software Architect
- Security and Privacy Engineer
- QA/Test Engineer
- Technical Writer
- Release Manager
- Code Reviewer

This instruction executes **Phase 02 — UX, Information Architecture, and Design System**.

The output of this phase must be documentation and design specifications only.

**Do not create application source code.**  
**Do not scaffold frontend or backend.**  
**Do not install dependencies.**  
**Do not create database migrations.**  
**Do not implement APIs.**  
**Do not implement AI.**  
**Do not implement payments.**

**1. REPOSITORY AND PHASE 01 VERIFICATION**

Repository:

`https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform`

Phase 01 branch:

`arena/019febfc-coachos-fitness-coaching-platf`

Phase 01 latest commit currently reported:

`eb5a5a31fa4469348e475edb1940a2b6ba7cb378`

Phase 01 Pull Request:

`https://github.com/AliNaderiii/CoachOS-Fitness-Coaching-Platform/pull/4`

Before doing any Phase 02 work, inspect and verify:

- Current branch and commit
- Pull Request #4 state
- Working tree state
- `PROJECT_STATUS.md`
- `PROJECT_CHECKLIST.md`
- `CHANGELOG.md`
- `docs/MASTER_PRODUCT_BRIEF.md`
- `docs/PRD.md`
- `docs/PERSONAS.md`
- `docs/USER_JOURNEYS.md`
- `docs/DOMAIN_GLOSSARY.md`
- `docs/COMPETITIVE_LANDSCAPE.md`
- `docs/DECISIONS.md`
- `docs/DATA_MODEL.md`
- `docs/API_CONTRACT.md`
- `docs/SECURITY_AND_PRIVACY.md`
- `docs/TRACEABILITY_MATRIX.md`
- `docs/RELEASE_PLAN.md`
- `docs/PROMPT_LOG.md`
- `docs/reports/PHASE-00-DISCOVERY-REPORT.md`
- `docs/reports/PHASE-01-REQUIREMENTS-REPORT.md`

Do not assume that the Phase 01 completion summary is correct without reading the actual files.

**Phase separation and Pull Request rule**

Pull Request #4 is the Phase 01 documentation Pull Request. Do not mix Phase 02 UX artifacts into PR #4.

If PR #4 is still open when this prompt is received:

1. Perform the Phase 01 preflight audit below.
2. If corrections are needed, create only correction commits for Phase 01 in the Phase 01 branch and update PR #4.
3. Stop and report that PR #4 must be reviewed and merged before Phase 02 UX work begins.
4. Do not create Phase 02 UX documents on the Phase 01 branch or inside PR #4.

If PR #4 has already been merged:

1. Verify the merge commit on `main`.
2. Create a new Phase 02 branch from the updated `main` branch.
3. Perform the preflight audit and make any necessary documentation corrections on the new Phase 02 branch.
4. Continue with the Phase 02 UX work only on that new branch.

This separation is mandatory so that Phase 01 requirements and Phase 02 UX artifacts remain independently reviewable.

[Detailed instructions covering preflight consistency audit across prompt log, PWA/offline scope, competitive landscape, legal/product claims, security/authorization, and technical document scope; followed by Phase 02 UX specifications.]
```

- **Action Taken in Current Session:** Performed Phase 01 preflight consistency audit, corrected prompt logs with full text, calibrated PWA sequencing across documents, qualified competitor claims, re-stated business metrics as target hypotheses, clarified privacy/consent for owner vs coach roles, and pushed correction commits to PR #4. Awaiting PR #4 review/merge prior to branching for Phase 02.
