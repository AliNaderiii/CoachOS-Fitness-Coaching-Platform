# Master Product Brief — CoachOS

**Document owner:** Product Strategist / Founding PM  
**Status:** Active (Phase 00 baseline)  
**Last updated:** 2026-08-10  
**Languages in product:** Persian (`fa-IR`, RTL), English (`en-US`, LTR)  
**Explicitly out of scope:** Arabic and all other locales until founder request  

---

## 1. Working identity

| Field | Value |
|-------|--------|
| Working codename | CoachOS |
| Final product name | TBD |
| Repository | AliNaderiii/CoachOS-Fitness-Coaching-Platform |
| License | MIT |
| Business model | B2B2C SaaS (coaches/gyms pay; athletes included) |
| Primary markets (initial hypothesis) | Iran-capable Persian UX + English international UX |

## 2. Problem

Fitness coaches and small gyms juggle programming, athlete adherence, messaging, progress photos, and admin work across WhatsApp, spreadsheets, and generic notes apps. Athletes lose clarity on “what do I train today?” and coaches lack structured adherence and history. Existing tools often fail Persian RTL quality, local content, low-bandwidth use, and coach business workflows.

## 3. Solution

A bilingual coaching operating system that:

1. Lets coaches build and assign structured training programs  
2. Lets athletes execute and log workouts on a mobile-first PWA  
3. Keeps communication and progress tied to the training context  
4. Gives gyms multi-coach tenancy and admin controls  
5. Evolves toward nutrition collaboration, monetization, and safe AI copilots — without blocking architecture  

## 4. Target users (summary)

| Role | Pays? | Primary jobs-to-be-done |
|------|-------|-------------------------|
| Platform Administrator | Internal | Moderate content, manage platform, support |
| Organization / Gym Owner | Yes | Manage locations, coaches, branding, membership |
| Location Manager | Optional seat | Day-to-day facility operations (post-MVP depth) |
| Coach / Trainer | Yes (or via org) | Program, assign, review logs, message athletes |
| Nutrition Professional | Later (P1) | Meal plans, macros, collab on athlete profile |
| Athlete / Client | No (included) | Train today, log, message coach, see progress |
| Support staff | Internal/org | Read-only assistance |

**MVP launch roles:** Platform Admin, Org Owner, Coach, Athlete.  
**Data model must allow** an athlete to be assigned to more than one professional later.

## 5. Value propositions

### For coaches / gyms

- Faster programming with reusable templates and exercise library  
- Adherence visibility and structured feedback  
- Professional boundary: org tenancy, roles, audit  
- Path to packages, payments, and storefront (later)  

### For athletes

- Clear “today’s workout”  
- Simple logging with coaching cues and media  
- Progress history in one place  
- Persian-first quality where needed  

### For the platform

- Expandable modular monolith  
- API-first for future native apps and integrations  
- Differentiated i18n (fa/en) and privacy posture  

## 6. Product principles

1. Smallest valuable product first  
2. Modular monolith for MVP  
3. API-first  
4. Athlete mobile-first; coach desktop/tablet capable  
5. Every feature: owner, permissions, AC, tests, docs  
6. AI is copilot + human review — not medical authority  
7. No diagnosis, treatment, drug, or medical claims  
8. Privacy and data ownership are features  
9. No unlicensed third-party media/content  
10. Never hide incomplete work  
11. Never commit secrets or real health PII  
12. Every phase ends with a verifiable report  

## 7. Scope boundaries

### P0 — MVP Core (build first)

- Identity, tenancy, invitations, RBAC + object-level auth  
- fa-IR / en-US with true RTL/LTR  
- Exercise library (canonical + coach-private), search, media rights metadata  
- Programs, phases/weeks/days, prescriptions, templates, assign, version  
- Athlete today/calendar, log sets, adherence, feedback flags  
- Messaging + in-app notifications + preferences  
- Admin moderation, audit events, basic usage/adherence analytics  
- Export/deletion **workflow design**; consent hooks  

### P1 — Professional coaching and nutrition (backlog)

- Nutrition professional role, multi-pro consent  
- Meal plans, foods/recipes, macros, Persian foods strategy  
- Habits, check-ins, scheduling  
- Packages, payment adapter, coach storefront, branded portal  

### P2 — Advanced (backlog)

- Marketplace, reviews, disputes  
- Wearables / Health Connect (policy review)  
- AI copilot features with full safety controls  
- White-label native apps, multi-currency  

### Explicit non-goals (now)

- Arabic language/locale  
- Autonomous AI programming without coach review  
- Medical diagnosis or rehab clinical claims  
- Copying proprietary exercise video libraries  
- Microservices split without ADR  

## 8. Localization requirements

- All UI strings from localization resources  
- CSS logical properties; true RTL layouts  
- Persian typography and font strategy  
- Persian and Latin digits handling  
- Date/time/number/weight/height/currency formatting per locale  
- Mixed-direction text (exercise names, emails, URLs, numbers)  
- Persian search normalization (character variant folding)  
- Test critical screens in both locales  

**Arabic:** out of scope. Architecture may use standard i18n frameworks that *could* add locales later, but no Arabic resources are created.

## 9. Monetization (hypothesis)

| Stage | Model |
|-------|--------|
| MVP | Org/coach subscription tiers (pricing TBD) |
| P1 | Seat-based + package sales to athletes via coach |
| P2 | Marketplace take-rate + premium AI add-on |

Athletes are not the primary payer in MVP.

## 10. Success metrics (draft — refine in Phase 01/14)

- Time for coach to assign first program < 15 minutes (pilot)  
- Athlete 7-day workout open rate / completion rate  
- Weekly active coaches and athletes (WAU)  
- Invitation → activated athlete conversion  
- Support tickets related to RTL/i18n (should trend to zero)  
- Zero critical authZ bugs in pilot  

## 11. Risks (product)

See `PROJECT_STATUS.md` §7. Highest product risks: content rights, regulatory posture for health data, payment geography, offline complexity.

## 12. Open product decisions (for Phase 01+)

1. Email-only auth vs phone OTP for MVP  
2. Jalali calendar first-class vs Gregorian with fa locale formatting  
3. Single-location MVP vs multi-location from day one  
4. Group assignment depth in MVP  
5. Progress photo storage and consent UX detail  
6. Pricing tiers and trial length  

Defaults will be recorded in `docs/DECISIONS.md` when chosen.

## 13. Related documents

- `docs/PRD.md`  
- `docs/RELEASE_PLAN.md`  
- `docs/SECURITY_AND_PRIVACY.md`  
- `docs/DECISIONS.md`  
- `docs/reports/PHASE-00-DISCOVERY-REPORT.md`  
