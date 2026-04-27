"""Group abort_reason strings into actionable failure categories.

Why: P50-02a's recent-failures list shows the last N failures
verbatim. Useful for debugging one execution, useless for spotting
trends. P50-04 classifies the reasons so the dashboard can answer
"what's been breaking lately?" — e.g. "5 planner: minimax 503 in
the last hour → call ops about MiniMax availability".

Categories map to the orchestrator's abort_reason prefixes
(see orchestrator.py):

    "planner: ..."              → PLANNER_ERROR
    "baseline test runner: ..." → TEST_RUNNER_ERROR
    "after test runner: ..."    → TEST_RUNNER_ERROR
    "test gate: ..."            → TEST_GATE
    "apply: ..."                → APPLY_ERROR
    "git: ..."                  → GIT_ERROR
    "gh: ..."                   → GH_ERROR
    "cancelled by ..."          → USER_CANCEL
    "user response: ..."        → USER_REJECT
    "user abort"                → USER_REJECT
    "unhandled: ..."            → UNHANDLED
    anything else                → OTHER

The detail extraction trims the prefix so dashboards can show a
short snippet ("minimax 503") rather than the verbose original.
"""

from __future__ import annotations

import dataclasses
import enum
from typing import Iterable

from well_harness.skill_executor.metrics import RecentFailure


class FailureCategory(str, enum.Enum):
    PLANNER_ERROR = "planner_error"
    TEST_RUNNER_ERROR = "test_runner_error"
    TEST_GATE = "test_gate"
    APPLY_ERROR = "apply_error"
    GIT_ERROR = "git_error"
    GH_ERROR = "gh_error"
    USER_CANCEL = "user_cancel"
    USER_REJECT = "user_reject"
    UNHANDLED = "unhandled"
    OTHER = "other"


# Order matters — first matching prefix wins. Keep most-specific
# prefixes earlier so e.g. "after test runner:" matches before a
# more general "test" prefix would.
_PREFIX_TO_CATEGORY: tuple[tuple[str, FailureCategory], ...] = (
    ("planner:", FailureCategory.PLANNER_ERROR),
    ("baseline test runner:", FailureCategory.TEST_RUNNER_ERROR),
    ("after test runner:", FailureCategory.TEST_RUNNER_ERROR),
    ("test gate:", FailureCategory.TEST_GATE),
    ("apply:", FailureCategory.APPLY_ERROR),
    ("git:", FailureCategory.GIT_ERROR),
    ("gh:", FailureCategory.GH_ERROR),
    ("cancelled by", FailureCategory.USER_CANCEL),
    ("user response:", FailureCategory.USER_REJECT),
    ("user abort", FailureCategory.USER_REJECT),
    ("unhandled:", FailureCategory.UNHANDLED),
)


@dataclasses.dataclass
class ClassifiedFailure:
    """One failure tagged with category + the post-prefix detail."""

    category: FailureCategory
    detail: str
    raw: str  # original abort_reason verbatim, for audit

    def to_json(self) -> dict:
        return {
            "category": self.category.value,
            "detail": self.detail,
            "raw": self.raw,
        }


@dataclasses.dataclass
class CategoryAggregate:
    """Per-category counts + sampled details so the UI can show
    a human-readable summary without re-grouping client-side."""

    category: FailureCategory
    count: int
    sample_details: list[str]  # up to N representative details

    def to_json(self) -> dict:
        return {
            "category": self.category.value,
            "count": self.count,
            "sample_details": list(self.sample_details),
        }


@dataclasses.dataclass
class FailureClassification:
    """Aggregate over a list of failures: total + per-category
    breakdown, sorted by count descending. Empty input produces
    total=0 and an empty by_category list."""

    total: int
    by_category: list[CategoryAggregate]

    def to_json(self) -> dict:
        return {
            "total": self.total,
            "by_category": [a.to_json() for a in self.by_category],
        }


def classify_failure(abort_reason: str) -> ClassifiedFailure:
    """Tag one abort_reason. Returns OTHER for unknown shapes
    rather than raising — the UI should still render.

    Detail extraction:
      - For "planner: minimax 503" → category=PLANNER_ERROR, detail="minimax 503"
      - For "cancelled by Kogami: stuck" → category=USER_CANCEL, detail="Kogami: stuck"
      - For "user abort" (no detail) → category=USER_REJECT, detail=""
      - For unrecognized prefix → category=OTHER, detail=full string
    """
    raw = (abort_reason or "").strip()
    if not raw:
        return ClassifiedFailure(
            category=FailureCategory.OTHER,
            detail="(no reason recorded)",
            raw="",
        )
    for prefix, category in _PREFIX_TO_CATEGORY:
        if raw.startswith(prefix):
            # Trim the prefix and any leading spaces/colons
            detail = raw[len(prefix):].lstrip(": ").strip()
            return ClassifiedFailure(
                category=category,
                detail=detail,
                raw=raw,
            )
    return ClassifiedFailure(
        category=FailureCategory.OTHER,
        detail=raw,
        raw=raw,
    )


def classify_failures(
    failures: Iterable[RecentFailure],
    *,
    sample_limit: int = 3,
) -> FailureClassification:
    """Aggregate. `failures` is consumed once. Output is sorted
    by count descending so the dashboard can show "biggest pain
    first"; ties broken by category name for determinism."""
    failures = list(failures)
    counts: dict[FailureCategory, int] = {}
    samples: dict[FailureCategory, list[str]] = {}

    for f in failures:
        classified = classify_failure(f.abort_reason)
        counts[classified.category] = counts.get(classified.category, 0) + 1
        bucket = samples.setdefault(classified.category, [])
        # Dedupe: don't fill the sample list with the same exact
        # detail repeated. Common case: same minimax 503 5 times
        # in a row should show as one sample with count=5, not
        # 5 identical samples.
        if classified.detail and classified.detail not in bucket:
            if len(bucket) < sample_limit:
                bucket.append(classified.detail)

    aggregates = [
        CategoryAggregate(
            category=cat,
            count=count,
            sample_details=samples.get(cat, []),
        )
        for cat, count in counts.items()
    ]
    # Sort: higher count first, ties broken by category name
    aggregates.sort(key=lambda a: (-a.count, a.category.value))

    return FailureClassification(
        total=len(failures),
        by_category=aggregates,
    )
