# Responsive Behavior & Touch Ergonomics Specification — CoachOS

**Document version:** 1.0.0 (Phase 02 Baseline)  
**Last updated:** 2026-08-10  
**Supported Locales:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR)  
**Strict constraint:** Arabic is strictly out of scope.  
**Design Phase:** Phase 02 — Documentation and specifications only. No application source code.

---

## 1. Responsive Breakpoint Taxonomy

CoachOS targets a fluid, device-agnostic responsive layout system governed by 6 standardized breakpoints:

| Breakpoint Name | Viewport Range (px) | Primary Target Devices | Primary User Role & Activity |
|---|---|---|---|
| **Small Mobile (`xs`)** | `< 375px` | iPhone SE, compact budget Androids | Athlete gym-floor workout execution |
| **Standard Mobile (`sm`)** | `375px – 639px` | iPhone 14/15/16, Galaxy S23/S24 | Athlete primary PWA & Coach quick check-in |
| **Tablet Portrait (`md`)** | `640px – 767px` | iPad Mini, small Android tablets | Coach on-the-floor athlete review |
| **Tablet Landscape (`lg`)** | `768px – 1023px` | iPad 10.2", iPad Air, Surface Go | Coach program building & Owner oversight |
| **Desktop (`xl`)** | `1024px – 1279px` | Laptops, MacBooks (13"/14") | Coach multi-week builder & Admin console |
| **Wide Desktop (`2xl`)** | `>= 1280px` | Desktop monitors (24"+), iMacs | High-density program periodization & analytics |

---

## 2. One-Handed Mobile Gym Ergonomics & Thumb Zone Analysis

During active workout execution, athletes typically operate smartphones with **one hand** while resting between heavy sets. All critical interactive targets are mapped to the **Natural Thumb Zone** (bottom 40% of the mobile screen):

```
┌─────────────────────────────────────────────────────────┐
│ HARD-TO-REACH ZONE (Top 25%)                            │
│ • Workout title, session elapsed timer, information icon │
├─────────────────────────────────────────────────────────┤
│ NEUTRAL ZONE (Middle 35%)                               │
│ • Exercise instructional video preview & coaching cues  │
│ • Prescribed targets & historical logs display          │
├─────────────────────────────────────────────────────────┤
│ NATURAL THUMB ZONE (Bottom 40%)                         │
│ • Weight & Rep numerical keypad input triggers          │
│ • Primary Set Completion Checkmark (48x48px hit area)   │
│ • Floating Rest Timer (+30s / Skip triggers)            │
│ • Exercise substitution & discomfort flag triggers      │
└─────────────────────────────────────────────────────────┘
```

### Key Mobile Ergonomic Rules:
1. **Minimum Touch Target Dimensions:** Every interactive button, input field, and navigation tab possesses a minimum touch dimension of **44x44 CSS pixels** (target **48x48px** for set checkmarks).
2. **Hit Area Margin Isolation:** Minimum 8px touch clearance between adjacent clickable elements to eliminate accidental taps with sweaty gym fingers.
3. **No Double-Tap Gestures:** All interactions execute on single tap. Swipe gestures are optional progressive enhancements with visible button alternatives.

---

## 3. Component Responsive Transformations

### 3.1 Coach Program Builder
- **Desktop (>= 1024px):** Dual-pane master-detail view. Left pane (35% width) renders the sticky Program Outline Tree; right pane (65% width) renders the Exercise Prescription Form.
- **Tablet / Mobile (< 1024px):** Transforms into a single-column accordion stack. Tapping a workout day in the tree expands the exercise prescription form full-width with a sticky back-to-tree button.

### 3.2 Data Tables & Roster Lists
- **Desktop (>= 768px):** Traditional multi-column tabular data grids with sortable column headers, checkbox selections, and right-aligned action menus.
- **Mobile (< 768px):** Automatically reflows into **Stacked Athlete Cards** displaying member avatar, name, adherence badge, and 1-tap quick action buttons.

### 3.3 Modal Dialogs vs Bottom Drawers
- **Desktop (>= 768px):** Centered floating modals (max-width: 560px) with backdrop blur.
- **Mobile (< 768px):** Transforms into an accessible **Bottom Sheet / Drawer** sliding up from the bottom edge, anchored within natural thumb reach.
