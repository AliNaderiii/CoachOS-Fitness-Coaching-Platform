import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

describe("PWA Baseline & Manifest Validation (ADR-011, ADR-046)", () => {
  const manifestPath = path.resolve(__dirname, "../public/manifest.json");

  it("ensures public/manifest.json exists and is valid JSON", () => {
    expect(fs.existsSync(manifestPath)).toBe(true);
    const content = fs.readFileSync(manifestPath, "utf-8");
    const manifest = JSON.parse(content);

    expect(manifest.name).toBe("CoachOS Fitness Coaching Platform");
    expect(manifest.short_name).toBe("CoachOS");
    expect(manifest.display).toBe("standalone");
    expect(manifest.start_url).toBe("/");
    expect(manifest.background_color).toBe("#0B0F17");
    expect(manifest.theme_color).toBe("#0B0F17");
  });

  it("contains both standard and maskable 192x192 and 512x512 icons", () => {
    const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf-8"));
    const icons = manifest.icons;

    expect(icons.length).toBeGreaterThanOrEqual(4);

    const has192Any = icons.some((i: any) => i.sizes === "192x192" && i.purpose === "any");
    const has192Maskable = icons.some(
      (i: any) => i.sizes === "192x192" && i.purpose === "maskable"
    );
    const has512Any = icons.some((i: any) => i.sizes === "512x512" && i.purpose === "any");
    const has512Maskable = icons.some(
      (i: any) => i.sizes === "512x512" && i.purpose === "maskable"
    );

    expect(has192Any).toBe(true);
    expect(has192Maskable).toBe(true);
    expect(has512Any).toBe(true);
    expect(has512Maskable).toBe(true);
  });

  it("ensures public icon assets exist on disk", () => {
    const iconFiles = [
      "icon-192x192.png",
      "icon-512x512.png",
      "maskable-icon-192x192.png",
      "maskable-icon-512x512.png",
    ];

    for (const icon of iconFiles) {
      const iconPath = path.resolve(__dirname, `../public/icons/${icon}`);
      expect(fs.existsSync(iconPath)).toBe(true);
    }
  });

  it("ensures Service Worker sw.js exists in public directory", () => {
    const swPath = path.resolve(__dirname, "../public/sw.js");
    expect(fs.existsSync(swPath)).toBe(true);
    const content = fs.readFileSync(swPath, "utf-8");
    expect(content).toContain("coachos-app-shell-v1");
  });
});
