/**
 * CoachOS Service Worker — Phase 04 PWA Baseline.
 * Implements Level 1 App-Shell Caching & Offline Fallback (ADR-035, ADR-046).
 */

const CACHE_NAME = "coachos-app-shell-v1";
const STATIC_CACHE_NAME = "coachos-static-v1";

const PRECACHE_ASSETS = [
  "/",
  "/manifest.json",
  "/icons/icon-192x192.png",
  "/icons/icon-512x512.png",
  "/icons/maskable-icon-192x192.png",
  "/icons/maskable-icon-512x512.png",
  "/fa-IR/offline",
  "/en-US/offline",
];

// Install event: Pre-cache app shell assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => {
        console.log("[SW] Pre-caching app shell assets");
        return cache.addAll(PRECACHE_ASSETS).catch((err) => {
          console.warn("[SW] Some assets failed to pre-cache:", err);
        });
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event: Clean up obsolete caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((key) => key !== CACHE_NAME && key !== STATIC_CACHE_NAME)
            .map((key) => {
              console.log("[SW] Removing old cache:", key);
              return caches.delete(key);
            })
        )
      )
      .then(() => self.clients.claim())
  );
});

// Fetch event: Apply routing strategies
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 1. Never cache API calls (Network-Only)
  if (url.pathname.startsWith("/api/")) {
    return;
  }

  // 2. Navigation requests: Network-First with Offline Page Fallback
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cache successful navigation responses in app shell cache
          if (response.status === 200) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone));
          }
          return response;
        })
        .catch(async () => {
          // Attempt to return cached page or fallback to offline screen
          const cachedResponse = await caches.match(request);
          if (cachedResponse) {
            return cachedResponse;
          }
          // Determine language from pathname or fallback to default Persian offline page
          const isEn = url.pathname.startsWith("/en-US");
          const fallbackPath = isEn ? "/en-US/offline" : "/fa-IR/offline";
          const fallback = await caches.match(fallbackPath);
          if (fallback) {
            return fallback;
          }
          // Embedded minimal fallback HTML if cache matching fails
          return new Response(
            `<!DOCTYPE html>
            <html lang="fa" dir="rtl">
            <head><meta charset="utf-8"><title>CoachOS - آفلاین</title></head>
            <body style="background:#0B0F17;color:#F9FAFB;font-family:sans-serif;text-align:center;padding:50px;">
              <h1>عدم اتصال به اینترنت</h1>
              <p>شما در حالت آفلاین هستید. لطفاً اتصال اینترنت خود را بررسی کنید.</p>
            </body>
            </html>`,
            {
              headers: { "Content-Type": "text/html; charset=utf-8" },
            }
          );
        })
    );
    return;
  }

  // 3. Static Assets (CSS, JS, Fonts, Images): Cache-First strategy
  if (
    request.destination === "style" ||
    request.destination === "script" ||
    request.destination === "font" ||
    request.destination === "image"
  ) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(request).then((networkResponse) => {
          if (networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(STATIC_CACHE_NAME).then((cache) => cache.put(request, responseClone));
          }
          return networkResponse;
        });
      })
    );
  }
});
