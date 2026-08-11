import { describe, it, expect } from "vitest";
import nextConfig, { getCspHeader } from "../next.config.mjs";

describe("Frontend Security Headers & Environment-Specific CSP Delivery (ADR-045)", () => {
  it("delivers baseline security headers on all routes", async () => {
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

  it("ensures development CSP allows HMR but is explicitly isolated", () => {
    const devCsp = (getCspHeader as (isProd?: boolean) => string)(false);
    expect(devCsp).toContain("unsafe-eval");
    expect(devCsp).toContain("unsafe-inline");
    expect(devCsp).toContain("default-src 'self'");
    expect(devCsp).toContain("object-src 'none'");
    expect(devCsp).toContain("frame-ancestors 'none'");
    expect(devCsp).toContain("base-uri 'self'");
  });

  it("ensures production CSP strictly eliminates unsafe-eval", () => {
    const prodCsp = (getCspHeader as (isProd?: boolean) => string)(true);
    expect(prodCsp).not.toContain("unsafe-eval");
    expect(prodCsp).toContain("script-src 'self' https:");
    expect(prodCsp).toContain("object-src 'none'");
    expect(prodCsp).toContain("frame-ancestors 'none'");
    expect(prodCsp).toContain("base-uri 'self'");
  });
});
