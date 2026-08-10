# State & Error Handling Matrix — CoachOS

**Document version:** 1.0.0 (Phase 02 Baseline)  
**Last updated:** 2026-08-10  
**Supported Locales:** Persian (`fa-IR`, RTL) and English (`en-US`, LTR)  
**Strict constraint:** Arabic is strictly out of scope.  
**Design Phase:** Phase 02 — Documentation and specifications only. No application source code.

---

## 1. Global UI State Paradigms (Proposed Patterns — Requires Implementation Validation)

Every screen and data-fetching component in CoachOS is *designed* to gracefully handle 8 standard system states (proposed patterns; requires implementation validation and user testing):

1. **Initial / Loading (Shimmer Skeleton):** Renders animated structural skeleton placeholders matching exact layout dimensions to eliminate Cumulative Layout Shift (CLS).
2. **Empty State:** Illustrated, localized empty view explaining why no content is present and offering a primary corrective CTA.
3. **Success State:** Immediate visual confirmation (e.g., green check badge, subtle toast, or celebratory volume summary).
4. **Validation Error (Client-Side):** Inline field-level error messages attached via `aria-describedby`, preventing form submission.
5. **Server Error (HTTP 500):** Friendly, non-technical error container with an actionable "Try Again" retry trigger.
6. **Permission Denied / Cross-Tenant (HTTP 403 / 404):** Clean access-restricted screen explaining why access is denied without leaking foreign tenant data.
7. **Session Expired / Unauthenticated (HTTP 401):** Saves active form state to session storage and redirects to `/login` with return URL.
8. **Network Unavailable / Offline:** Clear non-intrusive banner informing the user of offline status with progressive resilience behaviors.

---

## 2. Progressive PWA & Offline State Behavior Across Phases (Proposed Sequencing — Not Implemented in Phase 02)

| Feature Area | Phase 04 Baseline Behavior | Phase 07 Athlete Validation Behavior | Phase 12 Advanced Capabilities |
|---|---|---|---|
| **App Shell Launch** | Service Worker serves cached HTML/JS/CSS shell instantly; renders offline screen if network dead. | Shell loads from cache; surfaces cached active program snapshot. | Immediate background launch; background sync checks. |
| **Workout Data Fetch** | Requires network connection; displays standard offline fallback page if offline. | Renders cached Today's Workout snapshot from local memory. | Offline-first database reads from local IndexedDB storage. |
| **Set Logging During Offline** | Not in Phase 04 scope. | **In-Memory Form Preservation (temporary, not durable):** Athlete inputs remain in local React state; surfaces yellow offline toast: *"Offline — unsaved input retained temporarily; retry required after reconnection"* (no durable offline queue in Phase 07; durable IndexedDB queue in Phase 12); retry button on reconnect. | **IndexedDB Sync Queue:** Sets persist to local database queue; background sync automatically pushes records upon reconnection; handles conflict resolution. |
| **Rest Timer** | Client-side JavaScript execution (works offline). | Client-side JavaScript execution with local audio/haptics (works offline). | Native background worker / push timer notification. |
| **Media Video Playback** | Video requires live network connection. | Video attempts playback; shows *"Video demo unavailable offline — text cues shown below"* fallback. | Optional client-side video caching for favorite exercises. |

---

## 3. Comprehensive Feature State Matrix

| Feature Domain | Loading State | Empty State | Success State | Validation Error | Server / Auth Error | Network Drop / Offline (Phase 07) |
|---|---|---|---|---|---|---|
| **Authentication (`/login`, `/register`)** | Button displays spinner; inputs disabled. | n/a | Redirects to dashboard; sets auth cookie. | Inline red border: *"Please enter a valid email address"*. | Red banner: *"Invalid email or password"* (401) or *"Too many attempts"* (429). | Banner: *"Network unavailable — check your connection"*. |
| **Athlete Today's Workout (`/app/today`)** | 4 skeleton card placeholders shimmering. | Rest Card: *"Rest Day — Next workout scheduled for tomorrow"*. | Workout card with active CTA: *"Start Workout"*. | n/a | Error container: *"Unable to load workout — [Retry]"*. | Renders cached snapshot; displays offline badge. |
| **Live Set Logging (`/app/workouts/:id`)** | Immediate memory render. | If 0 sets: *"No prescribed sets"*. | Set row turns green with checkmark icon; triggers timer. | Keypad shakes; red border: *"Load must be a positive number"*. | Toast: *"Failed to save set — [Tap to Retry]"*. | Local form state preserved temporarily in memory; yellow banner: *"Offline — unsaved input retained temporarily; retry required after reconnection"* (no durable queue; Phase 12 provides durable IndexedDB queue). |
| **Exercise Search (`/coach/exercises`)** | Shimmer search result list. | Empty box: *"No exercises found for '...' — [Create Custom]"*. | Results list sorted by normalized relevance. | Query < 2 chars prompts: *"Type at least 2 characters"*. | Toast: *"Search service unavailable"*. | Displays cached canonical catalog items. |
| **Program Builder (`/coach/programs/:id`)** | Shimmer tree grid nodes. | Empty phase: *"Add your first workout day"*. | Auto-saves with green pill: *"All changes saved"*. | Highlighted missing exercise: *"Please select an exercise"*. | Toast: *"Save failed — [Retry Now]"*. | Disables builder mutations; surfaces reconnect prompt. |
| **Member Management (`/org/members`)** | 5-row table shimmer skeleton. | Empty state: *"No staff coaches invited yet — [Invite Coach]"*. | Member table rendered with status badges. | Email validation: *"Invalid email format"*. | Red alert: *"Failed to update member status"*. | Read-only cached roster display. |
| **Progress Photos (`/app/progress`)** | Shimmer grid placeholders. | Empty card: *"No photos uploaded — [Upload First Photo]"*. | Photo uploaded; thumbnail generated with consent tag. | File validation: *"Image must be JPEG/PNG under 10MB"*. | Error toast: *"Upload failed — try again"*. | Upload disabled until connection restored. |
| **1:1 Messages (`/app/messages`)** | Message bubbles skeleton shimmer. | Empty chat: *"No messages yet — send your coach a note"*. | Message appended with single checkmark (sent). | Textarea empty error on send. | Red retry icon next to failed message bubble. | Message not sent — unsaved input retained temporarily; retry required after reconnection *(no durable message queue in Phase 07; durable queue in Phase 12 if approved)*. |
