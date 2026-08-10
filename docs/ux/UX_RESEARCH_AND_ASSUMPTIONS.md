# UX Research, Assumptions & Validation Plan — CoachOS

**Document version:** 1.0.0 (Phase 02 Baseline)  
**Last updated:** 2026-08-10  
**Supported Locales:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR)  
**Strict constraint:** Arabic is strictly out of scope.  
**Design Phase:** Phase 02 — Documentation and specifications only. No application source code.

---

## 1. Categorization of Knowledge: Evidence vs Assumptions

To maintain engineering and product rigor, CoachOS strictly distinguishes between **established evidence**, **product hypotheses**, and **unvalidated assumptions**:

| Category | Definition | Current CoachOS Examples |
|---|---|---|
| **Established Evidence** | Verified facts from repository inspection, PR merges, technical constraints, and desk research. | Greenfield repository verified; PR #3 and PR #4 merged into `main`; Persian/English supported; Arabic strictly out of scope; B2B2C business model decided. |
| **Product & UX Hypotheses** | Plausible, testable assumptions regarding user behavior to be validated in pilot. | Coaches can build a 4-week program in < 10 minutes using templates; athletes can log a set in < 3 taps; dark mode reduces eye strain in gym environments. |
| **Unvalidated Design Decisions** | Architectural choices requiring empirical confirmation during usability testing. | Jalali Solar Hijri calendar display adequacy for Persian athletes; SMS OTP vs Email/Password login preference in Iran; PWA home-screen install friction. |

---

## 2. Research Questions by Stakeholder Persona

### 2.1 Persian-Speaking Coaches (`P-COACH`)
1. **Calendar System Expectations:** When prescribing a 4-week mesocycle, do you plan training days relative to Solar Hijri (Jalali / شنبه تا جمعه) dates or international Gregorian days?
2. **Exercise Search & Terminology:** What colloquial Persian fitness terms do you search for most often (e.g., *"زیربغل دمبل تک‌خم"*, *"سرشانه هالتر از پشت"*), and how often do you mix English abbreviations (e.g., *"RPE 8"*, *"AMRAP"*) into your prescriptions?
3. **Programming Velocity:** How many minutes do you currently spend writing a customized 4-week training program in spreadsheets or notes apps, and what is the biggest friction point?

### 2.2 International & English-Speaking Coaches (`P-COACH`)
1. **Builder Layout Preferences:** In a desktop dual-pane builder, do you prefer configuring prescriptions inline on a spreadsheet grid or in a dedicated form drawer?
2. **Adherence Thresholds:** What specific adherence rate triggers an intervention or check-in message for an athlete?

### 2.3 Gym & Studio Owners (`P-OWNER`)
1. **Data Ownership & Staff Transitions:** When a personal trainer leaves your facility, how do you currently transition their active client roster and historical program templates?
2. **Privacy vs Operational Oversight:** What level of detail do you need to see on an athlete's profile (e.g., high-level adherence % vs individual set logs)?

### 2.4 Athletes / Clients (`P-ATH`)
1. **Gym-Floor Usability & Connectivity:** How frequently does your mobile cellular data drop inside your gym facility, and how do you handle tracking your workouts when offline?
2. **Progress Photo Privacy Comfort:** Under what conditions are you comfortable uploading physical progress photos into a coaching platform? Do you expect the gym owner to see them, or only your assigned personal trainer?
3. **PWA Installation Willingness:** How willing are you to tap *"Add to Home Screen"* in your mobile browser compared to downloading a 150MB native app from the App Store?

### 2.5 Future Nutrition Professionals (`P-NUT` — P1 Scope)
1. **Persian Food Logging Realities:** What are the most common Iranian meals (e.g., Ghormeh Sabzi, Kebab Koobideh, Sangak bread) that clients struggle to track accurately in standard Western apps?
2. **Coach-Dietitian Communication:** How do you currently collaborate with an athlete's personal trainer when synchronizing calorie intake with heavy training phases?

---

## 3. Usability Testing & Pilot Validation Protocol (Phase 14 Prep)

### 3.1 Key Task Scenarios to Test
1. **Scenario 1 (Coach):** *You have a new client starting Monday. Search the catalog for "اسکوات", create an 8-week program with a superset on Day 1, save it as a template, and assign it.*
2. **Scenario 2 (Athlete):** *You arrive at the gym on Leg Day. Open CoachOS on your phone, watch the video cue for Back Squats, log 80kg for 8 reps, start the 90s rest timer, and flag mild knee discomfort.*
3. **Scenario 3 (Owner):** *A coach has departed the gym. Open the team roster, suspend their membership, and reassign their 5 active athletes to another trainer.*

### 3.2 Evaluation Metrics & Success Criteria
- **Task Completion Rate:** > 90% across all 3 scenarios without facilitator intervention.
- **Time on Task:** Coach program assignment < 10 minutes; Athlete single set log < 5 seconds.
- **System Usability Scale (SUS):** Target SUS score >= **82/100** during pilot testing.
