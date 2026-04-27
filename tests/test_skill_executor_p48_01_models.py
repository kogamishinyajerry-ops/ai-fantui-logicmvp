"""P48-01 — skill executor models / dataclass round-trip.

User direction (2026-04-27): the skill that executes proposal
modifications must be a standardized, traceable, independently
developed module — not Claude reading a markdown spec. P48-01 lays
the data layer: typed dataclasses, audit JSON shape, state machine.
No LLM calls, no file edits, no git in this slice.

Locks down:
  - every dataclass round-trips through to_json/from_json without
    losing information
  - enum-valued fields parse back to the enum (not a stale string)
  - schema version constant is explicit and stable
  - default values produce a record that, when serialized + reread,
    equals the original
"""

from __future__ import annotations

import json

import pytest

from well_harness.skill_executor.models import (
    AUDIT_SCHEMA_VERSION,
    Ask,
    AskResponse,
    AuditSource,
    ExecutionEvent,
    ExecutionKind,
    ExecutionRecord,
    FileEdit,
    PlannedChange,
    TestResult,
    deserialize_record,
    now_iso,
    serialize_record,
)
from well_harness.skill_executor.states import ExecutionState


# ─── 1. Schema version is explicit ────────────────────────────────────


def test_schema_version_is_one():
    """If we ever bump this, the change should be deliberate (and
    accompanied by a migration). Hardcoding the expected value here
    forces a conscious update."""
    assert AUDIT_SCHEMA_VERSION == 1


# ─── 2. FileEdit round-trip ───────────────────────────────────────────


def test_file_edit_round_trip():
    edit = FileEdit(
        path="src/well_harness/controller.py",
        old_snippet="if foo:",
        new_snippet="if foo and bar:",
        reason="add hysteresis check",
    )
    assert FileEdit.from_json(edit.to_json()) == edit


def test_file_edit_default_reason_is_empty():
    edit = FileEdit(path="x.py", old_snippet="a", new_snippet="b")
    assert edit.reason == ""


# ─── 3. TestResult round-trip ─────────────────────────────────────────


def test_test_result_round_trip():
    tr = TestResult(
        passed=1448,
        failed=0,
        skipped=2,
        errors=0,
        duration_sec=132.4,
        ran_at="2026-04-27T12:00:00Z",
        failed_test_ids=["tests/test_foo.py::test_bar"],
    )
    assert TestResult.from_json(tr.to_json()) == tr


def test_test_result_minimum_fields():
    tr = TestResult(passed=10, failed=0)
    js = tr.to_json()
    assert js["passed"] == 10
    assert js["failed"] == 0
    assert js["skipped"] == 0
    assert js["failed_test_ids"] == []


# ─── 4. PlannedChange round-trip ──────────────────────────────────────


def test_planned_change_round_trip():
    plan = PlannedChange(
        rationale="tighten SW2 condition on L2",
        file_edits=[
            FileEdit(path="src/x.py", old_snippet="a", new_snippet="b"),
            FileEdit(path="src/y.py", old_snippet="c", new_snippet="d", reason="r"),
        ],
        test_changes=[FileEdit(path="tests/t.py", old_snippet="e", new_snippet="f")],
        estimated_loc=12,
        affected_namespaces=["logic_truth"],
        risk_assessment={"logic_truth": "yellow"},
        planner_prompt="pretend prompt",
        planner_response="pretend response",
        planner_started_at="2026-04-27T12:00:00Z",
        planner_finished_at="2026-04-27T12:00:30Z",
        llm_backend="minimax-m2.7-highspeed",
    )
    rt = PlannedChange.from_json(plan.to_json())
    assert rt.rationale == plan.rationale
    assert len(rt.file_edits) == 2
    assert rt.file_edits[0] == plan.file_edits[0]
    assert rt.affected_namespaces == ["logic_truth"]
    assert rt.risk_assessment == {"logic_truth": "yellow"}
    assert rt.llm_backend == "minimax-m2.7-highspeed"


def test_planned_change_empty_lists_default():
    plan = PlannedChange(rationale="x", file_edits=[])
    js = plan.to_json()
    assert js["test_changes"] == []
    assert js["affected_namespaces"] == []
    assert js["risk_assessment"] == {}


# ─── 5. Ask round-trip ────────────────────────────────────────────────


def test_ask_round_trip_with_response():
    ask = Ask(
        ask_id="ASK-20260427T120100abc",
        question="approve plan?",
        shown_in_workbench_at="2026-04-27T12:01:00Z",
        user_response=AskResponse.APPROVED,
        user_responded_at="2026-04-27T12:03:00Z",
        user_actor="Kogami",
        note="LGTM",
    )
    rt = Ask.from_json(ask.to_json())
    assert rt == ask
    # Serialized form uses the enum string value, not the enum object
    js = ask.to_json()
    assert js["user_response"] == "approved"


def test_ask_round_trip_pending():
    """A pending ask (waiting for engineer click) has user_response
    null. Round-trip must preserve None, not turn it into 'None'
    string or default-enum."""
    ask = Ask(ask_id="ASK-x", question="q")
    rt = Ask.from_json(ask.to_json())
    assert rt.user_response is None


