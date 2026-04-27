"""Typed dataclasses for the skill-executor audit record + helpers
to round-trip them to/from JSON.

Schema is locked by tests in
`tests/test_skill_executor_p48_01_models.py`. The on-disk JSON shape
matches the dataclass fields 1:1 — there's no separate serializer.
ExecutionRecord.to_json() / from_json() are the canonical pair.

If you change a field here, bump AUDIT_SCHEMA_VERSION; the validator
will reject older audit files until they're migrated, and the CI
gate (P48-05) will refuse PRs whose audit was written against an
unknown schema version.
"""

from __future__ import annotations

import dataclasses
import enum
import json
from datetime import datetime, timezone
from typing import Any


AUDIT_SCHEMA_VERSION: int = 1


class ExecutionKind(str, enum.Enum):
    """What kind of change is being executed.

    `modify`     — a regular forward change (the usual case)
    `revert`     — a P47-02 revert proposal: undo a prior commit's
                   changes per Q2(b) plan/ask/edit semantics
    `backfill`   — Q7(a): a synthesized audit for a PR that
                   pre-dates P48 and was executed under the old
                   markdown skill. State is fixed at LANDED with
                   sparse fields.
    """

    MODIFY = "modify"
    REVERT = "revert"
    BACKFILL = "backfill"


class AuditSource(str, enum.Enum):
    """How the audit was produced.

    `live`     — written by the live skill_executor module as the
                 run progressed. The default and the trustworthy case.
    `backfill` — synthesized after the fact from git/git-log + manual
                 reconstruction. Marked separately so a reader can
                 distinguish "we observed this" from "we believe this
                 is what happened".
    """

    LIVE = "live"
    BACKFILL = "backfill"


