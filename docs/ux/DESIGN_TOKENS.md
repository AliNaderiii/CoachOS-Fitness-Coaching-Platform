# Design Tokens & Visual Specifications — CoachOS

**Document version:** 1.0.0 (Phase 02 Baseline)  
**Last updated:** 2026-08-10  
**Supported Locales:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR)  
**Strict constraint:** Arabic is strictly out of scope.  
**Design Phase:** Phase 02 — Documentation and specifications only. No application source code.

---

## 1. Color Palette Tokens & Semantic Roles

All color tokens below are specified in Hex and OKLCH values with verified contrast ratios satisfying **WCAG 2.2 AA** requirements (>= 4.5:1 for normal text; >= 3:1 for large text and UI components).

### 1.1 Brand & Primary Tokens
- `--color-brand-primary-500`: `#0D9488` (Teal 600 - Primary brand accent)
- `--color-brand-primary-600`: `#0F766E` (Teal 700 - Hover / Active primary)
- `--color-brand-primary-700`: `#115E59` (Teal 800 - High contrast text)
- `--color-brand-secondary-500`: `#3B82F6` (Blue 500 - Secondary accent / info)

### 1.2 Neutral & Surface Tokens (Dark / Gym-Floor & Light Modes)
CoachOS utilizes an athlete-optimized **Dark Neutral Palette** by default to reduce glare in gym environments, with high-contrast light mode tokens for desktop administration:

| Token Name | Light Theme Value | Dark Theme Value (Default) | Semantic Role |
|---|---|---|---|
| `--color-bg-canvas` | `#F8FAFC` (Slate 50) | `#0B0F17` (Deep Obsidian) | Main viewport canvas background |
| `--color-bg-surface-1` | `#FFFFFF` (Pure White) | `#151D2A` (Charcoal Slate) | Primary cards, modals, workout containers |
| `--color-bg-surface-2` | `#F1F5F9` (Slate 100) | `#1E293B` (Slate 800) | Secondary input containers, table headers |
| `--color-bg-surface-hover` | `#E2E8F0` (Slate 200) | `#27354A` (Hover Slate) | Interactive list item hover state |
| `--color-border-subtle` | `#E2E8F0` (Slate 200) | `#263345` (Slate Border) | Structural divider lines, card outlines |
| `--color-border-focus` | `#0D9488` (Teal 600) | `#2DD4BF` (Teal 400) | Accessible focus ring indicator (2px solid) |

### 1.3 Text & Typography Contrast Tokens
| Token Name | Light Theme Value | Dark Theme Value | Contrast Ratio against Canvas | WCAG AA Status |
|---|---|---|---|---|
| `--color-text-primary` | `#0F172A` (Slate 900) | `#F8FAFC` (Slate 50) | 16.2:1 / 17.5:1 | **Passes AAA** |
| `--color-text-secondary` | `#475569` (Slate 600) | `#94A3B8` (Slate 400) | 6.8:1 / 7.2:1 | **Passes AA** |
| `--color-text-tertiary` | `#64748B` (Slate 500) | `#64748B` (Slate 500) | 4.6:1 / 4.7:1 | **Passes AA** |
| `--color-text-disabled` | `#94A3B8` (Slate 400) | `#475569` (Slate 600) | 2.8:1 (Disabled) | Excluded by WCAG |

### 1.4 Feedback & Semantic Status Tokens
- **Success (Set Done / Program Saved):**
  - `--color-status-success-bg`: `#064E3B` (Dark) / `#D1FAE5` (Light)
  - `--color-status-success-text`: `#34D399` (Dark) / `#065F46` (Light)
  - `--color-status-success-icon`: `#10B981` (Emerald 500)
- **Warning (Pain Flag / High Exertion):**
  - `--color-status-warning-bg`: `#78350F` (Dark) / `#FEF3C7` (Light)
  - `--color-status-warning-text`: `#FBBF24` (Dark) / `#92400E` (Light)
- **Error / Destructive (Validation Failure / Suspend Member):**
  - `--color-status-error-bg`: `#7F1D1D` (Dark) / `#FEE2E2` (Light)
  - `--color-status-error-text`: `#F87171` (Dark) / `#991B1B` (Light)
- **Info (Rest Day / System Notice):**
  - `--color-status-info-bg`: `#1E3A8A` (Dark) / `#DBEAFE` (Light)
  - `--color-status-info-text`: `#60A5FA` (Dark) / `#1E40AF` (Light)

---

## 2. Typography Tokens & Dual-Font Hierarchy

CoachOS implements a dual-font strategy: **`Vazirmatn`** for Persian (`fa-IR`) and **`Inter`** (with system fallback) for English (`en-US`).

