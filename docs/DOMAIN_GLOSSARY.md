# Domain Glossary — CoachOS

**Document version:** 1.0.0 (Phase 01 Baseline)  
**Last updated:** 2026-08-10  
**Languages covered:** English (`en-US`), Persian (`fa-IR`)  
**Note:** Arabic is strictly out of scope.

This document establishes the canonical terminology and conceptual definitions for the CoachOS Fitness Coaching Platform. All product requirements, user stories, domain models, database schemas, API fields, and UI localization strings must adhere to these definitions.

---

## 1. Fitness, Exercise, and Training Programming Domain

| English Term | Persian Equivalent (`fa-IR`) | Definition & Domain Rules |
|--------------|------------------------------|---------------------------|
| **Exercise** | حرکت تمرینی / تمرین | A distinct physical movement pattern or activity with instructions, target muscles, equipment requirements, and instructional media. |
| **Exercise Alias** | نام مستعار حرکت | An alternative name or common colloquial variant for an exercise in English or Persian (e.g., "Lat Pulldown" vs "زیربغل سیم‌کش دست باز"). Used for search indexing and normalization. |
| **Movement Pattern** | الگوی حرکتی | Fundamental biomechanical classification (e.g., Squat, Hinge, Horizontal Push, Horizontal Pull, Vertical Push, Vertical Pull, Lunge, Carry, Rotation, Isolation). |
| **Muscle Group** | گروه عضلانی | Target anatomical grouping (e.g., Quadriceps / چهارسر ران, Hamstrings / همسترینگ, Latissimus Dorsi / زیربغل, Pectoralis / سینه, Deltoids / سرشانه). |
| **Training Program** | برنامه تمرینی | A structured multi-week or multi-phase regimen designed to achieve a specific athletic or fitness goal. |
| **Program Phase** | فاز تمرینی / دوره | A distinct macro/mesocycle period within a program (e.g., Hypertrophy Phase / فاز هایپرتروفی, Strength Phase / فاز قدرت, Deload Week / هفته تخلیه بار). |
| **Program Week** | هفته تمرینی | A microcycle unit containing scheduled training days. |
| **Program Day** | روز تمرینی | A container for scheduled workouts within a week (e.g., Day 1: Upper Body Power / روز ۱: بالاتنه قدرتی). |
| **Workout** | جلسه تمرینی | A single training session consisting of warm-up, main workout items, and cool-down segments. |
| **Workout Item / Prescription** | تجویز تمرینی / آیتم تمرین | The coach's prescribed instruction for a specific exercise in a workout, including sets, reps, load, RPE, tempo, rest, and coaching cues. |
| **Set** | ست / نوبت | A single bout of continuous exercise repetitions or duration. |
| **Repetitions (Reps)** | تکرار | The count of completed movement cycles within a set. |
| **Load / Weight** | وزنه / بار تمرینی | The mass lifted or resistance applied, specified in kilograms (`kg`) or pounds (`lbs`). Stored with unit metadata. |
| **Rate of Perceived Exertion (RPE)** | شاخص درک سختی (RPE) | A subjective 1–10 scale (or Borg scale) measuring exercise intensity, where 10 represents maximum possible exertion. |
| **Reps in Reserve (RIR)** | تکرار ذخیره (RIR) | The estimated number of additional repetitions an athlete could complete before momentary muscular failure (e.g., RIR 2 = 2 reps left). |
| **Tempo** | تمپو / آهنگ حرکت | A 4-digit notation representing the eccentric, bottom isometric, concentric, and top isometric duration in seconds (e.g., `3-1-1-0`). |
| **Rest Interval** | زمان استراحت | Prescribed duration (in seconds) between sets or exercises. |
| **Superset / Circuit / Group** | سوپرست / مدار تمرینی | Grouping of two or more exercises performed sequentially with minimal rest between them before repeating. |
| **One-Repetition Maximum (1RM)** | یک تکرار بیشینه (1RM) | The maximum load an athlete can lift for a single repetition with proper form. |
| **Template** | الگوی برنامه / تمپلیت | A reusable, unassigned program blueprint that can be cloned and customized for multiple athletes. |
| **Program Assignment** | انتساب برنامه | The formal binding of a program version to a specific athlete with explicit start and end dates. Creates an immutable snapshot. |
| **Program Version / Snapshot** | نسخه / تصویر لحظه‌ای برنامه | A point-in-time immutable copy of a program assigned to an athlete, ensuring future edits to the master template do not inadvertently alter active athlete training logs. |
| **Today's Workout** | تمرین امروز | The athlete's daily execution dashboard presenting the scheduled workout for the current date. |
| **Workout Session / Execution** | اجرای جلسه تمرینی | The athlete's active or completed performance record of a workout. |
| **Set Log (Actuals)** | ثبت ست / مقادیر واقعی | The athlete's recorded actuals (actual reps, actual load, actual RPE, completion status, notes) compared against prescribed targets. |
| **Workout Status** | وضعیت تمرین | Lifecycle state of a session: `Scheduled`, `In Progress`, `Completed`, `Skipped`, `Modified`. |
| **Modification Reason** | دلیل تغییر / علت جابجایی | Required structured reason when an athlete modifies or skips a prescribed exercise (e.g., Equipment Unavailable, Joint Pain, Time Constraint). |
| **Adherence Rate** | نرخ پایبندی / درصد تعهد | Percentage of prescribed workouts and sets completed within a scheduled cycle. |
| **Feedback Flag / Pain Flag** | پرچم بازخورد / گزارش درد | High-visibility indicator submitted by an athlete during logging to alert the coach to acute pain, discomfort, or excessive fatigue. |
| **Body Metric** | شاخص‌های بدنی | Quantitative physiological measurement (e.g., Body Weight, Body Fat %, Waist Circumference). |
| **Progress Photo** | عکس پیشرفت | Visual record of physical conditioning uploaded by athlete under strict privacy controls and explicit consent. |