@pytest.mark.parametrize("response", [r.value for r in AskResponse])
def test_ask_responses_parse(response):
    """All declared AskResponse values must round-trip from JSON."""
    ask = Ask(ask_id="ASK-x", question="q")
    js = ask.to_json()
    js["user_response"] = response
    rt = Ask.from_json(js)
    assert rt.user_response == AskResponse(response)


# ─── 6. ExecutionEvent round-trip ─────────────────────────────────────


def test_execution_event_state_transition():
    evt = ExecutionEvent(
        at="2026-04-27T12:00:00Z",
        kind="state_transition",
        from_state="INIT",
        to_state="PLANNING",
    )
    js = evt.to_json()
    # Serializer renames from_state→from / to_state→to to keep the
    # JSON compact and human-readable.
    assert js["from"] == "INIT"
    assert js["to"] == "PLANNING"
    rt = ExecutionEvent.from_json(js)
    assert rt == evt


def test_execution_event_breadcrumb_no_states():
    evt = ExecutionEvent(at="2026-04-27T12:00:00Z", kind="planner_invocation", note="x")
    js = evt.to_json()
    assert "from" not in js
    assert "to" not in js
    rt = ExecutionEvent.from_json(js)
    assert rt.from_state == ""
    assert rt.to_state == ""


# ─── 7. ExecutionRecord full round-trip ───────────────────────────────


def _make_full_record() -> ExecutionRecord:
    """A maximally-populated record so round-trip exercises every
    field. Used by the round-trip + serializer tests."""
    return ExecutionRecord(
        exec_id="EXEC-20260427T120000123456-abc123",
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id="PROP-20260426T075902988411-e27a6e",
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T12:00:00Z",
        finished_at="2026-04-27T12:35:00Z",
        state=ExecutionState.LANDED.value,
        executor_version="0.1.0",
        executor_host="MacBook-Pro.local",
        executor_user="Zhuanz",
        llm_backend="minimax-m2.7-highspeed",
        plan=PlannedChange(
            rationale="r",
            file_edits=[FileEdit(path="x.py", old_snippet="a", new_snippet="b")],
        ),
        asks=[
            Ask(
                ask_id="ASK-1",
                question="q",
                user_response=AskResponse.APPROVED,
                user_responded_at="2026-04-27T12:03:00Z",
                user_actor="Kogami",
            )
        ],
        tests_before=TestResult(passed=1448, failed=0),
        tests_after=TestResult(passed=1450, failed=0),
        branch="feat/exec-PROP-XXX",
        commits=["sha1", "sha2"],
        pr_url="https://github.com/x/y/pull/99",
        landed_sha="ec6f4fc94188fb3a7e68ef3763c3002b14ee105b",
        events=[
            ExecutionEvent(
                at="2026-04-27T12:00:00Z",
                kind="state_transition",
                from_state="INIT",
                to_state="PLANNING",
            ),
            ExecutionEvent(at="2026-04-27T12:00:30Z", kind="planner_invocation"),
        ],
    )


def test_execution_record_full_round_trip():
    record = _make_full_record()
    text = serialize_record(record)
    rt = deserialize_record(text)
    assert rt.exec_id == record.exec_id
    assert rt.kind == record.kind
    assert rt.audit_source == record.audit_source
    assert rt.state == record.state
    assert rt.plan is not None
    assert rt.plan.file_edits[0].path == "x.py"
    assert rt.asks[0].user_response == AskResponse.APPROVED
    assert rt.tests_before == record.tests_before
    assert rt.tests_after == record.tests_after
    assert rt.commits == record.commits
    assert rt.events[0].from_state == "INIT"
    assert rt.events[0].to_state == "PLANNING"


def test_execution_record_minimal():
    """Just the required fields — every optional field defaults
    cleanly through the round trip."""
    record = ExecutionRecord(
        exec_id="EXEC-20260427T120000123456-abc123",
        schema_version=AUDIT_SCHEMA_VERSION,
        proposal_id="PROP-foo",
        kind=ExecutionKind.MODIFY,
        audit_source=AuditSource.LIVE,
        started_at="2026-04-27T12:00:00Z",
    )
    text = serialize_record(record)
    rt = deserialize_record(text)
    assert rt.state == "INIT"
    assert rt.plan is None
    assert rt.asks == []
    assert rt.commits == []
    assert rt.events == []


def test_execution_record_serialized_form_is_pretty_json():
    """PR diff readability matters — the on-disk form should be
    indented and end in a newline so git renders sensibly."""
    record = _make_full_record()
    text = serialize_record(record)
    assert text.endswith("\n")
    assert "  " in text  # indent present
    # Round-trip the parsed form to make sure the indenting doesn't
    # break parse.
    parsed = json.loads(text)
    assert parsed["exec_id"] == record.exec_id


def test_execution_record_kind_serializes_to_string():
    record = _make_full_record()
    js = record.to_json()
    assert js["kind"] == "modify"
    assert js["audit_source"] == "live"


# ─── 8. now_iso shape ──────────────────────────────────────────────────


def test_now_iso_format():
    """Format must match proposal/audit history convention: ISO-8601
    UTC with 'Z' suffix, second precision."""
    s = now_iso()
    assert s.endswith("Z")
    assert "T" in s
    # YYYY-MM-DDTHH:MM:SSZ has 20 chars
    assert len(s) == 20