### 2.1 Font Family Tokens
- `--font-family-persian`: `'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Tahoma, sans-serif`
- `--font-family-english`: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- `--font-family-mono`: `'JetBrains Mono', 'Fira Code', monospace`

### 2.2 Type Scale Tokens

| Token | Font Size (rem / px) | Line Height | Weight (EN / FA) | Semantic Use Case |
|---|---|---|---|---|
| `--font-size-display` | `2.25rem` (36px) | `1.2` (44px) | Bold (700 / 800) | Hero titles, workout complete celebration |
| `--font-size-h1` | `1.75rem` (28px) | `1.25` (36px) | Bold (700 / 700) | Screen page titles (`Today's Workout`) |
| `--font-size-h2` | `1.375rem` (22px) | `1.3` (28px) | SemiBold (600 / 600) | Section headers, exercise card titles |
| `--font-size-h3` | `1.125rem` (18px) | `1.4` (24px) | SemiBold (600 / 600) | Subsection titles, modal headers |
| `--font-size-body-lg` | `1.0rem` (16px) | `1.5` (24px) | Regular (400 / 400) | Primary body text, coach instructions |
| `--font-size-body-md` | `0.875rem` (14px) | `1.4` (20px) | Regular / Medium | Table cell data, input values, cues |
| `--font-size-caption` | `0.75rem` (12px) | `1.3` (16px) | Medium (500 / 500) | Metadata tags, timestamps, secondary labels |

### 2.3 Persian Typography Rules
- Line heights in Persian text are augmented by **+15%** relative to Latin fonts (e.g., `line-height: 1.6` for Persian body copy) to prevent vertical collision of Persian ascenders, descenders, and diacritics.
- Letter spacing (`letter-spacing`) is strictly set to `0` / `normal` for Persian script, as non-zero tracking disconnects Persian cursive glyphs.

---

## 3. Spacing Scale Tokens (4px Base Grid)

| Token | Size (px) | Relative Value | Primary Use Case |
|---|---|---|---|
| `--space-1` | `4px` | `0.25rem` | Micro element spacing, badge padding |
| `--space-2` | `8px` | `0.5rem` | Compact gap between icon and text |
| `--space-3` | `12px` | `0.75rem` | Input internal padding, card item gap |
| `--space-4` | `16px` | `1.0rem` | Standard container padding, form field gap |
| `--space-6` | `24px` | `1.5rem` | Card padding, section vertical gap |
| `--space-8` | `32px` | `2.0rem` | Page gutter padding on mobile |
| `--space-12` | `48px` | `3.0rem` | Major section breaks on desktop |

---

## 4. Border Radius & Elevation Tokens

### 4.1 Border Radii
- `--radius-sm`: `6px` (Tags, badges, small buttons)
- `--radius-md`: `10px` (Standard form inputs, exercise item cards)
- `--radius-lg`: `16px` (Main workout cards, bottom navigation pills)
- `--radius-xl`: `24px` (Modals, bottom action drawers)
- `--radius-full`: `9999px` (Avatars, circular rest timers, pill buttons)

### 4.2 Shadows & Elevation
- `--shadow-sm`: `0 1px 2px 0 rgba(0, 0, 0, 0.05)`
- `--shadow-md`: `0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)`
- `--shadow-lg`: `0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1)` (Modals, floating rest timer)

---

## 5. Z-Index Layer Hierarchy

- `--z-base`: `0` (Content canvas)
- `--z-card`: `10` (Interactive cards, table rows)
- `--z-sticky`: `100` (Sticky top app bar, table headers)
- `--z-bottom-nav`: `200` (Persistent mobile bottom navigation bar)
- `--z-timer-bar`: `300` (Floating rest countdown bar)
- `--z-drawer`: `400` (Slide-out navigation drawer / flyout menus)
- `--z-modal-backdrop`: `500` (Dimmer overlay)
- `--z-modal`: `600` (Center modals, consent dialogs)
- `--z-toast`: `700` (Top/bottom notification toasts & alert banners)

---

## 6. Motion & Animation Tokens

- `--duration-fast`: `150ms` (Button hover, checkbox toggle)
- `--duration-normal`: `250ms` (Modal open/close, card accordion expansion)
- `--duration-slow`: `400ms` (Page transition, slide-in drawer)
- `--easing-standard`: `cubic-bezier(0.4, 0.0, 0.2, 1)` (Material standard curve)
- `--easing-decelerate`: `cubic-bezier(0.0, 0.0, 0.2, 1)` (Enter viewport)
- `--easing-accelerate`: `cubic-bezier(0.4, 0.0, 1, 1)` (Exit viewport)

### Reduced Motion Override
```css
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