---

## 2. Organization, Tenancy, and Identity Domain

| English Term | Persian Equivalent (`fa-IR`) | Definition & Domain Rules |
|--------------|------------------------------|---------------------------|
| **Tenant** | مستأجر / سازمان مستقل | An isolated customer boundary in the multi-tenant system representing an independent gym, coaching business, or sports organization. |
| **Organization** | سازمان / باشگاه | The top-level legal or business entity owning athletes, coaches, templates, and operational data. |
| **Primary Location** | شعبه اصلی / مکان | The physical facility or primary operating branch associated with an organization in MVP (single-location MVP). |
| **User** | کاربر | A global authentication identity identified by email, having credentials, locale preferences, and profile data. |
| **Membership** | عضویت در سازمان | The scoped relationship linking a User to an Organization with a specific Role and status (`Active`, `Invited`, `Suspended`). |
| **Platform Administrator** | مدیر کل پلتفرم | System-wide super-administrator responsible for exercise catalog moderation, security oversight, tenant management, and platform health. |
| **Organization Owner** | مالک سازمان / مدیر باشگاه | The primary administrative user of an organization with billing authority, coach onboarding, and tenant-wide visibility. |
| **Coach / Trainer** | مربی | A fitness professional within an organization who designs programs, assigns workouts, reviews logs, and communicates with assigned athletes. |
| **Athlete / Client** | ورزشکار / شاگرد | An individual client receiving coaching, viewing prescribed workouts, logging sessions, and sharing progress. Free/included account model. |
| **Nutrition Professional (P1)** | کارشناس تغذیه (P1) | A certified nutrition specialist who creates meal plans and tracks dietary adherence under explicit athlete consent. |
| **Support / Read-Only Staff** | کارشناس پشتیبانی / مشاهده‌گر | An organizational or platform role with read-only access for operational troubleshooting, audit inspection, or administrative assistance. |
| **Invitation** | دعوت‌نامه | A cryptographically secure, time-limited, single-use token sent via email to invite a new or existing user into an organization with a predefined role. |
| **Coach-Athlete Assignment** | انتساب مربی به شاگرد | An explicit authorization record binding an athlete to a specific coach within an organization. Governs object-level access control. |
| **Role-Based Access Control (RBAC)** | کنترل دسترسی مبتنی بر نقش | Authorization mechanism granting capabilities based on organization-level membership roles. |
| **Object-Level Authorization** | کنترل دسترسی در سطح شیء | Fine-grained server-side authorization ensuring a coach can only access athletes, workouts, and media assigned to them. |
| **Multi-Tenancy Isolation** | ایزولاسیون چندمستأجری | Architectural enforcement ensuring no organization can query, view, or mutate data belonging to another organization. |

