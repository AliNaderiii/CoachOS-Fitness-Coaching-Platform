import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

/**
 * Phase 07 temporary offline boundary scope scanner (ADR-036).
 * Confirms the athlete execution frontend implements only in-memory retry and
 * introduces NO durable offline primitives (IndexedDB, localStorage,
 * sessionStorage, Background Sync, Service-Worker-managed queues).
 * Durable offline is explicitly deferred to Phase 12.
 */
describe("Phase 07 offline scope boundary", () => {
  const dirs = [
    path.resolve(__dirname, "../components/athlete"),
    path.resolve(__dirname, "../lib/athlete"),
    path.resolve(__dirname, "../lib/api"),
  ];

  const files = dirs.flatMap((dir) =>
    fs.readdirSync(dir).filter((f) => f.endsWith(".ts") || f.endsWith(".tsx")).map((f) => path.join(dir, f)),
  );

  const FORBIDDEN = [
    /indexedDB/i,
    /localStorage/i,
    /sessionStorage/i,
    /navigator\.sync/i,
    /BackgroundSyncManager/i,
    /\.transaction\(.*readwrite/i,
  ];

  it("scans athlete execution modules for durable offline primitives", () => {
    const hits: string[] = [];
    for (const file of files) {
      const content = fs.readFileSync(file, "utf-8");
      for (const pattern of FORBIDDEN) {
        if (pattern.test(content)) {
          hits.push(`${file} matched ${pattern}`);
        }
      }
    }
    expect(hits).toEqual([]);
  });

  it("athlete offline boundary uses only in-memory state (no durable queue claim)", () => {
    const useNetworkStatus = fs.readFileSync(
      path.resolve(__dirname, "../lib/athlete/useNetworkStatus.ts"),
      "utf-8",
    );
    const offlineBanner = fs.readFileSync(
      path.resolve(__dirname, "../components/athlete/OfflineBanner.tsx"),
      "utf-8",
    );
    // Must explicitly document the temporary in-memory boundary.
    expect(useNetworkStatus).toContain("in-memory");
    expect(offlineBanner).toContain("No durable queue");
  });
});