@dataclasses.dataclass
class FileEdit:
    """One file change the planner produced. The pair (old_snippet,
    new_snippet) is what the executor will hand to Edit; matching is
    exact-string. The planner writes both; the executor verifies
    old_snippet exists in the file before applying."""

    path: str
    old_snippet: str
    new_snippet: str
    reason: str = ""

    def to_json(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_json(cls, data: dict) -> "FileEdit":
        return cls(
            path=str(data["path"]),
            old_snippet=str(data["old_snippet"]),
            new_snippet=str(data["new_snippet"]),
            reason=str(data.get("reason") or ""),
        )


@dataclasses.dataclass
class TestResult:
    """Pytest summary captured before/after edits. The executor
    refuses to merge if tests_after fails this comparator:

        passed_after >= passed_before
        AND no test that was passing in tests_before is now failing
    """

    # Tell pytest this dataclass is NOT a test class to collect
    # (the name starts with "Test", which pytest auto-collects by
    # default; without this attr it warns + skips on every run).
    __test__ = False

    passed: int
    failed: int
    skipped: int = 0
    errors: int = 0
    duration_sec: float = 0.0
    ran_at: str = ""  # ISO 8601 UTC, with 'Z'
    failed_test_ids: list[str] = dataclasses.field(default_factory=list)

    def to_json(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_json(cls, data: dict) -> "TestResult":
        return cls(
            passed=int(data["passed"]),
            failed=int(data["failed"]),
            skipped=int(data.get("skipped", 0) or 0),
            errors=int(data.get("errors", 0) or 0),
            duration_sec=float(data.get("duration_sec", 0.0) or 0.0),
            ran_at=str(data.get("ran_at") or ""),
            failed_test_ids=list(data.get("failed_test_ids") or []),
        )


@dataclasses.dataclass
class PlannedChange:
    """The output of the planner LLM. Every field that's not raw
    LLM text is structured so the executor can validate before any
    file is touched.

    `affected_namespaces`: which P47-01 namespaces this plan claims
    to touch. The executor cross-checks file_edits[].path against
    each namespace's file globs and refuses to apply a plan whose
    edits stray outside.

    `risk_assessment`: planner-self-assessed risk per namespace,
    "red" | "yellow" | "green". Recorded for review; not
    machine-acted on in P48-01."""

    rationale: str
    file_edits: list[FileEdit]
    test_changes: list[FileEdit] = dataclasses.field(default_factory=list)
    estimated_loc: int = 0
    affected_namespaces: list[str] = dataclasses.field(default_factory=list)
    risk_assessment: dict[str, str] = dataclasses.field(default_factory=dict)
    planner_prompt: str = ""
    planner_response: str = ""
    planner_started_at: str = ""
    planner_finished_at: str = ""
    llm_backend: str = ""

    def to_json(self) -> dict:
        return {
            "rationale": self.rationale,
            "file_edits": [e.to_json() for e in self.file_edits],
            "test_changes": [e.to_json() for e in self.test_changes],
            "estimated_loc": self.estimated_loc,
            "affected_namespaces": list(self.affected_namespaces),
            "risk_assessment": dict(self.risk_assessment),
            "planner_prompt": self.planner_prompt,
            "planner_response": self.planner_response,
            "planner_started_at": self.planner_started_at,
            "planner_finished_at": self.planner_finished_at,
            "llm_backend": self.llm_backend,
        }

    @classmethod
    def from_json(cls, data: dict) -> "PlannedChange":
        return cls(
            rationale=str(data.get("rationale") or ""),
            file_edits=[FileEdit.from_json(e) for e in (data.get("file_edits") or [])],
            test_changes=[FileEdit.from_json(e) for e in (data.get("test_changes") or [])],
            estimated_loc=int(data.get("estimated_loc") or 0),
            affected_namespaces=list(data.get("affected_namespaces") or []),
            risk_assessment=dict(data.get("risk_assessment") or {}),
            planner_prompt=str(data.get("planner_prompt") or ""),
            planner_response=str(data.get("planner_response") or ""),
            planner_started_at=str(data.get("planner_started_at") or ""),
            planner_finished_at=str(data.get("planner_finished_at") or ""),
            llm_backend=str(data.get("llm_backend") or ""),
        )


class AskResponse(str, enum.Enum):
    """Engineer's verdict on a plan presented in ASKING state."""

    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_CHANGES = "needs_changes"


@dataclasses.dataclass
class Ask:
    """One presentation of a plan to the engineer. Captures the
    full "what was shown / what was answered / when" so an audit
    reader can replay the decision.

    `shown_in_workbench_at`: when the workbench inbox first
    rendered the approval card.
    `user_responded_at`: when the engineer clicked
    Approve/Reject/Needs-Changes.
    `user_actor`: name from the workbench session (matches
    proposal.author_name conventions).
    """

    ask_id: str
    question: str
    shown_in_workbench_at: str = ""
    user_response: AskResponse | None = None
    user_responded_at: str = ""
    user_actor: str = ""
    note: str = ""

    def to_json(self) -> dict:
        return {
            "ask_id": self.ask_id,
            "question": self.question,
            "shown_in_workbench_at": self.shown_in_workbench_at,
            "user_response": self.user_response.value if self.user_response else None,
            "user_responded_at": self.user_responded_at,
            "user_actor": self.user_actor,
            "note": self.note,
        }

    @classmethod
    def from_json(cls, data: dict) -> "Ask":
        raw_resp = data.get("user_response")
        return cls(
            ask_id=str(data["ask_id"]),
            question=str(data["question"]),
            shown_in_workbench_at=str(data.get("shown_in_workbench_at") or ""),
            user_response=AskResponse(raw_resp) if raw_resp else None,
            user_responded_at=str(data.get("user_responded_at") or ""),
            user_actor=str(data.get("user_actor") or ""),
            note=str(data.get("note") or ""),
        )


@dataclasses.dataclass
class ExecutionEvent:
    """One entry in the events log. Every state transition writes
    one; the planner / executor may also write notes between
    transitions for breadcrumbs."""

    at: str
    kind: str
    note: str = ""
    from_state: str = ""
    to_state: str = ""

    def to_json(self) -> dict:
        out = {"at": self.at, "kind": self.kind, "note": self.note}
        if self.from_state:
            out["from"] = self.from_state
        if self.to_state:
            out["to"] = self.to_state
        return out

    @classmethod
    def from_json(cls, data: dict) -> "ExecutionEvent":
        return cls(
            at=str(data["at"]),
            kind=str(data["kind"]),
            note=str(data.get("note") or ""),
            from_state=str(data.get("from") or ""),
            to_state=str(data.get("to") or ""),
        )


@dataclasses.dataclass
class ExecutionRecord:
    """The full audit record persisted to
    `.planning/skill_executions/EXEC-<id>.json`.

    Required fields are enforced by the validator; optional fields
    default to empty/None and are filled in as the run progresses.
    """

    # Identity
    exec_id: str
    schema_version: int
    proposal_id: str
    kind: ExecutionKind
    audit_source: AuditSource

    # Timing
    started_at: str
    finished_at: str = ""

    # State machine
    state: str = "INIT"  # serialized ExecutionState value

    # Environment
    executor_version: str = "0.1.0"
    executor_host: str = ""
    executor_user: str = ""
    llm_backend: str = ""

    # Lifecycle artifacts (filled in as the run progresses)
    plan: PlannedChange | None = None
    asks: list[Ask] = dataclasses.field(default_factory=list)
    tests_before: TestResult | None = None
    tests_after: TestResult | None = None
    branch: str = ""
    commits: list[str] = dataclasses.field(default_factory=list)
    pr_url: str = ""
    landed_sha: str = ""
    abort_reason: str = ""
    events: list[ExecutionEvent] = dataclasses.field(default_factory=list)
    # P49-02a: governance gate verdict + reviewer outcome. Populated
    # after the planner runs if any rule fired. Stored as a dict for
    # forward-compat with future rule shapes; the contents are the
    # GovernanceVerdict.to_json() plus a `decision` ("approved" |
    # "rejected") and `decided_at` once a reviewer responds.
    governance_review: dict | None = None
    # P49-04: dry-run mode. When True, the orchestrator runs through
    # PLANNING/EDITING/TESTING but does NOT commit, push, or open a
    # PR; instead it captures the file diff and reverts. The audit
    # ends in DRY_RUN_COMPLETE so a reviewer can preview the change
    # before approving. dry_run_diff is the captured `git diff`
    # output (unified diff text); empty when no edits applied.
    dry_run: bool = False
    dry_run_diff: str = ""

    def to_json(self) -> dict:
        return {
            "exec_id": self.exec_id,
            "schema_version": self.schema_version,
            "proposal_id": self.proposal_id,
            "kind": self.kind.value,
            "audit_source": self.audit_source.value,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "state": self.state,
            "executor_version": self.executor_version,
            "executor_host": self.executor_host,
            "executor_user": self.executor_user,
            "llm_backend": self.llm_backend,
            "plan": self.plan.to_json() if self.plan else None,
            "asks": [a.to_json() for a in self.asks],
            "tests_before": self.tests_before.to_json() if self.tests_before else None,
            "tests_after": self.tests_after.to_json() if self.tests_after else None,
            "branch": self.branch,
            "commits": list(self.commits),
            "pr_url": self.pr_url,
            "landed_sha": self.landed_sha,
            "abort_reason": self.abort_reason,
            "events": [e.to_json() for e in self.events],
            "governance_review": (
                dict(self.governance_review)
                if self.governance_review is not None
                else None
            ),
            "dry_run": self.dry_run,
            "dry_run_diff": self.dry_run_diff,
        }

    @classmethod
    def from_json(cls, data: dict) -> "ExecutionRecord":
        return cls(
            exec_id=str(data["exec_id"]),
            schema_version=int(data["schema_version"]),
            proposal_id=str(data["proposal_id"]),
            kind=ExecutionKind(data["kind"]),
            audit_source=AuditSource(data["audit_source"]),
            started_at=str(data["started_at"]),
            finished_at=str(data.get("finished_at") or ""),
            state=str(data.get("state") or "INIT"),
            executor_version=str(data.get("executor_version") or "0.1.0"),
            executor_host=str(data.get("executor_host") or ""),
            executor_user=str(data.get("executor_user") or ""),
            llm_backend=str(data.get("llm_backend") or ""),
            plan=(PlannedChange.from_json(data["plan"]) if data.get("plan") else None),
            asks=[Ask.from_json(a) for a in (data.get("asks") or [])],
            tests_before=(
                TestResult.from_json(data["tests_before"])
                if data.get("tests_before")
                else None
            ),
            tests_after=(
                TestResult.from_json(data["tests_after"])
                if data.get("tests_after")
                else None
            ),
            branch=str(data.get("branch") or ""),
            commits=list(data.get("commits") or []),
            pr_url=str(data.get("pr_url") or ""),
            landed_sha=str(data.get("landed_sha") or ""),
            abort_reason=str(data.get("abort_reason") or ""),
            events=[ExecutionEvent.from_json(e) for e in (data.get("events") or [])],
            governance_review=(
                dict(data["governance_review"])
                if data.get("governance_review") is not None
                else None
            ),
            dry_run=bool(data.get("dry_run", False)),
            dry_run_diff=str(data.get("dry_run_diff") or ""),
        )


def now_iso() -> str:
    """ISO-8601 UTC with second precision and a trailing Z. Same
    format used by proposals so audit timestamps are directly
    comparable to history[]."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def serialize_record(record: ExecutionRecord) -> str:
    """Pretty JSON, deterministic key order via dataclass field
    order, trailing newline. Designed to diff cleanly in PR
    review."""
    return json.dumps(record.to_json(), ensure_ascii=False, indent=2) + "\n"


def deserialize_record(text: str) -> ExecutionRecord:
    """Parse JSON text into an ExecutionRecord. Caller is
    responsible for catching JSONDecodeError; the record validator
    (audit.py) wraps both calls behind a single AuditSchemaError."""
    return ExecutionRecord.from_json(json.loads(text))
