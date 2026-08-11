/**
 * Registers only the Phase 04 app-shell service worker. Unsupported browsers,
 * SSR, and test environments without a mocked Service Worker API are no-ops.
 */
export async function registerServiceWorker(): Promise<ServiceWorkerRegistration | null> {
  if (
    typeof window === "undefined" ||
    typeof navigator === "undefined" ||
    !("serviceWorker" in navigator)
  ) {
    return null;
  }

  try {
    return await navigator.serviceWorker.register("/sw.js", { scope: "/" });
  } catch {
    // Registration is an optional enhancement. Do not log browser or request data.
    return null;
  }
}
