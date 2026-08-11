import { SUPPORTED_LOCALES } from "../i18n/config";

export type PublicEnvironment = Record<string, string | undefined>;

const PRIVATE_KEY_PATTERN =
  /(^|_)(DJANGO_SECRET_KEY|DATABASE_URL|REDIS_URL|CELERY_(?:BROKER_URL|RESULT_BACKEND)|AWS_(?:ACCESS_KEY_ID|SECRET_ACCESS_KEY|SESSION_TOKEN)|S3_(?:ACCESS_KEY|SECRET_KEY)|PASSWORD|PASSWD|TOKEN|AUTHORIZATION|PRIVATE_KEY|CLIENT_SECRET|SECRET_KEY)($|_)/i;

const SAFE_RUNTIME_KEYS = new Set(["NODE_ENV"]);

function isSafeApiBaseUrl(value: string): boolean {
  if (value.startsWith("/")) {
    return value.startsWith("/") && !value.startsWith("//");
  }

  try {
    const parsed = new URL(value);
    return (
      (parsed.protocol === "http:" || parsed.protocol === "https:") &&
      parsed.username === "" &&
      parsed.password === ""
    );
  } catch {
    return false;
  }
}

/**
 * Rejects private configuration keys before public frontend configuration is used.
 * Values are deliberately omitted from errors so configuration secrets cannot leak.
 * NODE_ENV is the only non-public runtime key accepted because framework tooling
 * supplies it and it is not secret configuration.
 */
export function validatePublicEnv(env: PublicEnvironment): void {
  for (const [key, value] of Object.entries(env)) {
    if (value === undefined || value === "") {
      continue;
    }

    if (PRIVATE_KEY_PATTERN.test(key)) {
      throw new Error(`SECURITY VIOLATION: private configuration key "${key}" is not allowed`);
    }

    if (!key.startsWith("NEXT_PUBLIC_") && !SAFE_RUNTIME_KEYS.has(key)) {
      throw new Error(`SECURITY VIOLATION: non-public configuration key "${key}" is not allowed`);
    }
  }

  const apiBaseUrl = env.NEXT_PUBLIC_API_BASE_URL;
  if (apiBaseUrl && !isSafeApiBaseUrl(apiBaseUrl)) {
    throw new Error("SECURITY VIOLATION: NEXT_PUBLIC_API_BASE_URL must be a credential-free HTTP(S) or relative URL");
  }
}

// Keep reads explicit so only these public values can be included in a client bundle.
const publicEnv: PublicEnvironment = {
  NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
  NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME,
};

validatePublicEnv(publicEnv);

export const publicConfig = Object.freeze({
  appName: publicEnv.NEXT_PUBLIC_APP_NAME?.trim() || "CoachOS",
  apiBaseUrl: publicEnv.NEXT_PUBLIC_API_BASE_URL?.trim() || "/api/v1",
  supportedLocales: [...SUPPORTED_LOCALES],
});
