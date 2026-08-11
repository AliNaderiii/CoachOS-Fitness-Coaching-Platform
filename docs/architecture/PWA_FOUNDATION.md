# PWA Foundation Specification — CoachOS

**Document Version:** 1.1.0 (Phase 04 Baseline — Correction Update)  
**Date:** 2026-08-11 (UTC)  
**Status:** Approved Engineering Baseline  
**Governing ADRs:** ADR-011, ADR-035, ADR-036, ADR-046  

---

## 1. Executive Summary

CoachOS is designed as a **PWA-first platform**. Phase 04 implements the Level 1 PWA foundation: an installable application shell, standard Web App Manifest, Service Worker caching for static assets, network-first document routing with offline fallback, a network status banner, and platform-specific install guidance.

Phase 04 explicitly does **not** implement Level 3 offline workout synchronization or durable IndexedDB queues, which are allocated to Phase 12.

```
+-----------------------------------------------------------------------------+
|                          PWA THREE-LEVEL STRATEGY                           |
|                                                                             |
|  [PHASE 04: LEVEL 1 — FOUNDATION & APP SHELL] <--- (CURRENT PHASE)          |
|  - Web App Manifest (standalone, theme #0B0F17, 192/512 maskable icons)    |
|  - Service Worker (Cache-First static, Network-First navigation)            |
|  - Bilingual Offline Fallback Screen (/offline)                             |
|  - Network Status Indicator Banner (online/offline events)                  |
|  - Cross-Platform Install Guidance (Android prompt / iOS Safari instructions)|
|                                                                             |
|  [PHASE 07: LEVEL 2 — ATHLETE MOBILE EXECUTION]                             |
|  - Mobile workout execution UI & 48px touch targets                         |
|  - In-memory form state protection & network retry toasts                    |
|                                                                             |
|  [PHASE 12: LEVEL 3 — ADVANCED OFFLINE & SYNC]                              |
|  - Durable IndexedDB workout queue & conflict resolution                     |
|  - Background Sync API & Web Push notification integration                  |
|  - Wearable integration feasibility (HealthKit / Health Connect)            |
+-----------------------------------------------------------------------------+
```

---

## 2. Web App Manifest Specification

The manifest is located at `/frontend/public/manifest.json` and served at `/manifest.json` and `/manifest.webmanifest`:

```json
{
  "name": "CoachOS Fitness Coaching Platform",
  "short_name": "CoachOS",
  "description": "Bilingual fitness coaching, periodized program design, and athlete workout execution platform.",
  "start_url": "/",
  "scope": "/",
  "display": "standalone",
  "orientation": "portrait-primary",
  "background_color": "#0B0F17",
  "theme_color": "#0B0F17",
  "lang": "fa-IR",
  "dir": "rtl",
  "categories": ["fitness", "sports", "health", "productivity"],
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/maskable-icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/maskable-icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ]
}
```

### 2.1 Static Manifest Locale Strategy & Future Dynamic Manifest
- **Phase 04 Baseline:** The static `manifest.json` uses Persian (`fa-IR`, `dir: "rtl"`) as the canonical application title and metadata, reflecting the primary product market.
- **English Users in Phase 04:** English users receive full runtime bilingual localization on document headers (`<html lang="en-US" dir="ltr">`), page titles (`CoachOS — Fitness Coaching Platform`), and all UI components.
- **Future Roadmap (Phase 07):** Exploration of dynamic localized manifest delivery (e.g., serving dynamic manifest JSON via `/api/manifest?locale=en-US` when requested by international clients). Arabic remains strictly out of scope.

---

## 3. Service Worker Architecture

The Service Worker (`/frontend/public/sw.js`) provides an isolated offline caching layer:

### 3.1 Caching Strategies
1. **Static Immutable Assets (Cache-First):**
   - CSS, JS bundles, fonts (`Vazirmatn`, `Inter`), and app icons.
   - Served directly from cache; updated when new Service Worker activates.
2. **Dynamic Navigation Requests (Network-First with Fallback):**
   - HTML document routes (`/`, `/fa-IR/*`, `/en-US/*`).
   - Fetched from network; if network fails (offline), serves the pre-cached `/offline` fallback page.
3. **API Requests (`/api/v1/*`):**
   - **Network-Only.** Sensitive API data, authenticated user sessions, and private media signed URLs are never stored in the Service Worker cache.

### 3.2 Offline Fallback Experience
When a user loses network connectivity and navigates to an uncached route, the Service Worker displays a dedicated, bilingual Offline Fallback Page (`/offline`) stating:
- Persian: «شما در حالت آفلاین هستید. داده‌های ذخیره‌نشده به صورت موقت در حافظه نگهداری می‌شوند و برای ذخیره دائمی به اتصال اینترنت نیاز است.»
- English: "You are currently offline. Unsaved input is retained temporarily in memory. Reconnection is required to save changes."
- A retry button (`تلاش مجدد` / "Retry Connection") allowing immediate re-testing of network status.

---

## 4. Install Guidance and Network Status UI

### 4.1 Network Status Indicator (`NetworkStatusBanner.tsx`)
- Detects connectivity changes via `navigator.onLine` and `window.addEventListener('online' | 'offline')`.
- Displays a top warning banner when disconnected:
  - *"Offline Mode — Unsaved input is retained temporarily in memory. Reconnection is required to save changes."*
- Replaces incorrect claims of durable offline storage with precise architectural wording.

### 4.2 Install Prompt Banner (`InstallPromptBanner.tsx`)
- **Android / Chromium:** Intercepts `beforeinstallprompt` event, stores event handle, and displays an unobtrusive "Install CoachOS App" button.
- **iOS Safari:** Detects iOS Safari user agent (where `beforeinstallprompt` is unsupported) and renders step-by-step visual guidance:
  1. Tap the **Share** button in Safari toolbar.
  2. Scroll down and tap **"Add to Home Screen"**.

---

## 5. Platform Limitations and Technical Constraints

| Dimension | iOS Safari / WebKit | Android Chromium / Chrome | Desktop (Chrome / Edge / Safari) |
|---|---|---|---|
| **Standalone Display** | Supported (`<meta name="apple-mobile-web-app-capable">`) | Full PWA Manifest support | Full standalone window support |
| **Storage Quota & Eviction** | 7-day inactivity eviction for non-installed apps; persistent when installed | Up to several GBs; requests persistent storage permission | Generous local quota |
| **Background Sync** | **Not supported** | Supported via Service Worker | Supported |
| **Web Push Notifications** | Supported **only** in iOS 16.4+ when installed to Home Screen | Fully supported via VAPID | Fully supported |
| **Hardware / Sensors** | Strict permission gates | Supported | Supported |
