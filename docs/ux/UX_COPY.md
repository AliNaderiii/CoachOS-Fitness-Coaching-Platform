# UX Copy Guidelines & Microcopy Repository — CoachOS

**Document version:** 1.0.0 (Phase 02 Baseline)  
**Last updated:** 2026-08-10  
**Supported Locales:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR)  
**Strict constraint:** Arabic is strictly out of scope.  
**Design Phase:** Phase 02 — Documentation and specifications only. No application source code.

---

## 1. Tone of Voice & Content Principles

1. **Supportive & Action-Oriented:** Microcopy should be concise, energetic, and focused on immediate athletic execution (e.g., *"Start Workout"*, *"Log Set"*).
2. **Strictly Non-Clinical Framing:** CoachOS is a fitness coaching operating system, not a medical device. All physiological reports, fatigue scores, and discomfort flags must be framed as **subjective feedback signals for coach review**, never clinical diagnoses, medical treatments, or injury rehabilitation prescriptions.
3. **Transparent Privacy Communication:** Privacy notices, consent prompts, and account deletion dialogs must use clear, unambiguous plain language explaining exactly who can view the data.
4. **Natural Persian & English Parity:** Persian copy must feel natural and culturally fluent (`فارسی روان`), avoiding literal word-for-word machine translations from English while respecting Persian fitness terminology.

---

## 2. Bilingual Microcopy Reference Repository

### 2.1 Authentication & Onboarding

| Component Key | English (`en-US`) | Persian (`fa-IR`) | Notes |
|---|---|---|---|
| `auth.login.title` | Welcome back to CoachOS | به CoachOS خوش آمدید | Page Title |
| `auth.login.cta` | Log In | ورود به حساب | Primary Button |
| `auth.register.title` | Create your coaching account | ایجاد حساب کاربری جدید | Page Title |
| `auth.register.cta` | Create Account | ثبت‌نام | Primary Button |
| `auth.forgot_password.cta` | Send Reset Link | ارسال لینک بازیابی رمز | Reset CTA |
| `auth.invite.welcome` | You've been invited to join {org_name} | شما به باشگاه {org_name} دعوت شده‌اید | Invite Title |
| `auth.invite.accept_cta` | Accept Invitation & Join | پذیرش دعوت و شروع | Invite CTA |

---

### 2.2 Athlete Workout Execution & Feedback

| Component Key | English (`en-US`) | Persian (`fa-IR`) | Notes |
|---|---|---|---|
| `workout.today.title` | Today's Workout | تمرین امروز | Main Title |
| `workout.today.rest_day` | Rest & Recovery Day | روز استراحت و ریکاوری | Rest Empty State |
| `workout.today.start_cta` | Start Workout | شروع تمرین | Primary Mobile CTA |
| `workout.active.set_done` | Set Done | ثبت شد | Set Checkmark Button |
| `workout.active.rest_timer` | Rest Timer: {time} remaining | تایمر استراحت: {time} باقی‌مانده | Timer Live Text |
| `workout.active.substitute_cta` | Substitute Exercise | تغییر و جایگزینی حرکت | Action Trigger |
| `workout.active.pain_flag_cta` | Flag Discomfort | گزارش درد یا ناراحتی | Feedback Trigger |
| `workout.finish.cta` | Finish Workout | اتمام جلسه تمرین | Final CTA |
| `workout.summary.celebrate` | Great session! Workout completed | خداقوت! تمرین امروز با موفقیت ثبت شد | Completion Banner |

---

### 2.3 Subjective Feedback & Discomfort Framing (Non-Clinical)

| Component Key | English (`en-US`) | Persian (`fa-IR`) | Notes |
|---|---|---|---|
| `feedback.pain_modal.title` | Report Exercise Discomfort | گزارش ناراحتی یا درد در حین تمرین | Modal Title |
| `feedback.pain_modal.disclaimer` | This feedback alerts your coach to adjust your training. It is not a medical diagnosis. | این گزارش صرفاً مربی شما را جهت تنظیم برنامه مطلع می‌کند و جنبه تشخیص پزشکی ندارد. | **Mandatory Disclaimer** |
| `feedback.pain_modal.severity_mild` | Mild (Awareness / Slight Discomfort) | خفیف (احساس فشار جزئی یا ناراحتی کم) | Severity 1–3 |
| `feedback.pain_modal.severity_mod` | Moderate (Affecting Form / Straining) | متوسط (تأثیرگذار بر اجرای صحیح حرکت) | Severity 4–6 |
| `feedback.pain_modal.severity_sev` | High (Sharp Pain / Stopped Set) | شدید (درد تیز / توقف ست تمرینی) | Severity 7–10 |

---

### 2.4 Privacy, Consent & Data Governance

| Component Key | English (`en-US`) | Persian (`fa-IR`) | Notes |
|---|---|---|---|
| `privacy.photo_consent.title` | Progress Photo Privacy | حریم خصوصی عکس‌های پیشرفت | Consent Title |
| `privacy.photo_consent.body` | Your progress photos will only be visible to your assigned coach ({coach_name}). You can revoke access at any time. | عکس‌های پیشرفت بدنی شما منحصراً برای مربی اختصاصی شما ({coach_name}) قابل مشاهده خواهد بود. شما می‌توانید هر زمان این دسترسی را لغو کنید. | Explicit Consent Body |
| `privacy.photo_consent.grant_cta` | Allow Coach Access | اجازه دسترسی به مربی | Primary Consent CTA |
| `privacy.photo_consent.deny_cta` | Keep Photos Private | خصوصی بماند | Secondary Default CTA |
| `privacy.export.title` | Export Your Fitness Data | دریافت خروجی کامل از اطلاعات | Data Portability |
| `privacy.export.body` | Download a complete machine-readable archive of your workout history, set logs, and profile. | دانلود فایل کامل و استاندارد شامل تاریخچه تمرینات، ست‌های ثبت‌شده و اطلاعات حساب. | Export Description |
| `privacy.delete.title` | Delete Account & Personal Data | حذف حساب و پاک‌سازی اطلاعات شخصی | Right to Erasure |
| `privacy.delete.warning` | This action permanently deletes your personal profile, messages, and photos. | این عمل حساب کاربری، پیام‌ها و عکس‌های شما را به صورت دائمی حذف می‌کند. | Erasure Warning |

---

### 2.5 Progressive Web App (PWA) Installation Guidance

| Component Key | English (`en-US`) | Persian (`fa-IR`) | Notes |
|---|---|---|---|
| `pwa.install.banner_title` | Install CoachOS App | نصب برنامه CoachOS | Install Prompt Title |
| `pwa.install.banner_desc` | Add to your Home Screen for instant access and fast gym-floor logging. | برای دسترسی سریع و ثبت آسان تمرین در باشگاه، برنامه را به صفحه اصلی اضافه کنید. | Install Description |
| `pwa.install.ios_instructions` | Tap Share icon below and select 'Add to Home Screen'. | دکمه اشتراک‌گذاری (Share) در پایین مرورگر را بزنید و گزینه 'Add to Home Screen' را انتخاب کنید. | iOS Safari Guide |
| `pwa.install.cta` | Install Now | نصب برنامه | Android Chrome CTA |
| `pwa.offline.banner` | Offline — unsaved input retained temporarily; retry required after reconnection. | آفلاین — ورودی‌های ذخیره‌نشده به‌صورت موقت در حافظه نگه داشته می‌شود؛ پس از اتصال مجدد تلاش مجدد لازم است. | Offline Banner (temporary, not durable; Phase 12 provides durable queue) |
