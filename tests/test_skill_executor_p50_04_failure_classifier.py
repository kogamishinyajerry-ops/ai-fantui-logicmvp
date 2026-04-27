"""P50-04 — abort_reason classification.

Locks down: classify_failure recognizes every prefix the
orchestrator emits, classify_failures aggregates correctly,
the JSON shape is stable for the dashboard contract.
"""

from __future__ import annotations

import pytest

from well_harness.skill_executor.failure_classifier import (
    CategoryAggregate,
    ClassifiedFailure,
    FailureCategory,
    FailureClassification,
    classify_failure,
    classify_failures,
)
from well_harness.skill_executor.metrics import RecentFailure


def _failure(reason: str, exec_id: str = "EXEC-X") -> RecentFailure:
    return RecentFailure(
        exec_id=exec_id,
        proposal_id="PROP-X",
        state="FAILED",
        abort_reason=reason,
        finished_at="2026-04-27T13:00:00Z",
    )


# ─── 1. Prefix matching — orchestrator's actual abort_reason shapes


@pytest.mark.parametrize(
    "reason,expected_category,expected_detail",
    [
        ("planner: minimax 503 service unavailable",
         FailureCategory.PLANNER_ERROR, "minimax 503 service unavailable"),
        ("planner: timeout after 30s",
         FailureCategory.PLANNER_ERROR, "timeout after 30s"),
        ("baseline test runner: pytest not found",
         FailureCategory.TEST_RUNNER_ERROR, "pytest not found"),
        ("after test runner: timed out after 600s",
         FailureCategory.TEST_RUNNER_ERROR, "timed out after 600s"),
        ("test gate: 1 new failure: tests/test_foo.py::test_bar",
         FailureCategory.TEST_GATE, "1 new failure: tests/test_foo.py::test_bar"),
        ("apply: old_snippet not found in 'src/foo.py'",
         FailureCategory.APPLY_ERROR, "old_snippet not found in 'src/foo.py'"),
        ("git: git checkout -b feat/foo failed",
         FailureCategory.GIT_ERROR, "git checkout -b feat/foo failed"),
        ("gh: gh pr create returned 422",
         FailureCategory.GH_ERROR, "gh pr create returned 422"),
        ("cancelled by Kogami: changed mind",
         FailureCategory.USER_CANCEL, "Kogami: changed mind"),
        ("cancelled by anonymous",
         FailureCategory.USER_CANCEL, "anonymous"),
        ("user response: rejected",
         FailureCategory.USER_REJECT, "rejected"),
        ("user abort",
         FailureCategory.USER_REJECT, ""),
        ("unhandled: TypeError: NoneType has no attribute foo",
         FailureCategory.UNHANDLED,
         "TypeError: NoneType has no attribute foo"),
    ],
)
def test_classify_each_prefix_correctly(
    reason, expected_category, expected_detail
):
    result = classify_failure(reason)
    assert result.category == expected_category
    assert result.detail == expected_detail
    assert result.raw == reason


# ─── 2. Edge cases ──────────────────────────────────────────────────


def test_unknown_prefix_returns_other_with_full_text():
    result = classify_failure("something weird the dashboard hasn't seen")
    assert result.category == FailureCategory.OTHER
    assert result.detail == "something weird the dashboard hasn't seen"


def test_empty_reason_returns_other_with_placeholder():
    result = classify_failure("")
    assert result.category == FailureCategory.OTHER
    assert result.detail == "(no reason recorded)"
    assert result.raw == ""


def test_whitespace_only_reason_treated_as_empty():
    result = classify_failure("   \n  ")
    assert result.category == FailureCategory.OTHER
    assert result.detail == "(no reason recorded)"


def test_none_reason_treated_as_empty():
    """Defensive: if someone passes None (which shouldn't happen
    since RecentFailure declares str, but let's not crash)."""
    result = classify_failure(None)  # type: ignore[arg-type]
    assert result.category == FailureCategory.OTHER


# ─── 3. Aggregation ─────────────────────────────────────────────────


def test_classify_failures_empty_input_returns_zero_total():
    out = classify_failures([])
    assert out.total == 0
    assert out.by_category == []


def test_classify_failures_groups_by_category():
    failures = [
        _failure("planner: minimax 503"),
        _failure("planner: minimax 503"),  # same detail — should dedupe in sample
        _failure("planner: timeout"),
        _failure("git: branch already exists"),
    ]
    out = classify_failures(failures)
    assert out.total == 4
    by_cat = {a.category: a for a in out.by_category}
    assert by_cat[FailureCategory.PLANNER_ERROR].count == 3
    assert by_cat[FailureCategory.GIT_ERROR].count == 1


def test_aggregates_sorted_by_count_descending():
    failures = [
        _failure("git: bad branch"),
        _failure("planner: 503"),
        _failure("planner: 504"),
        _failure("planner: 503"),
    ]
    out = classify_failures(failures)
    # 3 planner errors > 1 git error
    assert out.by_category[0].category == FailureCategory.PLANNER_ERROR
    assert out.by_category[1].category == FailureCategory.GIT_ERROR


def test_sample_details_dedupe_and_capped():
    """5 identical 'minimax 503' should show as ONE sample, not 5.
    Different details accumulate up to sample_limit."""
    failures = [
        _failure("planner: minimax 503") for _ in range(5)
    ] + [
        _failure("planner: timeout"),
        _failure("planner: bad json"),
        _failure("planner: rate limit"),  # 4th distinct → exceeds default limit=3
    ]
    out = classify_failures(failures)
    planner = next(
        a for a in out.by_category
        if a.category == FailureCategory.PLANNER_ERROR
    )
    assert planner.count == 8
    # Default sample_limit=3 → at most 3 distinct details
    assert len(planner.sample_details) <= 3
    assert "minimax 503" in planner.sample_details


def test_sample_limit_override():
    failures = [
        _failure(f"planner: error variant {i}") for i in range(10)
    ]
    out = classify_failures(failures, sample_limit=5)
    planner = out.by_category[0]
    assert planner.count == 10
    assert len(planner.sample_details) == 5


# ─── 4. JSON serialization ──────────────────────────────────────────


def test_classified_failure_to_json_shape():
    cf = classify_failure("planner: minimax 503")
    j = cf.to_json()
    assert set(j.keys()) == {"category", "detail", "raw"}
    assert j["category"] == "planner_error"


def test_failure_classification_to_json_shape():
    out = classify_failures([
        _failure("planner: x"),
        _failure("git: y"),
    ])
    payload = out.to_json()
    assert set(payload.keys()) == {"total", "by_category"}
    assert payload["total"] == 2
    for entry in payload["by_category"]:
        assert set(entry.keys()) == {
            "category", "count", "sample_details"
        }


def test_category_values_are_lowercase_snake():
    """JSON contract: dashboard maps category strings to CSS
    classes — must stay stable lowercase_snake."""
    for cat in FailureCategory:
        assert cat.value.islower()
        assert " " not in cat.value


# ─── 5. Determinism ─────────────────────────────────────────────────


def test_tied_categories_sorted_by_name_for_stability():
    """Two categories with equal count should sort alphabetically
    so the dashboard doesn't reorder on every refresh."""
    failures = [
        _failure("git: x"),
        _failure("apply: y"),
    ]
    out = classify_failures(failures)
    cats = [a.category.value for a in out.by_category]
    # apply_error < git_error alphabetically
    assert cats == ["apply_error", "git_error"]
