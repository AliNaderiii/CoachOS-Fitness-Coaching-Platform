"""Phase 11 — AI Copilot constants and capability registry.

The capability registry is the single allowlist for what the Copilot may do.
Anything not listed here is rejected at the policy gate (fail closed).
"""

POLICY_VERSION = "2026-08-16.v1"

CAPABILITY_SUMMARIZE_PROGRESS = "summarize_progress"
CAPABILITY_DRAFT_CHECK_IN = "draft_check_in"
CAPABILITY_SUGGEST_PROGRAM_ADJUSTMENT = "suggest_program_adjustment"

#: Capability metadata: output schema id + whether the draft is consequential
#: (mandatory approve-before-use). All P0 capabilities are consequential.
CAPABILITIES = {
    CAPABILITY_SUMMARIZE_PROGRESS: {
        "output_schema": "ai_progress_summary.v1",
        "requires_human_review": True,
        "label_en": "Progress summary",
        "label_fa": "خلاصه پیشرفت",
    },
    CAPABILITY_DRAFT_CHECK_IN: {
        "output_schema": "ai_check_in_message.v1",
        "requires_human_review": True,
        "label_en": "Check-in message draft",
        "label_fa": "پیش‌نویس پیام پیگیری",
    },
    CAPABILITY_SUGGEST_PROGRAM_ADJUSTMENT: {
        "output_schema": "ai_program_adjustment.v1",
        "requires_human_review": True,
        "label_en": "Program adjustment suggestion",
        "label_fa": "پیشنهاد تعدیل برنامه",
    },
}

RUN_STATUS_CHOICES = [
    "queued",
    "running",
    "succeeded",
    "failed",
    "cancelled",
    "expired",
]

OUTPUT_STATUS_CHOICES = ["draft", "edited", "approved", "rejected", "quarantined", "expired"]

REPORT_TYPES = ["unsafe", "incorrect", "privacy", "hallucinated_source", "other"]

GENERATION_LANGUAGES = ["fa-IR", "en-US"]

# --- Policy / denial reason codes (safe, enumerable; never echo user text) ---
REASON_FEATURE_DISABLED = "feature_disabled"
REASON_CAPABILITY_UNKNOWN = "capability_unknown"
REASON_CAPABILITY_DISABLED = "capability_disabled"
REASON_PROHIBITED_INTENT = "prohibited_intent"
REASON_NOT_AUTHORIZED = "not_authorized"
REASON_RATE_LIMITED = "rate_limited"
REASON_QUOTA_EXHAUSTED = "quota_exhausted"
REASON_BUDGET_EXHAUSTED = "budget_exhausted"
REASON_PROVIDER_UNAVAILABLE = "provider_unavailable"
REASON_PROVIDER_TIMEOUT = "provider_timeout"
REASON_OUTPUT_INVALID = "output_invalid"
REASON_CONTEXT_TOO_LARGE = "context_too_large"

# Prohibited-intent screening. Defense in depth only: keyword screening is NOT
# claimed as a safety mechanism on its own (see AI_GOVERNANCE.md §10); scoped
# capabilities + structured output + human review + evaluation are the control.
# Patterns match against normalized lowercase free text supplied in request
# parameters (never against trusted system directives).
PROHIBITED_INTENT_PATTERNS = [
    # English medical / clinical
    "diagnose",
    "diagnosis",
    "prescribe",
    "prescription",
    "rehab plan",
    "rehabilitation",
    "physical therapy",
    "physiotherapy",
    "medication",
    "medicine",
    "ibuprofen",
    "painkiller",
    "steroid",
    "supplement dosage",
    "creatine dosage",
    "dosage",
    "eating disorder",
    "anorexia",
    "bulimia",
    "emergency",
    "chest pain",
    "heart attack",
    "clinical",
    "therapy plan",
    "injury prediction",
    "return to play clearance",
    "medical advice",
    "mental health diagnosis",
    "depression treatment",
    "suicide",
    # Prompt-policy fishing (treated as prohibited intent in parameters)
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "reveal your prompt",
    "show your instructions",
    "developer message",
    "api key",
    "access token",
    "password for",
    "other tenant",
    "another athlete's",
    # Persian medical / clinical
    "تشخیص پزشکی",
    "تشخیص بیماری",
    "نسخه",
    "دارو",
    "قرص",
    "مکمل",
    "دوز مصرفی",
    "بازتوانی درمانی",
    "فیزیوتراپی",
    "اختلال خوردن",
    "اورژانس",
    "درد قفسه سینه",
    "درمان افسردگی",
    "خودکشی",
    # Persian prompt-policy fishing
    "نادیده بگیر دستور",
    "دستورالعمل سیستم",
    "پرامپت سیستم",
    "کلید api",
]

# Categories of data the context builder never includes (transparency/testing).
CONTEXT_OMISSIONS = [
    "progress_photos",
    "body_metrics",
    "feedback_flag_details",
    "anatomical_locations",
    "contact_information",
    "other_athletes",
    "billing_data",
    "credentials",
]

DEFAULT_RATE_LIMIT_PER_MINUTE = 10
DEFAULT_DAILY_RUN_QUOTA_PER_ACTOR = 20
DEFAULT_DAILY_RUN_QUOTA_PER_ORG = 100
DEFAULT_DAILY_COST_CAP_MICRO_USD = 5_000_000  # 5.00 USD equivalent dev default
DEFAULT_CONTEXT_RETENTION_DAYS = 30
DEFAULT_MAX_ATTEMPTS = 2  # initial attempt + one bounded retry (transient only)
