import { describe, it, expect } from "vitest";
import fs from "fs";
import path from "path";

/**
 * Phase 08 scope-boundary and safety scanner.
 *
 * Asserts by inspection that the communication frontend introduces no durable
 * offline primitives (Phase 12), no unsafe HTML rendering, no out-of-scope
 * domain, and no Arabic resources.
 */

const MESSAGING_DIRS = [
  path.resolve(__dirname, "../components/messaging"),
  path.resolve(__dirname, "../lib/messaging"),
];

const MESSAGING_FILES = [
  ...MESSAGING_DIRS.flatMap((dir) =>
    fs
      .readdirSync(dir)
      .filter((file) => file.endsWith(".ts") || file.endsWith(".tsx"))
      .map((file) => path.join(dir, file)),
  ),
  path.resolve(__dirname, "../lib/api/messaging.ts"),
];

const read = (file: string) => fs.readFileSync(file, "utf-8");

/**
 * Strips comments before scanning.
 *
 * The scanner must flag real usage, not documentation. These modules
 * deliberately name the forbidden primitives in comments to record why they are
 * absent, and that prose must not trip the scanner.
 */
const readCode = (file: string) =>
  read(file)
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .replace(/^\s*\/\/.*$/gm, "")
    .replace(/\{\/\*[\s\S]*?\*\/\}/g, "");

describe("Phase 08 offline boundary (ADR-036)", () => {
  const FORBIDDEN = [
    /indexedDB/i,
    /localStorage/i,
    /sessionStorage/i,
    /navigator\.sync/i,
    /BackgroundSyncManager/i,
    /periodicSync/i,
    /pushManager\.subscribe/i,
  ];

  it("introduces no durable offline or push-subscription primitives", () => {
    const hits: string[] = [];
    for (const file of MESSAGING_FILES) {
      const content = readCode(file);
      for (const pattern of FORBIDDEN) {
        if (pattern.test(content)) hits.push(`${path.basename(file)} matched ${pattern}`);
      }
    }
    expect(hits).toEqual([]);
  });

  it("documents that nothing is queued while offline", () => {
    const conversation = read(
      path.resolve(__dirname, "../components/messaging/ConversationView.tsx"),
    );
    expect(conversation).toContain("no durable offline queue");
  });
});

describe("Phase 08 rendering safety", () => {
  it("never uses dangerouslySetInnerHTML in messaging components", () => {
    for (const file of MESSAGING_FILES) {
      expect(readCode(file)).not.toContain("dangerouslySetInnerHTML");
    }
  });

  it("never evaluates message content", () => {
    for (const file of MESSAGING_FILES) {
      const content = readCode(file);
      expect(content).not.toMatch(/\beval\(/);
      expect(content).not.toMatch(/new Function\(/);
      expect(content).not.toMatch(/innerHTML\s*=/);
    }
  });

  it("isolates user-controlled text with bdi in the message and inbox views", () => {
    const conversation = read(
      path.resolve(__dirname, "../components/messaging/ConversationView.tsx"),
    );
    const list = read(path.resolve(__dirname, "../components/messaging/ConversationList.tsx"));
    expect(conversation).toContain("<bdi>{message.body}</bdi>");
    expect(list).toContain("<bdi>{conversation.last_message_preview}</bdi>");
  });
});

describe("Phase 08 scope boundary", () => {
  const FORBIDDEN_DOMAINS: Record<string, RegExp> = {
    nutrition: /\bnutrition|calorie|macronutrient\b/i,
    billing: /\bstripe|checkout|invoice|payment_intent\b/i,
    ai: /\bopenai|anthropic|\bllm\b|gpt-|ai_summar/i,
    sms: /\btwilio|whatsapp\b/i,
    wearable: /\bhealthkit|garmin|fitbit\b/i,
    marketplace: /\bmarketplace\b/i,
  };

  it.each(Object.entries(FORBIDDEN_DOMAINS))(
    "contains no %s references",
    (_label, pattern) => {
      for (const file of MESSAGING_FILES) {
        expect(readCode(file)).not.toMatch(pattern);
      }
    },
  );

  it("makes no real-time or guaranteed-push claim in the dictionaries", () => {
    const en = read(path.resolve(__dirname, "../lib/i18n/dictionaries/en-US.json"));
    const parsed = JSON.parse(en);
    const notificationStrings = JSON.stringify(parsed.notifications).toLowerCase();
    expect(notificationStrings).not.toContain("real-time");
    expect(notificationStrings).not.toContain("realtime");
    expect(notificationStrings).not.toContain("instantly");
    // The refresh-based model is stated explicitly instead.
    expect(parsed.notifications.refresh_hint).toContain("refresh");
  });

  it("keeps both dictionaries free of Arabic locale resources", () => {
    const dir = path.resolve(__dirname, "../lib/i18n/dictionaries");
    expect(fs.readdirSync(dir).sort()).toEqual(["en-US.json", "fa-IR.json"]);
  });
});

describe("Phase 08 accessibility and touch targets", () => {
  it("uses 44px minimum interactive targets in messaging surfaces", () => {
    const composer = read(
      path.resolve(__dirname, "../components/messaging/ConversationView.tsx"),
    );
    expect(composer).toContain("min-h-[44px]");

    const preferences = read(
      path.resolve(__dirname, "../components/messaging/NotificationPreferences.tsx"),
    );
    expect(preferences).toContain("min-h-[44px]");
  });

  it("provides visible focus styling on messaging controls", () => {
    for (const file of MESSAGING_FILES.filter((f) => f.endsWith(".tsx"))) {
      expect(read(file)).toContain("focus-visible:ring");
    }
  });

  it("uses polite live regions rather than assertive notification spam", () => {
    for (const file of [
      path.resolve(__dirname, "../components/messaging/ConversationList.tsx"),
      path.resolve(__dirname, "../components/messaging/NotificationCenter.tsx"),
    ]) {
      const content = read(file);
      expect(content).toContain('aria-live="polite"');
      expect(content).not.toContain('aria-live="assertive"');
    }
  });
});
