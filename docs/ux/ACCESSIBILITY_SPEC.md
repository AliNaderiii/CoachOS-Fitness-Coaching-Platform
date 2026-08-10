# Accessibility Specification (WCAG 2.2 AA) — CoachOS

**Document version:** 1.0.0 (Phase 02 Baseline)  
**Last updated:** 2026-08-10  
**Compliance Target:** Web Content Accessibility Guidelines (WCAG) 2.2 Level AA  
**Supported Locales:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR)  
**Design Phase:** Phase 02 — Documentation and specifications only. No application source code.

---

## 1. Core Accessibility Standards & Compliance Targets

CoachOS is designed to guarantee equal access for athletes, coaches, and administrators regardless of motor, visual, auditory, or cognitive capabilities.

### 1.1 Non-Negotiable Accessibility Rules
1. **Perceivable:**
   - Text contrast ratio >= **4.5:1** for standard text (< 18pt) and >= **3:1** for large text (>= 18pt bold or >= 24pt regular) against its background.
   - UI controls, active borders, and focus rings possess >= **3:1** contrast against adjacent surfaces.
   - Information conveyed by color (e.g., Set Completed = Green, Pain Flag = Amber) must always be accompanied by redundant text labels and distinct semantic icons.
2. **Operable:**
   - 100% of interactive elements are reachable and operable via keyboard alone (`Tab`, `Shift+Tab`, `Enter`, `Space`, `Arrow Keys`, `Escape`).
   - Focus outline is prominently visible across all interactive components (2px solid `--color-border-focus` with 2px offset).
   - Touch targets have a minimum dimension of **44x44 CSS pixels**.
3. **Understandable:**
   - HTML document tag explicitly sets `lang` (`fa-IR` or `en-US`) and `dir` (`rtl` or `ltr`) attributes.
   - Form inputs provide persistent, visible `<label>` elements linked via `id` and `for` attributes; validation errors are announced to screen readers.
4. **Robust:**
   - Proper semantic HTML5 landmark tags (`<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>`) and ARIA 1.2 roles.

---

## 2. Component Accessibility Behaviors

### 2.1 Modal & Drawer Focus Trapping
- When a modal or bottom drawer opens, keyboard focus immediately moves to the first interactive element or dialog title (`role="dialog"` and `aria-modal="true"`).
- Tab navigation cycles strictly within the modal container.
- Pressing `Escape` closes the modal and returns focus to the trigger element that initiated it.

### 2.2 Accessible Rest Countdown Timer
- The rest countdown timer utilizes ARIA live regions:
  ```html
  <div role="status" aria-live="polite" class="sr-only">
    Rest timer: 30 seconds remaining
  </div>
  ```
- Timer completion announces *"Rest period complete — ready for next set"* and triggers haptic vibration where supported.

### 2.3 Form Validation & Screen-Reader Error Announcements
- Field-level error messages link to inputs via `aria-describedby="input-error-id"`.
- Erroneous fields set `aria-invalid="true"`.
- Form submission errors summarize at the top of the form in an `aria-live="assertive"` alert container.

---

## 3. WCAG 2.2 AA Verification Test Checklist

| Flow / Feature Area | Specific Accessibility Test Verification Criteria | WCAG Criteria | Target Phase |
|---|---|---|---|
| **User Registration & Login** | Inputs have visible labels; error messages announced; tab order logical; contrast >= 4.5:1. | 1.3.1, 1.4.3, 2.1.1, 3.3.2 | Phase 05 / 13 |
| **Language Switcher** | Dynamic switch updates `lang` and `dir` on `<html>`; screen reader announces new language in native pronunciation. | 3.1.1, 3.1.2 | Phase 04 / 13 |
| **Athlete Today View** | Exercise cards have semantic headings (`<h2>`); CTA button has 48x48px hit area; video clips provide text coaching cues. | 1.3.1, 1.4.3, 2.5.5, 1.2.2 | Phase 07 / 13 |
| **Live Set Logging** | Numeric inputs operable via keyboard; checkmark button announces *"Set 1 marked complete, 80 kilograms, 8 reps"*. | 2.1.1, 4.1.2, 4.1.3 | Phase 07 / 13 |
| **Rest Timer** | Visual ring accompanied by numeric text; countdown does not flood screen readers; completion announced via polite live region. | 1.4.3, 4.1.3, 2.2.1 | Phase 07 / 13 |
| **Program Builder** | Tree navigation operable via arrow keys; drag-and-drop has keyboard alternative (move up/down buttons); modal focus trapped. | 2.1.1, 2.4.3, 2.4.7, 4.1.2 | Phase 06 / 13 |
| **Pain Flag Submission** | Anatomical areas selectable by radio group / buttons; severity scale clearly labeled; advice notice readable. | 1.3.1, 3.3.2, 4.1.2 | Phase 07 / 13 |
| **Contextual Messages** | Messages thread organized in semantic list; incoming messages announced via polite live region; message timestamp accessible. | 1.3.1, 4.1.3 | Phase 08 / 13 |
| **Permission Denied / 403** | Error screen explains refusal clearly without jargon; provides return action button; focus moves to error heading. | 2.4.2, 3.3.1 | Phase 05 / 13 |
| **Reduced Motion** | Disables all non-essential scale, slide, and pulse animations when `prefers-reduced-motion: reduce` is active. | 2.3.3 | Phase 04 / 13 |
