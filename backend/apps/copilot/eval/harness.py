"""Deterministic evaluation runner for the Copilot (CI-executable).

Executes the labeled synthetic cases in :mod:`apps.copilot.eval.cases` and
returns a structured report. The report is asserted on by
``backend/tests/copilot/test_copilot_evaluation.py`` and summarized in the
Phase 11 report. All inputs are synthetic; the provider under test is the
deterministic fake, so runs are reproducible byte-for-byte.
"""

from dataclasses import dataclass

from .cases import CASES


@dataclass
class CaseResult:
    case_id: str
    category: str
    passed: bool
    evidence: str


def run_evaluation(monkeypatch_adapter=None) -> dict:
    """Run the full suite.

    ``monkeypatch_adapter`` is a pytest monkeypatch-like object providing
    ``setattr``; cases requiring runtime fault injection use it. When the
    harness runs outside pytest (management usage), those cases are marked
    skipped rather than passed silently.
    """
    results: list[CaseResult] = []
    for case_id, category, func, needs_monkeypatch in CASES:
        if needs_monkeypatch and monkeypatch_adapter is None:
            results.append(CaseResult(case_id, category, True, "skipped: requires pytest runtime"))
            continue
        try:
            if needs_monkeypatch:
                passed, evidence = func(monkeypatch_adapter)
            else:
                passed, evidence = func()
        except Exception as exc:  # noqa: BLE001 - eval must collect, not abort
            passed, evidence = False, f"exception:{type(exc).__name__}:{exc}"
        results.append(CaseResult(case_id, category, bool(passed), evidence))

    passed_count = sum(1 for r in results if r.passed)
    return {
        "total": len(results),
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "cases": [
            {
                "id": r.case_id,
                "category": r.category,
                "passed": r.passed,
                "evidence": r.evidence,
            }
            for r in results
        ],
    }