---

## 3. Localization and Internationalization (`i18n` & `l10n`) Domain

| English Term | Persian Equivalent (`fa-IR`) | Definition & Domain Rules |
|--------------|------------------------------|---------------------------|
| **Locale** | زبان و منطقه | The active language and regional formatting context: `fa-IR` (Persian / Iran) or `en-US` (English / United States). |
| **RTL (Right-to-Left)** | راست‌به‌چپ | The bidirectional layout direction applied for Persian text, UI components, navigation, and input controls. |
| **LTR (Left-to-Right)** | چپ‌به‌راست | The bidirectional layout direction applied for English text, UI components, and navigation. |
| **Logical CSS Properties** | ویژگی‌های منطقی CSS | Layout rules (e.g., `margin-inline-start`, `padding-inline-end`, `inset-inline-start`) that adapt automatically to RTL/LTR without hardcoded left/right values. |
| **Persian Normalization** | استانداردسازی نویسه‌های فارسی | Algorithmic Unicode normalization — Perso-Arabic script keyboard-variant normalization for Persian search — folding Perso-Arabic character variants (e.g., Arabic Yeh `ي` / `ى` → Persian `ی` (U+06CC), Arabic Kaf `ك` → Persian `ک` (U+06A9), Arabic-Indic digits `٠-٩` → Persian `۰-۹` or Latin `0-9`) to ensure reliable search matching. No Arabic localization or Arabic product support implied; normalization handles keyboard-variant input only. |
| **Bidirectional Text (BiDi)** | متن دوجهته | Mixed-direction content within a single string (e.g., English exercise names, weights, email addresses inside a Persian sentence) requiring proper Unicode BiDi isolation. |
| **Jalali / Solar Hijri Calendar** | تقویم هجری شمسی (جلالی) | The civil solar calendar used in Iran. Evaluated for UI display while preserving UTC/Gregorian timestamps in backend persistence. |
| **Gregorian Calendar** | تقویم میلادی | The international calendar used for all internal database storage, API timestamps (ISO 8601 UTC), and `en-US` UI display. |

---

## 4. Privacy, Security, and Compliance Domain

| English Term | Persian Equivalent (`fa-IR`) | Definition & Domain Rules |
|--------------|------------------------------|---------------------------|
| **Personally Identifiable Information (PII)** | اطلاعات هویتی شخصی | Data that can directly or indirectly identify an individual (e.g., Name, Email, Phone Number). |
| **Sensitive Health Data** | داده‌های حساس سلامت | Health-adjacent information (e.g., Body weight, Body fat %, Injuries, Pain flags, Check-in notes, Progress photos) requiring strict confidentiality and auditability. |
| **Data Minimization** | کمینه‌سازی داده‌ها | The principle of collecting and retaining only the minimum data strictly necessary to deliver coaching features. |
| **Purpose Limitation** | محدودیت هدف پردازش | Restricting the use of athlete data strictly to fitness coaching and authorized progress tracking. |
| **Consent Hook** | قلاب رضایت کاربر | An explicit UI and cryptographic record of user consent prior to collecting, sharing, or processing sensitive data (e.g., Progress photo sharing, Multi-pro access). |
| **Signed URL** | آدرس امضاشده امن | A time-limited, cryptographically signed URL providing controlled, authenticated access to private media in object storage without exposing public buckets. |
| **Media Provenance & Rights Metadata** | اصالت و فراداده حقوق رسانه | Mandatory structured metadata on all catalog media recording source URL, copyright license, creator attribution, and platform moderation approval. |
| **Audit Event** | رویداد بازرسی / گزارش امنیتی | An immutable structured log entry recording the actor, action, target entity, timestamp, IP hash, and outcome for all security- and authorization-sensitive operations. |
| **Data Portability / Export** | قابلیت انتقال و خروجی داده | The athlete's right to export all personal profile, workout history, and progress logs in a standardized, machine-readable format (e.g., JSON or CSV archive). |
| **Right to Erasure (Forget Me)** | حق فراموشی و حذف حساب | The workflow allowing an athlete to request permanent deletion or anonymization of their account and sensitive health data, subject to legal audit retention holds. |
