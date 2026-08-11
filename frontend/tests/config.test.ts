import { describe, it, expect } from "vitest";
import { validatePublicEnv, publicConfig } from "../lib/config/env";

describe("Frontend Secret Boundary & Public Config (ADR-045)", () => {
  it("allows safe NEXT_PUBLIC_ variables", () => {
    const safeEnv = {
      NEXT_PUBLIC_API_BASE_URL: "http://localhost:8000",
      NEXT_PUBLIC_APP_NAME: "CoachOS",
      NODE_ENV: "test",
    };

    expect(() => validatePublicEnv(safeEnv)).not.toThrow();
  });

  it("throws security error if private secret key pattern is detected", () => {
    const leakedEnv = {
      NEXT_PUBLIC_APP_NAME: "CoachOS",
      DJANGO_SECRET_KEY: "django-insecure-private-key",
    };

    expect(() => validatePublicEnv(leakedEnv)).toThrowError(/SECURITY VIOLATION/);
  });

  it("throws security error if database credentials are present", () => {
    const dbEnv = {
      DATABASE_URL: "postgres://user:password@localhost:5432/db",
    };

    expect(() => validatePublicEnv(dbEnv)).toThrowError(/SECURITY VIOLATION/);
  });

  it.each([
    "REDIS_URL",
    "CELERY_BROKER_URL",
    "AWS_SECRET_ACCESS_KEY",
    "NEXT_PUBLIC_API_TOKEN",
    "PRIVATE_KEY",
  ])("rejects private configuration key %s without exposing its value", (key) => {
    const privateValue = "must-not-appear-in-errors";

    expect(() => validatePublicEnv({ [key]: privateValue })).toThrowError(/SECURITY VIOLATION/);
    try {
      validatePublicEnv({ [key]: privateValue });
    } catch (error) {
      expect(String(error)).not.toContain(privateValue);
    }
  });

  it("rejects API base URLs containing embedded credentials", () => {
    expect(() =>
      validatePublicEnv({ NEXT_PUBLIC_API_BASE_URL: "https://user:password@example.com/api" })
    ).toThrowError(/SECURITY VIOLATION/);
  });

  it("exports safe public configuration properties", () => {
    expect(publicConfig.appName).toBe("CoachOS");
    expect(publicConfig.supportedLocales).toEqual(["fa-IR", "en-US"]);
    expect(publicConfig.apiBaseUrl).toBeDefined();
  });
});
