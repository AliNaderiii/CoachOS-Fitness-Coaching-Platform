"""PII/context redaction helpers for the Copilot pipeline.

Everything originating from user-generated content (athlete notes, program
titles, exercise names, reasons, display names) passes through here before
entering a provider-bound context payload or a persisted context snapshot.
Redaction here is *minimization*, not a security boundary: authorization is
enforced before this layer.
"""

import re

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"(?<!\w)(\+?[0-9][0-9\s\-()]{6,17}[0-9])(?!\w)")
_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_WHITESPACE_RUN_RE = re.compile(r"\n{3,}")


def sanitize_untrusted_text(value, *, max_chars: int = 280) -> str:
    """Neutralize and truncate untrusted free text for prompt embedding.

    - strips control characters (never logs, never echoes raw);
    - redacts emails, phone-shaped numbers, and URLs;
    - collapses pathological newline runs;
    - hard-truncates to ``max_chars``.

    The result remains *untrusted data*: callers must embed it inside explicit
    delimiters and the output layer never treats it as instruction.
    """
    if value is None:
        return ""
    text = str(value)
    text = _CONTROL_RE.sub(" ", text)
    text = _EMAIL_RE.sub("[email]", text)
    text = _URL_RE.sub("[url]", text)
    text = _PHONE_RE.sub("[phone]", text)
    text = _WHITESPACE_RUN_RE.sub("\n\n", text).strip()
    if len(text) > max_chars:
        text = text[: max_chars - 1].rstrip() + "…"
    return text


def stable_join_for_hash(parts) -> str:
    """Deterministic concatenation used for hashing only (never displayed)."""
    return "\x1f".join(str(p) for p in parts)
