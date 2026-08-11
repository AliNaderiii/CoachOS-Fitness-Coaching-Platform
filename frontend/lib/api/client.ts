import { publicConfig } from "../config/env";
import { DEFAULT_LOCALE, type Locale } from "../i18n/config";

const UNSAFE_METHODS = new Set(["POST", "PUT", "PATCH", "DELETE"]);
const UNSAFE_ERROR_CONTENT =
  /(traceback|stack trace|begin (?:rsa|openssh|pgp) private key|django-insecure-|postgres(?:ql)?:\/\/[^\s]+:[^\s]+@|authorization:\s*bearer)/i;

export interface ProblemDetails {
  type?: string;
  title: string;
  status: number;
  detail?: string;
  instance?: string;
  message_key?: string;
  field_errors?: Record<string, string[]>;
}

export class ApiError extends Error {
  readonly status: number;
  readonly problem: ProblemDetails;
  readonly requestId?: string;

  constructor(problem: ProblemDetails, requestId?: string) {
    super(`${problem.title} (${problem.status})`);
    this.name = "ApiError";
    this.status = problem.status;
    this.problem = problem;
    this.requestId = requestId;
  }
}

export interface ApiRequestOptions extends Omit<RequestInit, "headers" | "method"> {
  method?: string;
  headers?: HeadersInit;
  locale?: Locale;
  requestId?: string;
  idempotencyKey?: string;
  json?: unknown;
}

export function readCookie(name: string, cookieSource?: string): string | undefined {
  const source =
    cookieSource ?? (typeof document === "undefined" ? "" : document.cookie);
  const encodedName = `${encodeURIComponent(name)}=`;

  for (const part of source.split(";")) {
    const cookie = part.trim();
    if (cookie.startsWith(encodedName)) {
      const value = cookie.slice(encodedName.length);
      try {
        return decodeURIComponent(value);
      } catch {
        return undefined;
      }
    }
  }

  return undefined;
}

function buildApiUrl(path: string): string {
  if (!path || /^(?:[a-z]+:)?\/\//i.test(path)) {
    throw new TypeError("API request path must be relative");
  }

  const base = publicConfig.apiBaseUrl.replace(/\/$/, "");
  const relativePath = path.replace(/^\//, "");
  return `${base}/${relativePath}`;
}

function safeErrorText(value: unknown): string | undefined {
  if (typeof value !== "string" || value.length === 0) {
    return undefined;
  }
  return UNSAFE_ERROR_CONTENT.test(value) ? undefined : value.slice(0, 1000);
}

function toProblemDetails(body: unknown, response: Response): ProblemDetails {
  const candidate = body && typeof body === "object" ? (body as Record<string, unknown>) : {};
  const title = safeErrorText(candidate.title) || "Request failed";
  const detail = safeErrorText(candidate.detail);
  const fieldErrors: Record<string, string[]> = {};

  if (candidate.field_errors && typeof candidate.field_errors === "object") {
    for (const [field, messages] of Object.entries(candidate.field_errors as Record<string, unknown>)) {
      if (!Array.isArray(messages)) continue;
      const safeMessages = messages
        .map(safeErrorText)
        .filter((message): message is string => message !== undefined);
      if (safeMessages.length > 0) fieldErrors[field] = safeMessages;
    }
  }

  return {
    type: safeErrorText(candidate.type),
    title,
    status: response.status,
    detail,
    instance: safeErrorText(candidate.instance),
    message_key: safeErrorText(candidate.message_key),
    field_errors: Object.keys(fieldErrors).length > 0 ? fieldErrors : undefined,
  };
}

async function parseResponseBody(response: Response): Promise<unknown> {
  if (response.status === 204 || response.status === 205) {
    return undefined;
  }

  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("json")) {
    try {
      return await response.json();
    } catch {
      return undefined;
    }
  }

  const text = await response.text();
  return text || undefined;
}

/**
 * Minimal Phase 04 fetch wrapper. Authentication remains cookie-managed by the
 * browser; this client does not store access or refresh tokens.
 */
export async function request<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const {
    method: requestedMethod = "GET",
    headers: suppliedHeaders,
    locale = DEFAULT_LOCALE,
    requestId,
    idempotencyKey,
    json,
    ...requestInit
  } = options;
  const method = requestedMethod.toUpperCase();
  const headers = new Headers(suppliedHeaders);

  if (!headers.has("Accept")) headers.set("Accept", "application/json");
  headers.set("Accept-Language", locale);

  if (requestId) headers.set("X-Request-ID", requestId);
  if (idempotencyKey) headers.set("Idempotency-Key", idempotencyKey);

  const csrfToken = UNSAFE_METHODS.has(method) ? readCookie("csrftoken") : undefined;
  if (csrfToken) headers.set("X-CSRFToken", csrfToken);

  let body = requestInit.body;
  if (json !== undefined) {
    if (body !== undefined && body !== null) {
      throw new TypeError("Specify either body or json, not both");
    }
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(json);
  }

  const response = await fetch(buildApiUrl(path), {
    ...requestInit,
    method,
    headers,
    body,
    credentials: requestInit.credentials ?? "include",
  });
  const responseBody = await parseResponseBody(response);

  if (!response.ok) {
    throw new ApiError(toProblemDetails(responseBody, response), response.headers.get("X-Request-ID") || undefined);
  }

  return responseBody as T;
}

export const apiClient = Object.freeze({ request });
