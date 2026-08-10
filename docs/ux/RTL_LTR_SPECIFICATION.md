# Bidirectional (RTL / LTR) Layout Specification — CoachOS

**Document version:** 1.0.0 (Phase 02 Baseline)  
**Last updated:** 2026-08-10  
**Supported Locales:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR)  
**Strict constraint:** Arabic is strictly out of scope.  
**Design Phase:** Phase 02 — Documentation and specifications only. No application source code.

---

## 1. Bidirectional Engineering Principles

CoachOS enforces genuine bidirectional symmetry between Persian (`fa-IR`) and English (`en-US`):

1. **CSS Logical Properties First:** All layout dimensions, paddings, margins, positioning, and borders must be authored exclusively using CSS Logical Properties (`margin-inline-start`, `padding-inline-end`, `inset-inline-start`, `border-inline-start`, `text-align: start`). Physical properties (`left`, `right`, `margin-left`, `float: left`) are strictly prohibited in the design system.
2. **Context-Aware Semantic Icon Flipping:** Directional navigation icons (e.g., Chevron Left/Right, Back/Forward arrows, Breadcrumb separators) must automatically flip orientation when switching direction. Physical icons (e.g., Barbell, Dumbbell, Stopwatch timer, Camera, Checkmark) remain unflipped.
3. **Robust BiDi Isolation for Mixed Content:** Strings containing Latin exercise names (e.g., *"حرکت Barbell Bench Press با ۳ ست"*), email addresses, URLs, and numeric unit codes inside Persian sentences must be wrapped in `<bdi>` elements or CSS `unicode-bidi: isolate` to prevent punctuation distortion.
4. **Persian vs Arabic Linguistic Distinction:** While Persian and Arabic share the Perso-Arabic script family, CoachOS is specialized strictly for Persian:
   - Specific Persian letterforms (`پ`, `چ`, `ژ`, `گ`).
   - Standard Persian Yeh (`ی`, `\u06CC`) rather than Arabic Yeh (`ي`, `\u064A` or `ى`, `\u0649`).
   - Standard Persian Kaf (`ک`, `\u06A9`) rather than Arabic Kaf (`ك`, `\u0643`).
   - Persian typography font stack (`Vazirmatn`).
   - Zero Arabic translations, Arabic locale files, or Arabic-specific resources.

---

## 2. Logical CSS Property Mapping Matrix

| Physical Legacy CSS | CSS Logical Property Equivalent | English LTR Physical Resolved | Persian RTL Physical Resolved |
|---|---|---|---|
| `left: 0` | `inset-inline-start: 0` | Left: `0` | Right: `0` |
| `right: 0` | `inset-inline-end: 0` | Right: `0` | Left: `0` |
| `margin-left: 16px` | `margin-inline-start: 16px` | Margin Left: `16px` | Margin Right: `16px` |
| `margin-right: 16px` | `margin-inline-end: 16px` | Margin Right: `16px` | Margin Left: `16px` |
| `padding-left: 12px` | `padding-inline-start: 12px` | Padding Left: `12px` | Padding Right: `12px` |
| `padding-right: 12px` | `padding-inline-end: 12px` | Padding Right: `12px` | Padding Left: `12px` |
| `border-left: 2px solid` | `border-inline-start: 2px solid` | Border Left: `2px` | Border Right: `2px` |
| `text-align: left` | `text-align: start` | Left aligned | Right aligned |
| `text-align: right` | `text-align: end` | Right aligned | Left aligned |
| `border-top-left-radius: 8px` | `border-start-start-radius: 8px` | Top-Left radius | Top-Right radius |

---

## 3. Directional Component Mirroring Specifications

### 3.1 Desktop Sidebar & Navigation Drawer
- **English LTR:** Docked at the left edge (`inset-inline-start: 0`). Slide-in transition enters from left to right.
- **Persian RTL:** Docked at the right edge (`inset-inline-start: 0`). Slide-in transition enters from right to left.

### 3.2 Breadcrumb Trails & Stepper Indicators
- **English LTR:** `Programs > 8-Week Hypertrophy > Week 1` (Traverses Left-to-Right; chevron points Right `>`).
- **Persian RTL:** `برنامه‌ها > فاز هایپرتروفی ۸ هفته‌ای > هفته ۱` (Traverses Right-to-Left; chevron points Left `<`).

### 3.3 Program Builder Tree Hierarchy
- **English LTR:** Root Phase nodes dock at left; child Weeks and Workout Items indent to the right (`padding-inline-start: 24px`). Expand/collapse chevron points Right when closed, Down when open.
- **Persian RTL:** Root Phase nodes dock at right; child Weeks and Workout Items indent to the left (`padding-inline-start: 24px`). Expand/collapse chevron points Left when closed, Down when open.

### 3.4 Data Tables & Set Logging Grids
- **English LTR:** Columns order Left-to-Right: `[Set Index] | [Prescribed Targets] | [Load (kg)] | [Reps] | [Status Action]`.
- **Persian RTL:** Columns order Right-to-Left: `[شماره ست] | [هدف تجویز مربی] | [وزن (کیلو)] | [تکرار] | [وضعیت ست]`. All table headers align to `text-align: start` (Right in Persian).

### 3.5 Floating Rest Countdown Timer
- **English LTR:** Timer countdown ring fills clockwise; action buttons (`+30s`, `Skip`) dock to the right (`inline-end`).
- **Persian RTL:** Timer countdown ring fills clockwise; action buttons (`+30s`, `Skip`) dock to the left (`inline-end`). Remaining time text uses Persian numerals (`۰۱:۳۰`).

---

## 4. Mixed-Direction (BiDi) Content & Text Normalization Rules

### 4.1 Latin Terms Embedded in Persian Text
Fitness terminology frequently includes English exercise names or equipment codes inside Persian sentences. Without isolation, trailing periods, exclamation marks, or parentheses will jump to the wrong side of the sentence:

```html
<!-- INCORRECT: Punctuation error -->
<p>حرکت Barbell Bench Press را با ۳ ست انجام دهید.</p>

<!-- CORRECT: Isolated via <bdi> -->
<p>حرکت <bdi lang="en" dir="ltr">Barbell Bench Press</bdi> را با ۳ ست انجام دهید.</p>
```

### 4.2 Zero-Width Non-Joiner (ZWNJ / نیم‌فاصله) Handling
Persian compound words and verbal prefixes require Zero-Width Non-Joiners (`\u200C`) for correct orthography:
- Correct: `می‌خواهم` (with ZWNJ) vs Incorrect: `می خواهم` (unconnected space) or `میخواهم` (improperly joined).
- Correct: `دست‌گاه` vs Incorrect: `دستگاه`.
- The search indexing pipeline folds ZWNJ characters to standard whitespace during tokenization, ensuring queries with or without ZWNJ return identical results.

### 4.3 Persian Number Formatting & Units
- In `fa-IR` mode, all numbers format using standard Persian numerals: `۰, ۱, ۲, ۳, ۴, ۵, ۶, ۷, ۸, ۹` via `Intl.NumberFormat('fa-IR')`.
- Weight units format as `کیلوگرم` (kg) or `پوند` (lbs).
- Duration formats as `۵۵ دقیقه` (55 min) or `۱:۳۰ ثانیه`.
