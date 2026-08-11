import { describe, it, expect } from "vitest";
import nextConfig from "../next.config.mjs";

describe("Frontend Security Headers & CSP Delivery (ADR-045)", () => {
  it("delivers baseline security headers and CSP on all routes", async () => {
    if (!nextConfig.headers) {
      throw new Error("nextConfig.headers is not defined");
    }
    const headersConfig = await nextConfig.headers();
    const globalRule = headersConfig.find((rule: any) => rule.source === "/:path*");

    expect(globalRule).toBeDefined();
    if (!globalRule) return;

    const headerMap = new Map(globalRule.headers.map((h: any) => [h.key, h.value]));

    expect(headerMap.get("X-Content-Type-Options")).toBe("nosniff");
    expect(headerMap.get("X-Frame-Options")).toBe("DENY");
    expect(headerMap.get("Referrer-Policy")).toBe("strict-origin-when-cross-origin");
    expect(headerMap.get("Permissions-Policy")).toContain("camera=()");

    const csp = headerMap.get("Content-Security-Policy");
    expect(csp).toBeDefined();
    expect(csp).toContain("default-src 'self'");
    expect(csp).toContain("object-src 'none'");
    expect(csp).toContain("frame-ancestors 'none'");
    expect(csp).toContain("base-uri 'self'");
  });
});
