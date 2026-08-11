# PWA Architecture — CoachOS

**Version:** 1.0.0 Phase 03  
**Status:** Proposed — sequencing aligned across Phase 04 / 07 / 12  
**Constraints:** fa-IR RTL + en-US LTR only, no Arabic.

---

## 1. Overview

CoachOS is PWA-first mobile delivery to avoid app-store friction and low-connectivity gym basement failures. Strategy progresses across three milestones to balance velocity with resilience.

---

## 2. Three-Level Strategy (Authoritative)

### Phase 04 — Foundation: Manifest + App Shell + Offline Fallback (P0)

**Goal:** Installable, fast shell, basic offline UX.

- **Web App Manifest (`manifest.json`):**
  - `name`: CoachOS (localized? Actually `name` fa: کوچ‌اواس? Use bilingual? Provide both? Propose English name + short_name + localized `name` via manifest translation? But manifest itself not i18n dynamic — use neutral + localized via `description`. For MVP, set `name: CoachOS`, `short_name: CoachOS`, `description_en/en`, but include persian description in html meta? Actually manifest localization via multiple manifests? Deferred — use neutral).
  - `short_name`: CoachOS
  - `display`: `standalone` — fullscreen app view hiding browser URL chrome.
  - `start_url`: `/?source=pwa` or `/app/today` for athlete? Propose `/app/today` as start_url with scope `/`.
  - `theme_color`: `#0B0F17` dark obsidian (proposed, requires testing)
  - `background_color`: `#0B0F17`
  - `icons`: 192px, 512px, maskable 512px, purpose any/maskable.
  - `dir` and `lang`? Manifest supports `dir`? Actually manifest not per-locale dir — HTML `dir` attribute handles.
  - `orientation`: `any` — allow rotation for video demos.
- **Icons:** Provide PNG + SVG? 192, 512 maskable with safe zone 40%.
- **Standalone display check:** Launching from home screen opens standalone, no browser chrome.
- **Service Worker Registration:**
  - Register SW on first load `/sw.js` scope `/`.
  - Technology: Workbox or custom? Proposed Workbox (by Google) or `next-pwa` wrapper. Status: Proposed pending evaluation of bundle size vs custom minimal SW.
  - SW lifecycle: `install` → skipWaiting? Proposed prompt user? Minimal: skipWaiting optional with toast "New version available".
- **App-shell Caching (Phase04):**
  - Cache static assets: HTML shell, JS chunks, CSS, fonts (Vazirmatn woff2 subset), icons.
  - Strategy: `CacheFirst` for fonts/icons (versioned), `StaleWhileRevalidate` for JS/CSS shell.
  - Runtime caching: API GET `/api/v1/exercises` maybe cached? For P0 foundation, API not cached except maybe today view? Actually Phase04 does NOT cache workout data — requires network. Only shell.
  - Offline fallback page: `/offline.html` or fallback route rendering localized message "Offline — connect to view workouts" + retry button.
- **Install Guidance:**
  - UX copy `pwa.install_banner` with instructions for iOS Safari (Share → Add to Home Screen) and Android Chrome (automatic prompt).
  - `beforeinstallprompt` event captured and deferred, show custom install CTA (proposed).
  - No enforcement — optional.
- **Requirements (NFR-PWA-01/02):**
  - Valid manifest, standalone display, high-res icons, active SW registration.
  - Core app shell cached locally to allow immediate launch in zero connectivity.
- **Security:** SW scope same origin, HTTPS only.
- **Testing:** Lighthouse PWA audit score >= 90 proposed (requires validation in Phase13).

### Phase 07 — Athlete Mobile Validation: Touch-Optimized + Temporary Preservation (P0)

**Goal:** Validate athlete gym-floor execution PWA experience, with no promise of full conflict-free offline sync.

- **Athlete mobile execution:**
  - `/app/today` dashboard rendered from cached snapshot if previously loaded? Proposal: after first load, today's workout snapshot stored in React Query or SWR cache (memory). Offline can render last fetched snapshot (stale) with banner.
  - Active workout session mode fixed bottom nav hidden, full-screen canvas.
