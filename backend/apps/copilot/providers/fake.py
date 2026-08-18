"""Deterministic fake provider — the only fully implemented adapter (Phase 11).

Design rules:

- Fully deterministic: identical context payloads produce identical drafts
  (a variation counter is mixed in for regenerate flows).
- Treats every user-supplied field inside the context as inert data: drafts
  are composed from numeric aggregates, dates, and allowlisted identifiers
  only. User free text is NEVER interpolated verbatim into output, which makes
  prompt-injection-through-content incapable of altering output structure.
- Language is explicit: ``fa-IR`` or ``en-US`` templates; nothing else can be
  produced (Arabic is outside the template space by construction).
- Emits synthetic token/cost estimates so the quota, budget, and metering
  code paths run identically in CI.
"""

import hashlib
import json

from ..constants import (
    CAPABILITIES,
    GENERATION_LANGUAGES,
)
from .base import (
    ProviderOutputMalformed,
    ProviderRequest,
    ProviderResponse,
    estimate_tokens,
)

SLUG = "fake-deterministic"
MODEL_IDENTIFIER = "fake-deterministic-1"

# Synthetic per-1k-token cost (micro USD) so budget accounting is exercised.
FAKE_COST_PER_1K_INPUT = 400  # $0.0004
FAKE_COST_PER_1K_OUTPUT = 800  # $0.0008


