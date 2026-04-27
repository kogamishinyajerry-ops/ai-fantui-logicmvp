"""Test gate — compares before/after TestResults to decide whether
edits are safe to ship.

Per Q5(b) (2026-04-27 user direction), the gate refuses to advance
to PR_OPEN if EITHER:

  1. tests_after.passed < tests_before.passed   (some tests stopped
                                                  passing — likely
                                                  caused by edits)
  2. any test that was passing in tests_before is now in
     tests_after.failed_test_ids (a specific regression caused by
     edits)
  3. tests_after.errors > tests_before.errors   (new pytest-internal
                                                  errors — usually
                                                  collection failures
                                                  from a bad edit)

Q5(c) (non-trivial change must add ≥1 new test) is deferred to a
future phase.

The gate is a pure function — no IO, no subprocess. It produces a
GateResult with `ok` + `reason` + structured comparison numbers
the audit log can persist for review.
"""

from __future__ import annotations

import dataclasses

from well_harness.skill_executor.models import TestResult


@dataclasses.dataclass
class GateResult:
    """Outcome of the test-gate comparison."""

    ok: bool
    reason: str = ""           # human-readable; empty on pass
    passed_delta: int = 0      # after.passed - before.passed (>=0 expected)
    new_failures: list[str] = dataclasses.field(default_factory=list)
    became_passing: list[str] = dataclasses.field(default_factory=list)
    error_delta: int = 0       # after.errors - before.errors


def check_test_gate(
    *,
    before: TestResult,
    after: TestResult,
) -> GateResult:
    """Compare `before` and `after`; return GateResult(ok=True/False).

    Rules (any failure → gate.ok=False):
      A) after.passed < before.passed
      B) some failed_test_id in after.failed_test_ids was NOT in
         before.failed_test_ids
      C) after.errors > before.errors

    Notes:
      - A test that was already failing before AND is still failing
        after is FINE — the edit didn't regress it. The gate's
        concern is "what did THIS edit break", not "are there
        pre-existing problems".
      - Tests that FLIPPED from failing to passing are reported in
        `became_passing` for transparency but DON'T affect ok.
      - Skipped tests are ignored entirely.
    """
    before_failing = set(before.failed_test_ids or [])
    after_failing = set(after.failed_test_ids or [])

    new_failures = sorted(after_failing - before_failing)
    became_passing = sorted(before_failing - after_failing)
    passed_delta = after.passed - before.passed
    error_delta = after.errors - before.errors

    reasons: list[str] = []
    if passed_delta < 0:
        reasons.append(
            f"after.passed ({after.passed}) < before.passed "
            f"({before.passed}); {-passed_delta} test(s) stopped passing"
        )
    if new_failures:
        reasons.append(
            f"new failure(s) introduced: {new_failures}"
        )
    if error_delta > 0:
        reasons.append(
            f"after.errors ({after.errors}) > before.errors "
            f"({before.errors}); pytest-level error introduced"
        )

    return GateResult(
        ok=not reasons,
        reason="; ".join(reasons),
        passed_delta=passed_delta,
        new_failures=new_failures,
        became_passing=became_passing,
        error_delta=error_delta,
    )
