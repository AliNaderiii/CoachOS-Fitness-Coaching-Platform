# Design System & Component Library Specification — CoachOS

**Document version:** 1.0.0 (Phase 02 Baseline)  
**Last updated:** 2026-08-10  
**Supported Locales:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR)  
**Strict constraint:** Arabic is strictly out of scope.  
**Design Phase:** Phase 02 — Documentation and specifications only. No application source code.

---

## 1. Core Design Principles

1. **Athlete-First Mobile Clarity:** Mobile workout execution prioritizes high-contrast visibility, large hit targets (minimum **44×44px** per WCAG 2.5.5; **48×48px preferred design target** for primary CTAs — actual implementation must be tested against accessibility and device usability requirements), and minimal tap friction on busy gym floors.
2. **Coach Programming Velocity:** Desktop interfaces emphasize dense, keyboard-friendly data entry and rapid drag-and-drop structural manipulation.
3. **True Bilingual Parity:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR) receive identical functional depth, typography care (`Vazirmatn` vs `Inter`), and layout symmetry.
4. **Progressive Disclosure:** Complex periodization settings and physiological metrics unfold contextually without cluttering the primary workout loop.
5. **Trustworthy Privacy & Consent:** Clear, affirmative consent dialogs precede any progress photo upload or multi-professional sharing. Zero ambiguous sharing defaults.
6. **No Distracting Gamification in P0:** Strict focus on functional coaching utility, adherence clarity, and progress metrics rather than cartoonish badges or game mechanics.

---

## 2. Core UI Component Specifications

### 2.1 Buttons & Interactive Controls

#### Button (`Btn`)
- **Purpose:** Primary, secondary, tertiary, and destructive user actions.
- **Variants:**
  - `Primary` (Solid brand blue/teal; high emphasis actions: "Start Workout", "Save Program").
  - `Secondary` (Outlined surface border; medium emphasis: "Add Exercise", "Preview Plan").
  - `Tertiary / Ghost` (Text only; low emphasis: "Skip", "Cancel").
  - `Destructive` (Solid/outlined crimson red; dangerous actions: "Suspend Member", "Delete Program").
- **States:** Default, Hover, Focused (visible 2px ring), Active/Pressed, Disabled (`opacity: 0.5; pointer-events: none`), Loading (spinner replacing icon).
- **Accessibility:** Native `<button>` element; visible focus outline with 3:1 contrast; `aria-disabled="true"` when inactive.
- **RTL/LTR Behavior:** Leading icon renders at `inline-start`; trailing icon at `inline-end`.

#### Numeric Keypad & Stepper Inputs (`SetNumInput`)
- **Purpose:** Fast logging of load (`kg`/`lbs`), reps, and RPE during live workout sessions.
- **Variants:** Full keypad popup on mobile; inline stepper (+/- buttons) on tablet/desktop.
- **States:** Default, Focused (enlarged active border), Validated (green check), Invalid (red border + shake animation).
- **Mobile Ergonomics:** 52px height; oversized numerical digits; native virtual number keypad trigger (`inputmode="decimal"`).
- **RTL/LTR Behavior:** Numbers format in Persian digits (`۰-۹`) when active locale is `fa-IR`, and Latin digits (`0-9`) in `en-US`.

---

### 2.2 Date & Calendar Selectors

#### Bilingual Date Picker (`DatePicker`)
- **Purpose:** Selecting program start dates, calendar navigation, and historical log filtering.
- **Locale Modes:**
  - **`fa-IR` Mode:** Renders Solar Hijri (Jalali / شمسی) calendar grid (e.g., Farvardin to Esfand, Saturday to Friday week layout).
  - **`en-US` Mode:** Renders Gregorian calendar grid (January to December, Monday to Sunday week layout).
- **Underlying Storage:** Transmits ISO 8601 UTC timestamp strings to API handlers.
- **Accessibility:** Full keyboard navigability (Arrow keys navigate days, PageUp/PageDown navigate months, Enter selects).

---

### 2.3 Cards & Data Containers

#### Exercise Card (`ExerciseCard`)
- **Purpose:** Displays exercise name, target prescriptions, and media demo thumbnail on athlete today view and coach builders.
- **Structure:**
  - Header: Exercise sequence number, localized name, movement pattern tag.
  - Body: Prescription targets (Sets, Reps, Load, Tempo, Rest interval).
  - Media Strip: 16:9 video demo thumbnail with play badge.
  - Footer: Coach's custom notes and previous week's logged performance badge.
- **RTL/LTR Behavior:** Thumbnail docks at `inline-start` or top; text aligns to `inline-start`.

#### Workout Session Card (`WorkoutCard`)
- **Purpose:** Surfaces scheduled or completed workout summaries on calendar and dashboard views.
- **Status Badges:** `Scheduled` (Blue), `In Progress` (Amber), `Completed` (Emerald Green), `Skipped` (Slate Gray), `Modified` (Purple).

---

### 2.4 Program Tree & Hierarchical Nodes

#### Program Tree Node (`ProgramTreeNode`)
- **Purpose:** Renders the periodization hierarchy (Phase -> Week -> Day -> Exercise Item) in the Coach Program Builder.
- **Behaviors:** Collapsible accordion nodes; drag-and-drop handles for reordering; superset grouping bracket (`A1/A2`).
- **Keyboard Navigation:** Standard ARIA treegrid semantics (Right arrow expands in LTR / Left arrow in RTL; Up/Down arrows traverse items).

---

### 2.5 Modals, Drawers & Feedback Overlays

#### Consent Dialog (`ConsentModal`)
- **Purpose:** Explicit, affirmative consent capture before sensitive data processing (e.g., progress photo upload, nutritionist profile sharing).
- **Structure:**
  - Title: Clear, plain-language description (e.g., *"Allow Coach Reza to view progress photos"*).
  - Body: Plain-text explanation of data usage and unilateral athlete revocation rights.
  - Actions: Primary "Grant Consent" button vs Secondary "Keep Private" button.
- **Accessibility:** Focus trapped within dialog; Escape key closes; initial focus on "Keep Private" (privacy-first default).

#### Discomfort / Pain Flag Modal (`PainFlagModal`)
- **Purpose:** Captures subjective athlete discomfort signals during workout logging.
- **Structure:**
  - Anatomical Area Picker (Shoulder, Knee, Lower Back, Neck, Wrist, Hip, Ankle).
  - Severity Rating Scale (Mild 1–3, Moderate 4–6, Severe 7–10).
  - Optional descriptive notes textarea.
  - Notice: *"This report will be sent to your coach for workout adjustment. It is not a medical diagnosis."*

#### Rest Countdown Timer Overlay (`RestTimer`)
- **Purpose:** Visual and audio countdown between exercise sets.
- **Structure:** Circular SVG progress ring; large remaining time digits (`01:30`); quick-adjust buttons (`+30s`, `Skip`).
- **Accessibility:** `aria-live="polite"` announces interval completion; vibrates mobile device on completion.