def _digest(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()


def _json_size(value) -> int:
    return len(json.dumps(value, ensure_ascii=False, sort_keys=True))


class DeterministicFakeProvider:
    slug = SLUG

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        if request.capability not in CAPABILITIES:
            raise ProviderOutputMalformed("unknown capability")
        language = request.generation_language
        if language not in GENERATION_LANGUAGES:
            language = "en-US"
        builder = {
            "summarize_progress": self._progress_summary,
            "draft_check_in": self._check_in_message,
            "suggest_program_adjustment": self._program_adjustment,
        }[request.capability]
        payload = builder(request.context_payload, language)
        input_tokens = estimate_tokens(
            request.system_directive + json.dumps(request.context_payload, ensure_ascii=False)
        )
        output_tokens = estimate_tokens(json.dumps(payload, ensure_ascii=False))
        cost = int(
            input_tokens / 1000 * FAKE_COST_PER_1K_INPUT
            + output_tokens / 1000 * FAKE_COST_PER_1K_OUTPUT
        )
        return ProviderResponse(
            payload=payload,
            model_identifier=MODEL_IDENTIFIER,
            provider_request_id=f"fake-{_digest(request.output_schema, json.dumps(payload, sort_keys=True, ensure_ascii=False))[:20]}",
            input_tokens_est=input_tokens,
            output_tokens_est=output_tokens,
            cost_micro_usd=cost,
        )

    # ------------------------------------------------------------------ I18N
    _T = {
        "limitation_no_sources": {
            "fa-IR": "داده کافی برای استناد به همه موارد وجود ندارد؛ موارد بدون منبع به عنوان نامطمئن علامت‌گذاری شد‌اند.",
            "en-US": "Not all statements could be sourced; unsourced items are flagged as uncertain.",
        },
        "summary_line": {
            "fa-IR": "در {days} روز گذشته {done} جلسه تکمیل و {missed} جلسه از دست رفته است.",
            "en-US": "In the last {days} days, {done} sessions were completed and {missed} were missed.",
        },
        "highlight_load": {
            "fa-IR": "سنگین‌ترین ست ثبت‌شده: {name} با {load} کیلوگرم در {reps} تکرار.",
            "en-US": "Heaviest recorded set: {name} at {load} kg for {reps} reps.",
        },
        "concern_flags": {
            "fa-IR": "{count} پرچم بازخورد ذهنی ثبت شده است (غیربالینی)؛ در گفت‌وگوی حضوری بررسی شود.",
            "en-US": "{count} subjective feedback flags recorded (non-clinical); review in person.",
        },
        "concern_missed": {
            "fa-IR": "{count} جلسه از دست رفته در این بازه؛ دلیل آن را با ورزشکار هماهنگ کنید.",
            "en-US": "{count} missed sessions in this period; align on the reason with the athlete.",
        },
        "no_sessions": {
            "fa-IR": "فعالیتی در این بازه ثبت نشده است؛ خلاصه صرفاً بر همین مبنا محدود است.",
            "en-US": "No activity was recorded in this period; the summary is limited accordingly.",
        },
        "checkin_subject": {
            "fa-IR": "پیگیری تمرینی — {name}",
            "en-US": "Training check-in — {name}",
        },
        "checkin_body_done": {
            "fa-IR": "سلام {name}، در {days} روز گذشته {done} جلسه را تکمیل کرده‌ای. آیا نکته‌ای درباره تمرینات اخیرت هست که بخواهی مطرح کنی؟",
            "en-US": "Hi {name}, you completed {done} sessions in the last {days} days. Anything about recent training you would like to raise?",
        },
        "checkin_body_none": {
            "fa-IR": "سلام {name}، در {days} روز گذشته جلسه‌ای ثبت نشده است. دوست دارم وضعیتت را بشنوم و در صورت نیاز برنامه را با هم مرور کنیم.",
            "en-US": "Hi {name}, no sessions were logged in the last {days} days. I would like to hear how things are going and review the plan together if needed.",
        },
        "checkin_tone": {"fa-IR": "حمایتگرانه و کوتاه", "en-US": "Supportive and concise"},
        "adjustment_day": {
            "fa-IR": "روز {day}: {title}",
            "en-US": "Day {day}: {title}",
        },
        "rationale_substitute": {
            "fa-IR": "جایگزینی پیشنهادی از کتابخانه منتشرشده سازمان بر اساس الگوی حرکتی مشابه؛ تأیید نهایی با مربی است.",
            "en-US": "Suggested substitute from the organization published library with a similar movement pattern; final decision rests with the coach.",
        },
        "rationale_reduce_load": {
            "fa-IR": "با توجه به {count} پرچم بازخورد ذهنی، کاهش موقت شدت پیشنهاد می‌شود؛ تصمیم نهایی با مربی است.",
            "en-US": "Given {count} subjective feedback flags, a temporary intensity reduction is suggested; final decision rests with the coach.",
        },
        "rationale_default": {
            "fa-IR": "پیشنهاد آزمایشی محافظه‌کارانه برای بازبینی مربی؛ بر اساس داده‌های مجاز همین اجرا.",
            "en-US": "Conservative trial suggestion for coach review; grounded in this run's authorized data.",
        },
        "adjustment_disclaimer": {
            "fa-IR": "این پیش‌نویس هوش مصنوعی است، نسخه پزشکی یا تغییر خودکار برنامه نیست و فقط با تأیید صریح مربی معتبر می‌شود.",
            "en-US": "AI-generated draft. Not medical advice and not an automatic program change; valid only after explicit coach approval.",
        },
        "empty_day_title": {"fa-IR": "روز تمرینی", "en-US": "Training day"},
    }

    def _t(self, key: str, language: str) -> str:
        return self._T[key][language]

    # ------------------------------------------------------------- BUILDERS
    def _progress_summary(self, ctx: dict, language: str) -> dict:
        sessions = ctx.get("sessions") or []
        done = sum(1 for s in sessions if s.get("status") == "completed")
        missed = sum(1 for s in sessions if s.get("status") in ("skipped",))
        flags = (ctx.get("feedback_flag_summary") or {}).get("total", 0)

        highlights: list[str] = []
        aggregates = sorted(
            ctx.get("set_log_aggregates") or [],
            key=lambda row: (row.get("load_kg", 0), row.get("reps", 0)),
            reverse=True,
        )[:3]
        for row in aggregates:
            highlights.append(
                self._t("highlight_load", language).format(
                    name=row.get("exercise_name") or row.get("exercise_id"),
                    load=row.get("load_kg"),
                    reps=row.get("reps"),
                )
            )
        if not sessions:
            highlights.append(self._t("no_sessions", language))

        concerns: list[str] = []
        if flags:
            concerns.append(self._t("concern_flags", language).format(count=flags))
        if missed:
            concerns.append(self._t("concern_missed", language).format(count=missed))

        limitations = list(ctx.get("limitations") or [])
        limitations.append(self._t("limitation_no_sources", language))

        return {
            "schema_name": "ai_progress_summary.v1",
            "schema_version": 1,
            "ai_generated": True,
            "requires_human_review": True,
            "athlete_display_name": ctx.get("subject_display_name") or "",
            "period_days": int(ctx.get("period_days") or 14),
            "sessions_completed": done,
            "sessions_missed": missed,
            "summary": self._t("summary_line", language).format(
                days=int(ctx.get("period_days") or 14), done=done, missed=missed
            ),
            "highlights": highlights[:6],
            "concerns": concerns[:6],
            "limitations": limitations[:10],
            "source_ids": self._cite(ctx, limit=6),
        }

    def _check_in_message(self, ctx: dict, language: str) -> dict:
        sessions = ctx.get("sessions") or []
        done = sum(1 for s in sessions if s.get("status") == "completed")
        name = ctx.get("subject_display_name") or ("ورزشکار" if language == "fa-IR" else "athlete")
        period = int(ctx.get("period_days") or 14)
        if done:
            body = self._t("checkin_body_done", language).format(name=name, done=done, days=period)
        else:
            body = self._t("checkin_body_none", language).format(name=name, days=period)
        limitations = list(ctx.get("limitations") or [])
        limitations.append(
            "این پیام پیش‌نویس است و به‌صورت خودکار ارسال نمی‌شود."
            if language == "fa-IR"
            else "This message is a draft and is never sent automatically."
        )
        return {
            "schema_name": "ai_check_in_message.v1",
            "schema_version": 1,
            "ai_generated": True,
            "requires_human_review": True,
            "subject": self._t("checkin_subject", language).format(name=name)[:140],
            "body": body[:1600],
            "tone": self._t("checkin_tone", language),
            "limitations": limitations[:10],
            "source_ids": self._cite(ctx, limit=4),
        }

    def _program_adjustment(self, ctx: dict, language: str) -> dict:
        allowlist = ctx.get("exercise_allowlist") or []
        variation = int(ctx.get("variation") or 0)
        flags = (ctx.get("feedback_flag_summary") or {}).get("total", 0)
        snapshot = ctx.get("assignment_snapshot") or {}
        day_title = self._t("empty_day_title", language)
        if snapshot.get("days"):
            first_day = snapshot["days"][variation % len(snapshot["days"])]
            day_title = self._t("adjustment_day", language).format(
                day=first_day.get("day_number"), title=first_day.get("title") or ""
            )[:160]

        suggestions = []
        for index, entry in enumerate(allowlist[:3]):
            if index == 0 and flags:
                change_type = "reduce_load"
                rationale = self._t("rationale_reduce_load", language).format(count=flags)
            elif index == 0:
                change_type = "substitute"
                rationale = self._t("rationale_substitute", language)
            else:
                change_type = "coach_note"
                rationale = self._t("rationale_default", language)
            suggestions.append(
                {
                    "exercise_id": entry["exercise_id"],
                    "change_type": change_type,
                    "rationale": rationale[:280],
                }
            )

        limitations = list(ctx.get("limitations") or [])
        limitations.append(
            "پیشنهادها به کتابخانه منتشرشده سازمان محدود است و هرگز به‌صورت خودکار اعمال نمی‌شود."
            if language == "fa-IR"
            else "Suggestions are constrained to the organization published library and never applied automatically."
        )
        return {
            "schema_name": "ai_program_adjustment.v1",
            "schema_version": 1,
            "ai_generated": True,
            "requires_human_review": True,
            "target_day_title": day_title,
            "suggestions": suggestions[:8],
            "safety_disclaimer": self._t("adjustment_disclaimer", language)[:400],
            "limitations": limitations[:10],
            "source_ids": self._cite(ctx, limit=6),
        }

    # ---------------------------------------------------------------- UTILS
    @staticmethod
    def _cite(ctx: dict, *, limit: int) -> list[str]:
        """Citations come exclusively from the authorized context sources."""
        ids = []
        for row in ctx.get("sessions") or []:
            ids.append(row["source_id"])
        for row in ctx.get("set_log_aggregates") or []:
            ids.append(row["source_id"])
        assignment = ctx.get("active_assignment") or {}
        if assignment.get("source_id"):
            ids.append(assignment["source_id"])
        seen = []
        for sid in ids:
            if sid not in seen:
                seen.append(sid)
        return seen[:limit]
