import { afterEach, describe, expect, it, vi } from "vitest";
import { registerServiceWorker } from "../lib/pwa/register-sw";

describe("Service Worker registration helper", () => {
  afterEach(() => {
    Reflect.deleteProperty(navigator, "serviceWorker");
    vi.restoreAllMocks();
  });

  it("is a no-op when Service Workers are unsupported", async () => {
    Reflect.deleteProperty(navigator, "serviceWorker");
    await expect(registerServiceWorker()).resolves.toBeNull();
  });

  it("registers the Phase 04 worker at the root scope when the API is explicitly mocked", async () => {
    const registration = { scope: "http://localhost/" } as ServiceWorkerRegistration;
    const register = vi.fn().mockResolvedValue(registration);
    Object.defineProperty(navigator, "serviceWorker", {
      configurable: true,
      value: { register },
    });

    await expect(registerServiceWorker()).resolves.toBe(registration);
    expect(register).toHaveBeenCalledWith("/sw.js", { scope: "/" });
  });

  it("fails safely without logging registration details", async () => {
    const register = vi.fn().mockRejectedValue(new Error("registration unavailable"));
    Object.defineProperty(navigator, "serviceWorker", {
      configurable: true,
      value: { register },
    });
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => undefined);

    await expect(registerServiceWorker()).resolves.toBeNull();
    expect(consoleError).not.toHaveBeenCalled();
  });
});