- **Touch-optimized logging:**
  - 44×44px minimum WCAG 2.5.5, 48×48px preferred design target for primary CTA and set checkmarks — actual implementation must be tested.
  - Oversized numeric keypad triggers `inputmode="decimal"` native keypad.
  - Rest timer: client-side JS `setInterval` + visual SVG ring, audio/haptic on completion.
- **Form-state protection:**
  - Unsaved set inputs kept in local React component state (useState + useReducer) — surviving component remount? Preserve in sessionStorage optionally? But spec says in-memory only not durable — so memory.
  - On network loss during active session:
    - Show yellow banner: "Offline — unsaved input retained temporarily; retry required after reconnection" (`pwa.offline.banner` from UX_COPY).
    - Do NOT store to IndexedDB durable queue.
    - Allow continuous workout execution (timer still works).
    - Retry button attempts sync on reconnect (`navigator.onLine` + fetch retry).
- **Network-status indicator:**
  - Hook `useNetworkStatus()` listening `online`/`offline` events, shows badge in top bar when offline.
  - Optional `SW` offline detection? Use `fetch` failure.
- **Retry behavior:**
  - For set log POST failure due to network, present toast "Failed to save set — [Tap to Retry]" (state/error matrix).
  - No auto background sync yet — manual retry.
- **Video demos:**
  - Video requires live network; if offline, show fallback text cues: "Video demo unavailable offline — text cues shown below".
- **Messages:**
  - Message send not queued durably — unsaved input retained temporarily, retry required after reconnection (no durable message queue in Phase07).
- **No promise of full conflict-free offline sync:** Explicit boundaries in docs/ux/STATE_AND_ERROR_MATRIX.md.
- **Installed-PWA mobile validation:**
  - Test on iOS Safari 17+ and Android Chrome 120+ for standalone display, splash screen, status bar theming, one-handed thumb zone.

### Phase 12 — Advanced Capabilities: Durable Offline + Sync + Push + Wearables Evaluation (P2)

**Goal:** Full offline-first workout logging with durable queue and background sync.

- **IndexedDB workout data:**
  - Library: Dexie.js or idb-keyval (proposed) — wraps IndexedDB for structured storage.
  - Stores: `workout_sessions` (in_progress), `set_logs_queue` (unsynced), `exercise_catalog_cache` (canonical + org-private), `program_snapshot_cache`, `progress_photos_pending_upload` (optional).
- **Durable offline set queue:**
  - When offline, set logs persist to IndexedDB queue with client-generated UUIDv7 (proposed) — allows offline ID generation avoiding enumeration (but not authz bypass).
  - Each entry: `id` UUIDv7, `session_id`, `payload`, `created_at` local, `retry_count`, `status` pending/syncing/synced/failed/conflict.
- **Sync status UI:**
  - Indicator: "Synced", "Pending sync (3 sets)", "Sync failed — tap to retry".
  - Persistent footer badge.
- **Retry and backoff:**
  - Exponential backoff 2s, 5s, 15s, 60s + jitter.
  - On reconnect, attempt flush queue ordered by `created_at`.
- **Conflict resolution:**
  - Last-write-wins for set actuals? Or server-wins for program snapshot? Propose: set logs are append-only, no conflict; if same `set_index` logged offline and online simultaneously, server keeps latest `created_at` but preserves both versions in audit? Requires decision in Phase12 ADR.
  - Program assignment version: if coach pushes new version while athlete offline, athlete sees old snapshot until sync plus notification "New program version available".
- **Background synchronization where supported:**
  - Use Background Sync API `self.registration.sync.register('sync-sets')` if available (Chrome). iOS Safari does not support — fallback to foreground sync on app focus.
- **Push limitations:**
  - Web Push API requires Service Worker + Push subscription + VAPID keys. iOS support limited (16.4+ standalone only). Document limitations: push not reliable on iOS until added to home screen; fallback to email/in-app polling.
- **HealthKit / Health Connect evaluation:**
  - Evaluate native bridge vs PWA? PWA cannot directly access HealthKit/Health Connect; requires native wrapper (Capacitor/Cordova) or backend webhook integration with Garmin etc. Decision: document evaluation, not implement in Phase12 until privacy review. Requires pre-DPIA.
