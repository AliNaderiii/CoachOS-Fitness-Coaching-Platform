# Navigation Model & Interaction Patterns — CoachOS

**Document version:** 1.0.0 (Phase 02 Baseline)  
**Last updated:** 2026-08-10  
**Supported Locales:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR)  
**Strict constraint:** Arabic is strictly out of scope.  
**Design Phase:** Phase 02 — Documentation and specifications only. No application source code.

---

## 1. Multi-Device Navigation Paradigms

CoachOS employs responsive navigation patterns tailored to the physical context of the user:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ MOBILE VIEWPORT (< 768px)                                                   │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ [Top Bar]  (Org Brand / Page Title)          [Notification] [Profile]   │ │
│ ├─────────────────────────────────────────────────────────────────────────┤ │
│ │                                                                         │ │
│ │                        Main Content Canvas                              │ │
│ │                                                                         │ │
│ ├─────────────────────────────────────────────────────────────────────────┤ │
│ │ [Bottom Navigation Bar] (4–5 primary role-specific tabs with active pill) │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ TABLET / DESKTOP VIEWPORT (>= 768px)                                        │
│ ┌───────────────┬─────────────────────────────────────────────────────────┐ │
│ │ [Brand Logo]  │ [Top Utility Bar] (Org Switcher | Language | Profile)   │ │
│ ├───────────────┼─────────────────────────────────────────────────────────┤ │
│ │ [Sidebar Nav] │ [Breadcrumb Navigation]                                 │ │
│ │ • Dashboard   ├─────────────────────────────────────────────────────────┤ │
│ │ • Athletes    │                                                         │ │
│ │ • Programs    │            Dual-Pane / Master-Detail Canvas             │ │
│ │ • Exercises   │                                                         │ │
│ │ • Messages    │                                                         │ │
│ │ • Settings    │                                                         │ │
│ └───────────────┴─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Athlete Mobile Navigation Model (PWA-First)

### 2.1 Persistent Bottom Navigation Bar
The athlete mobile interface features a fixed bottom navigation bar (height: 64px) with large touch targets (minimum 48x48px hit areas), active tab indicators, and unread notification badges.

| Tab Index | Tab Title (English) | Tab Title (Persian) | Icon Semantic | Target Route | Behavioral Purpose |
|---|---|---|---|---|---|
| **1 (Primary)** | **Today** | **امروز** | Calendar Checkmark (`calendar-check`) | `/app/today` | Default landing page; immediate access to today's workout. |
| **2** | **Calendar** | **تقویم** | Grid Calendar (`calendar-month`) | `/app/calendar` | Monthly view of past logs and scheduled upcoming sessions. |
| **3** | **Progress** | **پیشرفت** | Trending Line Chart (`chart-line`) | `/app/progress` | Volume progression, body weight log, and private progress photos. |
| **4** | **Messages** | **پیام‌ها** | Chat Bubble (`message-square`) | `/app/messages` | 1:1 direct contextual thread with assigned coach. |
| **5** | **Profile** | **پروفایل** | User Circle (`user`) | `/app/profile` | Settings, language switcher (`fa`/`en`), unit toggle (`kg`/`lbs`), privacy export. |

### 2.2 Active Workout Mode (Modal Full-Screen Canvas)
When the athlete taps "Start Workout" on `/app/today`, the application transitions into **Active Workout Mode**:
- The bottom navigation bar is hidden to prevent accidental tab navigation during exercise.
- A sticky top header displays: *Workout Title*, *Elapsed Session Timer*, and a prominent *End Workout* button.
- Floating bottom bar hosts the *Rest Timer Countdown* and *Next Set* quick-advance trigger.
- Exiting early triggers a confirmation modal: *"Save and Pause Session"* or *"Discard Workout"*.

---

## 3. Coach & Admin Desktop Navigation Model

### 3.1 Collapsible Sidebar Navigation
For coaches, gym owners, and administrators on desktop/tablet, navigation is housed in a collapsible sidebar:
- **Expanded Width:** 260px (displays icon + localized label).
- **Collapsed Width (Mini-bar):** 72px (displays centered icon with tooltip on hover/focus).
- **Logical Mirroring:** Positioned at `inline-start` (Left in English LTR; Right in Persian RTL).

### 3.2 Top Utility Bar
Persistent across all desktop screens (height: 60px):
1. **Organization Switcher (Dropdown):** Displays active gym tenant name and logo. Clicking allows switching between authorized organizations.
2. **Global Language Switcher:** One-click toggle between `فارسی (fa-IR)` and `English (en-US)`.
3. **Notification Center:** Bell icon with unread badge opening a quick flyout drawer of recent athlete completions and pain alerts.
4. **User Profile Menu:** Displays avatar, name, active role, link to account settings, and logout action.

---

## 4. Master-Detail & Dual-Pane Layouts

### 4.1 Coach Program Builder Dual-Pane Pattern
On viewports >= 1024px, the Program Builder operates as a high-velocity dual-pane interface:
- **Pane 1 (Left in LTR / Right in RTL — 35% Width):** Program Structural Outline Tree (Phases -> Weeks -> Days -> Exercise Items). Supports drag-and-drop reordering.
- **Pane 2 (65% Width):** Exercise Prescription & Target Configuration Form (Prescribed Sets, Reps, Load, Tempo, RPE/RIR, Rest, Coaching Notes, Supersets).

### 4.2 Athlete Roster & Workout Log Review Pattern
- **Pane 1 (30% Width):** Filterable Athlete Roster with adherence indicators and pain alert badges.
- **Pane 2 (70% Width):** Selected athlete's historical workout sessions, set-by-set actuals comparison, and contextual feedback messaging form.

---

## 5. Breadcrumb & Deep-Linking Routing Contract

All hierarchical screens provide accessible breadcrumb navigation at the top of the content canvas:

```
Coach: Programs > 12-Week Hypertrophy > Week 1 > Day 1: Upper Body
(فارسی): برنامه‌ها > هایپرتروفی ۱۲ هفته‌ای > هفته ۱ > روز ۱: بالاتنه
```

### URL Structure & Parameter Conventions:
- `/coach/programs/:program_id/builder?phase=1&week=1&day=1`
- `/coach/athletes/:athlete_id/logs/:session_id`
- `/app/workouts/:session_id?exercise=:exercise_id`
- `/admin/exercises/moderation?status=pending&locale=fa-IR`
