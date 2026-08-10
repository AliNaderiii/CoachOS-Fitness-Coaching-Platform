# UX Requirements Traceability Matrix — CoachOS

**Document version:** 1.0.0 (Phase 02 Baseline)  
**Last updated:** 2026-08-10  
**Purpose:** End-to-end traceability mapping Phase 01 User Stories -> Screens -> User Flows -> Wireframes -> Design Tokens -> Accessibility & State Handlers.

---

## 1. P0 User Story to UX Artifact Traceability Mapping

| Story ID | User Story Title | Primary Screen ID | Secondary Screens | Target User Flow | Wireframe Spec | Design Components Required | RTL / LTR Rule | Accessibility Requirement | State Matrix Key | Planned Impl Phase |
|---|---|---|---|---|---|---|---|---|---|---|
| **US-AUTH-001** | User Registration | `SCR-AUTH-01` | `SCR-ORG-01` | `UF-OWNER-01` | `docs/ux/WIREFRAMES.md` §1 | `Input`, `PasswordInput`, `Btn`, `LocaleSelect` | Dynamic `dir` switch on select | Visible labels; ARIA live validation | `auth.register` | Phase 05 |
| **US-AUTH-002** | Secure Login & Rate Limit | `SCR-AUTH-02` | `SCR-AUTH-03` | `UF-OWNER-01` | `docs/ux/WIREFRAMES.md` §1 | `Input`, `PasswordInput`, `Btn`, `Alert` | Text align `start`; mirrored alert icon | Focus order; 429 lock announcement | `auth.login` | Phase 05 |
| **US-AUTH-003** | Password Reset Flow | `SCR-AUTH-03` | `SCR-AUTH-04` | `UF-OWNER-01` | `docs/ux/WIREFRAMES.md` §1 | `Input`, `Btn`, `Toast` | Mirrored input labels | Accessible email confirmation toast | `auth.forgot_password` | Phase 05 |
| **US-ORG-001** | Organization Creation | `SCR-ORG-01` | `SCR-ORG-02` | `UF-OWNER-01` | `docs/ux/WIREFRAMES.md` §1 | `Input`, `SlugInput`, `Btn`, `Card` | Mirrored slug preview layout | Accessible slug collision error | `org.create` | Phase 05 |
| **US-ORG-002** | Single Location Setup | `SCR-ORG-03` | `SCR-ORG-02` | `UF-OWNER-01` | `docs/ux/WIREFRAMES.md` §1 | `Input`, `PhoneInput`, `Btn` | Mirrored phone input BiDi wrapper | Standard form accessibility | `org.facility` | Phase 05 |
| **US-ORG-003** | Coach Invitation | `SCR-ORG-05` | `SCR-ORG-04` | `UF-OWNER-01` | `docs/ux/WIREFRAMES.md` §1 | `Modal`, `Input`, `Select`, `Btn` | Focus trapped modal; mirrored inputs | Modal focus trap; Escape key handler | `org.invite_coach` | Phase 05 |
| **US-ORG-004** | Athlete Invitation | `SCR-ORG-05` | `SCR-ORG-04` | `UF-OWNER-01` | `docs/ux/WIREFRAMES.md` §1 | `Modal`, `Input`, `CoachDropdown`, `Btn` | Mirrored dropdown menu | Screen reader selection announcement | `org.invite_athlete` | Phase 05 |
| **US-ORG-005** | Member Management & Suspend | `SCR-ORG-04` | `SCR-ORG-02` | `UF-OWNER-01` | `docs/ux/WIREFRAMES.md` §1 | `Table`, `Badge`, `DropdownMenu`, `ConfirmModal` | Right-aligned table headers in `fa-IR` | Accessible confirmation dialog | `org.members` | Phase 05 |
| **US-I18N-001** | Language Switcher (`fa`/`en`) | `SCR-ATH-09` | Global Nav | Global | Global Spec | `LocaleSwitcherPill`, `Icon` | Swaps `dir="rtl"` vs `dir="ltr"` | Announces new language in native voice | `i18n.switch` | Phase 04–07 |
| **US-I18N-002** | Persian Search Normalization | `SCR-COACH-08` | `SCR-COACH-06` | `UF-COACH-01` | `docs/ux/WIREFRAMES.md` §3 | `SearchInput`, `Badge`, `Card` | Arabic Yeh/Kaf variant folding | Real-time live region result count | `exercise.search` | Phase 06 |
| **US-EX-001** | Bilingual Exercise Catalog | `SCR-COACH-08` | `SCR-COACH-09` | `UF-COACH-01` | `docs/ux/WIREFRAMES.md` §3 | `FilterBar`, `ExerciseCard`, `VideoModal` | Mirrored filter pills & thumbnail dock | Video player accessible controls | `exercise.catalog` | Phase 06 |
| **US-EX-002** | Custom Private Exercise | `SCR-COACH-10` | `SCR-COACH-08` | `UF-COACH-01` | `docs/ux/WIREFRAMES.md` §3 | `Form`, `Input`, `MediaUploader`, `Select` | Bilingual side-by-side translation form | Accessible file upload dropzone | `exercise.create` | Phase 06 |
| **US-EX-003** | Admin Exercise Moderation | `SCR-ADMIN-02` | `SCR-ADMIN-01` | `UF-ADMIN-01` | `docs/ux/WIREFRAMES.md` §3 | `ModerationTable`, `VideoPlayer`, `Btn` | Mirrored action buttons (Approve/Reject) | Keyboard shortcuts (Shift+A, Shift+R) | `admin.moderation` | Phase 06 |
| **US-PRG-001** | Hierarchical Program Builder | `SCR-COACH-06` | `SCR-COACH-05` | `UF-COACH-01` | `docs/ux/WIREFRAMES.md` §3 | `ProgramTree`, `PrescriptionForm`, `Stepper` | Dual-pane tree docked at `inline-start` | ARIA treegrid keyboard navigation | `program.builder` | Phase 06 |
| **US-PRG-002** | Reusable Program Templates | `SCR-COACH-05` | `SCR-COACH-06` | `UF-COACH-01` | `docs/ux/WIREFRAMES.md` §3 | `CardGrid`, `Btn`, `Badge`, `CloneModal` | Mirrored card grid | Standard card button accessibility | `program.templates` | Phase 06 |
| **US-PRG-003** | Program Assignment & Snapshot | `SCR-COACH-07` | `SCR-COACH-02` | `UF-COACH-01` | `docs/ux/WIREFRAMES.md` §3 | `Modal`, `DatePicker (Jalali/Gregorian)`, `Btn` | Localized calendar grid layout | Date picker keyboard accessible | `program.assign` | Phase 06 |
| **US-ATH-001** | Athlete "Today's Workout" | `SCR-ATH-01` | `SCR-ATH-02` | `UF-ATH-01` | `docs/ux/WIREFRAMES.md` §2.1 | `WorkoutCard`, `ExerciseList`, `PrimaryCTA` | Mirrored card list; 48px touch CTA | `<h1>` landmark; accessible card cues | `ath.today` | Phase 07 |
| **US-ATH-002** | Workout Execution & Logging | `SCR-ATH-02` | `SCR-ATH-05` | `UF-ATH-01` | `docs/ux/WIREFRAMES.md` §2.2 | `SetTable`, `NumKeypad`, `RestTimer` | Mirrored set table; Persian numerals | Live region announces set complete | `ath.active_session` | Phase 07 |
| **US-ATH-003** | Exercise Substitution | `SCR-ATH-03` | `SCR-ATH-02` | `UF-ATH-01` | `docs/ux/WIREFRAMES.md` §2.2 | `Modal`, `SearchInput`, `ReasonSelect`, `Btn` | Mirrored selection modal | Accessible radio group for reasons | `ath.substitute` | Phase 07 |
| **US-ATH-004** | Pain Flag & Session Feedback | `SCR-ATH-04` | `SCR-ATH-05` | `UF-ATH-01` | `docs/ux/WIREFRAMES.md` §2.2 | `Modal`, `PainSeveritySlider`, `Textarea` | Mirrored slider & anatomical list | Non-clinical disclaimer announced | `ath.pain_flag` | Phase 07 |
| **US-ATH-005** | Progress Photo Upload & Consent | `SCR-ATH-07` | `SCR-ATH-09` | `UF-ATH-01` | `docs/ux/WIREFRAMES.md` §2.1 | `PhotoUploader`, `ConsentModal`, `Thumbnail` | Mirrored thumbnail grid | Mandatory consent modal focus trap | `ath.photos` | Phase 07 |
| **US-MSG-001** | Contextual 1:1 Messaging | `SCR-ATH-08` | `SCR-COACH-04` | `UF-ATH-01` | `docs/ux/WIREFRAMES.md` §2.1 | `ChatThread`, `SessionBadge`, `Input`, `Btn` | Message bubbles align to `inline-end` | Accessible chat thread semantics | `comms.messages` | Phase 08 |
| **US-NTF-001** | In-App Notifications & Prefs | `SCR-ATH-09` | Global Header | Global | Global Spec | `NotificationDrawer`, `ToggleSwitch`, `Badge` | Drawer enters from `inline-end` | Unread badge announced to screen reader | `comms.notifications` | Phase 08 |
| **US-AUD-001** | Immutable Audit Log Viewer | `SCR-ORG-06` | `SCR-ADMIN-04` | `UF-ADMIN-01` | `docs/ux/WIREFRAMES.md` §3 | `Table`, `FilterBar`, `JSONViewerModal` | Right-aligned log table in `fa-IR` | Standard tabular accessibility | `admin.audit` | Phase 05+ |
| **US-PRI-001** | Data Export Request | `SCR-ATH-09` | `SCR-ORG-02` | Global | `docs/ux/WIREFRAMES.md` §1 | `Card`, `Btn`, `Toast`, `ConfirmModal` | Mirrored export description card | Accessible confirmation toast | `privacy.export` | Phase 03/13 |
| **US-PRI-002** | Account Erasure ("Forget Me") | `SCR-ATH-09` | `SCR-AUTH-02` | Global | `docs/ux/WIREFRAMES.md` §1 | `DestructiveConfirmModal`, `PasswordInput` | Centered destructive modal | Screen reader destructive alert | `privacy.delete` | Phase 03/13 |
| **US-PWA-001** | PWA Shell & Home Screen Install | Global | Global | Global | Global Spec | `PWAInstallBanner`, `OfflineToast` | Bottom banner adapts to direction | Accessible install CTA button | `pwa.install` | Phase 04 |