- **Native bridge decision:**
  - At Phase12, decide whether to remain pure PWA or wrap via Capacitor for wearable access. No native builds in P0.

---

## 3. Browser / Platform Limitations (Documented Without Claiming Implementation)

| Feature | Chrome Android | Safari iOS | Firefox Desktop | Limitation Note |
|---------|----------------|------------|-----------------|-----------------|
| Web App Manifest installable | Yes (automatic prompt) | Yes but manual via Share → Add to Home Screen; no automatic prompt | Limited support | iOS requires user education via UX_COPY install guide |
| Service Worker caching | Yes | Yes | Yes | Storage quota ~50MB per origin typical |
| Standalone display | Yes | Yes (if added to home screen) | No (desktop opens as tab) | iOS status bar theming via meta tags |
| Background Sync API | Yes | No (as of 2026 still unsupported) | No | Phase12 must have foreground fallback |
| Periodic Background Sync | Chrome only (requires engagement) | No | No | Deferred |
| Web Push | Yes | Yes from iOS 16.4+ only if standalone installed | Yes | iOS push requires standalone + user permission |
| IndexedDB storage | Yes | Yes | Yes | Persistence may be cleared under storage pressure; request persistent storage via `navigator.storage.persist()` |
| Vibration API (haptics) | Yes | Limited (iOS 13+ partial) | No | Rest timer haptic fallback to audio beep |
| Native health APIs | No (requires native bridge) | No | No | Must evaluate Capacitor or backend integration in Phase12 |

All described as proposed patterns — requires implementation validation and device testing in Phase04/07/12.

---

## 4. Security & Privacy in PWA

- SW must not cache Tier4 sensitive media aggressively — no caching of signed URLs (TTL short) in Cache API; use memory only or NetworkOnly strategy for `/api/v1/*progress-photos*` and `/api/v1/*messages*`.
- SW must not log health data.
- `manifest.json` no PII.
- Request persistent storage only if needed; transparent to user.
- Clear cache on logout? Proposed yes — SW cache clear + IndexedDB clear on logout + erasure.

---

## 5. File Structure for PWA (Proposed, Not Implemented)

```
/public
  manifest.json (or manifest.webmanifest)
  icons/
    icon-192.png, icon-512.png, maskable-512.png, apple-touch-icon-180.png
  offline.html (fallback)
  sw.js (or generated by next-pwa Workbox)
```

Manifest example (illustrative, not served in Phase03 — spec only):

```json
{
  "name": "CoachOS",
  "short_name": "CoachOS",
  "description": "Bilingual fitness coaching platform — fa-IR & en-US",
  "start_url": "/app/today?source=pwa",
  "display": "standalone",
  "background_color": "#0B0F17",
  "theme_color": "#0B0F17",
  "dir": "auto",
  "lang": "en-US",
  "orientation": "any",
  "icons": [
    {"src": "/icons/icon-192.png","sizes":"192x192","type":"image/png","purpose":"any"},
    {"src": "/icons/icon-512.png","sizes":"512x512","type":"image/png","purpose":"any"},
    {"src": "/icons/maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}
  ]
}
```

---

## 6. Offline State Wording Consistency (Normative)

- Phase04: "Offline — cached app shell only. Connect to load workouts."
- Phase07: "Offline — unsaved input retained temporarily; retry required after reconnection" (NOT "sets saved locally" — that implies durable)
- Phase12: "Offline — 3 sets queued locally; will sync when reconnected" + sync status badges.

Enforced in STATE_AND_ERROR_MATRIX and UX_COPY.

---

## 7. References

- `docs/ux/STATE_AND_ERROR_MATRIX.md` — progressive offline matrix
- `docs/ux/NAVIGATION_MODEL.md` — mobile bottom nav + active canvas modal
- `NFR-PWA-01/02`, `ADR-011` PWA sequencing, `RELEASE_PLAN.md` PWA phasing
- `SYSTEM_CONTEXT.md`, `CONTAINER_ARCHITECTURE.md`
