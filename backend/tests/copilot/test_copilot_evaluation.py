"""Phase 11 — deterministic evaluation + red-team suite execution gate.

Executes the synthetic labeled harness end-to-end. A failure of any case fails
CI. Limitations of this gate (tiny synthetic corpus, deterministic provider)
are documented in the Phase 11 report; it proves control wiring, not model
accuracy.
"""

import pytest

from apps.copilot.eval.harness import run_evaluation


@pytest.mark.django_db
def test_evaluation_and_red_team_suite(monkeypatch):
    report = run_evaluation(monkeypatch_adapter=monkeypatch)
    failures = [case for case in report["cases"] if not case["passed"]]
    assert report["total"] == 16
    assert report["passed"] == report["total"], "Copilot evaluation failures: " + "; ".join(
        f"{c['id']}:{c['category']}:{c['evidence']}" for c in failures
    )
