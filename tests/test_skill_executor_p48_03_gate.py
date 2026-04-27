"""P48-03 — test gate decision logic.

Pure function test: given two TestResults (before / after), did the
edits regress anything? Three failure modes:
  A) after.passed < before.passed
  B) new failed_test_id introduced
  C) after.errors > before.errors

A test that flips from failing to passing is fine; the gate even
records `became_passing` for the audit so reviewers see the
positive delta.
"""

from __future__ import annotations

import pytest

from well_harness.skill_executor.gate import GateResult, check_test_gate
from well_harness.skill_executor.models import TestResult


def _result(
    *,
    passed: int = 0,
    failed: int = 0,
    skipped: int = 0,
    errors: int = 0,
    failed_ids: list[str] | None = None,
) -> TestResult:
    return TestResult(
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
        failed_test_ids=failed_ids or [],
    )


# ─── 1. Happy path: pass count strictly grows ─────────────────────────


def test_gate_pass_when_more_tests_pass():
    before = _result(passed=10, failed=0)
    after = _result(passed=12, failed=0)
    out = check_test_gate(before=before, after=after)
    assert out.ok is True
    assert out.passed_delta == 2
    assert out.new_failures == []


def test_gate_pass_when_count_unchanged():
    before = _result(passed=10, failed=0)
    after = _result(passed=10, failed=0)
    out = check_test_gate(before=before, after=after)
    assert out.ok is True
    assert out.passed_delta == 0


# ─── 2. Failure mode A: passed count dropped ──────────────────────────


def test_gate_fail_when_passed_count_drops():
    before = _result(passed=10, failed=0)
    after = _result(passed=9, failed=1, failed_ids=["tests/x.py::test_new"])
    out = check_test_gate(before=before, after=after)
    assert out.ok is False
    assert "stopped passing" in out.reason
    assert out.passed_delta == -1


# ─── 3. Failure mode B: new failure introduced ───────────────────────


def test_gate_fail_when_new_failure_appears():
    """Even if passed count is OK, a SPECIFIC test that wasn't
    failing before is failing now — that's the regression
    signature we care most about."""
    before = _result(passed=10, failed=1, failed_ids=["tests/x.py::existing_fail"])
    after = _result(
        passed=10,
        failed=2,
        failed_ids=["tests/x.py::existing_fail", "tests/x.py::new_fail"],
    )
    out = check_test_gate(before=before, after=after)
    assert out.ok is False
    assert "tests/x.py::new_fail" in out.reason
    assert out.new_failures == ["tests/x.py::new_fail"]


def test_gate_pass_when_pre_existing_failure_persists():
    """A test that was already failing AND is still failing isn't
    regression — the edit didn't cause it. The gate should NOT
    block on it."""
    before = _result(passed=10, failed=1, failed_ids=["tests/x.py::flaky"])
    after = _result(passed=10, failed=1, failed_ids=["tests/x.py::flaky"])
    out = check_test_gate(before=before, after=after)
    assert out.ok is True


def test_gate_records_became_passing():
    """A test that was failing and is now passing — the gate
    surfaces this in `became_passing` for the audit, but doesn't
    block on it (since fixing things is good)."""
    before = _result(passed=10, failed=1, failed_ids=["tests/x.py::was_broken"])
    after = _result(passed=11, failed=0)
    out = check_test_gate(before=before, after=after)
    assert out.ok is True
    assert out.became_passing == ["tests/x.py::was_broken"]


# ─── 4. Failure mode C: errors increased ─────────────────────────────


def test_gate_fail_when_errors_increased():
    before = _result(passed=10, failed=0, errors=0)
    after = _result(passed=10, failed=0, errors=1)
    out = check_test_gate(before=before, after=after)
    assert out.ok is False
    assert "error" in out.reason.lower()


def test_gate_pass_when_errors_unchanged():
    before = _result(passed=10, failed=0, errors=2)
    after = _result(passed=10, failed=0, errors=2)
    out = check_test_gate(before=before, after=after)
    assert out.ok is True


def test_gate_pass_when_errors_decreased():
    """Pre-existing errors that go away are good news, like
    became_passing — should not block."""
    before = _result(passed=10, failed=0, errors=2)
    after = _result(passed=10, failed=0, errors=0)
    out = check_test_gate(before=before, after=after)
    assert out.ok is True


# ─── 5. Composite failures: multiple reasons in single message ───────


def test_gate_fail_combines_multiple_reasons():
    """If both passed dropped AND new failures appeared, the
    reason text should mention both — review needs the full
    picture."""
    before = _result(passed=10, failed=1, failed_ids=["x"])
    after = _result(
        passed=8,
        failed=3,
        failed_ids=["x", "y", "z"],
    )
    out = check_test_gate(before=before, after=after)
    assert out.ok is False
    assert "stopped passing" in out.reason
    assert "y" in out.reason
    assert "z" in out.reason


# ─── 6. Skipped tests ignored ─────────────────────────────────────────


def test_gate_ignores_skipped_count():
    """Skipped tests aren't a regression signal either way."""
    before = _result(passed=10, failed=0, skipped=2)
    after = _result(passed=10, failed=0, skipped=5)
    out = check_test_gate(before=before, after=after)
    assert out.ok is True
