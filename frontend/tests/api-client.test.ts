import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError, readCookie, request } from "../lib/api/client";

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  return new Response(JSON.stringify(body), { ...init, headers });
}

describe("Phase 04 API client foundation", () => {
  beforeEach(() => {
    document.cookie = "csrftoken=; Max-Age=0; path=/";
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("extracts and decodes the readable Django CSRF cookie", () => {
    expect(readCookie("csrftoken", "theme=dark; csrftoken=abc%20123; language=fa-IR")).toBe(
      "abc 123"
    );
    expect(readCookie("missing", "csrftoken=value")).toBeUndefined();
  });

  it("adds CSRF and locale headers only to a state-changing request", async () => {
    document.cookie = "csrftoken=csrf-test-value; path=/";
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ ok: true }));
    vi.stubGlobal("fetch", fetchMock);

    await request("meta", { method: "POST", locale: "fa-IR", json: { safe: true } });

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = new Headers(init.headers);
    expect(headers.get("Accept-Language")).toBe("fa-IR");
    expect(headers.get("X-CSRFToken")).toBe("csrf-test-value");
    expect(headers.get("Content-Type")).toBe("application/json");
    expect(init.credentials).toBe("include");
  });

  it("omits CSRF on safe methods and forwards an explicit request ID", async () => {
    document.cookie = "csrftoken=csrf-test-value; path=/";
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ ok: true }));
    vi.stubGlobal("fetch", fetchMock);

    await request("meta", { locale: "en-US", requestId: "018f47a6-7b44-7f15-8a17-acde48001122" });

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = new Headers(init.headers);
    expect(headers.get("Accept-Language")).toBe("en-US");
    expect(headers.get("X-CSRFToken")).toBeNull();
    expect(headers.get("X-Request-ID")).toBe("018f47a6-7b44-7f15-8a17-acde48001122");
    expect(headers.get("Idempotency-Key")).toBeNull();
  });

  it("forwards an idempotency key only when the caller explicitly supplies one", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ ok: true }));
    vi.stubGlobal("fetch", fetchMock);

    await request("meta", { idempotencyKey: "explicit-operation-key" });

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(new Headers(init.headers).get("Idempotency-Key")).toBe("explicit-operation-key");
  });

  it("maps RFC 7807 responses to a typed error without retaining server stack fields", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse(
        {
          type: "https://coach.example/problems/validation",
          title: "Validation failed",
          status: 422,
          detail: "One or more fields are invalid.",
          message_key: "errors.validation",
          stack: "private server stack must not be retained",
        },
        { status: 422, headers: { "X-Request-ID": "request-from-server" } }
      )
    );
    vi.stubGlobal("fetch", fetchMock);

    try {
      await request("validation-example");
      throw new Error("Expected request to reject");
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      const apiError = error as ApiError;
      expect(apiError.status).toBe(422);
      expect(apiError.problem).toEqual({
        type: "https://coach.example/problems/validation",
        title: "Validation failed",
        status: 422,
        detail: "One or more fields are invalid.",
        instance: undefined,
        message_key: "errors.validation",
        field_errors: undefined,
      });
      expect(apiError.requestId).toBe("request-from-server");
      expect(apiError).not.toHaveProperty("stack", "private server stack must not be retained");
    }
  });
});
